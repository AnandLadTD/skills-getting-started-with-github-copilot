"""Tests for the Mergington High School Activities API"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestActivitiesAPI:
    """Test cases for activities endpoints"""

    def test_root_redirect(self, client):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_get_activities(self, client):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
        # Verify structure of activity object
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_signup_for_activity(self, client):
        """Test signing up for an activity"""
        test_email = "test@mergington.edu"
        test_activity = "Chess Club"
        
        response = client.post(
            f"/activities/{test_activity}/signup",
            params={"email": test_email}
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert test_email in result["message"]
        assert test_activity in result["message"]
        
        # Verify participant was added
        activities = client.get("/activities").json()
        assert test_email in activities[test_activity]["participants"]

    def test_signup_duplicate(self, client):
        """Test that duplicate signup fails"""
        test_email = "alex@mergington.edu"  # Already exists in Debate Team
        test_activity = "Debate Team"
        
        response = client.post(
            f"/activities/{test_activity}/signup",
            params={"email": test_email}
        )
        
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "already signed up" in result["detail"].lower()

    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "test@mergington.edu"}
        )
        
        assert response.status_code == 404
        result = response.json()
        assert "Activity not found" in result["detail"]

    def test_unregister_from_activity(self, client):
        """Test unregistering a participant from an activity"""
        # First, add a participant
        test_email = "unregister_test@mergington.edu"
        test_activity = "Art Studio"
        
        # Sign up
        client.post(
            f"/activities/{test_activity}/signup",
            params={"email": test_email}
        )
        
        # Verify participant was added
        activities = client.get("/activities").json()
        assert test_email in activities[test_activity]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/{test_activity}/unregister",
            params={"email": test_email}
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert test_email in result["message"]
        assert test_activity in result["message"]
        
        # Verify participant was removed
        activities = client.get("/activities").json()
        assert test_email not in activities[test_activity]["participants"]

    def test_unregister_not_signed_up(self, client):
        """Test unregistering someone not signed up"""
        response = client.delete(
            "/activities/Basketball Team/unregister",
            params={"email": "not_signed_up@mergington.edu"}
        )
        
        assert response.status_code == 400
        result = response.json()
        assert "not signed up" in result["detail"].lower()

    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister",
            params={"email": "test@mergington.edu"}
        )
        
        assert response.status_code == 404
        result = response.json()
        assert "Activity not found" in result["detail"]

    def test_participant_count_after_signup(self, client):
        """Test that participant count updates after signup"""
        test_email = "count_test@mergington.edu"
        test_activity = "Programming Class"
        
        # Get initial count
        activities_before = client.get("/activities").json()
        initial_count = len(activities_before[test_activity]["participants"])
        
        # Sign up
        client.post(
            f"/activities/{test_activity}/signup",
            params={"email": test_email}
        )
        
        # Get updated count
        activities_after = client.get("/activities").json()
        new_count = len(activities_after[test_activity]["participants"])
        
        assert new_count == initial_count + 1
