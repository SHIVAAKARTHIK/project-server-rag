# import pytest
# from fastapi.testclient import TestClient

# from src.main import app


# @pytest.fixture
# def client():
#     """Create a test client for the FastAPI app."""
#     with TestClient(app) as test_client:
#         yield test_client


# @pytest.fixture
# def mock_clerk_id():
#     """Provide a mock clerk ID for testing."""
#     return "test_clerk_id_12345"

l = [3,4,5,6,7]

for i in l:
    l.remove(i)
    
print(l)