import os
import io
import zipfile
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database.database import get_db
from app.repositories.api_key_repository import api_key_repository
from app.models.user import User

client = TestClient(app)


def create_sample_zip() -> bytes:
    """Create in-memory zip archive with sample Python source code."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        code = """
def add(a, b):
    # Sample function
    return a + b

def calculate_risk(x):
    if x > 10:
        return True
    return False
"""
        zip_file.writestr("main.py", code)
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def test_api_key_generation_and_validation():
    raw_key, prefix, key_hash = api_key_repository.generate_api_key()
    assert raw_key.startswith("sra_")
    assert prefix == raw_key[:10]
    assert len(key_hash) == 64  # SHA-256 length


def test_cli_help_execution():
    """Verify CLI client script runs cleanly with --help."""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(test_dir, "..", "..", ".."))
    cli_script = os.path.join(project_root, "cli", "reliability_cli.py")
    res = os.system(f'python "{cli_script}" --help')
    assert res == 0
