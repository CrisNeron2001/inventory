from core.abstracts.form import Form
from typing import Callable

class StepNavigator:
    def __init__(self, steps: list[Form], on_step_change: Callable):
        self.steps = steps
        self.current_step = 0
        self.on_step_change = on_step_change
        
    def next_step(self) -> bool:
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.on_step_change(self.current_step)
            return True
        return False
    
    def prev_step(self) -> bool:
        if self.current_step > 0:
            self.current_step -= 1
            self.on_step_change(self.current_step)
            return True
        return False
    
    def go_to_step(self, step_index: int) -> bool:
        if 0 <= step_index < len(self.steps):
            self.current_step = step_index
            self.on_step_change(self.current_step)
            return True
        return False
    
    def can_go_next(self) -> bool:
        return self.current_step < len(self.steps) - 1
    
    def can_go_prev(self) -> bool:
        return self.current_step > 0
    
    def get_current_step(self) -> Form:
        return self.steps[self.current_step]
    
    def is_last_step(self) -> bool:
        return self.current_step == len(self.steps) -1
    
    def is_first_step(self) -> bool:
        return self.current_step == 0
    
    def get_progress_percentage(self) -> float:
        return (self.current_step + 1) / len(self.steps) * 100
    
    def reset(self) -> None:
        self.current_step = 0
        self.on_step_change(self.current_step)