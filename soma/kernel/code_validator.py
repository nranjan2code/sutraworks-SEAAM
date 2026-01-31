from seaa.kernel.bus import bus, Event
from seaa.core.logging import get_logger
from seaa.core.config import config
import ast
import re
from typing import Tuple, List, Dict, Optional

logger = get_logger("soma.kernel.code_validator")

class SecurityIssue:
    """Represents a security finding in code"""
    def __init__(self, level: str, rule: str, location: Optional[str] = None, suggestion: str = ""):
        self.level = level  # "error", "warning"
        self.rule = rule
        self.location = location
        self.suggestion = suggestion

    def to_dict(self) -> Dict:
        return {
            'level': self.level,
            'rule': self.rule,
            'location': self.location,
            'suggestion': self.suggestion
        }

class CodeValidator:
    """Security enforcement layer for generated code.

    Validates all LLM-generated code before materialization by:
    - Checking syntax validity
    - Scanning for forbidden imports/functions
    - Verifying start() function signature
    - Detecting dangerous patterns
    - Enforcing decoupling rules
    """

    def __init__(self):
        # Forbidden imports that could compromise security
        self.forbidden_modules = [
            'pip', 'subprocess', 'os.system', 'eval', 'exec', 'compile',
            '__import__', 'ctypes', 'socket', 'pickle', 'shelve', 'importlib.import_module',
            'imp', 'pkgutil', 'importlib._bootstrap', 'sys.modules',
            'requests', 'urllib', 'http.client', 'ftplib', 'telnetlib', 'smtplib',
            'multiprocessing.managers', 'concurrent.futures',
        ]

        self.forbidden_functions = [
            'eval', 'exec', 'compile', '__import__', 'open',
            'input', 'raw_input'
        ]

        self.forbidden_patterns = [
            r'os\.system\(',
            r'os\.popen\(',
            r'os\.spawn',
            r'os\.exec',
            r'subprocess\.',
            r'__import__\(',
            r'eval\(',
            r'exec\(',
            r'compile\(',
            r'pickle\.load',
            r'socket\.',
            r'requests\.',
            r'urllib\.',
            r'from \* import',
            r'import \*',
        ]

        logger.info("CodeValidator initialized - Robinson enforces safety")

    def validate_code(self, code: str, module_name: str) -> Tuple[bool, str, List[SecurityIssue]]:
        """Validate generated code for security and correctness.

        Returns:
            (is_valid, error_message, security_issues)
        """
        issues: List[SecurityIssue] = []

        # 1. Syntax check
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error: {e.msg} at line {e.lineno}", []

        # 2. Check for start() function with correct signature
        has_start = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == 'start':
                has_start = True
                # Check that it has no required arguments
                if len(node.args.args) > 0:
                    issues.append(SecurityIssue(
                        'error',
                        'start_function_signature',
                        f'start() at line {node.lineno}',
                        'start() must have zero required arguments'
                    ))
                break

        if not has_start:
            return False, "Missing required start() function with zero arguments", issues

        # 3. Pattern-based security checks
        for pattern in self.forbidden_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append(SecurityIssue(
                    'error',
                    'forbidden_pattern',
                    suggestion=f'Pattern {pattern} is not allowed for security reasons'
                ))

        # 4. Import-based security checks
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split('.')[0]
                    if module in self.forbidden_modules:
                        issues.append(SecurityIssue(
                            'error',
                            'forbidden_import',
                            f'import {alias.name} at line {node.lineno}',
                            f'{module} is not allowed for security reasons'
                        ))

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    base_module = node.module.split('.')[0]
                    if base_module in self.forbidden_modules:
                        issues.append(SecurityIssue(
                            'error',
                            'forbidden_import',
                            f'from {node.module} at line {node.lineno}',
                            f'{base_module} is not allowed for security reasons'
                        ))

                # Check for wildcard imports
                for alias in node.names:
                    if alias.name == '*':
                        issues.append(SecurityIssue(
                            'error',
                            'wildcard_import',
                            f'from ... import * at line {node.lineno}',
                            'Wildcard imports are not allowed'
                        ))

        # 5. Function call checks
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.forbidden_functions:
                        issues.append(SecurityIssue(
                            'error',
                            'forbidden_function',
                            f'{node.func.id}() at line {node.lineno}',
                            f'{node.func.id}() is not allowed for security reasons'
                        ))

        # 6. Decoupling check: organ shouldn't directly import other soma modules
        if module_name.startswith('soma.'):
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith('soma.') and alias.name != module_name:
                            issues.append(SecurityIssue(
                                'error',
                                'decoupling_violation',
                                f'import {alias.name} at line {node.lineno}',
                                'Use EventBus to communicate with other soma modules, not direct imports'
                            ))

                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module.startswith('soma.'):
                        issues.append(SecurityIssue(
                            'error',
                            'decoupling_violation',
                            f'from {node.module} at line {node.lineno}',
                            'Use EventBus to communicate with other soma modules, not direct imports'
                        ))

        # Return result
        if issues:
            # Filter for errors vs warnings
            errors = [i for i in issues if i.level == 'error']
            warnings = [i for i in issues if i.level == 'warning']

            if errors:
                error_summary = f"Code validation failed with {len(errors)} error(s)"
                return False, error_summary, issues
            else:
                # Only warnings - still valid but log them
                logger.warn(f"Code has {len(warnings)} warning(s) but is valid")
                return True, "", issues

        return True, "", issues

    def validate_and_report(self, code: str, module_name: str) -> bool:
        """Validate code and publish validation event"""
        is_valid, error_msg, issues = self.validate_code(code, module_name)

        # Publish validation event
        bus.publish(Event(
            event_type='code.validated',
            data={
                'module_name': module_name,
                'is_valid': is_valid,
                'error': error_msg,
                'issues': [i.to_dict() for i in issues],
                'timestamp': __import__('time').time()
            }
        ))

        if not is_valid:
            logger.error(
                f"Code validation failed for {module_name}",
                error=error_msg,
                issue_count=len([i for i in issues if i.level == 'error'])
            )
        else:
            logger.debug(
                f"Code validation passed for {module_name}",
                warning_count=len([i for i in issues if i.level == 'warning'])
            )

        return is_valid

# REQUIRED ENTRY POINT (zero required args)
def start():
    validator = CodeValidator()
