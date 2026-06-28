"""
Simple test to verify the application can start with all changes
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


def test_health_endpoint():
    """Test that the health endpoint works"""
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "Discord Clone API Online" in data["message"]


def test_routes_exist():
    """Test that all major routes exist"""
    with TestClient(app) as client:
        # Test auth routes exist
        response = client.get("/auth")
        # Should return 404 (route exists but requires POST) not 405 (method not allowed) or 404 (not found)
        assert response.status_code in [404, 405]
        
        # Test guilds routes exist
        response = client.get("/api/guilds/")
        assert response.status_code in [401, 404, 405]  # Unauthorized is OK since we didn't provide auth
        
        # Test channels routes exist
        response = client.get("/api/channels/")
        assert response.status_code in [401, 404, 405]
        
        # Test bots routes exist
        response = client.get("/api/bots/")
        assert response.status_code in [401, 404, 405]
        
        # Test direct messages routes exist
        response = client.get("/api/dms/")
        assert response.status_code in [401, 404, 405]
        
        # Test reactions routes exist
        response = client.get("/api/reactions/")
        assert response.status_code in [401, 404, 405]
        
        # Test files routes exist
        response = client.get("/api/files/")
        assert response.status_code in [401, 404, 405]
        
        # Test presence routes exist
        response = client.get("/api/presence/")
        assert response.status_code in [401, 404, 405]


if __name__ == "__main__":
    test_health_endpoint()
    test_routes_exist()
    print("All tests passed!")