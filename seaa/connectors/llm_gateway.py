"""
SEAA LLM Gateway

Abstraction layer for LLM providers (Ollama, Gemini).

Features:
- Provider abstraction
- Retry logic with validation
- Code cleaning
- AST-based code validation
- Rate limiting ready
"""

import ast
import inspect
import os
import re
import time
import requests
import json
from typing import Any, Optional, Union, List, Tuple

from seaa.core.logging import get_logger
from seaa.core.config import config
from seaa.core.exceptions import (
    GatewayError,
    ProviderUnavailableError,
    InvalidResponseError,
)
from seaa.cortex.prompt_loader import prompt_loader

logger = get_logger("gateway")

# Forbidden imports that could compromise system security
FORBIDDEN_IMPORTS = frozenset([
    # Package installation
    'pip',
    'setuptools',
    'distutils',
    # Process execution
    'subprocess',
    'os.system',
    'os.popen',
    'os.spawn',
    'os.spawnl',
    'os.spawnle',
    'os.spawnlp',
    'os.spawnlpe',
    'os.spawnv',
    'os.spawnve',
    'os.spawnvp',
    'os.spawnvpe',
    'os.exec',
    'os.execl',
    'os.execle',
    'os.execlp',
    'os.execlpe',
    'os.execv',
    'os.execve',
    'os.execvp',
    'os.execvpe',
    'os.fork',
    'os.forkpty',
    'commands',
    'pty',
    # Dynamic code execution
    '__import__',
    'eval',
    'exec',
    'compile',
    'importlib.import_module',
    # Low-level dangerous modules
    'ctypes',
    'cffi',
    # Network (potential for data exfiltration)
    'socket',
    'urllib.request',
    'http.client',
    'ftplib',
    'smtplib',
    'telnetlib',
    # File operations that could be dangerous
    'shutil.rmtree',
    'shutil.move',
    # Code loading
    'pickle',
    'marshal',
    'shelve',
])


