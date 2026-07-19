#!/usr/bin/env python3
"""Generate subscribed iCalendar feeds from workouts.toml."""

from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    import tomllib
except ModuleNotFoundError as exc:
    raise SystemExit(
        "This generator needs Python 3.11+ for built-in TOML support. "
        "On this Mac, run `python3.12 scripts/generate_calendar.py` or `make generate`."
    ) from exc


DAY_INDEX = {
    "MO": 0,
    "TU": 1,
    "WE": 2,
    "TH": 3,
    "FR": 4,
    "SA": 5,
    "SU": 6,
}


@dataclass(frozen=True)
class Settings:
    start_date: date
    timezone_name: str
    floating_times: bool
    namespace: str
    site_url: str
    sequence: int


def load_plan(path: Path) -> dict:
    with path.open("rb") as file:
        return tomllib.load(file)


def parse_settings(plan: dict) -> Settings:
    raw = plan["settings"]
    start = raw["start_date"]
    if isinstance(start, str):
        start = date.fromisoformat(start)
    return Settings(
        start_date=start,
        timezone_name=raw["timezone"],
        floating_times=bool(raw.get("floating_times", False)),
        namespace=raw["namespace"],
        site_url=raw["site_url"].rstrip("/"),
        sequence=int(raw.get("sequence", 0)),
    )


def parse_time(value: str) -> tuple[int, int]:
    hour, minute = value.split(":", 1)
    return int(hour), int(minute)


def first_occurrence(start_date: date, day_code: str) -> date:
    target = DAY_INDEX[day_code]
    delta = (target - start_date.weekday()) % 7
    return start_date + timedelta(days=delta)


def slug(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def escape_text(value: object) -> str:
    text = str(value)
    text = text.replace("\\", "\\\\")
    text = text.replace(";", "\\;")
    text = text.replace(",", "\\,")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.replace("\n", "\\n")


def fold_line(line: str) -> str:
    lines: list[str] = []
    current = ""
    limit = 75

    for char in line:
        candidate = current + char
        if len(candidate.encode("utf-8")) > limit:
            lines.append(current)
            current = " " + char
            limit = 74
        else:
            current = candidate

    lines.append(current)
    return "\r\n".join(lines)


def prop(name: str, value: object) -> str:
    return fold_line(f"{name}:{escape_text(value)}")


def raw_prop(name: str, value: object) -> str:
    return fold_line(f"{name}:{value}")


def vtimezone(timezone_name: str) -> list[str]:
    if timezone_name != "America/New_York":
        return [
            "BEGIN:VTIMEZONE",
            raw_prop("TZID", timezone_name),
            "END:VTIMEZONE",
        ]

    return [
        "BEGIN:VTIMEZONE",
        "TZID:America/New_York",
        "X-LIC-LOCATION:America/New_York",
        "BEGIN:DAYLIGHT",
        "TZOFFSETFROM:-0500",
        "TZOFFSETTO:-0400",
        "TZNAME:EDT",
        "DTSTART:19700308T020000",
        "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU",
        "END:DAYLIGHT",
        "BEGIN:STANDARD",
        "TZOFFSETFROM:-0400",
        "TZOFFSETTO:-0500",
        "TZNAME:EST",
        "DTSTART:19701101T020000",
        "RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU",
        "END:STANDARD",
        "END:VTIMEZONE",
    ]


def event_lines(
    event: dict,
    feed_id: str,
    settings: Settings,
    dtstamp: str,
    log_form_url: str,
    movement_links: dict[str, str],
) -> list[str]:
    event_id = slug(event["id"])
    event_date = first_occurrence(settings.start_date, event["day"])
    hour, minute = parse_time(event["start"])
    if settings.floating_times:
        start = datetime(event_date.year, event_date.month, event_date.day, hour, minute)
        start_prop = "DTSTART"
        end_prop = "DTEND"
    else:
        tz = ZoneInfo(settings.timezone_name)
        start = datetime(event_date.year, event_date.month, event_date.day, hour, minute, tzinfo=tz)
        start_prop = f"DTSTART;TZID={settings.timezone_name}"
        end_prop = f"DTEND;TZID={settings.timezone_name}"
    end = start + timedelta(minutes=int(event["duration_minutes"]))
    uid = f"{feed_id}-{event_id}@{settings.namespace}"

    description = event["description"].strip()

    kettlebell_movements = event.get("kettlebell_movements", [])
    if event.get("kettlebell_reference_url"):
        description = (
            f"{description}\n\nKettlebell workout reference:\n"
            f"{event['kettlebell_reference_url']}"
        )
    if kettlebell_movements:
        link_lines = []
        for movement_id in kettlebell_movements:
            movement_url = movement_links.get(movement_id)
            if movement_url:
                movement_name = movement_id.replace("-", " ").title()
                link_lines.append(f"- {movement_name}: {movement_url}")
        if link_lines:
            description = f"{description}\n\nMovement demo links:\n" + "\n".join(link_lines)

    if event.get("log_link", True):
        form_url = event.get("form_url") or log_form_url
        if form_url:
            description = f"{description}\n\nLog workout:\n{form_url}"

    lines = [
        "BEGIN:VEVENT",
        prop("UID", uid),
        raw_prop("DTSTAMP", dtstamp),
        raw_prop("LAST-MODIFIED", dtstamp),
        raw_prop("SEQUENCE", int(event.get("sequence", settings.sequence))),
        raw_prop(start_prop, start.strftime("%Y%m%dT%H%M%S")),
        raw_prop(end_prop, end.strftime("%Y%m%dT%H%M%S")),
        "RRULE:FREQ=WEEKLY",
        prop("SUMMARY", event["summary"]),
        prop("DESCRIPTION", description),
        prop("LOCATION", event.get("location", "")),
    ]

    categories = event.get("categories", [])
    if categories:
        lines.append(f"CATEGORIES:{','.join(escape_text(category) for category in categories)}")

    lines.append("END:VEVENT")
    return lines


def calendar_lines(
    *,
    feed_id: str,
    feed: dict,
    events: list[dict],
    settings: Settings,
    dtstamp: str,
    log_form_url: str = "",
    movement_links: dict[str, str] | None = None,
) -> list[str]:
    movement_links = movement_links or {}
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "PRODID:-//Rowland Pettit//Workout Calendar//EN",
        prop("X-WR-CALNAME", feed["name"]),
        prop("X-WR-CALDESC", feed.get("description", "")),
        "REFRESH-INTERVAL;VALUE=DURATION:PT1H",
        "X-PUBLISHED-TTL:PT1H",
    ]

    if not settings.floating_times:
        lines.append(prop("X-WR-TIMEZONE", settings.timezone_name))

    if feed.get("color"):
        lines.append(prop("X-APPLE-CALENDAR-COLOR", feed["color"]))

    if not settings.floating_times:
        lines.extend(vtimezone(settings.timezone_name))

    for event in events:
        lines.extend(event_lines(event, feed_id, settings, dtstamp, log_form_url, movement_links))

    lines.append("END:VCALENDAR")
    return lines


