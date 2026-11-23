from fastapi.testclient import TestClient 
from app import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "Healthy"}

def test_gethome_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
  "message": "CloudOps Application",
  "version": "1.0.0"
}

def test_version_endpoint():
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {"version": "1.0.0"}

def test_create_users_endpoint():
    response = client.post(
        "/users",
        json={"name": "Test User"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Test User"
    assert isinstance(data["id"], int)

def test_get_user_endpoint():
    response = client.get("/users")

    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    
    for user in data:
        assert isinstance(user["id"], int) 
        assert isinstance(user["name"], str)

def test_user_id_endpoint():
    created = client.post(
        "/users",
        json={"name": "Individual Test"}
    )

    assert created.status_code == 200

    user_id = created.json()["id"]
    response = client.get(f"/users/{user_id}")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data["id"], int)
    assert data["id"] == user_id
    assert data["name"] == "Individual Test"

def test_update_user_endpoint():
    # Step 1: Create a user
    created = client.post(
        "/users",
        json={"name": "Original User"}
    )

    assert created.status_code == 200
    user_id = created.json()["id"]

    # Step 2: Update the user
    response = client.put(
        f"/users/{user_id}",
        json={"name": "Updated User"}
    )

    assert response.status_code == 200

    # Step 3: Verify the updated data
    data = response.json()

    assert data["id"] == user_id
    assert data["name"] == "Updated User"

def test_delete_user_endpoint():
    created = client.post(
        "/users",
        json={"name": "Deleted User"}
    )
    assert created.status_code == 200
    user_id = created.json()["id"]

    # delete user
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "User deleted successfully."
    assert data["user"]["id"] == user_id
    assert data["user"]["name"] == "Deleted User"


# Invalid user test (HTTP 422)

def test_invalid_user_endpoint():
    response = client.post(
        "/users",
        json={"name": ""}
    )

    assert response.status_code == 422

# Nonexistent user test (HTTP 404)
def test_nonexistent_user_endpoint():
    response = client.get("/users/999999")
    assert response.status_code == 404