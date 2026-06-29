from dataclasses import dataclass, field
from datetime import date, timedelta
from itertools import combinations
from typing import Optional


@dataclass
class ScheduledTask:
    time_slot: str  # e.g. "08:00"
    task: "Task"
    pet_name: str   # which pet this task belongs to


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str                          # "low", "medium", or "high"
    frequency: str = "daily"               # "daily" or "weekly"
    completed: bool = field(default=False)
    time: str = ""
    due_date: date = field(default_factory=date.today)

    def priority_score(self) -> int:
        """Return a numeric score (1-3) for sorting by priority."""
        scores = {"low": 1, "medium": 2, "high": 3}
        return scores.get(self.priority, 0)

    def fits_in_time(self, remaining_minutes: int) -> bool:
        """Return True if this task's duration fits within the remaining time."""
        return self.duration_minutes <= remaining_minutes

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> "Task":
        """Return a fresh, uncompleted Task scheduled for the next occurrence.

        The due_date is advanced by 1 day for daily tasks and 7 days for weekly
        tasks using timedelta. All other attributes (title, duration, priority,
        frequency) are copied from the original. The original task is not modified.
        """
        days = 1 if self.frequency == "daily" else 7
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            due_date=self.due_date + timedelta(days=days),
        )

    def reset(self) -> None:
        """Reset this task's completion status to pending."""
        self.completed = False

    def __str__(self) -> str:
        """Return a readable summary of the task."""
        status = "done" if self.completed else "pending"
        return (
            f"{self.title} ({self.duration_minutes} min, {self.priority} priority, "
            f"{self.frequency}) [due: {self.due_date}] [{status}]"
        )


@dataclass
class Pet:
    name: str
    species: str
    age: int = 0
    notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        self.tasks.append(task)

    def mark_task_complete(self, title: str) -> Optional[Task]:
        """Mark a task complete by title and auto-schedule its next occurrence.

        Returns the newly created next-occurrence Task, or None if no matching
        pending task was found.
        """
        for task in self.tasks:
            if task.title == title and not task.completed:
                task.mark_complete()
                next_task = task.next_occurrence()
                self.tasks.append(next_task)
                return next_task
        return None

    def get_pending_tasks(self) -> list[Task]:
        """Return all tasks that have not yet been completed."""
        return [t for t in self.tasks if not t.completed]

    def is_senior(self) -> bool:
        """Return True if this pet is at or above the senior age threshold for its species."""
        senior_age = {"dog": 7, "cat": 10}
        return self.age >= senior_age.get(self.species, 8)

    def __str__(self) -> str:
        """Return a readable summary of the pet."""
        senior_tag = " (senior)" if self.is_senior() else ""
        notes_tag = f" | notes: {self.notes}" if self.notes else ""
        return f"{self.name} the {self.species}{senior_tag}{notes_tag}"


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[tuple[str, Task]]:
        """Return all pending tasks across all pets as (pet_name, task) pairs."""
        return [(pet.name, task) for pet in self.pets for task in pet.get_pending_tasks()]

    def set_available_time(self, minutes: int) -> None:
        """Update the owner's available time for the day, in minutes."""
        if minutes < 0:
            raise ValueError("Available time cannot be negative.")
        self.available_minutes = minutes

    def add_preference(self, preference: str) -> None:
        """Append a scheduling preference for the owner."""
        self.preferences.append(preference)

    def __str__(self) -> str:
        """Return a readable summary of the owner, their pets, and preferences."""
        prefs = ", ".join(self.preferences) if self.preferences else "none"
        pet_names = ", ".join(p.name for p in self.pets) if self.pets else "none"
        return f"{self.name} — {self.available_minutes} min available | pets: {pet_names} | preferences: {prefs}"


