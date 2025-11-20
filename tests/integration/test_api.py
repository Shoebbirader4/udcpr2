import pytest
import requests
import time

BASE_URL = "http://localhost:5000/api"
RULE_ENGINE_URL = "http://localhost:5001"
RAG_URL = "http://localhost:8002"

class TestAuthAPI:
    def test_register_user(self):
        """Test user registration"""
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "name": "Test User",
            "email": f"test_{int(time.time())}@example.com",
            "password": "Test123!@#"
        })
        assert response.status_code == 201
        assert "token" in response.json()
    
    def test_login_user(self):
        """Test user login"""
        # First register
        email = f"test_{int(time.time())}@example.com"
        requests.post(f"{BASE_URL}/auth/register", json={
            "name": "Test User",
            "email": email,
            "password": "Test123!@#"
        })
        
        # Then login
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": "Test123!@#"
        })
        assert response.status_code == 200
        assert "token" in response.json()

class TestProjectAPI:
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        email = f"test_{int(time.time())}@example.com"
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "name": "Test User",
            "email": email,
            "password": "Test123!@#"
        })
        return response.json()["token"]
    
    def test_create_project(self, auth_token):
        """Test project creation"""
        response = requests.post(
            f"{BASE_URL}/projects",
            json={
                "name": "Test Project",
                "location": "Mumbai",
                "jurisdiction": "Maharashtra",
                "zone": "Residential",
                "plotArea": 1000,
                "roadWidth": 12,
                "buildingHeight": 15,
                "floors": 4,
                "builtUpArea": 800,
                "useType": "residential"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Test Project"
    
    def test_get_projects(self, auth_token):
        """Test getting user projects"""
        response = requests.get(
            f"{BASE_URL}/projects",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

class TestRuleEngineAPI:
    def test_evaluate_project(self):
        """Test rule engine evaluation"""
        response = requests.post(f"{RULE_ENGINE_URL}/evaluate", json={
            "jurisdiction": "Maharashtra",
            "zone": "Residential",
            "plot_area": 1000,
            "road_width": 12,
            "building_height": 15,
            "floors": 4,
            "built_up_area": 800,
            "use_type": "residential"
        })
        assert response.status_code == 200
        data = response.json()
        assert "fsi" in data
        assert "setbacks" in data
        assert "parking" in data
    
    def test_calculate_fsi(self):
        """Test FSI calculation"""
        response = requests.post(f"{RULE_ENGINE_URL}/calculate/fsi", json={
            "jurisdiction": "Maharashtra",
            "zone": "Residential",
            "plot_area": 1000,
            "road_width": 12
        })
        assert response.status_code == 200
        data = response.json()
        assert "base_fsi" in data
        assert "max_fsi" in data

class TestRAGAPI:
    def test_query_regulations(self):
        """Test RAG service query"""
        response = requests.post(f"{RAG_URL}/query", json={
            "question": "What is the FSI for residential buildings?",
            "jurisdiction": "Maharashtra"
        })
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
    
    def test_health_check(self):
        """Test RAG service health"""
        response = requests.get(f"{RAG_URL}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

class TestEndToEndWorkflow:
    def test_complete_project_workflow(self):
        """Test complete project submission and evaluation workflow"""
        # 1. Register user
        email = f"test_{int(time.time())}@example.com"
        register_response = requests.post(f"{BASE_URL}/auth/register", json={
            "name": "Test User",
            "email": email,
            "password": "Test123!@#"
        })
        assert register_response.status_code == 201
        token = register_response.json()["token"]
        
        # 2. Create project
        project_response = requests.post(
            f"{BASE_URL}/projects",
            json={
                "name": "Integration Test Project",
                "location": "Mumbai",
                "jurisdiction": "Maharashtra",
                "zone": "Residential",
                "plotArea": 1000,
                "roadWidth": 12,
                "buildingHeight": 15,
                "floors": 4,
                "builtUpArea": 800,
                "useType": "residential"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert project_response.status_code == 201
        project_id = project_response.json()["_id"]
        
        # 3. Evaluate project
        eval_response = requests.post(
            f"{BASE_URL}/projects/{project_id}/evaluate",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert eval_response.status_code == 200
        
        # 4. Get project details
        get_response = requests.get(
            f"{BASE_URL}/projects/{project_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == 200
        assert get_response.json()["evaluation"] is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
