from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    HTTPException,
    Depends
)

from database import get_db
from models import DataRoom, User
from dependencies import get_current_user
from api.v0.schemas import dataroom

router = APIRouter(prefix="/datarooms")


@router.get("", response_model=List[dataroom.DataRoomListResponse])
def list_datarooms(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get all data rooms for the current authenticated user.

    Requires: Valid JWT token in Authorization header
    """
    datarooms = db.query(DataRoom).filter(DataRoom.owner_id == current_user.id).all()
    return datarooms


@router.post("", response_model=dataroom.DataRoomResponse)
def create_dataroom(
    dataroom_data: dataroom.DataRoomCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new data room for the current authenticated user.

    Requires: Valid JWT token in Authorization header
    """
    # Create new database object from request data
    db_dataroom = DataRoom(
        name=dataroom_data.name,
        description=dataroom_data.description,
        owner_id=current_user.id
    )
    db.add(db_dataroom)
    db.commit()
    db.refresh(db_dataroom)
    return db_dataroom


@router.get("/{dataroom_id}", response_model=dataroom.DataRoomResponse)
def get_dataroom(
    dataroom_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific data room with all its folders and files.

    Requires: Valid JWT token and ownership of the dataroom
    """
    db_dataroom = db.query(DataRoom).filter(DataRoom.id == dataroom_id).first()
    if not db_dataroom:
        raise HTTPException(status_code=404, detail="Data room not found")

    # Check ownership
    if db_dataroom.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return db_dataroom


@router.put("/{dataroom_id}", response_model=dataroom.DataRoomResponse)
def update_dataroom(
    dataroom_id: int,
    dataroom_data: dataroom.DataRoomUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a data room.

    Requires: Valid JWT token and ownership of the dataroom
    """
    db_dataroom = db.query(DataRoom).filter(DataRoom.id == dataroom_id).first()
    if not db_dataroom:
        raise HTTPException(status_code=404, detail="Data room not found")

    # Check ownership
    if db_dataroom.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Update only fields that were provided (not None)
    if dataroom_data.name:
        db_dataroom.name = dataroom_data.name
    if dataroom_data.description is not None:
        db_dataroom.description = dataroom_data.description

    # Update the updated_at timestamp
    db_dataroom.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_dataroom)
    return db_dataroom


@router.delete("/{dataroom_id}", status_code=204)
def delete_dataroom(
    dataroom_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a data room.

    Requires: Valid JWT token and ownership of the dataroom
    """
    db_dataroom = db.query(DataRoom).filter(DataRoom.id == dataroom_id).first()
    if not db_dataroom:
        raise HTTPException(status_code=404, detail="Data room not found")

    # Check ownership
    if db_dataroom.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    db.delete(db_dataroom)
    db.commit()
    return {"message": "Data room deleted successfully"}