class Schedule:
    def __init__(self, owner: Owner, start_time: str = "08:00") -> None:
        """Set up a schedule for all of an owner's pets starting at start_time."""
        self.owner = owner
        self.start_time = start_time
        self._plan: list[ScheduledTask] = []

    def _parse_time(self, time_str: str) -> int:
        """Convert 'HH:MM' to total minutes since midnight."""
        hours, minutes = map(int, time_str.split(":"))
        return hours * 60 + minutes

    def _format_time(self, total_minutes: int) -> str:
        """Convert total minutes since midnight back to 'HH:MM'."""
        return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"

    def generate(self) -> list[ScheduledTask]:
        """Sort all pending tasks by priority and greedily assign time slots."""
        all_tasks = self.owner.get_all_tasks()
        sorted_tasks = sorted(all_tasks, key=lambda pt: pt[1].priority_score(), reverse=True)

        self._plan = []
        current_time = self._parse_time(self.start_time)
        remaining = self.owner.available_minutes

        for pet_name, task in sorted_tasks:
            if task.fits_in_time(remaining):
                task.time = self._format_time(current_time)
                self._plan.append(ScheduledTask(task.time, task, pet_name))
                current_time += task.duration_minutes
                remaining -= task.duration_minutes

        return self._plan

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> list[ScheduledTask]:
        """Return a filtered subset of the current scheduled plan.

        Args:
            pet_name: If provided, only include tasks belonging to this pet.
            completed: If True, return only completed tasks. If False, return
                only pending tasks. If None (default), completion status is ignored.

        Both filters compose — passing both applies both at once. Returns the
        full plan unchanged if both arguments are None.
        """
        results = self._plan
        if pet_name is not None:
            results = [st for st in results if st.pet_name == pet_name]
        if completed is not None:
            results = [st for st in results if st.task.completed == completed]
        return results

    def sort_by_time(self) -> list[Task]:
        """Return all scheduled Task objects sorted ascending by their assigned time slot.

        Relies on the task.time attribute, which is set by generate(). Always
        call generate() before sort_by_time(), otherwise task.time will be an
        empty string and the sort order will be undefined.
        """
        return sorted(
            (st.task for st in self._plan),
            key=lambda t: self._parse_time(t.time)
        )

    def detect_conflicts(self) -> list[str]:
        """Check the current plan for overlapping time windows.

        Returns a list of human-readable warning strings — one per conflict pair.
        Never raises; an empty list means no conflicts.
        """
        warnings = []
        for a, b in combinations(self._plan, 2):
            a_start = self._parse_time(a.time_slot)
            a_end = a_start + a.task.duration_minutes
            b_start = self._parse_time(b.time_slot)
            b_end = b_start + b.task.duration_minutes
            if a_start < b_end and b_start < a_end:
                warnings.append(
                    f"WARNING: [{a.pet_name}] {a.task.title} "
                    f"({a.time_slot}–{self._format_time(a_end)}) overlaps with "
                    f"[{b.pet_name}] {b.task.title} "
                    f"({b.time_slot}–{self._format_time(b_end)})"
                )
        return warnings

    def explain(self) -> str:
        """Return a human-readable plan showing scheduled and skipped tasks."""
        if not self._plan:
            return "No plan generated yet. Call generate() first."

        lines = [
            f"Daily plan for {self.owner.name}'s pets",
            f"Available time: {self.owner.available_minutes} min | Start: {self.start_time}",
            "",
        ]
        for scheduled in self._plan:
            t = scheduled.task
            lines.append(
                f"  {scheduled.time_slot} — [{scheduled.pet_name}] {t.title} "
                f"({t.duration_minutes} min) [priority: {t.priority}]"
            )

        scheduled_ids = {id(s.task) for s in self._plan}
        skipped = [(pn, t) for pn, t in self.owner.get_all_tasks() if id(t) not in scheduled_ids]
        if skipped:
            lines.append("")
            lines.append("Skipped (not enough time):")
            for pet_name, t in skipped:
                lines.append(f"  - [{pet_name}] {t.title} ({t.duration_minutes} min)")

        return "\n".join(lines)
