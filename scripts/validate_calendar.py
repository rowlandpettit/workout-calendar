#!/usr/bin/env python3
"""Check the 30-minute, choose-one-path workout feeds and subscription identity."""

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
EVENT_IDS = {
    0: "upper-a",
    1: "lower-a",
    2: "wednesday-choice",
    3: "upper-b",
    4: "lower-b",
}
PATHS = ("Weights", "DB only", "KB only")
ABS_FINISHERS = {
    "Weights": "Kneeling rope cable crunch",
    "DB only": "DB weighted crunch",
    "KB only": "KB weighted crunch",
}


def validate_description(description: str, label: str) -> None:
    notes = description.replace(r"\n", "\n")
    assert re.search(r"\b(?:pick|choose)\s+one\b", notes, re.I), (
        f"{label}: missing choose-one instruction"
    )
    assert "Progress each path separately:" in notes, (
        f"{label}: missing independent progression"
    )
    assert "Week 4:" in notes, f"{label}: missing lighter-week instruction"
    assert not re.search(r"\b\d{1,2}:\d{2}\b|\bsauna\b|\bmile\b|swaps", notes, re.I), (
        f"{label}: obsolete timed itinerary or swap-only notes"
    )
    headings = list(re.finditer(r"^(Weights|DB only|KB only)\s*$", notes, re.M))
    assert tuple(match.group(1) for match in headings) == PATHS, (
        f"{label}: expected one block for each equipment path"
    )
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else notes.index(
            "Progress each path separately:"
        )
        block = notes[heading.end():end]
        exercises = [
            line for line in block.splitlines()
            if re.search(r"\b\d+\s*[x×]\s*\d+", line)
        ]
        assert len(exercises) == 4, (
            f"{label}: {heading.group(1)} needs three lifts and a weighted abs finisher"
        )
        assert ABS_FINISHERS[heading.group(1)] in exercises[-1], (
            f"{label}: {heading.group(1)} needs its weighted abs finisher last"
        )


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
    active_feeds = {}
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
            assert end - start == timedelta(minutes=30), f"{filename}: not 30 minutes"
            assert SPLIT[day] in event["SUMMARY"], f"{filename}: wrong split day"
            assert event["RRULE"] == "FREQ=WEEKLY", f"{filename}: not recurring"
            assert int(event["SEQUENCE"]) >= 10, f"{filename}: stale update sequence"
            validate_description(event["DESCRIPTION"], f"{filename}: {event['SUMMARY']}")
            feed_id = "all" if filename == "workouts.ics" else "lifting"
            expected_uid = f"{feed_id}-{EVENT_IDS[day]}@workout-calendar.rowlandpettit"
            assert event["UID"] == expected_uid, f"{filename}: changed subscription UID"
            assert event["UID"] not in uids, f"{filename}: duplicate UID"
            days.add(day)
            uids.add(event["UID"])
        if expected_count:
            assert days == set(SPLIT), f"{filename}: missing weekday"
            active_feeds[filename] = {
                event["DTSTART"]: {key: value for key, value in event.items() if key != "UID"}
                for event in events
            }
        print(f"OK public/{filename}: {expected_count} floating events")
    assert active_feeds["lifting.ics"] == active_feeds["workouts.ics"], (
        "Active feeds disagree on workout content or schedule"
    )


if __name__ == "__main__":
    main()
