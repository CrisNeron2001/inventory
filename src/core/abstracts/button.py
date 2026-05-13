from abc import ABC, abstractmethod
import flet as ft


class Button(ABC):
    def __init__(self, title: str, title_id: str) -> None:
        self.title = title
        self.title_id = title_id
        self.controls: list[ft.Control] = []

    @abstractmethod
    def create_controls(self) -> list[ft.Control]:
        pass
