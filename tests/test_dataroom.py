import unittest
from fastapi import status
from tests.unittest_base import BaseTestCase


class TestDataRoomList(BaseTestCase):
    """Tests for the GET /datarooms endpoint."""

    def test_list_datarooms_authenticated(self):
        """Test listing datarooms for authenticated user."""
        response = self.client.get(
            "/api/v0/datarooms",
            headers=self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.test_dataroom.id)
        self.assertEqual(data[0]["name"], "Test DataRoom")

    def test_list_datarooms_unauthenticated(self):
        """Test listing datarooms without authentication."""
        response = self.client.get("/api/v0/datarooms")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_datarooms_empty(self):
        """Test listing datarooms when user has none."""
        response = self.client.get(
            "/api/v0/datarooms",
            headers=self.auth_headers_2
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 0)


class TestDataRoomCreate(BaseTestCase):
    """Tests for the POST /datarooms endpoint."""

    def test_create_dataroom_success(self):
        """Test successful dataroom creation."""
        response = self.client.post(
            "/api/v0/datarooms",
            headers=self.auth_headers,
            json={
                "name": "New DataRoom",
                "description": "New Description"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["name"], "New DataRoom")
        self.assertEqual(data["description"], "New Description")
        self.assertIn("id", data)

    def test_create_dataroom_without_description(self):
        """Test dataroom creation without description."""
        response = self.client.post(
            "/api/v0/datarooms",
            headers=self.auth_headers,
            json={
                "name": "DataRoom Without Desc"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["name"], "DataRoom Without Desc")

    def test_create_dataroom_unauthenticated(self):
        """Test dataroom creation without authentication."""
        response = self.client.post(
            "/api/v0/datarooms",
            json={
                "name": "New DataRoom",
                "description": "New Description"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestDataRoomGet(BaseTestCase):
    """Tests for the GET /datarooms/{dataroom_id} endpoint."""

    def test_get_dataroom_success(self):
        """Test successfully retrieving a dataroom."""
        response = self.client.get(
            f"/api/v0/datarooms/{self.test_dataroom.id}",
            headers=self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["id"], self.test_dataroom.id)
        self.assertEqual(data["name"], self.test_dataroom.name)

    def test_get_dataroom_not_found(self):
        """Test retrieving non-existent dataroom."""
        response = self.client.get(
            "/api/v0/datarooms/99999",
            headers=self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_dataroom_unauthorized(self):
        """Test retrieving dataroom owned by another user."""
        response = self.client.get(
            f"/api/v0/datarooms/{self.test_dataroom.id}",
            headers=self.auth_headers_2
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_dataroom_unauthenticated(self):
        """Test retrieving dataroom without authentication."""
        response = self.client.get(f"/api/v0/datarooms/{self.test_dataroom.id}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestDataRoomUpdate(BaseTestCase):
    """Tests for the PUT /datarooms/{dataroom_id} endpoint."""

    def test_update_dataroom_success(self):
        """Test successful dataroom update."""
        response = self.client.put(
            f"/api/v0/datarooms/{self.test_dataroom.id}",
            headers=self.auth_headers,
            json={
                "name": "Updated DataRoom",
                "description": "Updated Description"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["name"], "Updated DataRoom")
        self.assertEqual(data["description"], "Updated Description")

    def test_update_dataroom_partial(self):
        """Test partial dataroom update (only name)."""
        response = self.client.put(
            f"/api/v0/datarooms/{self.test_dataroom.id}",
            headers=self.auth_headers,
            json={
                "name": "Updated Name"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["name"], "Updated Name")

    def test_update_dataroom_not_found(self):
        """Test updating non-existent dataroom."""
        response = self.client.put(
            "/api/v0/datarooms/99999",
            headers=self.auth_headers,
            json={
                "name": "Updated Name"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_dataroom_unauthorized(self):
        """Test updating dataroom owned by another user."""
        response = self.client.put(
            f"/api/v0/datarooms/{self.test_dataroom.id}",
            headers=self.auth_headers_2,
            json={
                "name": "Hacked Name"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestDataRoomDelete(BaseTestCase):
    """Tests for the DELETE /datarooms/{dataroom_id} endpoint."""

    def test_delete_dataroom_success(self):
        """Test successful dataroom deletion."""
        response = self.client.delete(
            f"/api/v0/datarooms/{self.test_dataroom.id}",
            headers=self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_dataroom_not_found(self):
        """Test deleting non-existent dataroom."""
        response = self.client.delete(
            "/api/v0/datarooms/99999",
            headers=self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_dataroom_unauthorized(self):
        """Test deleting dataroom owned by another user."""
        response = self.client.delete(
            f"/api/v0/datarooms/{self.test_dataroom.id}",
            headers=self.auth_headers_2
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_dataroom_unauthenticated(self):
        """Test deleting dataroom without authentication."""
        response = self.client.delete(f"/api/v0/datarooms/{self.test_dataroom.id}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
