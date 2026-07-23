"""
API Key Scanner Service
-----------------------
Scans uploaded project files for embedded API keys (from .env, config files,
source code, etc.) and validates whether they are working or failed by making
lightweight test requests to the respective provider APIs.
"""

import os
import re
import zipfile
import tempfile
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

import httpx


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class KeyStatus(str, Enum):
    VALID = "valid"
    INVALID = "invalid"
    EXPIRED = "expired"
    RATE_LIMITED = "rate_limited"
    UNKNOWN = "unknown"


SCANNABLE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".env", ".cfg", ".ini", ".toml",
    ".yaml", ".yml", ".json", ".xml",
    ".properties", ".conf", ".sh", ".bat",
    ".go", ".java", ".cs", ".rb", ".php",
}

IGNORED_DIRS = {
    "node_modules", ".venv", "venv", "__pycache__",
    ".git", "build", "dist", ".next", ".nuxt",
    "vendor", "target", "bin", "obj",
}

VALIDATION_TIMEOUT = 5.0        # seconds per key
TOTAL_VALIDATION_TIMEOUT = 30.0  # seconds total


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class DetectedKey:
    """Represents a single API key found in the source code."""
    provider: str
    raw_key: str
    masked_key: str
    file_path: str
    line_number: int
    status: str = KeyStatus.UNKNOWN
    error_message: Optional[str] = None
    failure_chance: float = 0.0
    risk_level: str = "low"
    reasons: List[str] = field(default_factory=list)


@dataclass
class ScanResult:
    """Aggregated result of an API key scan."""
    total_keys_found: int = 0
    valid_keys: int = 0
    invalid_keys: int = 0
    unknown_keys: int = 0
    detected_keys: List[DetectedKey] = field(default_factory=list)
    scan_status: str = "completed"


# ---------------------------------------------------------------------------
# Key pattern definitions
# ---------------------------------------------------------------------------

# Each entry: (provider_name, compiled_regex, group_index_for_key)
# The regex should capture the actual key value in group 1 (or the full match).

