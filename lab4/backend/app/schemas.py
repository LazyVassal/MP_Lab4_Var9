from pydantic import BaseModel
from datetime import date
from typing import Optional

# --- Клиенты ---
class ClientBase(BaseModel):
    name: str
    phone: str
    email: str

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class ClientOut(ClientBase):
    id: int
    class Config:
        orm_mode = True

# --- Абонементы ---
class MembershipBase(BaseModel):
    client_id: int
    type: str  # Например: "Разовый", "Месячный", "Годовой"
    start_date: date
    end_date: date
    is_active: bool

class MembershipCreate(MembershipBase):
    pass

class MembershipOut(MembershipBase):
    id: int
    class Config:
        orm_mode = True

# --- Тренировки ---
class TrainingBase(BaseModel):
    client_id: int
    date: date
    activity: str  # Например: "Тренажерный зал", "Йога"
    duration_minutes: int

class TrainingCreate(TrainingBase):
    pass

class TrainingOut(TrainingBase):
    id: int
    class Config:
        orm_mode = True