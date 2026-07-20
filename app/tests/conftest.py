import sys
import os
import pytest

# Add the backend root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.database.base import Base
from app.database.session import engine
import app.models  # Ensures all models are registered with Base


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Automated fixture to ensure all tables exist during test execution."""
    Base.metadata.create_all(bind=engine)
    yield
    # Optional teardown after test session completes
