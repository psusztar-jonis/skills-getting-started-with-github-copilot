"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to known state before each test"""
    from app import activities
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
    })


class TestGetActivities:
    """Tests for getting activities"""

    def test_get_activities_returns_200(self, client):
        """Test that getting activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that getting activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self, client):
        """Test that activities contain the expected activities"""
        response = client.get("/activities")
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_contains_activity_details(self, client):
        """Test that each activity contains required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_get_activities_contains_participants(self, client):
        """Test that activities contain participants"""
        response = client.get("/activities")
        data = response.json()
        assert len(data["Chess Club"]["participants"]) > 0


class TestSignup:
    """Tests for signing up for activities"""

    def test_signup_returns_200(self, client):
        """Test that signup returns a 200 status code on success"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200

    def test_signup_adds_participant(self, client):
        """Test that signup adds the participant to the activity"""
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]

    def test_signup_returns_success_message(self, client):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]

    def test_signup_duplicate_returns_400(self, client):
        """Test that signing up twice returns a 400 error"""
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_to_nonexistent_activity_returns_404(self, client):
        """Test that signing up for a non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_full_activity_returns_400(self, client):
        """Test that signing up for a full activity returns 400"""
        from app import activities
        # Create an activity at capacity
        activities["Full Activity"] = {
            "description": "Full activity",
            "schedule": "Never",
            "max_participants": 1,
            "participants": ["existing@mergington.edu"]
        }
        
        response = client.post(
            "/activities/Full Activity/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 400
        assert "full" in response.json()["detail"]


class TestUnregister:
    """Tests for unregistering from activities"""

    def test_unregister_returns_200(self, client):
        """Test that unregister returns a 200 status code on success"""
        response = client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200

    def test_unregister_removes_participant(self, client):
        """Test that unregister removes the participant from the activity"""
        client.post("/activities/Chess Club/unregister?email=michael@mergington.edu")
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]

    def test_unregister_returns_success_message(self, client):
        """Test that unregister returns a success message"""
        response = client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]

    def test_unregister_not_registered_returns_400(self, client):
        """Test that unregistering when not registered returns 400"""
        response = client.post(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_from_nonexistent_activity_returns_404(self, client):
        """Test that unregistering from a non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestRoot:
    """Tests for the root endpoint"""

    def test_root_redirects(self, client):
        """Test that the root endpoint redirects to the static page"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
