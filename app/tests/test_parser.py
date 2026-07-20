import sys
import os

# Add the backend root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.feature_extraction.parser import analyze_python_file, analyze_generic_code_file

def test_analyze_python_file():
    code_content = """import sys
import os

def dummy_function(a, b, c=1):
    if a > 0:
        for i in range(10):
            print(i)
    try:
        import requests
        requests.get("https://example.com")
        db.execute("SELECT * FROM users")
    except Exception as e:
        pass
"""

    metrics = analyze_python_file(code_content)
    
    assert metrics["number_of_functions"] == 1
    assert metrics["number_of_parameters"] == 3
    assert metrics["if_statement_count"] == 1
    assert metrics["loop_count"] == 1
    assert metrics["exception_handling_count"] == 1
    assert metrics["imports_count"] == 3  # sys, os, requests
    assert metrics["external_api_calls"] == 1  # requests.get
    assert metrics["database_queries"] == 2  # matches both .execute( and SELECT
    assert metrics["cyclomatic_complexity"] == 4  # base(1) + if(1) + for(1) + try(1)
    assert metrics["lines_of_code"] > 0

def test_analyze_generic_code_file():
    js_content = """
    // This is a comment
    import axios from 'axios';
    
    function calculate(x) {
        if (x > 10) {
            for (let i = 0; i < 5; i++) {
                console.log(i);
            }
        }
        try {
            axios.get('/api/users');
        } catch (err) {
            console.error(err);
        }
    }
    """
    
    metrics = analyze_generic_code_file(js_content)
    
    assert metrics["number_of_functions"] == 1
    assert metrics["if_statement_count"] == 1
    assert metrics["loop_count"] == 1
    assert metrics["exception_handling_count"] == 2  # matches both 'try' and 'catch'

    assert metrics["imports_count"] == 1
    assert metrics["external_api_calls"] == 1
    assert metrics["cyclomatic_complexity"] == 5  # 1 + if(1) + loop(1) + tries(2)