KEY_PATTERNS: List[Tuple[str, re.Pattern, int]] = [
    # OpenAI
    ("openai", re.compile(
        r"""(?:^|["'\s=:,])"""          # boundary
        r"""(sk-[A-Za-z0-9_-]{20,})"""  # sk- followed by 20+ alphanum
        r"""(?:["'\s,;]|$)""",
        re.MULTILINE,
    ), 1),

    # OpenAI Project keys
    ("openai", re.compile(
        r"""(?:^|["'\s=:,])"""
        r"""(sk-proj-[A-Za-z0-9_-]{20,})"""
        r"""(?:["'\s,;]|$)""",
        re.MULTILINE,
    ), 1),

    # Google Cloud / Firebase API key
    ("google_cloud", re.compile(
        r"""(?:^|["'\s=:,])"""
        r"""(AIza[A-Za-z0-9_-]{35})"""
        r"""(?:["'\s,;]|$)""",
        re.MULTILINE,
    ), 1),

    # AWS Access Key ID
    ("aws", re.compile(
        r"""(?:^|["'\s=:,])"""
        r"""(AKIA[A-Z0-9]{16})"""
        r"""(?:["'\s,;]|$)""",
        re.MULTILINE,
    ), 1),

    # AWS Secret Access Key (40-char base64)
    ("aws_secret", re.compile(
        r"""(?:aws_secret_access_key|AWS_SECRET_ACCESS_KEY)\s*[=:]\s*["']?"""
        r"""([A-Za-z0-9/+=]{40})"""
        r"""["']?""",
        re.MULTILINE,
    ), 1),

    # Stripe Secret Key
    ("stripe", re.compile(
        r"""(?:^|["'\s=:,])"""
        r"""(sk_(?:live|test)_[A-Za-z0-9]{24,})"""
        r"""(?:["'\s,;]|$)""",
        re.MULTILINE,
    ), 1),

    # Stripe Publishable Key
    ("stripe_publishable", re.compile(
        r"""(?:^|["'\s=:,])"""
        r"""(pk_(?:live|test)_[A-Za-z0-9]{24,})"""
        r"""(?:["'\s,;]|$)""",
        re.MULTILINE,
    ), 1),

    # GitHub Token
    ("github", re.compile(
        r"""(?:^|["'\s=:,])"""
        r"""(gh[pous]_[A-Za-z0-9_]{36,})"""
        r"""(?:["'\s,;]|$)""",
        re.MULTILINE,
    ), 1),

    # GitHub Classic PAT
    ("github", re.compile(
        r"""(?:^|["'\s=:,])"""
        r"""(github_pat_[A-Za-z0-9_]{22,})"""
        r"""(?:["'\s,;]|$)""",
        re.MULTILINE,
    ), 1),

    # Twilio API Key
    ("twilio", re.compile(
        r"""(?:^|["'\s=:,])"""
        r"""(SK[a-f0-9]{32})"""
        r"""(?:["'\s,;]|$)""",
        re.MULTILINE,
    ), 1),

    # SendGrid API Key
    ("sendgrid", re.compile(
        r"""(?:^|["'\s=:,])"""
        r"""(SG\.[A-Za-z0-9_-]{22,}\.[A-Za-z0-9_-]{22,})"""
        r"""(?:["'\s,;]|$)""",
        re.MULTILINE,
    ), 1),

    # Slack Bot Token
    ("slack", re.compile(
        r"""(?:^|["'\s=:,])"""
        r"""(xox[bpas]-[A-Za-z0-9-]{10,})"""
        r"""(?:["'\s,;]|$)""",
        re.MULTILINE,
    ), 1),

    # Mailgun API Key
    ("mailgun", re.compile(
        r"""(?:^|["'\s=:,])"""
        r"""(key-[A-Za-z0-9]{32})"""
        r"""(?:["'\s,;]|$)""",
        re.MULTILINE,
    ), 1),

    # HuggingFace Token
    ("huggingface", re.compile(
        r"""(?:^|["'\s=:,])"""
        r"""(hf_[A-Za-z0-9]{34,})"""
        r"""(?:["'\s,;]|$)""",
        re.MULTILINE,
    ), 1),

    # Azure Subscription Key (32 hex chars, context-dependent)
    ("azure", re.compile(
        r"""(?:azure[_-]?(?:api[_-]?)?key|ocp-apim-subscription-key)\s*[=:]\s*["']?"""
        r"""([a-f0-9]{32})"""
        r"""["']?""",
        re.IGNORECASE | re.MULTILINE,
    ), 1),

    # Generic env-style keys (API_KEY=..., SECRET_KEY=..., etc.)
    ("generic", re.compile(
        r"""(?:API_KEY|SECRET_KEY|ACCESS_TOKEN|AUTH_TOKEN|PRIVATE_KEY_ID)\s*=\s*["']?"""
        r"""([A-Za-z0-9_\-./+=]{16,})"""
        r"""["']?\s*$""",
        re.MULTILINE,
    ), 1),
]


# ---------------------------------------------------------------------------
# Masking utility
# ---------------------------------------------------------------------------

def mask_key(raw_key: str) -> str:
    """Mask a key showing first 6 and last 4 chars."""
    if len(raw_key) <= 12:
        return raw_key[:4] + "..." + raw_key[-2:]
    return raw_key[:6] + "..." + raw_key[-4:]


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

def _should_scan_file(filename: str) -> bool:
    """Check if the file should be scanned based on extension."""
    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    # Also scan dotfiles like .env, .env.local, etc.
    basename = os.path.basename(filename).lower()
    if basename.startswith(".env"):
        return True

    return ext in SCANNABLE_EXTENSIONS


def detect_keys_in_content(content: str, file_path: str) -> List[DetectedKey]:
    """Scan file content for API keys using regex patterns."""
    detected: List[DetectedKey] = []
    seen_keys = set()  # Avoid duplicates in the same file

    for provider, pattern, group_idx in KEY_PATTERNS:
        for match in pattern.finditer(content):
            raw_key = match.group(group_idx).strip()

            # Skip if already seen or too short
            if raw_key in seen_keys or len(raw_key) < 10:
                continue

            # Calculate line number
            line_num = content[:match.start()].count("\n") + 1

            seen_keys.add(raw_key)
            detected.append(DetectedKey(
                provider=provider,
                raw_key=raw_key,
                masked_key=mask_key(raw_key),
                file_path=file_path,
                line_number=line_num,
            ))

    return detected


