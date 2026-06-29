from pawpal_system import Task, Pet


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
