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

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

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
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