def write_calendar(path: Path, lines: list[str]) -> None:
    path.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8", newline="")


def write_index(public_dir: Path, feeds: dict, settings: Settings) -> None:
    links = []
    for feed in feeds.values():
        filename = feed["filename"]
        https_url = f"{settings.site_url}/{filename}"
        webcal_url = https_url.replace("https://", "webcal://", 1)
        links.append(
            f"""
            <li>
              <strong>{html.escape(feed["name"])}</strong><br>
              <a href="{html.escape(webcal_url)}">Subscribe with Apple Calendar</a><br>
              <a href="{html.escape(https_url)}">{html.escape(https_url)}</a>
            </li>
            """
        )

    index = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Rowland Fitness Calendar</title>
  <style>
    body {{
      color: #1f2933;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
      margin: 0;
      padding: 2rem;
    }}
    main {{
      max-width: 760px;
    }}
    li {{
      margin: 1rem 0;
    }}
    code {{
      background: #f2f4f7;
      padding: 0.1rem 0.25rem;
    }}
  </style>
</head>
<body>
  <main>
    <h1>Rowland Fitness Calendar</h1>
    <p>Subscribe once. Edit <code>workouts.toml</code>. Regenerate and push.</p>
    <ul>
      {"".join(links)}
    </ul>
  </main>
</body>
</html>
"""
    (public_dir / "index.html").write_text(index, encoding="utf-8")
    (public_dir / ".nojekyll").write_text("", encoding="utf-8")


def generate(root: Path) -> None:
    plan_path = root / "workouts.toml"
    public_dir = root / "public"
    public_dir.mkdir(parents=True, exist_ok=True)

    plan = load_plan(plan_path)
    settings = parse_settings(plan)
    feeds = plan["feeds"]
    events = plan.get("events", [])
    logging = plan.get("logging", {})
    log_form_url = logging.get("form_url", "")
    movement_links = plan.get("movement_links", {})
    dtstamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    by_feed = {feed_id: [] for feed_id in feeds}
    for event in events:
        by_feed[event["feed"]].append(event)

    for feed_id, feed in feeds.items():
        feed_events = by_feed.get(feed_id, [])
        lines = calendar_lines(
            feed_id=feed_id,
            feed=feed,
            events=feed_events,
            settings=settings,
            dtstamp=dtstamp,
            log_form_url=log_form_url,
            movement_links=movement_links,
        )
        write_calendar(public_dir / feed["filename"], lines)

    all_feed = {
        "name": "Rowland Fitness - All Workouts",
        "filename": "workouts.ics",
        "description": "Combined lifting and cardio workout calendar.",
        "color": "#2f5d8c",
    }
    all_lines = calendar_lines(
        feed_id="all",
        feed=all_feed,
        events=events,
        settings=settings,
        dtstamp=dtstamp,
        log_form_url=log_form_url,
        movement_links=movement_links,
    )
    write_calendar(public_dir / all_feed["filename"], all_lines)

    all_feeds = dict(feeds)
    all_feeds["all"] = all_feed
    write_index(public_dir, all_feeds, settings)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Project root containing workouts.toml.",
    )
    args = parser.parse_args()
    generate(args.root)


if __name__ == "__main__":
    main()
