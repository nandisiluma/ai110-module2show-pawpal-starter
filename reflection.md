# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

- What classes did you include, and what responsibilities did you assign to each?

Owner tracks name of the user, their availability and preferences
Pet tracks name of the pet, species, owner
Task tracks title of the task, duration_minutes, priority
Schedule tracks tasks, their duration and prioritization

Class | Key attributes | Key Methods
Owner | name, available_minutes | Constructor, set_available_time()
Pet | name, species, owner | Constructor
Task | title, duration_minutes, priority | priority_score(), fits_in_time()
Schedule | pet_name, tasks, start_time | generate_plan(), explain()

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

I received the following feedback from AI:

generate() return type is too vague

The UML says generate() list and the skeleton says list[Task]. But a schedule isn't just a list of tasks — each task needs an assigned time slot. Returning bare Task objects loses the "when" information. Consider returning a list of tuples like list[tuple[str, Task]] (e.g. [("08:00", walk_task), ("08:30", feed_task)]) or a small ScheduledTask dataclass with time_slot and task.

changes made:
Update the return type of generate() to carry time slot data, not just tasks.

---

Improvements

Scheduling Algorithm

1. Tie-break same-priority tasks by shortest duration first

Equal-priority tasks are ordered arbitrarily. Sorting by (priority_score DESC, duration_minutes ASC) packs more tasks into limited time — classic Shortest Job First for equal-weight work.

2. Fill leftover time with skipped tasks (gap-filling pass)

After the greedy pass, a second pass over skipped tasks can slot in any that now fit in the remaining minutes. Currently, a 5-minute gap left by a medium task would be wasted even if a short low-priority task fits perfectly.

Task Model 3. Add a must_schedule flag on Task

Medication tasks (like Mochi's meds) should never be silently dropped. A must_schedule: bool = False field lets generate() always slot these in first, separate from the priority queue — guarantees critical care regardless of available time.

4. Frequency-aware sorting

daily and weekly tasks are treated identically. Daily tasks should be scheduled before weekly tasks of the same priority level, since missing a daily task has compounding consequences.

Pet Model 5. Auto-boost senior pet task priority

is_senior() exists in pawpal_system.py:58 but the scheduler never uses it. Senior pets (Mochi at 11) could have their task priority_score() bumped +1 automatically during scheduling — their health needs are higher-stakes.

6. Group tasks by pet

The scheduler interleaves tasks from different pets arbitrarily. Grouping consecutive tasks by pet reduces context-switching (and is less disorienting for animals). Sort by (pet_name, priority_score DESC) after the priority sort, or group using itertools.groupby.

Owner / Preferences 7. Parse time preferences to enforce a hard start window

Preferences like "no tasks before 8am" are stored as raw strings in pawpal_system.py:92 but never read. A small regex (r'(\d+)(am|pm)') could extract the constraint and enforce start_time accordingly in generate().

8. Deduplicate tasks on add

add_task in pawpal_system.py:50 has no guard against duplicate titles. A check like if any(t.title == task.title for t in self.tasks) prevents accidental double-scheduling of the same task.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The `generate()` method uses a greedy algorithm: it sorts all tasks by priority score and assigns them to time slots in order, stopping whenever a task does not fit in the remaining time. It never backtracks or tries rearranging earlier decisions.

This means a long high-priority task that barely exceeds the remaining budget causes the scheduler to skip it — and then also skip any smaller lower-priority tasks that could have filled that gap, even if their total duration would have fit. An optimal knapsack algorithm would consider all combinations and find the highest-value set of tasks that fits within the available time.

The tradeoff is reasonable here because a pet care schedule is small (typically under 20 tasks per day), runs once per day, and needs to be easy to reason about. A greedy approach is O(n log n), always produces the same predictable result, and correctly handles the most common case where high-priority tasks (medication, feeding) are short enough to always be scheduled first. Optimality only matters when the schedule is tight and tasks are densely packed — a scenario where the owner's available time should simply be increased rather than relying on a more complex algorithm.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

I used AI tools at every stage, from creating the UML diagram, I gave it the list of classes I planned on implementing, then asked for a fully fledged UML diagram showing the relationships. I later used it to modify the UML diagram to match the final system design.

I also used AI to write all the code including the tests for this system. I wrote prompts in plain english and asked the AI assistant to translate my logic to code.

- What kinds of prompts or questions were most helpful?

I found direct prompts, that also asked the AI to validate its response helpful in ensuring that the code didn't break.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?

I am 4.5/5 confident.

- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I was able to implement all the required functionalities, and my tests passed.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

Weekly tasks (e.g. Brushing) compete for daily time slots the same way daily tasks do. An owner with 90 minutes might want weekly tasks only scheduled on specific days.
Fix: Add an optional preferred_days: list[str] field to Task (e.g. ["Monday", "Friday"]) and filter them out in generate() when today isn't a preferred day.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

It's important to understand the overall functionality of the system so you can lead the direction of the implementation. AI saves a great amount of time, and does a good job translating prompts to actual code.
