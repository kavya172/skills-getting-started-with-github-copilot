import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original activities
    original_activities = {
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
        "Art Club": {
            "description": "Explore different art techniques and create your own masterpieces",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["ava@mergington.edu", "liam@mergington.edu"]
        },
        "Music Club": {
            "description": "Learn to play instruments and perform in school concerts",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, stage production, and theater performances",                    
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["ethan@mergington.edu", "mia@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "olivia@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop public speaking and critical thinking skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["benjamin@mergington.edu", "amelia@mergington.edu"]
        }
    }
    
    # Reset activities to original state
    activities.clear()
    activities.update(original_activities)
    yield

class TestRoot:
    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"

class TestGetActivities:
    def test_get_activities(self, client):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 8  # All activities present
        
        # Check structure of one activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

class TestSignup:
    def test_signup_success(self, client):
        """Test successful signup"""
        response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify participant was added
        get_response = client.get("/activities")
        activities_data = get_response.json()
        assert "test@mergington.edu" in activities_data["Chess Club"]["participants"]

    def test_signup_duplicate(self, client):
        """Test signing up when already registered"""
        # First signup
        client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")
        
        # Second signup should fail
        response = client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_signup_invalid_activity(self, client):
        """Test signing up for nonexistent activity"""
        response = client.post("/activities/Nonexistent%20Activity/signup?email=test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

class TestUnregister:
    def test_unregister_success(self, client):
        """Test successful unregister"""
        # First sign up
        client.post("/activities/Programming%20Class/signup?email=unregister_test@mergington.edu")
        
        # Then unregister
        response = client.delete("/activities/Programming%20Class/unregister?email=unregister_test@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "unregister_test@mergington.edu" in data["message"]
        
        # Verify participant was removed
        get_response = client.get("/activities")
        activities_data = get_response.json()
        assert "unregister_test@mergington.edu" not in activities_data["Programming Class"]["participants"]

    def test_unregister_not_signed_up(self, client):
        """Test unregistering when not signed up"""
        response = client.delete("/activities/Chess%20Club/unregister?email=not_signed_up@mergington.edu")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"]

    def test_unregister_invalid_activity(self, client):
        """Test unregistering from nonexistent activity"""
        response = client.delete("/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]