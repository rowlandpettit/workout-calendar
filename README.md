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
Its warm-up is separate: one light set of 15–20 reps, followed by lighter ramp-up sets as needed.
Weighted abs finish every path: kneeling rope cable crunches for Weights,
and weighted crunches holding a dumbbell or kettlebell at the chest for DB/KB.

Thirty minutes is the session target, including warm-up sets and transitions.
Warm up the first lift with lighter sets. Rest about two minutes for the first lift
and 60–90 seconds for the others. Do not rush heavy warm-up sets or technique
to fit the clock; omit a set of the third exercise if needed to finish with abs.

## Progression

Use current strength to select challenging loads with 1–2 clean reps left.
Keep a separate load/rep record for **each exercise in each equipment path**,
including abs. Switching equipment does not mean copying the same weight.

1. Start at the bottom of the stated rep range.
2. Build reps at that load until every set reaches the top with clean form and 1–2 reps left.
3. Add the smallest available load and restart at the bottom. If the increment is too large,
   keep the previous load; there is no forced weekly weight increase.
4. Every fourth training week, use 2 / 1 / 1 / 1 working sets with the same or a lighter load.
   Then repeat the four-week cycle. Begin counting with the first week on this plan.

For suitcase marches, progress to the top of the step range before adding load.
For push-ups, progress reps and then use a harder variation. If DB/KB loads are
limited, a pause or slower lowering can add difficulty, but light weights do not
replace the strength stimulus of a heavy barbell. Technical Olympic lifts are not included.

The old Duke program informed the compound lifts and lighter weeks; its historical
prescribed weights are not used as present-day starting loads.

The calendar supplies the progression rules; it does not automatically record loads
or adjust the workout. Each weekday event retains the existing Google Form logging link.
The form itself has not been changed by this calendar update.

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
