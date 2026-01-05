import unittest
from io import BytesIO
from fastapi import status
from tests.unittest_base import BaseTestCase
from models.data_room import File


class TestFileList(BaseTestCase):
    """Tests for the GET /files endpoint."""

    def test_list_files_authenticated(self):
        """Test listing files for authenticated user."""
        # Create a test file
        test_file = File(
            name="Test PDF",
            folder_id=self.test_folder.id,
            file_path="/uploads/2026/1/1/test.pdf",
            file_size=1024,
            file_type="pdf"
        )
        self.db.add(test_file)
        self.db.commit()

        response = self.client.get(
            f"/api/v0/files?folder_id={self.test_folder.id}",
            headers=self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertGreaterEqual(len(data), 1)

    def test_list_files_unauthenticated(self):
        """Test listing files without authentication."""
        response = self.client.get(
            f"/api/v0/files?folder_id={self.test_folder.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_files_invalid_folder(self):
        """Test listing files in non-existent folder."""
        response = self.client.get(
            "/api/v0/files?folder_id=99999",
            headers=self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_files_unauthorized_folder(self):
        """Test listing files in folder from dataroom owned by another user."""
        response = self.client.get(
            f"/api/v0/files?folder_id={self.test_folder.id}",
            headers=self.auth_headers_2
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestFileUpload(BaseTestCase):
    """Tests for the POST /files endpoint."""

    def test_upload_file_success(self):
        """Test successful file upload."""
        pdf_content = b"%PDF-1.4\n%Test PDF content"

        response = self.client.post(
            f"/api/v0/files?folder_id={self.test_folder.id}&name=Test+File",
            headers=self.auth_headers,
            files={"file": ("test.pdf", BytesIO(pdf_content), "application/pdf")}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["name"], "Test File")
        self.assertEqual(data["folder_id"], self.test_folder.id)

    def test_upload_non_pdf_file(self):
        """Test uploading non-PDF file."""
        response = self.client.post(
            f"/api/v0/files?folder_id={self.test_folder.id}&name=Test+File",
            headers=self.auth_headers,
            files={"file": ("test.txt", BytesIO(b"Not a PDF"), "text/plain")}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_to_invalid_folder(self):
        """Test uploading to non-existent folder."""
        pdf_content = b"%PDF-1.4\n%Test PDF"

        response = self.client.post(
            f"/api/v0/files?folder_id=99999&name=Test+File",
            headers=self.auth_headers,
            files={"file": ("test.pdf", BytesIO(pdf_content), "application/pdf")}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_upload_unauthorized_folder(self):
        """Test uploading to folder in dataroom owned by another user."""
        pdf_content = b"%PDF-1.4\n%Test PDF"

        response = self.client.post(
            f"/api/v0/files?folder_id={self.test_folder.id}&name=Test+File",
            headers=self.auth_headers_2,
            files={"file": ("test.pdf", BytesIO(pdf_content), "application/pdf")}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestFileGet(BaseTestCase):
    """Tests for the GET /files/{file_id} endpoint."""

    def test_get_file_success(self):
        """Test successfully retrieving file details."""
        test_file = File(
            name="Test PDF",
            folder_id=self.test_folder.id,
            file_path="/uploads/2026/1/1/test.pdf",
            file_size=1024,
            file_type="pdf"
        )
        self.db.add(test_file)
        self.db.commit()
        self.db.refresh(test_file)

        response = self.client.get(
            f"/api/v0/files/{test_file.id}",
            headers=self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["id"], test_file.id)
        self.assertEqual(data["name"], "Test PDF")

    def test_get_file_not_found(self):
        """Test retrieving non-existent file."""
        response = self.client.get(
            "/api/v0/files/99999",
            headers=self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_file_unauthorized(self):
        """Test retrieving file from dataroom owned by another user."""
        test_file = File(
            name="Test PDF",
            folder_id=self.test_folder.id,
            file_path="/uploads/2026/1/1/test.pdf",
            file_size=1024,
            file_type="pdf"
        )
        self.db.add(test_file)
        self.db.commit()
        self.db.refresh(test_file)

        response = self.client.get(
            f"/api/v0/files/{test_file.id}",
            headers=self.auth_headers_2
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestFileUpdate(BaseTestCase):
    """Tests for the PATCH /files/{file_id} endpoint."""

    def test_update_file_success(self):
        """Test successful file rename."""
        test_file = File(
            name="Test PDF",
            folder_id=self.test_folder.id,
            file_path="/uploads/2026/1/1/test.pdf",
            file_size=1024,
            file_type="pdf"
        )
        self.db.add(test_file)
        self.db.commit()
        self.db.refresh(test_file)

        response = self.client.patch(
            f"/api/v0/files/{test_file.id}",
            headers=self.auth_headers,
            json={"name": "Renamed PDF"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["name"], "Renamed PDF")

    def test_update_file_not_found(self):
        """Test updating non-existent file."""
        response = self.client.patch(
            "/api/v0/files/99999",
            headers=self.auth_headers,
            json={"name": "Renamed PDF"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_file_unauthorized(self):
        """Test updating file in dataroom owned by another user."""
        test_file = File(
            name="Test PDF",
            folder_id=self.test_folder.id,
            file_path="/uploads/2026/1/1/test.pdf",
            file_size=1024,
            file_type="pdf"
        )
        self.db.add(test_file)
        self.db.commit()
        self.db.refresh(test_file)

        response = self.client.patch(
            f"/api/v0/files/{test_file.id}",
            headers=self.auth_headers_2,
            json={"name": "Hacked Name"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestFileDelete(BaseTestCase):
    """Tests for the DELETE /files/{file_id} endpoint."""

    def test_delete_file_success(self):
        """Test successful file deletion."""
        test_file = File(
            name="Test PDF",
            folder_id=self.test_folder.id,
            file_path="/uploads/2026/1/1/test.pdf",
            file_size=1024,
            file_type="pdf"
        )
        self.db.add(test_file)
        self.db.commit()
        self.db.refresh(test_file)

        response = self.client.delete(
            f"/api/v0/files/{test_file.id}",
            headers=self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_file_not_found(self):
        """Test deleting non-existent file."""
        response = self.client.delete(
            "/api/v0/files/99999",
            headers=self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_file_unauthorized(self):
        """Test deleting file in dataroom owned by another user."""
        test_file = File(
            name="Test PDF",
            folder_id=self.test_folder.id,
            file_path="/uploads/2026/1/1/test.pdf",
            file_size=1024,
            file_type="pdf"
        )
        self.db.add(test_file)
        self.db.commit()
        self.db.refresh(test_file)

        response = self.client.delete(
            f"/api/v0/files/{test_file.id}",
            headers=self.auth_headers_2
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestFileShare(BaseTestCase):
    """Tests for file sharing endpoints."""

    def test_create_file_share_success(self):
        """Test successful file share creation."""
        test_file = File(
            name="Test PDF",
            folder_id=self.test_folder.id,
            file_path="/uploads/2026/1/1/test.pdf",
            file_size=1024,
            file_type="pdf"
        )
        self.db.add(test_file)
        self.db.commit()
        self.db.refresh(test_file)

        response = self.client.post(
            f"/api/v0/files/{test_file.id}/share",
            headers=self.auth_headers,
            json={}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("token", data)
        self.assertEqual(data["file_id"], test_file.id)

    def test_create_file_share_invalid_file(self):
        """Test creating share for non-existent file."""
        response = self.client.post(
            "/api/v0/files/99999/share",
            headers=self.auth_headers,
            json={}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_file_shares_success(self):
        """Test listing file shares."""
        test_file = File(
            name="Test PDF",
            folder_id=self.test_folder.id,
            file_path="/uploads/2026/1/1/test.pdf",
            file_size=1024,
            file_type="pdf"
        )
        self.db.add(test_file)
        self.db.commit()
        self.db.refresh(test_file)

        # Create a share
        self.client.post(
            f"/api/v0/files/{test_file.id}/share",
            headers=self.auth_headers,
            json={}
        )

        # List shares
        response = self.client.get(
            f"/api/v0/files/{test_file.id}/shares",
            headers=self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
