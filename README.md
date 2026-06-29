# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

| Feature | Algorithm / Behavior |
|---|---|
| **Priority-based scheduling** | `Schedule.generate()` scores every pending task (high=3, medium=2, low=1) and sorts descending before filling time slots. High-priority tasks always land first, regardless of the order they were added. |
| **Chronological sort** | `Schedule.sort_by_time()` re-orders the generated plan by each task's assigned `HH:MM` slot, so the day can be displayed in reading order independently of priority. |
| **Conflict detection** | `Schedule.detect_conflicts()` tests every unique pair of scheduled tasks using `itertools.combinations` and interval-overlap math (`a_start < b_end AND b_start < a_end`). Returns one warning string per overlapping pair; never raises. |
| **Composable filtering** | `Schedule.filter_tasks(pet_name, completed)` applies up to two independent filters at once. Omit either argument to ignore that dimension; pass both to narrow to, e.g., Mochi's pending tasks only. |
| **Daily / weekly recurrence** | `Task.next_occurrence()` creates a fresh, uncompleted copy of the task with `due_date` advanced by `timedelta(days=1)` for daily tasks or `timedelta(days=7)` for weekly ones. `Pet.mark_task_complete()` triggers this automatically and appends the new task to the pet's list. |
| **Available-time gating** | A task is only placed in the plan if its duration fits within the owner's remaining minutes. Tasks that exceed remaining time are skipped and surfaced in a separate list. |
| **Senior pet detection** | `Pet.is_senior()` flags dogs ≥ 7 years and cats ≥ 10 years so the UI can surface a visual senior tag. |

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample CLI Output

Run `python main.py` from the project root to see all scheduler behaviors exercised end-to-end:

```
Jordan — 90 min available | pets: Mochi, Biscuit | preferences: no tasks before 8am
Mochi the cat (senior) | notes: hyperthyroid, needs morning meds
  Brushing (15 min, low priority, weekly) [due: 2026-06-29] [pending]
  Feeding (10 min, high priority, daily) [due: 2026-06-29] [pending]
  Morning meds (5 min, high priority, daily) [due: 2026-06-29] [pending]
Biscuit the dog
  Playtime (25 min, low priority, daily) [due: 2026-06-29] [pending]
  Training (20 min, medium priority, daily) [due: 2026-06-29] [pending]
  Morning walk (30 min, high priority, daily) [due: 2026-06-29] [pending]

========================================
Daily plan for Jordan's pets
Available time: 90 min | Start: 08:00

  08:00 — [Mochi] Feeding (10 min) [priority: high]
  08:10 — [Mochi] Morning meds (5 min) [priority: high]
  08:15 — [Biscuit] Morning walk (30 min) [priority: high]
  08:45 — [Biscuit] Training (20 min) [priority: medium]
  09:05 — [Mochi] Brushing (15 min) [priority: low]

Skipped (not enough time):
  - [Biscuit] Playtime (25 min)

========================================
Tasks sorted by scheduled time:
  08:00 — Feeding (high priority)
  08:10 — Morning meds (high priority)
  08:15 — Morning walk (high priority)
  08:45 — Training (medium priority)
  09:05 — Brushing (low priority)

========================================
Biscuit's scheduled tasks:
  08:15 — Morning walk (high priority)
  08:45 — Training (medium priority)

========================================
Conflict detection:
  Conflicts in generated plan: 0 (expected 0)
  Conflicts after injecting overlapping task: 3
  WARNING: [Mochi] Feeding (08:00–08:10) overlaps with [Mochi] Emergency vet (08:05–08:25)
  WARNING: [Mochi] Morning meds (08:10–08:15) overlaps with [Mochi] Emergency vet (08:05–08:25)
  WARNING: [Biscuit] Morning walk (08:15–08:45) overlaps with [Mochi] Emergency vet (08:05–08:25)

========================================
Marking tasks complete and checking next occurrences:

  Completed: Mochi's Feeding
  Next occurrence: Feeding | due: 2026-06-30 | status: pending

  Completed: Mochi's Brushing
  Next occurrence: Brushing | due: 2026-07-06 | status: pending

========================================
Mochi's full task list after completions:
  Brushing (15 min, low priority, weekly) [due: 2026-06-29] [done]
  Feeding (10 min, high priority, daily) [due: 2026-06-29] [done]
  Morning meds (5 min, high priority, daily) [due: 2026-06-29] [pending]
  Feeding (10 min, high priority, daily) [due: 2026-06-30] [pending]
  Brushing (15 min, low priority, weekly) [due: 2026-07-06] [pending]
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest
python -m pytest

# Run with coverage:
pytest --cov

test_sort_by_time_returns_chronological_order

Creates an owner with one pet and three tasks of different priorities. Calls generate() so every task gets a time string assigned (e.g. "08:00", "08:30"), then calls sort_by_time() and checks that the returned list of times is in ascending order. The key insight: generate() fills slots greedily by priority, so the clock times happen to be ascending already — but sort_by_time() must enforce that order explicitly via _parse_time, not rely on insertion order.

test_daily_task_recurrence_schedules_next_day

Creates a pet with a single daily task due today. Calls mark_task_complete("Feeding") and checks three things on the returned new task: it's not None (meaning a match was found), its completed flag is False (a fresh occurrence starts pending), and its due_date is exactly today + 1 day. This pins the timedelta(days=1) branch in pawpal_system.py

test_detect_conflicts_flags_overlapping_tasks

Builds a schedule normally, then forces both tasks to "08:00" so their windows definitely overlap (the greedy scheduler itself would never double-book). This is intentional: it tests detect_conflicts() in isolation without relying on the scheduler producing a conflict naturally. The test then asserts that at least one warning string is returned and that it contains "WARNING".

```

