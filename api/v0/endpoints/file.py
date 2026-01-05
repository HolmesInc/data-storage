import os
from datetime import datetime
from typing import (
    List,
    Optional,
)
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    UploadFile,
    File as FastAPIFile,
    Query,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import get_db
from models import (
    Folder,
    File as FileModel,
    FileShare,
    DataRoom,
    User
)
from dependencies import get_current_user
from api.v0.schemas import file as file_schemas

# Directory where uploaded files will be stored
# Files are organized in subdirectories by date (yyyy/mm/dd)
UPLOAD_DIR = "uploads"

router = APIRouter(prefix="/files")

@router.get("", response_model=List[file_schemas.FileResponse])
def list_files(
    folder_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all files in a folder (requires authentication).

    Requires: Valid JWT token and ownership of the dataroom
    """
    query = db.query(FileModel)
    if folder_id:
        # Verify the folder belongs to user's dataroom
        folder = db.query(Folder).filter(Folder.id == folder_id).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")

        dataroom = db.query(DataRoom).filter(DataRoom.id == folder.dataroom_id).first()
        if dataroom.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        query = query.filter(FileModel.folder_id == folder_id)

    return query.all()


@router.post("", response_model=file_schemas.FileResponse)
async def upload_file(
    folder_id: int = Query(..., description="ID of the folder"),
    name: str = Query(..., description="Name for the file"),
    file: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a PDF file to a folder (requires authentication).

    Requires: Valid JWT token and ownership of the dataroom
    """
    # Check if folder exists
    db_folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not db_folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # Verify ownership through dataroom
    dataroom = db.query(DataRoom).filter(DataRoom.id == db_folder.dataroom_id).first()
    if dataroom.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        # Read file content
        contents = await file.read()

        # Create file path (organize by date)
        now = datetime.utcnow()
        file_dir = os.path.join(UPLOAD_DIR, str(now.year), str(now.month), str(now.day))
        os.makedirs(file_dir, exist_ok=True)

        # Generate unique filename
        file_path = os.path.join(file_dir, file.filename)
        file_count = 1
        base_path = file_path
        while os.path.exists(file_path):
            name_part, ext = os.path.splitext(file.filename)
            file_path = os.path.join(file_dir, f"{name_part}_{file_count}{ext}")
            file_count += 1

        # Write file to disk
        with open(file_path, "wb") as f:
            f.write(contents)

        # Get file size
        file_size = len(contents)

        # Create database record
        db_file = FileModel(
            name=name,
            folder_id=folder_id,
            file_path=file_path,
            file_size=file_size,
            file_type="pdf"
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        return db_file

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.get("/{file_id}", response_model=file_schemas.FileResponse)
def get_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get file details (requires authentication and ownership).
    """
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    # Verify ownership through folder and dataroom
    folder = db.query(Folder).filter(Folder.id == db_file.folder_id).first()
    dataroom = db.query(DataRoom).filter(DataRoom.id == folder.dataroom_id).first()

    if dataroom.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return db_file


@router.patch("/{file_id}", response_model=file_schemas.FileResponse)
def update_file(
    file_id: int,
    file_update: file_schemas.FileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a file (rename - requires authentication and ownership).
    """
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    # Verify ownership
    folder = db.query(Folder).filter(Folder.id == db_file.folder_id).first()
    dataroom = db.query(DataRoom).filter(DataRoom.id == folder.dataroom_id).first()

    if dataroom.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    db_file.name = file_update.name
    db_file.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_file)
    return db_file


@router.delete("/{file_id}")
def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a file from the system (requires authentication and ownership).
    """
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    # Verify ownership
    folder = db.query(Folder).filter(Folder.id == db_file.folder_id).first()
    dataroom = db.query(DataRoom).filter(DataRoom.id == folder.dataroom_id).first()

    if dataroom.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Delete file from disk if it exists
    if os.path.exists(db_file.file_path):
        os.remove(db_file.file_path)

    # Delete database record
    db.delete(db_file)
    db.commit()
    return {"message": "File deleted successfully"}


@router.get("/{file_id}/download")
def download_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download a file (requires authentication and ownership).
    """
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    # Verify ownership
    folder = db.query(Folder).filter(Folder.id == db_file.folder_id).first()
    dataroom = db.query(DataRoom).filter(DataRoom.id == folder.dataroom_id).first()

    if dataroom.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    if not os.path.exists(db_file.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=db_file.file_path,
        filename=f"{db_file.name}.pdf",
        media_type="application/pdf"
    )


@router.get("/share/{share_token}/download")
def download_shared_file(share_token: str, db: Session = Depends(get_db)):
    """
    Download a file using a share token (PUBLIC - no authentication required).

    Anyone with a valid share token can download the file.
    """
    # Find the share record
    db_share = db.query(FileShare).filter(FileShare.token == share_token).first()
    if not db_share:
        raise HTTPException(status_code=404, detail="Share not found")

    # Check if share has expired
    if db_share.expires_at < datetime.utcnow():
        raise HTTPException(status_code=403, detail="Share link has expired")

    # Get the file
    db_file = db.query(FileModel).filter(FileModel.id == db_share.file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    if not os.path.exists(db_file.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=db_file.file_path,
        filename=f"{db_file.name}.pdf",
        media_type="application/pdf"
    )


@router.post("/{file_id}/share", response_model=file_schemas.FileShareResponse)
def create_file_share(
    file_id: int,
    share_data: file_schemas.FileShareCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a shareable link for a file (requires authentication and ownership).

    Returns a shareable token that can be used to download the file without authentication.
    """
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    # Verify ownership
    folder = db.query(Folder).filter(Folder.id == db_file.folder_id).first()
    dataroom = db.query(DataRoom).filter(DataRoom.id == folder.dataroom_id).first()

    if dataroom.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Create a new file share
    db_share = FileShare(
        file_id=file_id,
        expires_at=share_data.expires_at
    )
    db.add(db_share)
    db.commit()
    db.refresh(db_share)
    return db_share


@router.get("/{file_id}/shares", response_model=List[file_schemas.FileShareResponse])
def list_file_shares(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all shares for a file (requires authentication and ownership).
    """
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    # Verify ownership
    folder = db.query(Folder).filter(Folder.id == db_file.folder_id).first()
    dataroom = db.query(DataRoom).filter(DataRoom.id == folder.dataroom_id).first()

    if dataroom.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return db.query(FileShare).filter(FileShare.file_id == file_id).all()


@router.delete("/share/{share_id}")
def delete_file_share(
    share_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a file share (revoke access - requires authentication).
    """
    db_share = db.query(FileShare).filter(FileShare.id == share_id).first()
    if not db_share:
        raise HTTPException(status_code=404, detail="Share not found")

    # Verify ownership
    db_file = db.query(FileModel).filter(FileModel.id == db_share.file_id).first()
    folder = db.query(Folder).filter(Folder.id == db_file.folder_id).first()
    dataroom = db.query(DataRoom).filter(DataRoom.id == folder.dataroom_id).first()

    if dataroom.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    db.delete(db_share)
    db.commit()
    return {"message": "Share deleted successfully"}
