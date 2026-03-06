"""
Rate Limit Tracker
──────────────────
Tracks daily API call count for the CampaignX external API.
The API enforces a 100 calls/day limit across all endpoints.
"""

import logging
from datetime import date
from typing import Dict

logger = logging.getLogger(__name__)

# Daily limit per the CampaignX API docs
DAILY_LIMIT = 100


class RateLimitTracker:
    """
    Simple in-memory daily API call counter.
    Resets automatically when the date changes.
    """

    def __init__(self):
        self._counts: Dict[str, int] = {}
        self._date: date = date.today()
        self._total: int = 0

    def _reset_if_new_day(self):
        today = date.today()
        if today != self._date:
            logger.info(f"New day — resetting rate limit counter (was {self._total} calls)")
            self._counts = {}
            self._total = 0
            self._date = today

    def track(self, endpoint: str) -> bool:
        """
        Records an API call. Returns True if under limit, False if limit exceeded.
        """
        self._reset_if_new_day()
        self._total += 1
        self._counts[endpoint] = self._counts.get(endpoint, 0) + 1

        remaining = DAILY_LIMIT - self._total
        if remaining <= 10:
            logger.warning(f"⚠️  Rate limit warning: {remaining} calls remaining today")
        if remaining <= 0:
            logger.error(f"🚫 Daily rate limit of {DAILY_LIMIT} calls exceeded!")
            return False

        logger.info(f"API call #{self._total}: {endpoint} ({remaining} remaining today)")
        return True

    @property
    def remaining(self) -> int:
        self._reset_if_new_day()
        return max(0, DAILY_LIMIT - self._total)

    @property
    def total_today(self) -> int:
        self._reset_if_new_day()
        return self._total

    def summary(self) -> dict:
        """Returns a summary of today's API usage."""
        self._reset_if_new_day()
        return {
            "date": str(self._date),
            "total_calls": self._total,
            "remaining": self.remaining,
            "limit": DAILY_LIMIT,
            "by_endpoint": dict(self._counts),
        }
