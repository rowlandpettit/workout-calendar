#!/usr/bin/env python3
"""Check the published feeds preserve the weekday 6:15 AM floating schedule."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
FILES = {"lifting.ics": 5, "cardio.ics": 0, "workouts.ics": 5}
SPLIT = {
    0: "Chest",
    1: "Back",
    2: "Legs",
    3: "Arms",
    4: "Shoulders",
}


def events_in(text: str) -> list[dict[str, str]]:
    unfolded = re.sub(r"\r?\n[ \t]", "", text)
    events = []
    for block in re.findall(r"BEGIN:VEVENT\r?\n(.*?)END:VEVENT", unfolded, re.S):
        fields = {}
        for line in block.splitlines():
            if ":" in line:
                name, value = line.split(":", 1)
                fields[name] = value
        events.append(fields)
    return events


def main() -> None:
    for filename, expected_count in FILES.items():
        text = (PUBLIC / filename).read_text(encoding="utf-8")
        assert text.startswith("BEGIN:VCALENDAR"), f"{filename}: missing calendar start"
        assert "END:VCALENDAR" in text, f"{filename}: missing calendar end"
        assert "DTSTART;TZID=" not in text, f"{filename}: DTSTART should be floating"
        assert "BEGIN:VTIMEZONE" not in text, f"{filename}: should not include VTIMEZONE"

        events = events_in(text)
        assert len(events) == expected_count, f"{filename}: expected {expected_count} events"
        days = set()
        uids = set()
        for event in events:
            start = datetime.strptime(event["DTSTART"], "%Y%m%dT%H%M%S")
            end = datetime.strptime(event["DTEND"], "%Y%m%dT%H%M%S")
            day = start.weekday()
            assert day in SPLIT, f"{filename}: weekend event"
            assert start.date() == date(2026, 9, 14) + timedelta(days=day), (
                f"{filename}: wrong first occurrence"
            )
            assert start.hour == 6 and start.minute == 15, f"{filename}: not 6:15 AM"
            assert end - start == timedelta(minutes=45), f"{filename}: not 45 minutes"
            assert SPLIT[day] in event["SUMMARY"], f"{filename}: wrong split day"
            assert event["RRULE"] == "FREQ=WEEKLY", f"{filename}: not recurring"
            assert "Kettlebell swaps:" in event["DESCRIPTION"], (
                f"{filename}: missing kettlebell alternatives"
            )
            assert "6:45-7:00: Sauna" in event["DESCRIPTION"], (
                f"{filename}: missing 15-minute sauna"
            )
            assert event["UID"] not in uids, f"{filename}: duplicate UID"
            days.add(day)
            uids.add(event["UID"])
        if expected_count:
            assert days == set(SPLIT), f"{filename}: missing weekday"
        print(f"OK public/{filename}: {expected_count} floating events")


if __name__ == "__main__":
    main()
