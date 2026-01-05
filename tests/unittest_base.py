import os
import shutil
import unittest
import tempfile
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from main import app
from database import Base, get_db
from models.user import User
from models.data_room import DataRoom, Folder, File
from auth import hash_password, create_access_token


# Create a temporary file for SQLite test database
# Using file-based instead of in-memory to avoid connection issues
test_db_fd, test_db_path = tempfile.mkstemp(suffix='.db')
os.close(test_db_fd)

TEST_DATABASE_URL = f"sqlite:///{test_db_path}"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override the get_db dependency with test database."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


class BaseTestCase(unittest.TestCase):
    """Base test case class with common setup and teardown."""

    client = None  # Class variable to store the test client

    @classmethod
    def setUpClass(cls):
        """Set up test database and override dependencies once for all tests."""
        # Create all tables in the test database
        Base.metadata.create_all(bind=engine)

        # Override the dependency BEFORE creating the client
        app.dependency_overrides[get_db] = override_get_db

        # Create test client
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()
        engine.dispose()
        # Delete the temporary database file
        try:
            os.unlink(test_db_path)
        except OSError:
            # TODO: log the error
            pass

        # Delete upploads directory if it was created during tests
        current_dir = Path(__file__).resolve().parent
        upploads_dir = current_dir / "uploads"

        if upploads_dir.exists() and upploads_dir.is_dir():
            shutil.rmtree(upploads_dir)

    def setUp(self):
        """Set up for each test."""
        # Get a fresh database connection for this test
        self.db = TestingSessionLocal()

        # Create test users
        self.test_user = User(
            email="testuser@example.com",
            username="testuser",
            hashed_password=hash_password("password123"),
            is_active=True
        )
        self.db.add(self.test_user)
        self.db.commit()
        self.db.refresh(self.test_user)

        self.test_user_2 = User(
            email="otheruser@example.com",
            username="otheruser",
            hashed_password=hash_password("password123"),
            is_active=True
        )
        self.db.add(self.test_user_2)
        self.db.commit()
        self.db.refresh(self.test_user_2)

        # Create auth tokens and headers
        self.auth_token = create_access_token(data={"sub": str(self.test_user.id)})
        self.auth_token_2 = create_access_token(data={"sub": str(self.test_user_2.id)})

        self.auth_headers = {"Authorization": f"Bearer {self.auth_token}"}
        self.auth_headers_2 = {"Authorization": f"Bearer {self.auth_token_2}"}

        # Create test data room
        self.test_dataroom = DataRoom(
            name="Test DataRoom",
            description="Test Description",
            owner_id=self.test_user.id
        )
        self.db.add(self.test_dataroom)
        self.db.commit()
        self.db.refresh(self.test_dataroom)

        # Create test folder
        self.test_folder = Folder(
            name="Test Folder",
            dataroom_id=self.test_dataroom.id,
            parent_id=None
        )
        self.db.add(self.test_folder)
        self.db.commit()
        self.db.refresh(self.test_folder)

        # Create test subfolder
        self.test_subfolder = Folder(
            name="Test SubFolder",
            dataroom_id=self.test_dataroom.id,
            parent_id=self.test_folder.id
        )
        self.db.add(self.test_subfolder)
        self.db.commit()
        self.db.refresh(self.test_subfolder)

    def tearDown(self):
        """Tear down after each test."""
        # Clean up test data
        self.db.query(File).delete()
        self.db.query(Folder).delete()
        self.db.query(DataRoom).delete()
        self.db.query(User).delete()
        self.db.commit()
        self.db.close()


class TestCase(BaseTestCase):
    """Alias for BaseTestCase for easier use."""
    pass
