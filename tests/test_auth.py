import unittest
from fastapi import status
from tests.unittest_base import BaseTestCase


class TestAuthRegister(BaseTestCase):
    """Tests for the POST /auth/register endpoint."""

    def test_register_success(self):
        """Test successful user registration."""
        response = self.client.post(
            "/api/v0/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "password123"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["email"], "newuser@example.com")
        self.assertEqual(data["username"], "newuser")
        self.assertIn("id", data)
        self.assertNotIn("hashed_password", data)

    def test_register_duplicate_email(self):
        """Test registration with duplicate email."""
        response = self.client.post(
            "/api/v0/auth/register",
            json={
                "email": self.test_user.email,
                "username": "anotheruser",
                "password": "password123"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Email already registered", response.json()["detail"])

    def test_register_duplicate_username(self):
        """Test registration with duplicate username."""
        response = self.client.post(
            "/api/v0/auth/register",
            json={
                "email": "another@example.com",
                "username": self.test_user.username,
                "password": "password123"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Username already taken", response.json()["detail"])

    def test_register_invalid_email(self):
        """Test registration with invalid email format."""
        response = self.client.post(
            "/api/v0/auth/register",
            json={
                "email": "invalid-email",
                "username": "newuser",
                "password": "password123"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_register_missing_fields(self):
        """Test registration with missing required fields."""
        response = self.client.post(
            "/api/v0/auth/register",
            json={
                "email": "user@example.com"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)


class TestAuthLogin(BaseTestCase):
    """Tests for the POST /auth/login endpoint."""

    def test_login_success(self):
        """Test successful login."""
        response = self.client.post(
            "/api/v0/auth/login",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")

    def test_login_invalid_username(self):
        """Test login with invalid username."""
        response = self.client.post(
            "/api/v0/auth/login",
            json={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Invalid username or password", response.json()["detail"])

    def test_login_invalid_password(self):
        """Test login with invalid password."""
        response = self.client.post(
            "/api/v0/auth/login",
            json={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Invalid username or password", response.json()["detail"])

    def test_login_missing_fields(self):
        """Test login with missing fields."""
        response = self.client.post(
            "/api/v0/auth/login",
            json={
                "username": "testuser"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