def scan_directory_for_keys(dir_path: str) -> List[DetectedKey]:
    """Walk a directory tree and detect API keys in all scannable files."""
    all_detected: List[DetectedKey] = []

    for root, dirs, files in os.walk(dir_path):
        # Filter out ignored directories in-place
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for filename in files:
            if not _should_scan_file(filename):
                continue

            file_path = os.path.join(root, filename)
            # Relative path for display
            rel_path = os.path.relpath(file_path, dir_path)

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                keys = detect_keys_in_content(content, rel_path)
                all_detected.extend(keys)
            except Exception:
                continue

    return all_detected


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

async def _validate_openai(key: str, client: httpx.AsyncClient) -> Tuple[str, Optional[str]]:
    """Validate an OpenAI API key."""
    try:
        resp = await client.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {key}"},
            timeout=VALIDATION_TIMEOUT,
        )
        if resp.status_code == 200:
            return KeyStatus.VALID, None
        elif resp.status_code == 401:
            return KeyStatus.INVALID, "Authentication failed - key is invalid or revoked"
        elif resp.status_code == 429:
            return KeyStatus.RATE_LIMITED, "Rate limited - key may still be valid"
        else:
            return KeyStatus.INVALID, f"HTTP {resp.status_code}"
    except httpx.TimeoutException:
        return KeyStatus.UNKNOWN, "Request timed out"
    except Exception as e:
        return KeyStatus.UNKNOWN, str(e)


async def _validate_google_cloud(key: str, client: httpx.AsyncClient) -> Tuple[str, Optional[str]]:
    """Validate a Google Cloud API key."""
    try:
        resp = await client.get(
            f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={key}",
            timeout=VALIDATION_TIMEOUT,
        )
        if resp.status_code == 200:
            return KeyStatus.VALID, None
        elif resp.status_code == 400:
            # Try as API key instead of access token
            resp2 = await client.get(
                f"https://maps.googleapis.com/maps/api/geocode/json?key={key}&address=test",
                timeout=VALIDATION_TIMEOUT,
            )
            if resp2.status_code == 200:
                data = resp2.json()
                if data.get("status") != "REQUEST_DENIED":
                    return KeyStatus.VALID, None
            return KeyStatus.INVALID, "Invalid API key"
        else:
            return KeyStatus.INVALID, f"HTTP {resp.status_code}"
    except httpx.TimeoutException:
        return KeyStatus.UNKNOWN, "Request timed out"
    except Exception as e:
        return KeyStatus.UNKNOWN, str(e)


async def _validate_stripe(key: str, client: httpx.AsyncClient) -> Tuple[str, Optional[str]]:
    """Validate a Stripe secret key."""
    try:
        resp = await client.get(
            "https://api.stripe.com/v1/balance",
            headers={"Authorization": f"Bearer {key}"},
            timeout=VALIDATION_TIMEOUT,
        )
        if resp.status_code == 200:
            return KeyStatus.VALID, None
        elif resp.status_code == 401:
            return KeyStatus.INVALID, "Invalid API key"
        elif resp.status_code == 429:
            return KeyStatus.RATE_LIMITED, "Rate limited"
        else:
            return KeyStatus.INVALID, f"HTTP {resp.status_code}"
    except httpx.TimeoutException:
        return KeyStatus.UNKNOWN, "Request timed out"
    except Exception as e:
        return KeyStatus.UNKNOWN, str(e)


async def _validate_github(key: str, client: httpx.AsyncClient) -> Tuple[str, Optional[str]]:
    """Validate a GitHub token."""
    try:
        resp = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {key}",
                "Accept": "application/vnd.github+json",
            },
            timeout=VALIDATION_TIMEOUT,
        )
        if resp.status_code == 200:
            return KeyStatus.VALID, None
        elif resp.status_code == 401:
            return KeyStatus.INVALID, "Bad credentials"
        elif resp.status_code == 403:
            return KeyStatus.EXPIRED, "Token expired or insufficient permissions"
        else:
            return KeyStatus.INVALID, f"HTTP {resp.status_code}"
    except httpx.TimeoutException:
        return KeyStatus.UNKNOWN, "Request timed out"
    except Exception as e:
        return KeyStatus.UNKNOWN, str(e)


