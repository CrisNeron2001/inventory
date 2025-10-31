import flet as ft
from abc import ABC, abstractmethod
from typing import Any

class Info(ABC):
    def __init__(self, title: str, info_id: str) -> None:
        self.title = title
        self.info_id = info_id
        self.controls: list[ft.Control] = []
        
    @abstractmethod
    def create_controls(self, info_data: Any) -> list[ft.Control]:
        pass
    
    @abstractmethod
    def get_data(self) -> dict[str, Any]:
        pass