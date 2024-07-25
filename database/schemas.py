from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, ConfigDict


class UserDTO(BaseModel):
    tg_id: int
    username: Optional[str]
    name: Optional[str]
