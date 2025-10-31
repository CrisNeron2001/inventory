import flet as ft
from abc import ABC, abstractmethod
from typing import Any

class Form(ABC):
    def __init__(self, title: str, form_id: str) -> None:
        self.title = title
        self.form_id = form_id
        self.controls: list[ft.Control] = []
        
    @abstractmethod
    def create_controls(self, form_data: dict) -> list[ft.Control]:
        pass
    
    @abstractmethod
    def get_data(self) -> dict[Any, str]:
        pass
    
    @abstractmethod
    def validate(self) -> tuple[bool, list[str]]:
        pass
    
    @abstractmethod
    def reset(self) -> None:
        pass