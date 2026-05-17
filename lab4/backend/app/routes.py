from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import schemas, models
from .database import get_db

router = APIRouter(prefix="/api")

# ---------- Клиенты ----------
@router.get("/clients", response_model=List[schemas.ClientOut])
def get_clients(db: Session = Depends(get_db)):
    return db.query(models.Client).all()

@router.get("/clients/{client_id}", response_model=schemas.ClientOut)
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.post("/clients", response_model=schemas.ClientOut)
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    # Проверяем уникальность телефона и почты
    if db.query(models.Client).filter(models.Client.phone == client.phone).first():
        raise HTTPException(status_code=400, detail="Phone already registered")
    if db.query(models.Client).filter(models.Client.email == client.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    db_client = models.Client(**client.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@router.put("/clients/{client_id}", response_model=schemas.ClientOut)
def update_client(client_id: int, client: schemas.ClientUpdate, db: Session = Depends(get_db)):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    for key, value in client.dict(exclude_unset=True).items():
        setattr(db_client, key, value)
    db.commit()
    db.refresh(db_client)
    return db_client

@router.delete("/clients/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(db_client)
    db.commit()
    return {"message": "Client deleted"}

# ---------- Абонементы ----------
@router.get("/memberships/active")
def get_active_memberships(db: Session = Depends(get_db)):
    query_result = db.query(
        models.Membership.id,
        models.Membership.client_id,
        models.Client.name.label("client_name"), # Берем имя клиента
        models.Membership.type,
        models.Membership.start_date,
        models.Membership.end_date,
        models.Membership.is_active
    ).join(
        models.Client, models.Membership.client_id == models.Client.id
    ).filter(
        models.Membership.is_active == True
    ).all()
    result_list = []
    for row in query_result:
        result_list.append({
            "id": row.id,
            "client_id": row.client_id,
            "client_name": row.client_name,
            "type": row.type,
            "start_date": row.start_date,
            "end_date": row.end_date,
            "is_active": row.is_active
        })
    
    return result_list

@router.post("/memberships", response_model=schemas.MembershipOut)
def create_membership(membership: schemas.MembershipCreate, db: Session = Depends(get_db)):
    # Проверяем существование клиента
    client = db.query(models.Client).filter(models.Client.id == membership.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db_membership = models.Membership(**membership.dict())
    db.add(db_membership)
    db.commit()
    db.refresh(db_membership)
    return db_membership

# ---------- Тренировки ----------
@router.get("/trainings", response_model=List[schemas.TrainingOut])
def get_trainings(db: Session = Depends(get_db)):
    return db.query(models.Training).all()

@router.get("/clients/{client_id}/trainings", response_model=List[schemas.TrainingOut])
def get_client_trainings(client_id: int, db: Session = Depends(get_db)):
    # Проверяем существование клиента (опционально)
    # if not db.query(models.Client).get(client_id):
    #     raise HTTPException(404, "Client not found")
        
    return db.query(models.Training).filter(models.Training.client_id == client_id).all()

@router.post("/trainings", response_model=schemas.TrainingOut)
def create_training(training: schemas.TrainingCreate, db: Session = Depends(get_db)):
    # Проверяем существование клиента
    client = db.query(models.Client).filter(models.Client.id == training.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db_training = models.Training(**training.dict())
    db.add(db_training)
    db.commit()
    db.refresh(db_training)
    return db_training
# НОВЫЙ МАРШРУТ: Статистика посещений клиента
@router.get("/clients/{client_id}/visit-stat", response_model=dict)
def get_client_visit_stat(client_id: int, db: Session = Depends(get_db)):
    # Считаем количество записей в таблице Training для данного клиента
    visit_count = db.query(models.Training).filter(models.Training.client_id == client_id).count()
    
    if visit_count == 0:
        raise HTTPException(status_code=404, detail="Тренировок для этого клиента не найдено")
    
    return {
        "client_id": client_id,
        "total_visits": visit_count
    }
# НОВЫЙ МАРШРУТ: История тренировок (улучшенный)
@router.get("/clients/{client_id}/trainings", response_model=List[schemas.TrainingOut])
def get_client_trainings(client_id: int, db: Session = Depends(get_db)):
    # Проверяем, существует ли клиент
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    
    # Получаем все тренировки для этого клиента
    trainings = db.query(models.Training).filter(models.Training.client_id == client_id).all()
    
    if not trainings:
        raise HTTPException(status_code=404, detail="Тренировок для этого клиента не найдено")
    
    return trainings