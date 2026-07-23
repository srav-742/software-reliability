import sys
import os

# Add the backend root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.services.api_key_scanner import (
    detect_keys_in_content,
    calculate_key_reliability,
    DetectedKey,
    KeyStatus,
)

def test_detect_keys_in_content():
    content = """
    # Configuration keys
    OPENAI_KEY = "sk-proj-fake1234567890abcdef1234567890abcdef1234567890abcdef"
    STRIPE_KEY = "sk_test_fake1234567890abcdef1234567890abcdef"
    GENERIC_KEY = "SECRET_KEY=my-super-secret-key-that-is-long"
    """
    
    keys = detect_keys_in_content(content, "config.py")
    
    providers = [k.provider for k in keys]
    assert "openai" in providers
    assert "stripe" in providers
    assert "generic" in providers
    
    # Check masking
    openai_key = next(k for k in keys if k.provider == "openai")
    assert openai_key.masked_key.startswith("sk-pro")
    assert len(openai_key.masked_key) < len(openai_key.raw_key)

def test_calculate_key_reliability():
    # 1. Invalid key, hardcoded in python source code
    key1 = DetectedKey(
        provider="openai",
        raw_key="sk-123",
        masked_key="sk-...",
        file_path="src/main.py",
        line_number=5,
        status=KeyStatus.INVALID,
    )
    chance1, risk1, reasons1 = calculate_key_reliability(key1)
    assert chance1 == 1.0
    assert risk1 == "critical"
    assert any("validation failed" in r.lower() for r in reasons1)
    assert any("hardcoded" in r.lower() for r in reasons1)

    # 2. Valid key in configuration (.env)
    key2 = DetectedKey(
        provider="stripe",
        raw_key="sk_test_123",
        masked_key="sk_tes...",
        file_path=".env",
        line_number=2,
        status=KeyStatus.VALID,
    )
    chance2, risk2, reasons2 = calculate_key_reliability(key2)
    assert chance2 == 0.10
    assert risk2 == "low"
    assert any("active and successfully validated" in r.lower() for r in reasons2)
    assert not any("hardcoded" in r.lower() for r in reasons2)

    # 3. Unknown status key, hardcoded in source code
    key3 = DetectedKey(
        provider="github",
        raw_key="ghp_123",
        masked_key="ghp_...",
        file_path="index.js",
        line_number=10,
        status=KeyStatus.UNKNOWN,
    )
    chance3, risk3, reasons3 = calculate_key_reliability(key3)
    # Base chance unknown (0.40) + hardcoded penalty (0.30) = 0.70
    assert chance3 == 0.70
    assert risk3 == "high"
    assert any("could not be validated online" in r.lower() for r in reasons3)
    assert any("hardcoded in source code" in r.lower() for r in reasons3)
