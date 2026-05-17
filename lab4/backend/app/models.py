from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from .database import Base

# 1. Модель Клиента (заменяет Product)
class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False, unique=True) # Телефон как уникальный ID
    email = Column(String, nullable=False, unique=True)
    
    # Связь с абонементами и тренировками
    memberships = relationship("Membership", back_populates="client")
    trainings = relationship("Training", back_populates="client")

# 2. Модель Абонемента (заменяет логику Supply)
class Membership(Base):
    __tablename__ = "memberships"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    
    type = Column(String, nullable=False) # "Разовый", "Месячный", "Годовой"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True) # Для быстрой фильтрации активных

    # Связь с клиентом
    client = relationship("Client", back_populates="memberships")

# 3. Модель Тренировки (новая сущность для истории посещений)
class Training(Base):
    __tablename__ = "trainings"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    
    date = Column(Date, nullable=False)
    activity = Column(String) # "Тренажерный зал", "Йога", "Плавание"
    duration_minutes = Column(Integer) # Длительность в минутах

    # Связь с клиентом
    client = relationship("Client", back_populates="trainings")