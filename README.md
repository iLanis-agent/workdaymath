# Workday Math

Working-day counting arithmetic. Twelve calendar days are not twelve working days.

## What it computes

- **The count truth** - every kind of day between two dates, ends included: 2026-10-19 to 2026-10-30 with one listed holiday is 9 working days.
- **The add truth** - the date a number of working days after a start date: 5 working days after 2026-10-19, with 2026-10-26 listed, is 2026-10-27.
- **The buffer truth** - working days after the start through a deadline against the days a job needs: 8 available, 6 needed, 2 spare.

## Boundary

Arithmetic only. Workday Math counts weekdays between the dates you type and skips only the holidays you list. It does not know any country's or company's holidays, and it does not say whether a deadline is realistic or what a contract allows. You decide that.

## Files

- `index.html` - landing page.
- `app.html` - the interactive calculator.
- `engine.js` - the arithmetic.
- `oracle.py` - the Python mirror that generates `expected.json`.
- `test.js` - compares every engine output against `expected.json` (31 cases).
- `expected.json` - the golden answers.

## Test

```
python3 oracle.py
node test.js
```

Live: https://ilanis-agent.github.io/workdaymath/
Repo: https://github.com/iLanis-agent/workdaymath
