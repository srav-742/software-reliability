import ast
import re
from typing import Dict, Any, List


class PythonASTVisitor(ast.NodeVisitor):
    """
    AST Visitor to collect code complexity and static analysis metrics from Python AST.
    """

    def __init__(self):
        self.cyclomatic_complexity = 1  # Base complexity is 1
        self.number_of_functions = 0
        self.number_of_parameters = 0
        self.if_statement_count = 0
        self.loop_count = 0
        self.imports_count = 0
        self.exception_handling_count = 0
        self.max_depth = 0
        self.current_depth = 0

    def generic_visit(self, node):
        self.current_depth += 1
        if self.current_depth > self.max_depth:
            self.max_depth = self.current_depth

        super().generic_visit(node)
        self.current_depth -= 1

    def visit_FunctionDef(self, node):
        self.number_of_functions += 1
        # Count parameters (posonlyargs, args, kwonlyargs, vararg, kwarg)
        args_count = len(node.args.args) + len(node.args.posonlyargs) + len(node.args.kwonlyargs)
        if node.args.vararg:
            args_count += 1
        if node.args.kwarg:
            args_count += 1
        self.number_of_parameters += args_count

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_If(self, node):
        self.cyclomatic_complexity += 1
        self.if_statement_count += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.cyclomatic_complexity += 1
        self.loop_count += 1
        self.generic_visit(node)

    def visit_AsyncFor(self, node):
        self.visit_For(node)

    def visit_While(self, node):
        self.cyclomatic_complexity += 1
        self.loop_count += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.cyclomatic_complexity += 1
        self.exception_handling_count += 1
        self.generic_visit(node)

    def visit_With(self, node):
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        # Each additional condition in boolean operation (and, or) adds a branch
        self.cyclomatic_complexity += len(node.values) - 1
        self.generic_visit(node)

    def visit_Import(self, node):
        self.imports_count += len(node.names)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self.imports_count += len(node.names)
        self.generic_visit(node)


def analyze_python_file(content: str) -> Dict[str, Any]:
    """
    Parses Python source code content and returns extracted static analysis metrics.
    """
    lines = content.splitlines()
    non_empty_lines = [l.strip() for l in lines if l.strip() and not l.strip().startswith("#")]
    loc = len(non_empty_lines)

    visitor = PythonASTVisitor()
    try:
        tree = ast.parse(content)
        visitor.visit(tree)
    except SyntaxError:
        # Fallback regex parsing if syntax is incomplete/broken
        pass

    # Regex checks for Database Queries and External API Calls
    db_query_pattern = re.compile(
        r"(\.query\(|\.filter\(|\.execute\(|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bdb\.commit\b)",
        re.IGNORECASE,
    )
    external_api_pattern = re.compile(
        r"(\brequests\.(get|post|put|delete|patch)|\bhttpx\.(get|post|put|delete)|\baxios\.(get|post|put)|\bfetch\()",
        re.IGNORECASE,
    )

    db_queries = len(db_query_pattern.findall(content))
    external_api_calls = len(external_api_pattern.findall(content))

    return {
        "lines_of_code": loc,
        "cyclomatic_complexity": visitor.cyclomatic_complexity,
        "number_of_functions": visitor.number_of_functions,
        "number_of_parameters": visitor.number_of_parameters,
        "nested_depth": visitor.max_depth,
        "if_statement_count": visitor.if_statement_count,
        "loop_count": visitor.loop_count,
        "imports_count": visitor.imports_count,
        "exception_handling_count": visitor.exception_handling_count,
        "database_queries": db_queries,
        "external_api_calls": external_api_calls,
    }


def analyze_generic_code_file(content: str) -> Dict[str, Any]:
    """
    Regex fallback metric extractor for non-Python files (JavaScript, TypeScript, Go, Java, C#, etc.).
    """
    lines = content.splitlines()
    loc = len([l for l in lines if l.strip() and not l.strip().startswith(("//", "/*", "*", "#"))])

    func_pattern = re.compile(r"\b(function\s+\w+|const\s+\w+\s*=\s*\([^)]*\)\s*=>|def\s+\w+|class\s+\w+)", re.IGNORECASE)
    if_pattern = re.compile(r"\bif\s*\(", re.IGNORECASE)
    loop_pattern = re.compile(r"\b(for|while)\s*\(", re.IGNORECASE)
    import_pattern = re.compile(r"\b(import|require\(|include)\b", re.IGNORECASE)
    try_pattern = re.compile(r"\b(try|catch|except)\b", re.IGNORECASE)

    db_query_pattern = re.compile(r"(\.query\(|\.filter\(|\.execute\(|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b)", re.IGNORECASE)
    api_pattern = re.compile(r"(\baxios\.(get|post)|\bfetch\(|\brequests\.(get|post)|\bhttpx\.)", re.IGNORECASE)

    functions = len(func_pattern.findall(content))
    ifs = len(if_pattern.findall(content))
    loops = len(loop_pattern.findall(content))
    imports = len(import_pattern.findall(content))
    tries = len(try_pattern.findall(content))

    complexity = 1 + ifs + loops + tries

    return {
        "lines_of_code": loc,
        "cyclomatic_complexity": complexity,
        "number_of_functions": functions,
        "number_of_parameters": functions * 2,  # Approximation
        "nested_depth": 3 if ifs or loops else 1,
        "if_statement_count": ifs,
        "loop_count": loops,
        "imports_count": imports,
        "exception_handling_count": tries,
        "database_queries": len(db_query_pattern.findall(content)),
        "external_api_calls": len(api_pattern.findall(content)),
    }
