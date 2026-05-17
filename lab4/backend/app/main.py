from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import router
from . import models
from datetime import date

# Создаём таблицы
Base.metadata.create_all(bind=engine)

# Функция для начального заполнения БД (seed)
def seed_db():
    from sqlalchemy.orm import Session
    from .database import SessionLocal
    db = SessionLocal()
    
    # Проверяем, есть ли уже данные, чтобы не дублировать
    if db.query(models.Client).count() == 0:
        # Добавляем тестовых клиентов
        client1 = models.Client(name="Иван Петров", phone="+79001112233", email="ivan@mail.ru")
        client2 = models.Client(name="Мария Сидорова", phone="+79004445566", email="maria@mail.ru")
        
        db.add_all([client1, client2])
        db.commit()
        
        
        membership1 = models.Membership(
            client_id=1,
            type="Месячный",
            start_date=date(2026, 5, 16),   # Объект date: год, месяц, день
            end_date=date(2026, 6, 16),     # Объект date
            is_active=True
        )
        membership2 = models.Membership(
            client_id=2,
            type="Разовый",
            start_date=date(2026, 5, 16),
            end_date=date(2026, 5, 16),
            is_active=True
        )
        db.add_all([membership1, membership2])
        db.commit()
        
        # Добавляем историю тренировок
        # В функции seed_db()
        training1 = models.Training(
            client_id=1,
            date=date(2026, 5, 15), # Объект date
            activity="Тренажерный зал",
            duration_minutes=60
        )
        training2 = models.Training(
            client_id=2,
            date=date(2026, 5, 14), # Объект date
            activity="Йога",
            duration_minutes=90
        )
        db.add_all([training1, training2])
        db.commit()
        
    db.close()

app = FastAPI(title="Fitness Club API")

# Настройка CORS (разрешаем запросы с фронтенда)
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://frontend:80",
    "null"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
def startup():
    seed_db()