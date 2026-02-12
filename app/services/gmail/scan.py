"""
Gmail Scanning Operations
--------------------------
Functions for scanning emails to find unsubscribe links.
Optimized for large inboxes (100k+ emails) with streaming mode.
"""

import logging
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from email.utils import parsedate_to_datetime
from typing import Optional, Generator, List, Dict, Any

from app.core import state
from app.core.config import settings
from app.core.exceptions import GmailCleanerError
from app.services.auth import get_gmail_service
from app.services.gmail.error_handler import handle_gmail_errors, with_retry
from app.services.gmail.helpers import (
    build_gmail_query,
    get_unsubscribe_from_headers,
    get_sender_info,
    get_subject,
)

logger = logging.getLogger(__name__)


class UnsubscribeData:
    """Memory-efficient data structure for unsubscribe tracking."""
    
    __slots__ = ['link', 'count', 'subjects', 'type', 'sender', 'email', 'first_date', 'last_date']
    
    def __init__(self):
        self.link: Optional[str] = None
        self.count: int = 0
        self.subjects: List[str] = []
        self.type: Optional[str] = None
        self.sender: str = ""
        self.email: str = ""
        self.first_date: Optional[str] = None
        self.last_date: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'link': self.link,
            'count': self.count,
            'subjects': self.subjects,
            'type': self.type,
            'sender': self.sender,
            'email': self.email,
            'first_date': self.first_date,
            'last_date': self.last_date,
        }


@handle_gmail_errors
def scan_emails(limit: int = 500, filters: Optional[dict] = None):
    """
    Scan emails for unsubscribe links using Gmail Batch API.
    Optimized for large inboxes with streaming mode support.
    """
    if limit <= 0:
        state.reset_scan()
        state.scan_status["error"] = "Limit must be greater than 0"
        state.scan_status["done"] = True
        return

    state.reset_scan()
    state.scan_status["message"] = "Connecting to Gmail..."

    service, error = get_gmail_service()
    if error:
        state.scan_status["error"] = error
        state.scan_status["done"] = True
        return

    try:
        state.scan_status["message"] = "Fetching email list..."
        query = build_gmail_query(filters)
        
        # Use streaming mode for large inboxes
        if settings.enable_streaming and limit > settings.chunk_size:
            _scan_streaming(service, query, limit)
        else:
            _scan_standard(service, query, limit)
            
    except Exception as e:
        logger.exception("Error during email scan")
        state.scan_status["error"] = str(e)
        state.scan_status["done"] = True


