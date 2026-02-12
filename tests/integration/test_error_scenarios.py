import pytest
from unittest.mock import MagicMock, patch
from googleapiclient.errors import HttpError
from app.services.gmail.scan import scan_emails
from app.services.gmail.delete import delete_emails_by_sender
from app.core import state


class TestErrorScenarios:
    """Integration tests for error handling."""

    @pytest.fixture(autouse=True)
    def reset_state(self):
        state.reset_scan()
        state.reset_delete_scan()
        yield
        state.reset_scan()

    def test_scan_gmail_api_error(self):
        """Test scan handling of Gmail API errors."""
        mock_service = MagicMock()
        mock_messages = mock_service.users().messages()

        # Simulate API error
        error_content = b'{"error": {"code": 500, "message": "Internal Error"}}'
        error_resp = MagicMock(status=500, reason="Internal Error")
        mock_messages.list.side_effect = HttpError(
            resp=error_resp, content=error_content
        )

        with patch(
            "app.services.gmail.scan.get_gmail_service",
            return_value=(mock_service, None),
        ):
            scan_emails(limit=10)

            assert state.scan_status["done"] is True
            assert "Internal Error" in state.scan_status["error"]

    def test_delete_rate_limit_handling(self):
        """Test handling of rate limits during deletion."""
        mock_service = MagicMock()
        mock_messages = mock_service.users().messages()

        # Mock finding messages - ensure NO nextPageToken key to avoid infinite loop
        mock_messages.list.return_value.execute.return_value = {
            "messages": [{"id": "msg1"}]
        }

        # Simulate Rate Limit error on batch execution
        error_content = b'{"error": {"code": 429, "message": "Rate Limit Exceeded"}}'
        error_resp = MagicMock(status=429, reason="Rate Limit Exceeded")

        # Mock batchModify to raise error
        mock_batch_modify = mock_messages.batchModify.return_value
        mock_batch_modify.execute.side_effect = HttpError(
            resp=error_resp, content=error_content
        )

        with patch(
            "app.services.gmail.delete.get_gmail_service",
            return_value=(mock_service, None),
        ):
            # We expect it to handle the error gracefully (log it and return error message)
            result = delete_emails_by_sender("sender@example.com")

            assert result["success"] is False
            assert "Rate Limit Exceeded" in result["message"]

    def test_auth_failure_handling(self):
        """Test handling of authentication failures."""
        # Mock get_gmail_service returning error
        with patch(
            "app.services.gmail.scan.get_gmail_service",
            return_value=(None, "Auth Error"),
        ):
            scan_emails(limit=10)

            assert state.scan_status["done"] is True
            assert state.scan_status["error"] == "Auth Error"

    def test_scan_invalid_limit(self):
        """Test scan with invalid limit."""
        scan_emails(limit=-1)
        assert state.scan_status["done"] is True
        assert "Limit must be greater than 0" in state.scan_status["error"]
