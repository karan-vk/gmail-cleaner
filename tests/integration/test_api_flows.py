import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.core import state


class TestApiFlows:
    """Integration tests for API flows."""

    @pytest.fixture(autouse=True)
    def reset_state(self):
        """Reset global state before each test."""
        state.reset_scan()
        state.reset_delete_scan()
        state.reset_mark_read()
        state.current_user = {"email": None, "logged_in": False}
        yield
        state.reset_scan()

    def test_scan_flow(self, client: TestClient):
        """Test the full scan flow: start scan -> check status -> get results."""

        # Mock the Gmail service and its responses
        mock_service = MagicMock()
        mock_messages = mock_service.users().messages()

        # Mock list messages response
        mock_messages.list.return_value.execute.return_value = {
            "messages": [{"id": "msg1"}, {"id": "msg2"}],
            "nextPageToken": None,
        }

        # Mock batch execution
        def mock_batch_callback(callback):
            # Simulate batch responses
            callback(
                "req1",
                {
                    "payload": {
                        "headers": [
                            {
                                "name": "List-Unsubscribe",
                                "value": "<https://example.com/unsub>",
                            },
                            {"name": "From", "value": "Sender <sender@example.com>"},
                            {"name": "Subject", "value": "Test Subject"},
                            {
                                "name": "Date",
                                "value": "Thu, 12 Feb 2026 10:00:00 +0000",
                            },
                        ]
                    }
                },
                None,
            )
            return MagicMock()

        mock_service.new_batch_http_request.side_effect = lambda callback: MagicMock(
            execute=lambda: mock_batch_callback(callback), add=MagicMock()
        )

        # Patch get_gmail_service to return our mock
        with patch(
            "app.services.gmail.scan.get_gmail_service",
            return_value=(mock_service, None),
        ):
            # 1. Start Scan
            response = client.post(
                "/api/scan", json={"limit": 10, "filters": {"older_than": "30d"}}
            )
            assert response.status_code == 200
            assert response.json() == {"status": "started"}

            # 2. Check Status (Background task should have completed synchronously in TestClient)
            response = client.get("/api/status")
            assert response.status_code == 200
            status_data = response.json()
            assert status_data["done"] is True

            # 3. Get Results
            response = client.get("/api/results")
            assert response.status_code == 200
            results = response.json()
            assert len(results) == 1
            assert results[0]["domain"] == "example.com"
            assert results[0]["count"] == 1

    def test_auth_flow(self, client: TestClient):
        """Test authentication flow."""

        # 1. Check initial auth status
        response = client.get("/api/auth-status")
        assert response.status_code == 200
        assert response.json()["logged_in"] is False

        # 2. Trigger Sign In
        # We mock get_gmail_service to simulate the auth process starting
        with patch("app.services.auth.get_gmail_service") as mock_get_service:
            mock_get_service.return_value = (None, "Sign-in started")

            response = client.post("/api/sign-in")
            assert response.status_code == 200
            assert response.json() == {"status": "signing_in"}

        # 3. Simulate successful login by mocking check_login_status
        with patch("app.api.status.check_login_status") as mock_check_login:
            mock_check_login.return_value = {
                "logged_in": True,
                "email": "test@example.com",
            }

            # 4. Check auth status again
            response = client.get("/api/auth-status")
            assert response.status_code == 200
            assert response.json()["logged_in"] is True
            assert response.json()["email"] == "test@example.com"

        # 5. Sign Out
        with patch("app.services.auth.os.remove") as mock_remove:
            response = client.post("/api/sign-out")
            assert response.status_code == 200
            assert response.json()["success"] is True

            # Verify state is cleared (check_login_status mock is gone, so it should be logged out)
            response = client.get("/api/auth-status")
            assert response.json()["logged_in"] is False

    def test_delete_scan_flow(self, client: TestClient):
        """Test delete scan flow."""
        mock_service = MagicMock()
        mock_messages = mock_service.users().messages()

        # Mock list messages
        mock_messages.list.return_value.execute.return_value = {
            "messages": [{"id": "msg1"}],
            "nextPageToken": None,
        }

        # Mock batch execution for delete scan
        def mock_batch_callback(callback):
            callback(
                "req1",
                {
                    "payload": {
                        "headers": [
                            {"name": "From", "value": "Spam <spam@example.com>"},
                            {"name": "Subject", "value": "Spam Subject"},
                            {
                                "name": "Date",
                                "value": "Thu, 12 Feb 2026 10:00:00 +0000",
                            },
                        ],
                        "sizeEstimate": 1024,
                    }
                },
                None,
            )
            return MagicMock()

        mock_service.new_batch_http_request.side_effect = lambda callback: MagicMock(
            execute=lambda: mock_batch_callback(callback), add=MagicMock()
        )

        with patch(
            "app.services.gmail.delete.get_gmail_service",
            return_value=(mock_service, None),
        ):
            # 1. Start Delete Scan
            response = client.post("/api/delete-scan", json={"limit": 10})
            assert response.status_code == 200

            # 2. Check Status
            response = client.get("/api/delete-scan-status")
            assert response.json()["done"] is True

            # 3. Get Results
            response = client.get("/api/delete-scan-results")
            assert response.status_code == 200
            results = response.json()
            assert len(results) > 0
            assert results[0]["email"] == "spam@example.com"