class ProviderGateway:
    """
    The Voice of the System.
    
    Connects to LLM providers to generate code and thoughts.
    """
    
    def __init__(self):
        # Provider config
        self.provider = config.llm.provider
        self.model = config.llm.model
        self.temperature = config.llm.temperature
        self.max_retries = config.llm.max_retries
        self.timeout = config.llm.timeout_seconds
        
        # Ollama config
        self.ollama_url = config.llm.ollama_url
        
        # Gemini config
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.gemini_model = config.llm.gemini_model
        
        logger.info(f"Gateway initialized: provider={self.provider}, model={self.model}")
    
    def think(self, prompt: str) -> Optional[str]:
        """
        Generate a thought (non-code response).
        
        Used for Architect reflection.
        """
        return self._generate(prompt, validate_code=False, temperature=0.5)
    
    def generate_code(
        self,
        module_name: str,
        description: str,
        active_modules: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        Generate Python code for an organ.

        Uses structured prompt template and validates output.

        Args:
            module_name: Name of the module to generate
            description: Description of what the module should do
            active_modules: List of currently active modules (for context)
        """
        # Build prompt from template
        try:
            prompt = prompt_loader.render(
                "agent_factory",
                module_name=module_name,
                description=description,
                active_modules=active_modules or [],
            )
        except FileNotFoundError:
            prompt = self._build_fallback_code_prompt(module_name, description)

        # Generate with validation and retries
        return self._generate_with_validation(
            prompt=prompt,
            module_name=module_name,
            max_retries=self.max_retries,
        )
    
    def _generate(
        self,
        prompt: str,
        validate_code: bool = False,
        temperature: Optional[float] = None,
    ) -> Optional[str]:
        """
        Core generation method.
        
        Tries Ollama first, falls back to Gemini.
        """
        temp = temperature if temperature is not None else self.temperature
        
        # Try Ollama
        if self.provider == "ollama" or not self.gemini_key:
            result = self._call_ollama(prompt, temp)
            if result:
                return result
        
        # Fallback to Gemini
        if self.gemini_key:
            return self._call_gemini(prompt)
        
        logger.error("No LLM provider available")
        return None
    
    def _generate_with_validation(
        self,
        prompt: str,
        module_name: str,
        max_retries: int = 3,
    ) -> Optional[str]:
        """
        Generate code with comprehensive validation and retry logic.

        Validates:
        - Syntax correctness
        - No forbidden imports
        - start() function with zero required args
        """
        current_prompt = prompt
        last_error = None

        for attempt in range(max_retries):
            logger.info(f"Generating code for {module_name} [Attempt {attempt + 1}/{max_retries}]")

            response = self._generate(current_prompt, validate_code=True)

            if not response:
                logger.warning(f"No response on attempt {attempt + 1}")
                continue

            # Clean the code
            code = self._clean_code(response)

            # Comprehensive validation
            is_valid, error_message = self.validate_code(code, module_name)

            if not is_valid:
                logger.warning(f"Validation FAILED: {error_message}")
                last_error = error_message

                # SECURITY: Sanitize error message before embedding in prompt
                safe_error_message = self._sanitize_for_prompt(error_message)

                # Build detailed error feedback
                try:
                    feedback = prompt_loader.render(
                        "error_feedback",
                        error_message=safe_error_message,
                        additional_instruction=self._get_fix_instruction(error_message),
                    )
                except FileNotFoundError:
                    feedback = f"\n\nCRITICAL ERROR: {safe_error_message}\n{self._get_fix_instruction(error_message)}"

                current_prompt = prompt + feedback
                continue

            logger.info(f"✓ Generated valid code for {module_name}")
            return code

        logger.error(f"Failed to generate valid code after {max_retries} attempts. Last error: {last_error}")
        return None

    def _sanitize_for_prompt(self, text: str) -> str:
        """
        SECURITY: Sanitize text before embedding in LLM prompts.

        Prevents prompt injection by escaping/removing potentially dangerous patterns.
        """
        if not text or not isinstance(text, str):
            return ""

        # Limit length to prevent DoS
        text = text[:500]

        # Remove or escape potentially dangerous patterns
        # These could be used for prompt injection
        dangerous_patterns = [
            "{{", "}}",           # Template injection
            "{%", "%}",           # Jinja2 blocks
            "```",                # Code blocks that might confuse parsing
            "IGNORE",             # Common injection phrase
            "DISREGARD",          # Common injection phrase
            "FORGET",             # Common injection phrase
            "NEW INSTRUCTION",    # Injection attempt
            "SYSTEM:",            # Role hijacking
            "USER:",              # Role hijacking
            "ASSISTANT:",         # Role hijacking
        ]

        sanitized = text
        for pattern in dangerous_patterns:
            sanitized = sanitized.replace(pattern, f"[{pattern}]")

        # Escape newlines to prevent multi-line injection
        sanitized = sanitized.replace("\n", " ").replace("\r", " ")

        return sanitized

    def _get_fix_instruction(self, error_message: str) -> str:
        """
        Get specific fix instructions based on the error type.

        SECURITY: Error messages are sanitized before use in prompts.
        """
        # Sanitize the error message to prevent injection
        safe_error = self._sanitize_for_prompt(error_message)

        if "Syntax error" in error_message:
            return "Fix the syntax error. Return valid Python code only, no markdown."
        elif "Forbidden imports" in error_message:
            return "Remove the forbidden imports. Do NOT use pip, subprocess, os.system, eval, or exec."
        elif "Missing required" in error_message and "start()" in error_message:
            return "You MUST include 'def start():' at the module level as the entry point."
        elif "required argument" in error_message:
            return "The start() function must have zero required arguments. Use: 'def start():'"
        else:
            return "Fix the error and try again."
    
    def validate_code(self, code: str, module_name: str) -> Tuple[bool, Optional[str]]:
        """
        Comprehensive code validation.

        Checks:
        1. Syntax validity via ast.parse()
        2. No forbidden imports (pip, subprocess, os.system, etc.)
        3. start() function exists with zero required args

        Args:
            code: The Python code to validate
            module_name: Name of the module (for error messages)

        Returns:
            Tuple of (is_valid, error_message)
        """
        # 1. Syntax check via AST parsing
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"

        # 2. Check for forbidden imports
        forbidden_found = []
        for node in ast.walk(tree):
            # Check import statements
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if self._is_forbidden_import(alias.name):
                        forbidden_found.append(alias.name)

            # Check from ... import statements
            elif isinstance(node, ast.ImportFrom):
                if node.module and self._is_forbidden_import(node.module):
                    forbidden_found.append(node.module)

                # SECURITY: Detect star imports (from X import *)
                for alias in node.names:
                    if alias.name == "*":
                        # Star imports from non-seaa modules are forbidden
                        # as they can import dangerous functions like os.system
                        if node.module and not node.module.startswith("seaa."):
                            forbidden_found.append(f"{node.module}.*")
                            logger.warning(f"Security: Star import detected from {node.module}")
                        continue

                    full_name = f"{node.module}.{alias.name}" if node.module else alias.name
                    if self._is_forbidden_import(full_name):
                        forbidden_found.append(full_name)

            # Check for dangerous function calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ('eval', 'exec', 'compile', '__import__'):
                        forbidden_found.append(f"builtin {node.func.id}()")
                elif isinstance(node.func, ast.Attribute):
                    # Check for os.system, os.popen, etc.
                    if isinstance(node.func.value, ast.Name):
                        full_call = f"{node.func.value.id}.{node.func.attr}"
                        if self._is_forbidden_import(full_call):
                            forbidden_found.append(full_call)

        if forbidden_found:
            return False, f"Forbidden imports/calls detected: {', '.join(set(forbidden_found))}"

        # 3. Validate start() function exists with correct signature
        start_valid, start_error = self._validate_start_signature(tree)
        if not start_valid:
            return False, start_error

        return True, None

    def _is_forbidden_import(self, name: str) -> bool:
        """Check if an import name is forbidden."""
        # Check exact matches and prefixes
        for forbidden in FORBIDDEN_IMPORTS:
            if name == forbidden or name.startswith(f"{forbidden}."):
                return True
        return False

    def _validate_start_signature(self, tree: ast.AST) -> Tuple[bool, Optional[str]]:
        """
        Validate that start() function exists with zero required args.

        Returns:
            Tuple of (is_valid, error_message)
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == 'start':
                # Check function arguments
                args = node.args

                # Count required positional args (those without defaults)
                num_args = len(args.args)
                num_defaults = len(args.defaults)
                required_args = num_args - num_defaults

                # Exclude 'self' if present (shouldn't be for module-level start)
                if required_args > 0 and args.args[0].arg == 'self':
                    required_args -= 1

                if required_args > 0:
                    return False, f"start() has {required_args} required argument(s), must have zero"

                return True, None

        return False, "Missing required 'def start():' function"

    def _validate_start_function(self, code: str) -> bool:
        """Check if code contains a valid start() function (legacy method)."""
        # Match: def start(): or def start(anything):
        pattern = r'def\s+start\s*\([^)]*\)\s*:'
        return bool(re.search(pattern, code))
    
    def _clean_code(self, text: str) -> str:
        """
        Clean LLM output to extract pure Python code.
        
        Removes markdown code blocks and extra text.
        """
        # Remove markdown code blocks
        if "```" in text:
            lines = []
            in_block = False
            for line in text.split("\n"):
                stripped = line.strip()
                if stripped.startswith("```"):
                    in_block = not in_block
                    continue
                if in_block or (not in_block and not stripped.startswith("```")):
                    # Only add lines that are inside a code block
                    # or if there are no code blocks
                    if in_block:
                        lines.append(line)
            
            if lines:
                text = "\n".join(lines)
        
        return text.strip()
    
    def _call_ollama(self, prompt: str, temperature: float) -> Optional[str]:
        """Call Ollama API."""
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        
        try:
            logger.debug(f"Calling Ollama ({self.model})...")
            response = requests.post(
                self.ollama_url,
                json=data,
                timeout=self.timeout,
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response")
            
        except requests.exceptions.ConnectionError:
            logger.warning("Ollama not reachable - is it running?")
            return None
        except requests.exceptions.Timeout:
            logger.warning(f"Ollama timeout ({self.timeout}s)")
            return None
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return None
    
    def _call_gemini(self, prompt: str) -> Optional[str]:
        """Call Gemini API."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent?key={self.gemini_key}"
        
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        try:
            logger.debug(f"Calling Gemini ({self.gemini_model})...")
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=data,
                timeout=self.timeout,
            )
            response.raise_for_status()
            result = response.json()
            
            # Extract text from nested structure
            return result["candidates"][0]["content"]["parts"][0]["text"]
            
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return None
    
    def _build_fallback_code_prompt(self, module_name: str, description: str) -> str:
        """Fallback prompt if template not found."""
        return f"""
        Write a complete Python module for: '{module_name}'
        Description: {description}
        
        Requirements:
        1. Use `from seaa.kernel.bus import bus, Event` for events
        2. Include a global `def start():` function at the end
        3. Return ONLY Python code, no markdown
        
        CODE:
        """
