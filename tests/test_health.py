"""
Unit tests for health check and other general endpoints using unittest.
"""
import unittest
from fastapi import status
from tests.unittest_base import BaseTestCase


class TestHealthCheck(BaseTestCase):
    """Tests for the GET /health endpoint."""

    def test_health_check_success(self):
        """Test health check endpoint returns healthy status."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["status"], "healthy")


class TestRootEndpoint(BaseTestCase):
    """Tests for root endpoints and static file serving."""

    def test_api_docs_accessible(self):
        """Test that API documentation is accessible."""
        response = self.client.get("/api/docs")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_openapi_schema_accessible(self):
        """Test that OpenAPI schema is accessible."""
        response = self.client.get("/api/openapi.json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("openapi", data)
        self.assertIn("paths", data)


if __name__ == '__main__':
    unittest.main()