Sample test output:

```
# ================================================================================= 7 passed in 0.02s ===

```

# Confidence level in system reliability = 4/5

## 📐 Smarter Scheduling

| Feature             | Method(s)                                            | Notes                                                                                                                                                                                                                                                             |
| ------------------- | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Task sorting        | `Schedule.sort_by_time()`                            | Returns scheduled `Task` objects in ascending time-slot order. Relies on `task.time`, which is set during `generate()` — must be called after the plan is generated.                                                                                              |
| Filtering by pet    | `Schedule.filter_tasks(pet_name=...)`                | Returns only the `ScheduledTask` entries belonging to the named pet.                                                                                                                                                                                              |
| Filtering by status | `Schedule.filter_tasks(completed=...)`               | Pass `True` for completed tasks or `False` for pending ones. Both filters compose — `filter_tasks(pet_name="Mochi", completed=False)` returns Mochi's pending tasks only.                                                                                         |
| Conflict detection  | `Schedule.detect_conflicts()`                        | Checks every unique pair of scheduled tasks using `itertools.combinations`. Returns a list of warning strings — one per overlapping pair — without raising exceptions. Uses interval overlap math: two tasks conflict when `a_start < b_end AND b_start < a_end`. |
| Recurring tasks     | `Task.next_occurrence()`, `Pet.mark_task_complete()` | Calling `pet.mark_task_complete(title)` marks the matching task done and automatically appends a fresh copy with an advanced `due_date`: +1 day for `"daily"` tasks, +7 days for `"weekly"` tasks (via Python's `timedelta`).                                     |

## 📸 Demo Walkthrough

### Streamlit UI (`streamlit run app.py`)

The app is divided into four sections that a user works through top to bottom.

**Section 1 — Owner Info**
Enter your name, how many minutes you have available today, and an optional scheduling preference (e.g. "no tasks before 9am"). Click **Save owner** to lock in your profile.

**Section 2 — Add a Pet**
Register each pet with a name, species, and age. Cats 10 years and older and dogs 7 years and older are automatically labelled as senior. An optional notes field stores care reminders (e.g. "needs morning meds").

**Section 3 — Add Tasks**
Select a pet from the dropdown and fill in a task name, duration in minutes, priority (high / medium / low), and frequency (daily / weekly). Each pet's full task list is shown below the form as a table.

**Section 4 — Today's Schedule**
Click **Generate schedule** to produce the daily plan. The scheduler:
- Sorts all pending tasks by priority (high first) and greedily fills time slots
- Skips any task whose duration exceeds remaining available minutes

After generating, the UI shows:
- A green **No conflicts detected** banner, or amber **WARNING** banners if two tasks overlap
- A **Filter Tasks** panel — choose a pet and/or status (Pending / Completed) to narrow the view
- A time-sorted table of all matching scheduled tasks
- A collapsible **Skipped tasks** expander listing anything that didn't fit

---

### Example Workflow

1. Fill in Owner Info: name **Jordan**, 90 min available
2. Add **Mochi** (cat, age 11, notes: "hyperthyroid, needs morning meds") — she's tagged as senior
3. Add tasks for Mochi: Morning meds (5 min, high, daily), Feeding (10 min, high, daily), Brushing (15 min, low, weekly)
4. Add **Biscuit** (dog, age 4)
5. Add tasks for Biscuit: Morning walk (30 min, high, daily), Training (20 min, medium, daily), Playtime (25 min, low, daily)
6. Click **Generate schedule** — all three high-priority tasks fill first; Playtime is skipped (only 10 min left)
7. Conflict banner shows green — no overlaps in the generated plan
8. Use the **Filter by pet** dropdown to select Mochi and see only her three scheduled tasks
