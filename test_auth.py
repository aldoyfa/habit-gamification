"""
Simple script to test authentication and protected endpoints
"""
import requests
from uuid import uuid4

BASE_URL = "http://localhost:8000/api"

# Create a test user (you'll need to manually add to repository)
test_username = "test_user"
test_password = "test_password"

def test_login():
    """Test login endpoint"""
    print("\n=== Testing Login ===")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": test_username,
            "password": test_password
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        return response.json()["accessToken"]
    return None


def test_create_habit(token):
    """Test creating a habit with authentication"""
    print("\n=== Testing Create Habit (Protected) ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/habits",
        json={
            "userId": str(uuid4()),  # This will be ignored, user from token is used
            "title": "Morning Exercise",
            "description": "Do 30 minutes of exercise every morning"
        },
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        return response.json()["habitId"]
    return None


def test_without_auth():
    """Test accessing protected endpoint without auth"""
    print("\n=== Testing Without Authentication ===")
    response = requests.post(
        f"{BASE_URL}/habits",
        json={
            "userId": str(uuid4()),
            "title": "Test Habit",
            "description": "Should fail without auth"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")


if __name__ == "__main__":
    print("Starting Authentication Tests...")
    print(f"Base URL: {BASE_URL}")
    
    # Test without authentication
    test_without_auth()
    
    # Test login and get token
    token = test_login()
    
    if token:
        print(f"\n✓ Got token: {token[:20]}...")
        
        # Test creating habit with authentication
        habit_id = test_create_habit(token)
        
        if habit_id:
            print(f"\n✓ Created habit: {habit_id}")
    else:
        print("\n✗ Login failed - make sure to create a test user first")
        print("\nTo create a test user, you can either:")
        print("1. Add a /register endpoint")
        print("2. Manually add to repository in main.py startup")