def _scan_standard(service, query: str, limit: int) -> None:
    """Standard scan mode for smaller inboxes."""
    message_ids = []
    page_token = None

    while len(message_ids) < limit:
        list_params = {
            "userId": "me",
            "maxResults": min(500, limit - len(message_ids)),
        }
        if page_token:
            list_params["pageToken"] = page_token
        if query:
            list_params["q"] = query

        result = service.users().messages().list(**list_params).execute()
        messages = result.get("messages", [])
        message_ids.extend([m["id"] for m in messages])

        page_token = result.get("nextPageToken")
        if not page_token:
            break

    if not message_ids:
        state.scan_status["message"] = "No emails found"
        state.scan_status["done"] = True
        return

    total = len(message_ids)
    state.scan_status["message"] = f"Found {total} emails. Scanning..."

    unsubscribe_data: Dict[str, dict] = defaultdict(
        lambda: {
            "link": None,
            "count": 0,
            "subjects": [],
            "type": None,
            "sender": "",
            "email": "",
            "first_date": None,
            "last_date": None,
        }
    )
    processed = 0
    batch_size = settings.batch_size

    def process_message(request_id, response, exception) -> None:
        nonlocal processed
        if exception:
            return
        processed += 1
        headers = response.get("payload", {}).get("headers", [])
        unsub_link, unsub_type = get_unsubscribe_from_headers(headers)

        if unsub_link:
            sender_name, sender_email = get_sender_info(headers)
            subject = get_subject(headers)
            domain = sender_email.split("@")[-1] if "@" in sender_email else sender_email

            email_date = None
            for header in headers:
                if header["name"].lower() == "date":
                    email_date = header["value"]
                    break

            unsubscribe_data[domain]["link"] = unsub_link
            unsubscribe_data[domain]["count"] += 1
            unsubscribe_data[domain]["type"] = unsub_type
            unsubscribe_data[domain]["sender"] = sender_name
            unsubscribe_data[domain]["email"] = sender_email
            if len(unsubscribe_data[domain]["subjects"]) < 3:
                unsubscribe_data[domain]["subjects"].append(subject)

            if email_date:
                _update_dates(unsubscribe_data[domain], email_date)

    for i in range(0, len(message_ids), batch_size):
        batch_ids = message_ids[i:i + batch_size]
        batch = service.new_batch_http_request(callback=process_message)

        for msg_id in batch_ids:
            batch.add(
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=msg_id,
                    format="metadata",
                    metadataHeaders=["From", "Subject", "Date", "List-Unsubscribe", "List-Unsubscribe-Post"],
                )
            )

        batch.execute()
        progress = int((i + len(batch_ids)) / total * 100)
        state.scan_status["progress"] = progress
        state.scan_status["message"] = f"Scanned {processed}/{total} emails ({len(unsubscribe_data)} found)"

        if settings.adaptive_rate_limit and (i // batch_size + 1) % 5 == 0:
            time.sleep(0.3)

    _finalize_results(unsubscribe_data, processed)


def _scan_streaming(service, query: str, limit: int) -> None:
    """Streaming scan mode for large inboxes."""
    unsubscribe_data: Dict[str, dict] = defaultdict(
        lambda: {
            "link": None,
            "count": 0,
            "subjects": [],
            "type": None,
            "sender": "",
            "email": "",
            "first_date": None,
            "last_date": None,
        }
    )
    processed = 0
    chunk_size = settings.chunk_size
    checkpoint_interval = settings.checkpoint_interval
    last_checkpoint = 0
    
    state.scan_status["message"] = f"Scanning in streaming mode..."
    
    # Fetch and process in chunks
    message_ids = []
    page_token = None
    
    while processed < limit:
        # Fetch next page
        list_params = {
            "userId": "me",
            "maxResults": min(500, limit - processed),
        }
        if page_token:
            list_params["pageToken"] = page_token
        if query:
            list_params["q"] = query

        result = service.users().messages().list(**list_params).execute()
        messages = result.get("messages", [])
        message_ids.extend([m["id"] for m in messages])
        
        # Process chunk when full
        while len(message_ids) >= chunk_size:
            chunk = message_ids[:chunk_size]
            message_ids = message_ids[chunk_size:]
            _process_batch(service, chunk, unsubscribe_data)
            processed += len(chunk)
            
            progress = min(int(processed / limit * 100), 99)
            state.scan_status["progress"] = progress
            state.scan_status["message"] = f"Scanned {processed:,} emails ({len(unsubscribe_data)} subscriptions)"
            
            if processed - last_checkpoint >= checkpoint_interval:
                state.scan_status["checkpoint"] = {"processed": processed}
                last_checkpoint = processed
        
        page_token = result.get("nextPageToken")
        if not page_token:
            break
    
    # Process remaining messages
    if message_ids:
        _process_batch(service, message_ids, unsubscribe_data)
        processed += len(message_ids)
    
    _finalize_results(unsubscribe_data, processed)


def _process_batch(service, message_ids: List[str], unsubscribe_data: Dict) -> None:
    """Process a batch of messages."""
    batch_size = settings.batch_size
    
    def process_message(request_id, response, exception) -> None:
        if exception:
            return
        headers = response.get("payload", {}).get("headers", [])
        unsub_link, unsub_type = get_unsubscribe_from_headers(headers)

        if unsub_link:
            sender_name, sender_email = get_sender_info(headers)
            subject = get_subject(headers)
            domain = sender_email.split("@")[-1] if "@" in sender_email else sender_email

            email_date = None
            for header in headers:
                if header["name"].lower() == "date":
                    email_date = header["value"]
                    break

            unsubscribe_data[domain]["link"] = unsub_link
            unsubscribe_data[domain]["count"] += 1
            unsubscribe_data[domain]["type"] = unsub_type
            unsubscribe_data[domain]["sender"] = sender_name
            unsubscribe_data[domain]["email"] = sender_email
            if len(unsubscribe_data[domain]["subjects"]) < 3:
                unsubscribe_data[domain]["subjects"].append(subject)

            if email_date:
                _update_dates(unsubscribe_data[domain], email_date)

    for i in range(0, len(message_ids), batch_size):
        batch_ids = message_ids[i:i + batch_size]
        batch = service.new_batch_http_request(callback=process_message)
        
        for msg_id in batch_ids:
            batch.add(
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=msg_id,
                    format="metadata",
                    metadataHeaders=["From", "Subject", "Date", "List-Unsubscribe", "List-Unsubscribe-Post"],
                )
            )
        
        batch.execute()
        
        if settings.adaptive_rate_limit and i + batch_size < len(message_ids):
            time.sleep(0.05)


def _update_dates(data: dict, email_date: str) -> None:
    """Update first and last dates for a sender."""
    try:
        msg_datetime = parsedate_to_datetime(email_date)
        
        if data["first_date"] is None:
            data["first_date"] = email_date
        else:
            try:
                if msg_datetime < parsedate_to_datetime(data["first_date"]):
                    data["first_date"] = email_date
            except (ValueError, TypeError):
                if email_date < data["first_date"]:
                    data["first_date"] = email_date
        
        if data["last_date"] is None:
            data["last_date"] = email_date
        else:
            try:
                if msg_datetime > parsedate_to_datetime(data["last_date"]):
                    data["last_date"] = email_date
            except (ValueError, TypeError):
                if email_date > data["last_date"]:
                    data["last_date"] = email_date
    except (ValueError, TypeError):
        pass


def _finalize_results(unsubscribe_data: Dict, total_processed: int) -> None:
    """Sort and finalize scan results."""
    sorted_results = sorted(
        [
            {
                "domain": k,
                "link": v["link"],
                "count": v["count"],
                "subjects": v["subjects"],
                "type": v["type"],
                "sender": v["sender"],
                "email": v["email"],
                "first_date": v["first_date"],
                "last_date": v["last_date"],
            }
            for k, v in unsubscribe_data.items()
        ],
        key=lambda x: x.get("count", 0) or 0,
        reverse=True,
    )

    state.scan_results = sorted_results
    state.scan_status["message"] = f"Found {len(state.scan_results)} subscriptions in {total_processed:,} emails"
    state.scan_status["progress"] = 100
    state.scan_status["done"] = True


def get_scan_status() -> dict:
    """Get current scan status."""
    return state.scan_status.copy()


def get_scan_results() -> list:
    """Get scan results."""
    return state.scan_results.copy()
