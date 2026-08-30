from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# Health policy constants
# ---------------------------------------------------------------------------
CONSECUTIVE_FAILURE_THRESHOLD = 3    # consecutive failures before cooldown
COOLDOWN_SECONDS_DEFAULT      = 60   # standard cooldown for temporary errors
COOLDOWN_SECONDS_RATE_LIMIT   = 120  # longer cooldown for rate-limit errors


def _cooldown_seconds(error_type: str) -> int:
    """Return the cooldown duration in seconds for a given temporary error type."""
    if error_type == "ProviderRateLimitError":
        return COOLDOWN_SECONDS_RATE_LIMIT
    return COOLDOWN_SECONDS_DEFAULT


@dataclass
class ProviderHealthRecord:
    """Holds in-memory health statistics for a single provider."""

    provider_name:             str
    success_count:             int                = field(default=0)
    failure_count:             int                = field(default=0)
    consecutive_failure_count: int                = field(default=0)
    last_failure_type:         Optional[str]      = field(default=None)
    last_outcome:              Optional[str]      = field(default=None)
    last_success_time:         Optional[datetime] = field(default=None)
    last_failure_time:         Optional[datetime] = field(default=None)
    cooldown_until:            Optional[datetime] = field(default=None)
    permanently_unavailable:   bool               = field(default=False)


class ProviderHealthTracker:
    """
    Thread-safe, in-memory tracker for provider health outcomes.

    Day 12 Part 1: records success and failure events.
    Day 12 Part 2: adds consecutive failure tracking, timed cooldowns,
    and permanent process-level unavailability for configuration errors.
    """

    def __init__(self) -> None:
        self._lock:   threading.Lock                  = threading.Lock()
        self._health: dict[str, ProviderHealthRecord] = {}

    def _get_or_create_record(self, provider_name: str) -> ProviderHealthRecord:
        """Return the existing record for a provider, or create a fresh one."""
        if provider_name not in self._health:
            self._health[provider_name] = ProviderHealthRecord(
                provider_name=provider_name
            )
        return self._health[provider_name]

    def record_success(self, provider_name: str) -> None:
        """
        Record a successful response from the given provider.

        Increments success_count, updates last_outcome and last_success_time.
        Resets consecutive_failure_count to 0 and clears cooldown_until.
        Does NOT clear permanently_unavailable.
        """
        with self._lock:
            record = self._get_or_create_record(provider_name)
            record.success_count             += 1
            record.last_outcome               = "success"
            record.last_success_time          = datetime.now(timezone.utc)
            record.consecutive_failure_count  = 0
            record.cooldown_until             = None

        print(
            "[AOIP][Health] " + provider_name
            + " | success_count=" + str(record.success_count)
            + " | consecutive_failures_reset=0"
        )

    def record_failure(self, provider_name: str, error_type: str) -> None:
        """
        Record a failed attempt for the given provider.

        Increments failure_count and consecutive_failure_count.
        Sets permanently_unavailable=True for ProviderConfigurationError.
        Sets cooldown_until when consecutive failure threshold is reached
        for all other temporary errors.
        """
        with self._lock:
            record = self._get_or_create_record(provider_name)
            record.failure_count             += 1
            record.consecutive_failure_count += 1
            record.last_outcome               = "failure"
            record.last_failure_type          = error_type
            record.last_failure_time          = datetime.now(timezone.utc)

            if error_type == "ProviderConfigurationError":
                record.permanently_unavailable = True
            elif record.consecutive_failure_count >= CONSECUTIVE_FAILURE_THRESHOLD:
                secs = _cooldown_seconds(error_type)
                record.cooldown_until = datetime.now(timezone.utc) + timedelta(seconds=secs)

        status_suffix = ""
        if record.permanently_unavailable:
            status_suffix = " | permanently_unavailable=True"
        elif record.cooldown_until:
            status_suffix = " | cooldown_until=" + record.cooldown_until.isoformat()

        print(
            "[AOIP][Health] " + provider_name
            + " | failure_count=" + str(record.failure_count)
            + " | consecutive=" + str(record.consecutive_failure_count)
            + " | last_failure_type=" + error_type
            + status_suffix
        )

    def is_available(self, provider_name: str) -> bool:
        """
        Return True if the provider is currently eligible to be tried.

        A provider is unavailable if:
          - it is marked permanently_unavailable (ProviderConfigurationError), or
          - it is within an active cooldown period.

        A provider never seen before is considered available.
        Thread-safe: acquires lock for the duration of the read.
        """
        with self._lock:
            record = self._health.get(provider_name)
            if record is None:
                return True
            if record.permanently_unavailable:
                return False
            if record.cooldown_until is None:
                return True
            return datetime.now(timezone.utc) > record.cooldown_until

    def get_status(self) -> dict[str, dict]:
        """
        Return a snapshot of the current health state for all tracked providers.

        Returns a plain dict suitable for logging or a future health endpoint.
        Includes all Day 12 Part 2 fields.
        """
        with self._lock:
            result = {}
            for name, rec in self._health.items():
                result[name] = {
                    "provider_name":             rec.provider_name,
                    "success_count":             rec.success_count,
                    "failure_count":             rec.failure_count,
                    "consecutive_failure_count": rec.consecutive_failure_count,
                    "last_failure_type":         rec.last_failure_type,
                    "last_outcome":              rec.last_outcome,
                    "last_success_time": (
                        rec.last_success_time.isoformat()
                        if rec.last_success_time else None
                    ),
                    "last_failure_time": (
                        rec.last_failure_time.isoformat()
                        if rec.last_failure_time else None
                    ),
                    "cooldown_until": (
                        rec.cooldown_until.isoformat()
                        if rec.cooldown_until else None
                    ),
                    "permanently_unavailable": rec.permanently_unavailable,
                }
            return result


# ---------------------------------------------------------------------------
# Module-level singleton -- shared across all requests for the lifetime of
# the FastAPI server process. Resets automatically on server restart.
# ---------------------------------------------------------------------------
health_tracker = ProviderHealthTracker()
