# Build Simple Tkinter Countdown Timer

## Overview
Build a simple Python Tkinter countdown timer app with start/pause/reset controls and basic input validation.

## Scope
Create a minimal desktop countdown timer in `calc/calc.py` that lets users enter minutes/seconds, start countdown, pause/resume, and reset.

## Requirements
- Provide a small Tkinter window with:
  - Input fields for minutes and seconds
  - A large time display in `MM:SS`
  - `Start`, `Pause/Resume`, and `Reset` buttons
- Implement countdown logic using Tkinter `after()` so the UI stays responsive.
- Validate input:
  - Accept only non-negative integers
  - Normalize values (for example, seconds over 59 convert into minutes)
  - Show a message dialog for invalid input
- Manage timer state safely with `running`, `remaining_seconds`, and `after_id` to avoid duplicate scheduled callbacks.
- On completion (`00:00`), stop the timer and show a `"Time's up"` dialog.

## Verification
- Run the app with `python calc/calc.py`.
- Verify:
  - Countdown starts correctly
  - Pause/resume works without speed-up or double ticks
  - Reset returns to the initial entered value
  - Invalid input is handled gracefully
  - Completion alert appears at `00:00`