async def _validate_sendgrid(key: str, client: httpx.AsyncClient) -> Tuple[str, Optional[str]]:
    """Validate a SendGrid API key."""
    try:
        resp = await client.get(
            "https://api.sendgrid.com/v3/scopes",
            headers={"Authorization": f"Bearer {key}"},
            timeout=VALIDATION_TIMEOUT,
        )
        if resp.status_code == 200:
            return KeyStatus.VALID, None
        elif resp.status_code in (401, 403):
            return KeyStatus.INVALID, "Invalid API key"
        else:
            return KeyStatus.INVALID, f"HTTP {resp.status_code}"
    except httpx.TimeoutException:
        return KeyStatus.UNKNOWN, "Request timed out"
    except Exception as e:
        return KeyStatus.UNKNOWN, str(e)


async def _validate_slack(key: str, client: httpx.AsyncClient) -> Tuple[str, Optional[str]]:
    """Validate a Slack token."""
    try:
        resp = await client.post(
            "https://slack.com/api/auth.test",
            headers={"Authorization": f"Bearer {key}"},
            timeout=VALIDATION_TIMEOUT,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("ok"):
                return KeyStatus.VALID, None
            return KeyStatus.INVALID, data.get("error", "Invalid token")
        return KeyStatus.INVALID, f"HTTP {resp.status_code}"
    except httpx.TimeoutException:
        return KeyStatus.UNKNOWN, "Request timed out"
    except Exception as e:
        return KeyStatus.UNKNOWN, str(e)


async def _validate_huggingface(key: str, client: httpx.AsyncClient) -> Tuple[str, Optional[str]]:
    """Validate a HuggingFace token."""
    try:
        resp = await client.get(
            "https://huggingface.co/api/whoami-v2",
            headers={"Authorization": f"Bearer {key}"},
            timeout=VALIDATION_TIMEOUT,
        )
        if resp.status_code == 200:
            return KeyStatus.VALID, None
        elif resp.status_code == 401:
            return KeyStatus.INVALID, "Invalid token"
        else:
            return KeyStatus.INVALID, f"HTTP {resp.status_code}"
    except httpx.TimeoutException:
        return KeyStatus.UNKNOWN, "Request timed out"
    except Exception as e:
        return KeyStatus.UNKNOWN, str(e)


# Validation dispatcher
VALIDATORS = {
    "openai": _validate_openai,
    "google_cloud": _validate_google_cloud,
    "stripe": _validate_stripe,
    "github": _validate_github,
    "sendgrid": _validate_sendgrid,
    "slack": _validate_slack,
    "huggingface": _validate_huggingface,
}


async def validate_detected_keys(keys: List[DetectedKey]) -> List[DetectedKey]:
    """Validate all detected keys by calling their provider APIs."""
    if not keys:
        return keys

    async with httpx.AsyncClient() as client:
        tasks = []

        for key_obj in keys:
            validator = VALIDATORS.get(key_obj.provider)
            if validator:
                tasks.append((key_obj, validator(key_obj.raw_key, client)))
            else:
                # No validator available — mark as unknown
                key_obj.status = KeyStatus.UNKNOWN
                key_obj.error_message = "No validator available for this provider"

        # Run validations concurrently with total timeout
        if tasks:
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(
                        *[t[1] for t in tasks],
                        return_exceptions=True,
                    ),
                    timeout=TOTAL_VALIDATION_TIMEOUT,
                )

                for (key_obj, _), result in zip(tasks, results):
                    if isinstance(result, Exception):
                        key_obj.status = KeyStatus.UNKNOWN
                        key_obj.error_message = str(result)
                    else:
                        status, error_msg = result
                        key_obj.status = status
                        key_obj.error_message = error_msg

            except asyncio.TimeoutError:
                # Mark remaining un-validated keys as unknown
                for key_obj, _ in tasks:
                    if key_obj.status == KeyStatus.UNKNOWN and not key_obj.error_message:
                        key_obj.error_message = "Total validation timeout exceeded"

    return keys


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def scan_from_path(source_path: str) -> List[DetectedKey]:
    """
    Scan a file path (zip or directory) for API keys.
    Returns list of DetectedKey (without validation — call validate separately).
    """
    if not source_path or not os.path.exists(source_path):
        return []

    if os.path.isdir(source_path):
        return scan_directory_for_keys(source_path)

    if zipfile.is_zipfile(source_path):
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(source_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
            return scan_directory_for_keys(temp_dir)

    # Single file
    if _should_scan_file(source_path):
        try:
            with open(source_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            return detect_keys_in_content(content, os.path.basename(source_path))
        except Exception:
            return []

    return []


def calculate_key_reliability(key_obj: DetectedKey) -> Tuple[float, str, List[str]]:
    """
    Evaluate the key's failure risk/chance of failure based on its validation status,
    location (source code vs env config), and provider.
    """
    reasons = []
    
    # 1. Base chance of failure from the validation status
    if key_obj.status == "invalid":
        chance = 1.0
        reasons.append("API key validation failed: key is invalid or revoked by the provider.")
    elif key_obj.status == "expired":
        chance = 1.0
        reasons.append("API key validation failed: key is expired.")
    elif key_obj.status == "rate_limited":
        chance = 0.85
        reasons.append("API key is currently rate limited. High risk of intermittent failures.")
    elif key_obj.status == "unknown":
        if key_obj.error_message and "timeout" in key_obj.error_message.lower():
            chance = 0.65
            reasons.append("Validation request timed out. Key might be blocked, expired, or rate-limited.")
        else:
            # Pattern matched but no validator available (e.g. AWS pattern-only)
            chance = 0.40
            reasons.append("Key detected by pattern but could not be validated online. Status is unknown.")
    else:  # status == "valid"
        chance = 0.10
        reasons.append("API key is active and successfully validated with the provider.")

    # 2. Risk from storage location (Hardcoded Secret Risk)
    _, ext = os.path.splitext(key_obj.file_path)
    is_source_code = ext.lower() in {".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".java", ".cs", ".php", ".rb"}
    if is_source_code:
        chance = min(chance + 0.30, 0.95) if chance < 1.0 else 1.0
        reasons.append(f"Hardcoded in source code file ({key_obj.file_path}). High risk of compromise, leakage, and revocation.")

    # 3. Provider-specific modifier
    if key_obj.provider == "generic":
        chance = min(chance + 0.15, 0.95) if chance < 1.0 else 1.0
        reasons.append("Generic variable match. High risk of false positive or config placeholder.")

    # Determine risk level
    if chance >= 0.90:
        risk_level = "critical"
    elif chance >= 0.60:
        risk_level = "high"
    elif chance >= 0.30:
        risk_level = "medium"
    else:
        risk_level = "low"

    return round(chance, 2), risk_level, reasons


async def scan_and_validate(source_path: str) -> ScanResult:
    """
    Full pipeline: detect keys from source path, validate each one,
    and calculate failure probability / risk assessment.
    Returns a ScanResult with counts and details.
    """
    try:
        detected = scan_from_path(source_path)
        validated = await validate_detected_keys(detected)

        # Calculate failure risk and risk level for all keys
        for key in validated:
            chance, risk_level, reasons = calculate_key_reliability(key)
            key.failure_chance = chance
            key.risk_level = risk_level
            key.reasons = reasons

        result = ScanResult(
            total_keys_found=len(validated),
            valid_keys=sum(1 for k in validated if k.status == KeyStatus.VALID),
            invalid_keys=sum(1 for k in validated if k.status in (KeyStatus.INVALID, KeyStatus.EXPIRED)),
            unknown_keys=sum(1 for k in validated if k.status in (KeyStatus.UNKNOWN, KeyStatus.RATE_LIMITED)),
            detected_keys=validated,
            scan_status="completed",
        )
        return result

    except Exception as e:
        return ScanResult(
            scan_status="failed",
        )
