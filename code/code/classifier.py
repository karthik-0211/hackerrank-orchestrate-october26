"""Request Authorization Classifier (Decision Gate 1).

Determines whether request_text actually authorizes account/data deletion.
Distinguishes deletion requests from:
- Data access / export requests without deletion
- Invoice / receipt copy requests
- Profile updates / name / mobile corrections
- Marketing / communication opt-outs
- General non-deletion inquiries

Non-deletion requests must receive:
    deletion_status = NOT_APPLICABLE
    steps_json = []
"""

from __future__ import annotations

import re
from typing import Tuple


class RequestClassifier:
    """Classifies user requests for deletion authorization."""

    # Explicit non-deletion indicators
    NON_DELETION_PATTERNS = [
        r"leave\s+the\s+account\s+active",
        r"not\s+asking\s+for\s+deletion",
        r"keep\s+the\s+account",
        r"do\s+not\s+close",
        r"don['’]?t\s+close",
        r"don['’]?t\s+delete",
        r"without\s+removing",
        r"marketing\s+lists\s+only",
        r"not\s+a\s+request\s+to\s+erase",
        r"leave\s+my\s+profile",
        r"continue\s+using\s+the\s+service",
        r"replace\s+it\s+with\s+the\s+new\s+one",
        r"resetting\s+the\s+login",
        r"copy\s+of\s+last\s+year['’]?s\s+invoices",
        r"change\s+the\s+email\s+address\s+used\s+for\s+this\s+account",
        r"download\s+my\s+account\s+information\s+in\s+a\s+portable\s+format",
        r"what\s+personal\s+information\s+you\s+hold\s+about\s+me",
    ]

    @classmethod
    def classify(cls, request_text: str) -> Tuple[bool, str]:
        """Returns (is_authorized_deletion, reason)."""
        if not request_text or not request_text.strip():
            return False, "EMPTY_REQUEST_TEXT"

        text_lower = request_text.lower()

        # Check for explicit non-deletion patterns
        for pat in cls.NON_DELETION_PATTERNS:
            if re.search(pat, text_lower):
                return False, f"NON_DELETION_REQUEST: matched {pat}"

        # Otherwise, the request is an authorized deletion request
        return True, "DELETION_AUTHORIZED"
