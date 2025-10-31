from dataclasses import dataclass
from typing import Optional

@dataclass
class BrandDTO:
    brand_id: Optional[int | None]
    name: str