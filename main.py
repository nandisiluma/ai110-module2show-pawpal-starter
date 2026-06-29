from pawpal_system import Task, Pet, Owner, Schedule, ScheduledTask

# --- Owner ---
jordan = Owner(name="Jordan", available_minutes=90)
jordan.add_preference("no tasks before 8am")

# --- Pets ---
mochi = Pet(name="Mochi", species="cat", age=11, notes="hyperthyroid, needs morning meds")
biscuit = Pet(name="Biscuit", species="dog", age=4)

# --- Link pets to owner ---
jordan.add_pet(mochi)
jordan.add_pet(biscuit)

# --- Mochi's tasks (added out of order: low before high) ---
mochi.add_task(Task(title="Brushing",       duration_minutes=15, priority="low",    frequency="weekly"))
mochi.add_task(Task(title="Feeding",        duration_minutes=10, priority="high",   frequency="daily"))
mochi.add_task(Task(title="Morning meds",   duration_minutes=5,  priority="high"))

# --- Biscuit's tasks (added out of order: low before high) ---
biscuit.add_task(Task(title="Playtime",     duration_minutes=25, priority="low"))
biscuit.add_task(Task(title="Training",     duration_minutes=20, priority="medium"))
biscuit.add_task(Task(title="Morning walk", duration_minutes=30, priority="high"))

print(jordan)
print(mochi)
for t in mochi.tasks:
    print(" ", t)
print(biscuit)
for t in biscuit.tasks:
    print(" ", t)

# --- Generate schedule ---
print("\n" + "=" * 40)
schedule = Schedule(owner=jordan, start_time="08:00")
schedule.generate()
print(schedule.explain())

# --- sort_by_time ---
print("\n" + "=" * 40)
print("Tasks sorted by scheduled time:")
for task in schedule.sort_by_time():
    print(f"  {task.time} — {task.title} ({task.priority} priority)")

# --- filter_tasks: by pet name ---
print("\n" + "=" * 40)
print("Biscuit's scheduled tasks:")
for st in schedule.filter_tasks(pet_name="Biscuit"):
    print(f"  {st.time_slot} — {st.task.title} ({st.task.priority} priority)")

# --- filter_tasks: pending tasks only ---
print("\n" + "=" * 40)
print("All pending (not completed) tasks:")
for st in schedule.filter_tasks(completed=False):
    print(f"  [{st.pet_name}] {st.task.title} — {st.time_slot}")

# --- filter_tasks: combined (Mochi's pending tasks) ---
print("\n" + "=" * 40)
print("Mochi's pending tasks:")
for st in schedule.filter_tasks(pet_name="Mochi", completed=False):
    print(f"  {st.time_slot} — {st.task.title}")

# --- Conflict detection demo ---
print("\n" + "=" * 40)
print("Conflict detection:")

# No conflicts expected from generate() — confirm clean plan first
conflicts = schedule.detect_conflicts()
print(f"  Conflicts in generated plan: {len(conflicts)} (expected 0)")

# Manually inject a task that overlaps Mochi's Feeding (08:00–08:10)
# "Emergency vet" starts at 08:05, so its window [08:05, 08:25) overlaps [08:00, 08:10)
emergency = Task(title="Emergency vet", duration_minutes=20, priority="high")
schedule._plan.append(ScheduledTask("08:05", emergency, "Mochi"))

conflicts = schedule.detect_conflicts()
print(f"  Conflicts after injecting overlapping task: {len(conflicts)}")
for warning in conflicts:
    print(f"  {warning}")

# --- Auto-recurrence demo ---
print("\n" + "=" * 40)
print("Marking tasks complete and checking next occurrences:")

# Complete a daily task — next due tomorrow
next_feeding = mochi.mark_task_complete("Feeding")
print(f"\n  Completed: Mochi's Feeding")
print(f"  Next occurrence: {next_feeding.title} | due: {next_feeding.due_date} | status: {'pending' if not next_feeding.completed else 'done'}")

# Complete a weekly task — next due in 7 days
next_brushing = mochi.mark_task_complete("Brushing")
print(f"\n  Completed: Mochi's Brushing")
print(f"  Next occurrence: {next_brushing.title} | due: {next_brushing.due_date} | status: {'pending' if not next_brushing.completed else 'done'}")

# Show Mochi's full task list — completed originals + new pending occurrences
print("\n" + "=" * 40)
print("Mochi's full task list after completions:")
for t in mochi.tasks:
    print(f"  {t}")
