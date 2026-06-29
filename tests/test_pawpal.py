from datetime import date, timedelta

from pawpal_system import Task, Pet, Owner, Schedule


def test_mark_complete_changes_status():
    task = Task(title="Morning walk", duration_minutes=30, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_reset_clears_completed_status():
    task = Task(title="Morning walk", duration_minutes=30, priority="high")
    task.mark_complete()
    task.reset()
    assert task.completed is False


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="cat")
    assert len(pet.tasks) == 0
    pet.add_task(Task(title="Feeding", duration_minutes=10, priority="high"))
    assert len(pet.tasks) == 1
    pet.add_task(Task(title="Brushing", duration_minutes=15, priority="low"))
    assert len(pet.tasks) == 2


def test_mark_complete_is_idempotent():
    task = Task(title="Morning walk", duration_minutes=30, priority="high")
    task.mark_complete()
    task.mark_complete()
    assert task.completed is True


# --- Sorting correctness ---

def test_sort_by_time_returns_chronological_order():
    # Three tasks with different priorities so generate() places them in
    # priority order (high first), but sort_by_time() must re-sort them by
    # their assigned clock time — which is also earliest-first after a
    # greedy fill, so we verify the actual HH:MM values are ascending.
    owner = Owner(name="Alex", available_minutes=120)
    pet = Pet(name="Buddy", species="dog")
    pet.add_task(Task(title="Walk",     duration_minutes=30, priority="high"))
    pet.add_task(Task(title="Feeding",  duration_minutes=20, priority="medium"))
    pet.add_task(Task(title="Grooming", duration_minutes=15, priority="low"))
    owner.add_pet(pet)

    schedule = Schedule(owner, start_time="08:00")
    schedule.generate()
    tasks_in_time_order = schedule.sort_by_time()

    times = [t.time for t in tasks_in_time_order]
    assert times == sorted(times), f"Expected ascending times, got {times}"


# --- Recurrence logic ---

def test_daily_task_recurrence_schedules_next_day():
    today = date.today()
    pet = Pet(name="Luna", species="cat")
    pet.add_task(Task(
        title="Feeding",
        duration_minutes=10,
        priority="high",
        frequency="daily",
        due_date=today,
    ))

    next_task = pet.mark_task_complete("Feeding")

    assert next_task is not None, "Expected a new Task to be returned"
    assert next_task.completed is False, "Next occurrence must start as pending"
    assert next_task.due_date == today + timedelta(days=1), (
        f"Expected due_date {today + timedelta(days=1)}, got {next_task.due_date}"
    )


# --- Conflict detection ---

def test_detect_conflicts_flags_overlapping_tasks():
    # Build a schedule where two tasks share the exact same time slot so
    # their windows definitely overlap, then confirm a warning is produced.
    owner = Owner(name="Sam", available_minutes=240)
    pet_a = Pet(name="Rex",   species="dog")
    pet_b = Pet(name="Mochi", species="cat")
    pet_a.add_task(Task(title="Walk",    duration_minutes=30, priority="high"))
    pet_b.add_task(Task(title="Feeding", duration_minutes=20, priority="high"))
    owner.add_pet(pet_a)
    owner.add_pet(pet_b)

    schedule = Schedule(owner, start_time="08:00")
    schedule.generate()

    # Force both tasks onto the same time slot to guarantee a conflict.
    for st in schedule._plan:
        st.task.time = "08:00"
        st.time_slot = "08:00"

    conflicts = schedule.detect_conflicts()
    assert len(conflicts) > 0, "Expected at least one conflict warning"
    assert "WARNING" in conflicts[0]
