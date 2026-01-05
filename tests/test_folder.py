import unittest
from fastapi import status
from tests.unittest_base import BaseTestCase


class TestFolderList(BaseTestCase):
    """Tests for the GET /folders endpoint."""

    def test_list_folders_authenticated(self):
        """Test listing folders for authenticated user."""
        response = self.client.get(
            f"/api/v0/folders?dataroom_id={self.test_dataroom.id}",
            headers=self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertGreaterEqual(len(data), 1)

    def test_list_folders_unauthenticated(self):
        """Test listing folders without authentication."""
        response = self.client.get(
            f"/api/v0/folders?dataroom_id={self.test_dataroom.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_folders_invalid_dataroom(self):
        """Test listing folders for non-existent dataroom."""
        response = self.client.get(
            "/api/v0/folders?dataroom_id=99999",
            headers=self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_folders_unauthorized_dataroom(self):
        """Test listing folders in dataroom owned by another user."""
        response = self.client.get(
            f"/api/v0/folders?dataroom_id={self.test_dataroom.id}",
            headers=self.auth_headers_2
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestFolderCreate(BaseTestCase):
    """Tests for the POST /folders endpoint."""

    def test_create_folder_success(self):
        """Test successful folder creation."""
        response = self.client.post(
            "/api/v0/folders",
            headers=self.auth_headers,
            json={
                "name": "New Folder",
                "dataroom_id": self.test_dataroom.id
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["name"], "New Folder")
        self.assertEqual(data["dataroom_id"], self.test_dataroom.id)

    def test_create_folder_with_parent(self):
        """Test creating a subfolder."""
        response = self.client.post(
            "/api/v0/folders",
            headers=self.auth_headers,
            json={
                "name": "SubFolder",
                "dataroom_id": self.test_dataroom.id,
                "parent_id": self.test_folder.id
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["name"], "SubFolder")
        self.assertEqual(data["parent_id"], self.test_folder.id)

    def test_create_folder_invalid_dataroom(self):
        """Test creating folder in non-existent dataroom."""
        response = self.client.post(
            "/api/v0/folders",
            headers=self.auth_headers,
            json={
                "name": "New Folder",
                "dataroom_id": 99999
            }
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_folder_unauthorized_dataroom(self):
        """Test creating folder in dataroom owned by another user."""
        response = self.client.post(
            "/api/v0/folders",
            headers=self.auth_headers_2,
            json={
                "name": "New Folder",
                "dataroom_id": self.test_dataroom.id
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_folder_invalid_parent(self):
        """Test creating folder with non-existent parent."""
        response = self.client.post(
            "/api/v0/folders",
            headers=self.auth_headers,
            json={
                "name": "New Folder",
                "dataroom_id": self.test_dataroom.id,
                "parent_id": 99999
            }
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestFolderGet(BaseTestCase):
    """Tests for the GET /folders/{folder_id} endpoint."""

    def test_get_folder_success(self):
        """Test successfully retrieving a folder."""
        response = self.client.get(
            f"/api/v0/folders/{self.test_folder.id}",
            headers=self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["id"], self.test_folder.id)
        self.assertEqual(data["name"], self.test_folder.name)

    def test_get_folder_not_found(self):
        """Test retrieving non-existent folder."""
        response = self.client.get(
            "/api/v0/folders/99999",
            headers=self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_folder_unauthorized(self):
        """Test retrieving folder in dataroom owned by another user."""
        response = self.client.get(
            f"/api/v0/folders/{self.test_folder.id}",
            headers=self.auth_headers_2
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_folder_unauthenticated(self):
        """Test retrieving folder without authentication."""
        response = self.client.get(f"/api/v0/folders/{self.test_folder.id}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestFolderUpdate(BaseTestCase):
    """Tests for the PATCH /folders/{folder_id} endpoint."""

    def test_update_folder_success(self):
        """Test successful folder rename."""
        response = self.client.patch(
            f"/api/v0/folders/{self.test_folder.id}",
            headers=self.auth_headers,
            json={
                "name": "Renamed Folder"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["name"], "Renamed Folder")

    def test_update_folder_not_found(self):
        """Test updating non-existent folder."""
        response = self.client.patch(
            "/api/v0/folders/99999",
            headers=self.auth_headers,
            json={
                "name": "Renamed Folder"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_folder_unauthorized(self):
        """Test updating folder in dataroom owned by another user."""
        response = self.client.patch(
            f"/api/v0/folders/{self.test_folder.id}",
            headers=self.auth_headers_2,
            json={
                "name": "Hacked Name"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_folder_unauthenticated(self):
        """Test updating folder without authentication."""
        response = self.client.patch(
            f"/api/v0/folders/{self.test_folder.id}",
            json={
                "name": "Renamed Folder"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestFolderDelete(BaseTestCase):
    """Tests for the DELETE /folders/{folder_id} endpoint."""

    def test_delete_folder_success(self):
        """Test successful folder deletion."""
        response = self.client.delete(
            f"/api/v0/folders/{self.test_folder.id}",
            headers=self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_folder_not_found(self):
        """Test deleting non-existent folder."""
        response = self.client.delete(
            "/api/v0/folders/99999",
            headers=self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_folder_unauthorized(self):
        """Test deleting folder in dataroom owned by another user."""
        response = self.client.delete(
            f"/api/v0/folders/{self.test_folder.id}",
            headers=self.auth_headers_2
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_folder_unauthenticated(self):
        """Test deleting folder without authentication."""
        response = self.client.delete(f"/api/v0/folders/{self.test_folder.id}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
