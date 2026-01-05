import secrets
from database import Base
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship


class DataRoom(Base):
    """
    DataRoom Model - Represents the top-level container for documents.
    
    Attrs:
        - id: Unique identifier (primary key)
        - name: The name of the data room
        - description: Optional description of the data room
        - owner_id: Foreign key linking to the User who owns this dataroom
        - created_at: Timestamp when the data room was created
        - updated_at: Timestamp when the data room was last updated
        - owner: Relationship to the User who owns this dataroom
        - folders: Relationship to all folders in this data room
    """
    __tablename__ = "dataroom"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship: many DataRooms belong to one User
    owner = relationship("User", back_populates="datarooms")

    # Relationship: one DataRoom has many Folders
    # When a DataRoom is deleted, all its folders are also deleted (cascade)
    folders = relationship("Folder", back_populates="dataroom", cascade="all, delete-orphan")


class Folder(Base):
    """
    Folder Model - Represents a folder that can contain files and other folders.
    
    Attrs:
        - id: Unique identifier (primary key)
        - name: The name of the folder
        - dataroom_id: Foreign key linking to the DataRoom
        - parent_id: Foreign key linking to parent Folder (for nesting)
        - created_at: Timestamp when the folder was created
        - updated_at: Timestamp when the folder was last updated
        - dataroom: Relationship to the parent DataRoom
        - parent: Relationship to parent Folder
        - subfolders: Relationship to child Folders
        - files: Relationship to all files in this folder
    """
    __tablename__ = "folder"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    dataroom_id = Column(Integer, ForeignKey("dataroom.id"), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("folder.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship: many Folders belong to one DataRoom
    dataroom = relationship("DataRoom", back_populates="folders")

    # Self-referential relationship: Folders can contain other Folders
    # parent: The folder that contains this folder
    # subfolders: The folders contained in this folder
    parent = relationship(
        "Folder",
        remote_side=[id],
        back_populates="subfolders",
        foreign_keys=[parent_id]
    )
    subfolders = relationship(
        "Folder",
        back_populates="parent",
        cascade="all, delete-orphan",
        foreign_keys=[parent_id]
    )

    # Relationship: one Folder has many Files
    files = relationship("File", back_populates="folder", cascade="all, delete-orphan")


class File(Base):
    """
    File Model - Represents a PDF file stored in a folder.
    
    Attrs:
        - id: Unique identifier (primary key)
        - name: The display name of the file
        - folder_id: Foreign key linking to the Folder
        - file_path: The actual path to the file on disk
        - file_size: Size of the file in bytes
        - file_type: The type of file (always 'pdf' for now)
        - created_at: Timestamp when the file was created
        - updated_at: Timestamp when the file was last updated
        - folder: Relationship to the parent Folder
    """
    __tablename__ = "file"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    folder_id = Column(Integer, ForeignKey("folder.id"), nullable=False, index=True)
    file_path = Column(String(512), nullable=False)
    file_size = Column(BigInteger, default=0)
    file_type = Column(String(50), default="pdf")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship: many Files belong to one Folder
    folder = relationship("Folder", back_populates="files")
    shares = relationship("FileShare", back_populates="file", cascade="all, delete-orphan")


class FileShare(Base):
    """
    FileShare Model - Represents a shareable link for a file.

    Attrs:
        - id: Unique identifier (primary key)
        - file_id: Foreign key linking to the File
        - token: Unique token for the share link
        - created_at: Timestamp when the share was created
        - expires_at: Optional expiration timestamp (None = never expires)
        - file: Relationship to the shared File
    """
    __tablename__ = "file_share"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("file.id"), nullable=False, index=True)
    token = Column(String(64), nullable=False, unique=True, index=True, default=lambda: secrets.token_urlsafe(48))
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(days=1))

    file = relationship("File", back_populates="shares")
