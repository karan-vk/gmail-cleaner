import pytest
from unittest.mock import MagicMock, patch, call
from app.services.gmail.delete import delete_emails_bulk_background
from app.services.gmail.archive import archive_emails_background
from app.services.gmail.mark_read import mark_emails_as_read
from app.core import state


class TestGmailOperations:
    """Integration tests for Gmail service operations."""

    @pytest.fixture(autouse=True)
    def reset_state(self):
        state.reset_scan()
        state.reset_delete_scan()
        state.reset_mark_read()
        yield
        state.reset_scan()

    def test_delete_emails_bulk(self):
        """Test bulk deletion of emails from multiple senders."""
        mock_service = MagicMock()
        mock_messages = mock_service.users().messages()

        # Mock finding messages for a sender
        # First call: list messages for sender1
        # Second call: list messages for sender2
        mock_messages.list.side_effect = [
            MagicMock(execute=lambda: {"messages": [{"id": "msg1"}, {"id": "msg2"}]}),
            MagicMock(execute=lambda: {"messages": [{"id": "msg3"}]}),
        ]

        # Mock batch modify
        mock_batch_modify = mock_messages.batchModify.return_value
        mock_batch_modify.execute.return_value = {}

        with patch(
            "app.services.gmail.delete.get_gmail_service",
            return_value=(mock_service, None),
        ):
            senders = ["sender1@example.com", "sender2@example.com"]
            delete_emails_bulk_background(senders)

            # Verify list was called for each sender
            assert mock_messages.list.call_count == 2

            # Verify batch modify was called
            # delete_emails_bulk_background collects all IDs and then calls batchModify in chunks of 1000
            # We have 3 messages total, so 1 call to batchModify
            assert mock_messages.batchModify.call_count == 1
            args, kwargs = mock_messages.batchModify.call_args
            assert set(kwargs["body"]["ids"]) == {"msg1", "msg2", "msg3"}
            assert kwargs["body"]["addLabelIds"] == ["TRASH"]

            # Verify state update
            assert state.delete_bulk_status["done"] is True
            assert (
                "Successfully deleted 3 emails" in state.delete_bulk_status["message"]
            )

    def test_archive_emails(self):
        """Test archiving emails from multiple senders."""
        mock_service = MagicMock()
        mock_messages = mock_service.users().messages()

        # Mock finding messages
        mock_messages.list.return_value.execute.return_value = {
            "messages": [{"id": "msg1"}],
            "nextPageToken": None,
        }

        # Mock batch modify (archive = remove INBOX label)
        mock_batch_modify = mock_messages.batchModify.return_value
        mock_batch_modify.execute.return_value = {}

        with patch(
            "app.services.gmail.archive.get_gmail_service",
            return_value=(mock_service, None),
        ):
            senders = ["sender@example.com"]
            archive_emails_background(senders)

            # Verify batch modify was called
            assert mock_messages.batchModify.call_count == 1
            args, kwargs = mock_messages.batchModify.call_args
            assert kwargs["body"]["ids"] == ["msg1"]
            assert kwargs["body"]["removeLabelIds"] == ["INBOX"]

            # Verify state
            assert state.archive_status["done"] is True
            assert "Archived 1 emails" in state.archive_status["message"]

    def test_mark_emails_as_read(self):
        """Test marking emails as read."""
        mock_service = MagicMock()
        mock_messages = mock_service.users().messages()

        # Mock finding unread messages (label:UNREAD)
        mock_messages.list.return_value.execute.return_value = {
            "messages": [{"id": "msg1"}, {"id": "msg2"}],
            "nextPageToken": None,
        }

        # Mock batch modify
        mock_batch_modify = mock_messages.batchModify.return_value
        mock_batch_modify.execute.return_value = {}

        with patch(
            "app.services.gmail.mark_read.get_gmail_service",
            return_value=(mock_service, None),
        ):
            mark_emails_as_read(count=10)

            # Verify list called with q='is:unread' (default query in mark_read.py)
            call_args = mock_messages.list.call_args
            # The query is constructed as "is:unread" + filters
            assert "is:unread" in call_args[1]["q"]

            # Verify batch modify (remove UNREAD label)
            assert mock_messages.batchModify.call_count == 1
            args, kwargs = mock_messages.batchModify.call_args
            assert kwargs["body"]["ids"] == ["msg1", "msg2"]
            assert kwargs["body"]["removeLabelIds"] == ["UNREAD"]

            assert state.mark_read_status["done"] is True
            assert "Marked 2 emails as read" in state.mark_read_status["message"]

    def test_batch_efficiency(self):
        """Test that operations use batching efficiently."""
        mock_service = MagicMock()
        mock_messages = mock_service.users().messages()

        # Mock finding many messages (e.g. 1500)
        # We need multiple pages
        page1 = [{"id": f"msg{i}"} for i in range(500)]
        page2 = [{"id": f"msg{i}"} for i in range(500, 1000)]
        page3 = [{"id": f"msg{i}"} for i in range(1000, 1500)]

        mock_messages.list.side_effect = [
            MagicMock(execute=lambda: {"messages": page1, "nextPageToken": "token1"}),
            MagicMock(execute=lambda: {"messages": page2, "nextPageToken": "token2"}),
            MagicMock(execute=lambda: {"messages": page3}),
        ]

        # Mock batch modify
        mock_batch_modify = mock_messages.batchModify.return_value
        mock_batch_modify.execute.return_value = {}

        with patch(
            "app.services.gmail.delete.get_gmail_service",
            return_value=(mock_service, None),
        ):
            senders = ["sender@example.com"]
            delete_emails_bulk_background(senders)

            # Verify list called 3 times (pagination)
            assert mock_messages.list.call_count == 3

            # Verify batch modify called 2 times (1000 limit per batch)
            # 1500 messages -> 1 batch of 1000, 1 batch of 500
            assert mock_messages.batchModify.call_count == 2

            # Verify first batch size
            args1, kwargs1 = mock_messages.batchModify.call_args_list[0]
            assert len(kwargs1["body"]["ids"]) == 1000

            # Verify second batch size
            args2, kwargs2 = mock_messages.batchModify.call_args_list[1]
            assert len(kwargs2["body"]["ids"]) == 500
