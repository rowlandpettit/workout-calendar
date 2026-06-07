# Rowland Fitness Calendar

Subscribed workout calendars generated from one editable source file.

## Live Feeds

After GitHub Pages deploys, subscribe to these URLs in Apple Calendar:

- Lifting: `webcal://rowlandpettit.com/workout-calendar/lifting.ics`
- Cardio: `webcal://rowlandpettit.com/workout-calendar/cardio.ics`
- Combined: `webcal://rowlandpettit.com/workout-calendar/workouts.ics`

Use either the separate lifting/cardio feeds or the combined feed, not both, unless you want duplicate events.

Workout times are generated as floating local times. A `6:30 AM` workout should stay at `6:30 AM` wherever the calendar is being viewed, instead of converting from Eastern time.

## Edit The Plan

Edit `workouts.toml`. The key source fields are:

- `summary`: calendar event title
- `day`: `MO`, `TU`, `WE`, `TH`, `FR`, `SA`, or `SU`
- `start`: local start time
- `duration_minutes`: calendar block length
- `description`: event notes shown in Apple Calendar

Keep each event `id` stable. That keeps Apple Calendar seeing edits as updates instead of unrelated new events.

## Generate Locally

```bash
make generate
```

Generated feeds are written to `public/`:

- `public/lifting.ics`
- `public/cardio.ics`
- `public/workouts.ics`

The generated files are not tracked in git. GitHub Actions regenerates them on every push and deploys `public/` as the live subscribed-calendar site.

## Validate

```bash
make validate
```

## Publish

Push to `main`. GitHub Actions regenerates the feeds and deploys `public/` as the GitHub Pages site.

Apple Calendar subscriptions refresh on their own schedule, so changes may not appear instantly.
