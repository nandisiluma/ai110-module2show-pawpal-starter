from dataclasses import dataclass, field


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

    def reset(self) -> None:
        """Reset this task's completion status to pending."""
        self.completed = False

    def __str__(self) -> str:
        """Return a readable summary of the task."""
        status = "done" if self.completed else "pending"
        return f"{self.title} ({self.duration_minutes} min, {self.priority} priority, {self.frequency}) [{status}]"


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
                self._plan.append(ScheduledTask(self._format_time(current_time), task, pet_name))
                current_time += task.duration_minutes
                remaining -= task.duration_minutes

        return self._plan

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
