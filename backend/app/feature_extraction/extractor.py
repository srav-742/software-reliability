import os
import zipfile
import tempfile
from typing import Dict, Any

from app.feature_extraction.parser import analyze_python_file, analyze_generic_code_file
from app.feature_extraction.dependency import extract_dependency_count_from_dir
from app.feature_extraction.complexity import calculate_duplicate_code_score

VALID_EXTENSIONS = {
    ".py": "python",
    ".js": "generic",
    ".ts": "generic",
    ".jsx": "generic",
    ".tsx": "generic",
    ".java": "generic",
    ".go": "generic",
    ".cpp": "generic",
    ".c": "generic",
    ".cs": "generic",
}


class FeatureExtractor:
    """
    High-level Orchestrator to analyze source code repositories and extract all metrics required for ApiMetric DB model.
    """

    @staticmethod
    def extract_metrics_from_directory(dir_path: str) -> Dict[str, Any]:
        aggregated = {
            "lines_of_code": 0,
            "cyclomatic_complexity": 0,
            "number_of_functions": 0,
            "number_of_parameters": 0,
            "nested_depth": 0,
            "if_statement_count": 0,
            "loop_count": 0,
            "imports_count": 0,
            "exception_handling_count": 0,
            "database_queries": 0,
            "external_api_calls": 0,
        }

        file_contents = []

        for root, _, files in os.walk(dir_path):
            # Ignore vendor, build, node_modules, .git directories
            if any(ignored in root for ignored in ["node_modules", ".venv", "venv", ".git", "__pycache__", "build", "dist"]):
                continue

            for file in files:
                _, ext = os.path.splitext(file)
                ext = ext.lower()
                if ext in VALID_EXTENSIONS:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()

                        file_contents.append(content)

                        if VALID_EXTENSIONS[ext] == "python":
                            metrics = analyze_python_file(content)
                        else:
                            metrics = analyze_generic_code_file(content)

                        # Aggregate sums
                        for key in aggregated.keys():
                            if key == "nested_depth":
                                aggregated[key] = max(aggregated[key], metrics.get(key, 0))
                            else:
                                aggregated[key] += metrics.get(key, 0)

                    except Exception:
                        pass

        # Dependency & Duplication Analysis
        dep_count = extract_dependency_count_from_dir(dir_path)
        dup_score = calculate_duplicate_code_score(file_contents)

        # Default/Simulated runtime and quality markers
        cpu_usage = 12.5  # %
        memory_usage = 256.0  # MB
        avg_response_time = 145.0  # ms
        test_coverage = 78.5  # %
        historical_bug_count = 0

        # Calculate target label `api_failure` (0 or 1 binary threshold rule)
        # Failure triggered if extreme complexity, very low test coverage, or high bug density
        api_failure = 0
        if (
            aggregated["cyclomatic_complexity"] > 50
            or aggregated["nested_depth"] > 8
            or dup_score > 0.45
            or (aggregated["lines_of_code"] > 1500 and test_coverage < 30)
        ):
            api_failure = 1

        return {
            "lines_of_code": max(aggregated["lines_of_code"], 10),
            "cyclomatic_complexity": max(aggregated["cyclomatic_complexity"], 1),
            "number_of_functions": aggregated["number_of_functions"],
            "number_of_parameters": aggregated["number_of_parameters"],
            "nested_depth": max(aggregated["nested_depth"], 1),
            "if_statement_count": aggregated["if_statement_count"],
            "loop_count": aggregated["loop_count"],
            "imports_count": aggregated["imports_count"],
            "dependency_count": dep_count,
            "duplicate_code_score": dup_score,
            "exception_handling_count": aggregated["exception_handling_count"],
            "database_queries": aggregated["database_queries"],
            "external_api_calls": aggregated["external_api_calls"],
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "average_response_time": avg_response_time,
            "test_coverage": test_coverage,
            "historical_bug_count": historical_bug_count,
            "api_failure": api_failure,
        }

    @classmethod
    def extract_from_path(cls, source_path: str) -> Dict[str, Any]:
        """
        Processes a file path (zip archive or directory) and extracts complete metrics.
        """
        if not source_path or not os.path.exists(source_path):
            # Return realistic default metrics if no source code archive exists
            return cls.get_default_metrics()

        if os.path.isdir(source_path):
            return cls.extract_metrics_from_directory(source_path)

        if zipfile.is_zipfile(source_path):
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(source_path, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)
                return cls.extract_metrics_from_directory(temp_dir)

        return cls.get_default_metrics()

    @staticmethod
    def get_default_metrics() -> Dict[str, Any]:
        return {
            "lines_of_code": 150,
            "cyclomatic_complexity": 8,
            "number_of_functions": 12,
            "number_of_parameters": 24,
            "nested_depth": 3,
            "if_statement_count": 5,
            "loop_count": 2,
            "imports_count": 10,
            "dependency_count": 5,
            "duplicate_code_score": 0.05,
            "exception_handling_count": 3,
            "database_queries": 4,
            "external_api_calls": 2,
            "cpu_usage": 15.0,
            "memory_usage": 128.0,
            "average_response_time": 120.0,
            "test_coverage": 85.0,
            "historical_bug_count": 0,
            "api_failure": 0,
        }
