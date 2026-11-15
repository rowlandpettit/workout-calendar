# Rowland Fitness Calendar

Weekday strength, Saturday long run, and Sunday swim published as subscribed calendars.

## Weekly plan

Monday chest, Tuesday back, Wednesday legs, Thursday arms, Friday shoulders.
Weekday lifts run 6:15–6:45 AM. Saturday Long Run runs 6:15–7:15 AM beginning November 21, 2026; Sunday Swim runs 6:15–6:45 AM beginning November 22, 2026. All use local floating time, including when traveling.

Each weekday event contains three complete alternatives. Choose **one**:

- **Weights:** full gym, including barbell, bench, rack, dumbbells, and cables.
- **DB only:** dumbbells and bodyweight; a bench is optional where a floor alternative is listed.
- **KB only:** kettlebells and bodyweight; the leg session uses two bells.

Each path has four exercises and ten working sets: 4 / 2 / 2 / 2.
The first exercise in every path is a compound lift with four heavy working sets.
Warm-up: 1 x 15–20. Each path ends with weighted abs.
Each weekday event retains the Google Form logging link.

## Subscribe

- Lifting: `webcal://rowlandpettit.com/workout-calendar/lifting.ics`
- Combined: `webcal://rowlandpettit.com/workout-calendar/workouts.ics`

Both active feeds contain the same seven workouts. Subscribe to only one.
The existing lifting.ics URL also carries the weekend sessions so current subscribers receive the full week without changing subscriptions.
The retired cardio feed stays published empty for existing subscribers.

## Edit and publish

Edit `workouts.toml` for titles, days, start times, durations, or notes.
New weekend events use per-event start_date anchors to avoid adding past sessions.
Keep existing event IDs, feed IDs, namespace, and recurrence anchors stable so calendar
clients update existing series. Increase `settings.sequence` when publishing edits.

```bash
make validate
```

This generates `public/lifting.ics`, `public/cardio.ics`, `public/workouts.ics`,
and the subscription page, then checks the schedule and complete workout paths.
Generated files are not tracked in git.

Push to `main` to generate, validate, and deploy through GitHub Actions to GitHub Pages.
Apple Calendar refreshes on its own schedule; the feeds request hourly refresh.
