import os
import json
import re
# Primitive types (str, int) are built-in in Python


def extract_dependency_count_from_dir(directory_path: str) -> int:
    """
    Scans directory for dependency configuration files and counts third-party packages.
    """
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        return 0

    dependency_count = 0

    for root, _, files in os.walk(directory_path):
        # Prevent searching node_modules or venv
        if "node_modules" in root or ".venv" in root or "venv" in root:
            continue

        for file in files:
            file_path = os.path.join(root, file)

            if file.lower() == "requirements.txt":
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                        valid_reqs = [
                            line.strip()
                            for line in lines
                            if line.strip() and not line.strip().startswith(("#", "-"))
                        ]
                        dependency_count += len(valid_reqs)
                except Exception:
                    pass

            elif file.lower() == "package.json":
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        data = json.load(f)
                        deps = len(data.get("dependencies", {}))
                        dev_deps = len(data.get("devDependencies", {}))
                        dependency_count += (deps + dev_deps)
                except Exception:
                    pass

            elif file.lower() == "pyproject.toml":
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        # Find dependencies under [tool.poetry.dependencies] or dependencies = [...]
                        req_matches = re.findall(r'^[a-zA-Z0-9_\-]+(?:\s*[=<>]|=)', content, re.MULTILINE)
                        dependency_count += len(req_matches)
                except Exception:
                    pass

    return max(dependency_count, 0)
