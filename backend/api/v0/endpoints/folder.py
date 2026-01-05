from datetime import datetime
from typing import (
    List,
    Optional,
)
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from database import get_db
from models import (
    DataRoom,
    Folder,
    User
)
from dependencies import get_current_user
from api.v0.schemas import folder as folder_schemas

router = APIRouter(prefix="/folders")

@router.get("", response_model=List[folder_schemas.FolderResponse])
def list_folders(
    dataroom_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all folders in a dataroom (requires authentication).

    Requires: Valid JWT token and ownership of the dataroom
    """
    query = db.query(Folder)
    if dataroom_id:
        # Verify ownership of dataroom
        dataroom = db.query(DataRoom).filter(DataRoom.id == dataroom_id).first()
        if not dataroom:
            raise HTTPException(status_code=404, detail="Data room not found")

        if dataroom.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        query = query.filter(Folder.dataroom_id == dataroom_id)

    return query.all()


@router.post("", response_model=folder_schemas.FolderResponse)
def create_folder(
    folder: folder_schemas.FolderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new folder (requires authentication and ownership).

    Requires: Valid JWT token and ownership of the dataroom
    """
    # Check if dataroom exists and user owns it
    dataroom_exists = db.query(DataRoom).filter(DataRoom.id == folder.dataroom_id).first()
    if not dataroom_exists:
        raise HTTPException(status_code=404, detail="Data room not found")

    if dataroom_exists.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Check if parent folder exists (if provided)
    if folder.parent_id:
        parent_exists = db.query(Folder).filter(Folder.id == folder.parent_id).first()
        if not parent_exists:
            raise HTTPException(status_code=404, detail="Parent folder not found")

        # Verify parent folder belongs to same dataroom
        if parent_exists.dataroom_id != folder.dataroom_id:
            raise HTTPException(status_code=400, detail="Parent folder must be in the same dataroom")

    # Create new folder
    db_folder = Folder(
        name=folder.name,
        dataroom_id=folder.dataroom_id,
        parent_id=folder.parent_id
    )
    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)
    return db_folder


@router.get("/{folder_id}", response_model=folder_schemas.FolderResponse)
def get_folder(
    folder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific folder with its files and subfolders (requires authentication).

    Requires: Valid JWT token and ownership of the dataroom
    """
    db_folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not db_folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # Verify ownership through dataroom
    dataroom = db.query(DataRoom).filter(DataRoom.id == db_folder.dataroom_id).first()
    if dataroom.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return db_folder


@router.patch("/{folder_id}", response_model=folder_schemas.FolderResponse)
def update_folder(
    folder_id: int,
    folder: folder_schemas.FolderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a folder (rename - requires authentication).

    Requires: Valid JWT token and ownership of the dataroom
    """
    db_folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not db_folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # Verify ownership through dataroom
    dataroom = db.query(DataRoom).filter(DataRoom.id == db_folder.dataroom_id).first()
    if dataroom.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    db_folder.name = folder.name
    db_folder.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_folder)
    return db_folder


@router.delete("/{folder_id}", status_code=204)
def delete_folder(
    folder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a folder and all its contents (requires authentication).

    Requires: Valid JWT token and ownership of the dataroom
    """
    db_folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not db_folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # Verify ownership through dataroom
    dataroom = db.query(DataRoom).filter(DataRoom.id == db_folder.dataroom_id).first()
    if dataroom.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    db.delete(db_folder)
    db.commit()
