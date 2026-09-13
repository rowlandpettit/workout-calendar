# Rowland Fitness Calendar

Subscribed workout calendars generated from one editable source file.

## Live Feeds

The weekly plan is Monday chest, Tuesday back, Wednesday legs, Thursday arms, and Friday shoulders. Wake at 6:00 AM. Each 6:15-7:00 AM gym block has an easy mile, about 17 minutes of lifting, and an optional 15-minute sauna. Head upstairs to shower afterward. Each event lists gym exercises and kettlebell swaps. These are local floating times, so the event stays at 6:15 AM when you travel and your calendar changes time zone. Start with manageable weights and keep 2-3 reps in reserve while getting back into the routine.

Subscribe to one of these URLs in Apple Calendar:

- Lifting: `webcal://rowlandpettit.com/workout-calendar/lifting.ics`
- Combined: `webcal://rowlandpettit.com/workout-calendar/workouts.ics`

Both active feeds contain the same five workouts, so subscribe to only one. The old cardio feed remains published empty to clear its former weekend run and swim events for existing subscribers.

The 45-minute block is tight. If the mile takes longer than 12 minutes, trim a lifting set instead of speeding up. The sauna depends on it being warm and available; skip it if you feel dizzy, ill, or dehydrated, and rehydrate afterward.

Each event includes a `Log workout` link to the Google Form. Responses land in the linked `Workout Log (Responses)` Google Sheet.

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
- `public/cardio.ics` (retired, empty)
- `public/workouts.ics`

The generated files are not tracked in git. GitHub Actions regenerates them on every push and deploys `public/` as the live subscribed-calendar site.

## Validate

```bash
make validate
```

## Publish

Push to `main`. GitHub Actions regenerates the feeds and deploys `public/` as the GitHub Pages site.

Apple Calendar subscriptions refresh on their own schedule, so changes may not appear instantly.
