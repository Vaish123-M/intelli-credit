from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app, _default_state, _persist_state, state


def _reset_state() -> None:
    state.clear()
    state.update(_default_state())
    _persist_state()


def test_register_user():
    """Test user registration."""
    _reset_state()
    client = TestClient(app)
    
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "securepassword123",
            "role": "analyst",
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert data["role"] == "analyst"
    assert "id" in data
    assert "hashed_password" in data
    assert data["is_active"] is True


def test_register_duplicate_email():
    """Test that duplicate email registration fails."""
    _reset_state()
    client = TestClient(app)
    
    # Register first user
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser1",
            "password": "securepassword123",
            "role": "analyst",
        }
    )
    
    # Try to register with same email
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser2",
            "password": "securepassword123",
            "role": "analyst",
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success():
    """Test successful login."""
    _reset_state()
    client = TestClient(app)
    
    # Register user first
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "securepassword123",
            "role": "analyst",
        }
    )
    
    # Login
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "securepassword123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    _reset_state()
    client = TestClient(app)
    
    response = client.post(
        "/auth/login",
        data={"username": "nonexistent", "password": "wrongpassword"}
    )
    
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_login_wrong_password():
    """Test login with correct username but wrong password."""
    _reset_state()
    client = TestClient(app)
    
    # Register user
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "securepassword123",
            "role": "analyst",
        }
    )
    
    # Login with wrong password
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_get_me_with_token():
    """Test getting current user info with valid token."""
    _reset_state()
    client = TestClient(app)
    
    # Register and login
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "securepassword123",
            "role": "analyst",
        }
    )
    
    login_response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "securepassword123"}
    )
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


def test_get_me_without_token():
    """Test getting current user without token fails."""
    _reset_state()
    client = TestClient(app)
    
    response = client.get("/auth/me")
    
    assert response.status_code == 401


def test_get_me_with_invalid_token():
    """Test getting current user with invalid token fails."""
    _reset_state()
    client = TestClient(app)
    
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401


def test_rate_limiting_on_register():
    """Test that rate limiting works on register endpoint."""
    _reset_state()
    client = TestClient(app)
    
    # Try to register multiple times quickly (should hit rate limit after 5)
    responses = []
    for i in range(7):
        response = client.post(
            "/auth/register",
            json={
                "email": f"test{i}@example.com",
                "username": f"testuser{i}",
                "password": "securepassword123",
                "role": "analyst",
            }
        )
        responses.append(response.status_code)
    
    # First 5 should succeed, rest should be rate limited
    assert responses.count(201) == 5
    assert responses.count(429) >= 1
