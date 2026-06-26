from dataclasses import dataclass


@dataclass
class Owner:
    name: str
    available_minutes: int

    def set_available_time(self, minutes: int) -> None:
        pass

    def __str__(self) -> str:
        pass


@dataclass
class Pet:
    name: str
    species: str
    owner: Owner

    def __str__(self) -> str:
        pass


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", or "high"

    def priority_score(self) -> int:
        pass

    def fits_in_time(self, remaining_minutes: int) -> bool:
        pass

    def __str__(self) -> str:
        pass


class Schedule:
    def __init__(self, pet: Pet, start_time: str = "08:00") -> None:
        self.pet = pet
        self.tasks: list[Task] = []
        self.start_time = start_time

    def add_task(self, task: Task) -> None:
        pass

    def generate(self) -> list[Task]:
        pass

    def explain(self) -> str:
        pass
