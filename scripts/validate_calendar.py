#!/usr/bin/env python3
"""Lightweight structural checks for generated iCalendar feeds."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
FILES = ["lifting.ics", "cardio.ics", "workouts.ics"]


def main() -> None:
    for filename in FILES:
        path = PUBLIC / filename
        text = path.read_text(encoding="utf-8")
        assert text.startswith("BEGIN:VCALENDAR"), f"{filename}: missing BEGIN:VCALENDAR"
        assert "END:VCALENDAR" in text, f"{filename}: missing END:VCALENDAR"
        assert "UID:" in text, f"{filename}: missing UID"
        assert "DTSTAMP:" in text, f"{filename}: missing DTSTAMP"
        assert "TZID=America/New_York" in text, f"{filename}: missing timezone"
        print(f"OK public/{filename}")


if __name__ == "__main__":
    main()
