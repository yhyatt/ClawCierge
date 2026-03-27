"""
Tests for tabit.py timezone handling — verifies DST-aware UTC conversion.
Israel uses UTC+2 in winter (last Sunday Oct → last Sunday Mar)
and UTC+3 in summer (last Sunday Mar → last Sunday Oct).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import patch
from datetime import datetime
from zoneinfo import ZoneInfo

# Import the function we're testing
from tabit import _to_utc_iso, _IL_TZ


class TestTabitTimezone:
    """Test DST-aware UTC conversion in tabit._to_utc_iso."""

    def test_summer_time_offset_is_utc_plus_3(self):
        """In summer (June), Israel is UTC+3 — 20:00 local = 17:00 UTC."""
        result = _to_utc_iso("2025-06-15", "20:00")
        assert result == "2025-06-15T17:00:00.000Z", (
            f"Expected UTC+3 offset in summer, got: {result}"
        )

    def test_winter_time_offset_is_utc_plus_2(self):
        """In winter (January), Israel is UTC+2 — 20:00 local = 18:00 UTC."""
        result = _to_utc_iso("2026-01-15", "20:00")
        assert result == "2026-01-15T18:00:00.000Z", (
            f"Expected UTC+2 offset in winter, got: {result}"
        )

    def test_midnight_summer(self):
        """Edge: midnight in summer — 00:00 local = 21:00 UTC previous day."""
        result = _to_utc_iso("2025-08-01", "00:00")
        assert result == "2025-07-31T21:00:00.000Z", (
            f"Midnight summer should cross day boundary, got: {result}"
        )

    def test_midnight_winter(self):
        """Edge: midnight in winter — 00:00 local = 22:00 UTC previous day."""
        result = _to_utc_iso("2026-02-01", "00:00")
        assert result == "2026-01-31T22:00:00.000Z", (
            f"Midnight winter should cross day boundary, got: {result}"
        )

    def test_dst_spring_forward_before(self):
        """Day before spring DST change (Israel 2026: last Friday/Saturday → clocks forward).
        In 2026, DST starts March 27. Mar 26 is still UTC+2 — 20:00 local = 18:00 UTC.
        """
        result = _to_utc_iso("2026-03-26", "20:00")
        assert result == "2026-03-26T18:00:00.000Z", (
            f"Day before spring DST, expected UTC+2, got: {result}"
        )

    def test_dst_spring_forward_after(self):
        """Day after spring DST change (Mar 27 2026 DST → UTC+3).
        Mar 28 is UTC+3 — 20:00 local = 17:00 UTC.
        """
        result = _to_utc_iso("2026-03-28", "20:00")
        assert result == "2026-03-28T17:00:00.000Z", (
            f"Day after spring DST, expected UTC+3, got: {result}"
        )

    def test_dst_fall_back_before(self):
        """Day before fall DST change (last Sunday of October 2025 is Oct 26).
        Oct 25 is still UTC+3 — 20:00 local = 17:00 UTC.
        """
        result = _to_utc_iso("2025-10-25", "20:00")
        assert result == "2025-10-25T17:00:00.000Z", (
            f"Day before fall DST, expected UTC+3, got: {result}"
        )

    def test_dst_fall_back_after(self):
        """Day after fall DST change (Oct 27 2025 clocks fall back to UTC+2).
        Oct 27 is UTC+2 — 20:00 local = 18:00 UTC.
        """
        result = _to_utc_iso("2025-10-27", "20:00")
        assert result == "2025-10-27T18:00:00.000Z", (
            f"Day after fall DST, expected UTC+2, got: {result}"
        )

    def test_output_format(self):
        """Output must match Tabit's expected ISO format: YYYY-MM-DDTHH:MM:SS.000Z."""
        result = _to_utc_iso("2026-05-01", "12:30")
        assert result.endswith(".000Z"), f"Expected .000Z suffix, got: {result}"
        # Verify full ISO format
        assert len(result) == 24, f"Expected 24-char ISO string, got len={len(result)}: {result}"

    def test_hardcoded_3_would_be_wrong_in_winter(self):
        """
        Regression: the old ISRAEL_UTC_OFFSET = 3 would give wrong results in winter.
        In Jan 2026, UTC+3 would give 17:00 UTC for a 20:00 booking.
        The correct answer is 18:00 UTC (UTC+2).
        """
        result = _to_utc_iso("2026-01-20", "20:00")
        wrong_answer = "2026-01-20T17:00:00.000Z"  # what hardcoded UTC+3 would give
        correct_answer = "2026-01-20T18:00:00.000Z"  # UTC+2 in winter
        assert result != wrong_answer, "ZoneInfo gives same wrong answer as hardcoded UTC+3!"
        assert result == correct_answer

    def test_il_tz_is_zoneinfo(self):
        """Verify _IL_TZ is properly initialized as a ZoneInfo instance."""
        assert isinstance(_IL_TZ, ZoneInfo), f"_IL_TZ should be ZoneInfo, got {type(_IL_TZ)}"
        assert str(_IL_TZ) == "Asia/Jerusalem"
