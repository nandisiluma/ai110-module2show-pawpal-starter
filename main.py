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

# --- Mochi's tasks ---
mochi.add_task(Task(title="Morning meds",   duration_minutes=5,  priority="high"))
mochi.add_task(Task(title="Feeding",        duration_minutes=10, priority="high",   frequency="daily"))
mochi.add_task(Task(title="Brushing",       duration_minutes=15, priority="low",    frequency="weekly"))

# --- Biscuit's tasks ---
biscuit.add_task(Task(title="Morning walk", duration_minutes=30, priority="high"))
biscuit.add_task(Task(title="Training",     duration_minutes=20, priority="medium"))
biscuit.add_task(Task(title="Playtime",     duration_minutes=25, priority="low"))

print(jordan)
print(mochi)
for t in mochi.tasks:
    print(" ", t)
print(biscuit)
for t in biscuit.tasks:
    print(" ", t)

# --- Generate and print today's schedule ---
print("\n" + "=" * 40)
schedule = Schedule(owner=jordan, start_time="08:00")
schedule.generate()
print(schedule.explain())
