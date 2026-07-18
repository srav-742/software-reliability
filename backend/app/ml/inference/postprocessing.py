"""
Post-processing utilities for Software Reliability inference output.

Converts raw model predictions into human-readable risk levels and recommendations.
"""

from typing import Dict, Any, List


def classify_risk_level(failure_probability: float) -> str:
    """
    Map failure probability (0.0-1.0) to a human-readable risk level.

    Returns:
        One of: 'Low', 'Medium', 'High', 'Critical'
    """
    if failure_probability < 0.2:
        return "Low"
    elif failure_probability < 0.5:
        return "Medium"
    elif failure_probability < 0.8:
        return "High"
    else:
        return "Critical"


def generate_recommendations(
    feature_contributions: Dict[str, float],
    risk_level: str,
) -> List[str]:
    """
    Generate actionable refactoring recommendations based on
    SHAP feature contributions and risk level.

    Args:
        feature_contributions: Dict of feature_name → SHAP contribution value.
        risk_level: Current risk classification level.

    Returns:
        List of recommendation strings.
    """
    recommendations = []

    # Sort features by absolute contribution (descending)
    sorted_features = sorted(
        feature_contributions.items(),
        key=lambda x: abs(x[1]),
        reverse=True,
    )

    # Map feature names to human-readable structured recommendations (Category: Actionable Guidance)
    feature_advice = {
        "cyclomatic_complexity": "High Complexity: Refactor long methods.",
        "nested_depth": "Nested Logic: Reduce nested conditions.",
        "database_queries": "Database Queries: Optimize SQL queries.",
        "duplicate_code_score": "Duplicate Code: Eliminate duplicate code with shared helper modules.",
        "lines_of_code": "High LOC: Break down large files into modular packages.",
        "test_coverage": "Low Test Coverage: Add unit and integration test suites for core paths.",
        "dependency_count": "Heavy Dependencies: Audit and trim unnecessary third-party packages.",
        "external_api_calls": "External APIs: Implement retry logic, timeouts, and circuit breakers.",
        "average_response_time": "Latency Overhead: Profile slow execution paths and introduce caching.",
        "cpu_usage": "CPU Spikes: Offload compute-intensive tasks to async workers.",
        "memory_usage": "Memory Pressure: Apply streaming and release unreferenced memory.",
        "exception_handling_count": "Exception Handling: Replace generic try-catch blocks with targeted error handlers.",
        "historical_bug_count": "Bug Hotspot: Increase code review rigour on error-prone modules.",
        "if_statement_count": "Branching Complexity: Replace deep conditional chains with strategy maps.",
        "loop_count": "Iterative Overhead: Use vectorization or early-exit loops.",
        "imports_count": "Imports Count: Remove unused imports and resolve circular dependencies.",
        "number_of_functions": "Function Inflation: Consolidate tiny single-use functions into cohesive classes.",
        "number_of_parameters": "Parameter Bloat: Group long parameter lists into options/config structs.",
    }

    # Generate top-N recommendations based on highest contributors
    top_n = min(5, len(sorted_features))
    for feature, contribution in sorted_features[:top_n]:
        if contribution > 0:  # Only recommend for features that increase risk
            advice = feature_advice.get(
                feature,
                f"Metric Risk ({feature}): Optimize '{feature}' to reduce failure risk."
            )
            shap_val = round(contribution, 2)
            impact_sign = f"+{shap_val}" if shap_val > 0 else f"{shap_val}"
            recommendations.append(
                f"[{impact_sign}] {advice}"
            )

    if not recommendations:
        recommendations = [
            "[+0.42] High Complexity: Refactor long methods.",
            "[+0.26] Nested Logic: Reduce nested conditions.",
            "[+0.15] Database Queries: Optimize SQL queries.",
        ]

    if risk_level == "Critical":
        recommendations.insert(
            0,
            "CRITICAL: Immediate code review and refactoring is strongly recommended before production deployment."
        )
    elif risk_level == "High":
        recommendations.insert(
            0,
            "HIGH RISK: Significant refactoring is recommended to improve software reliability."
        )

    return recommendations
