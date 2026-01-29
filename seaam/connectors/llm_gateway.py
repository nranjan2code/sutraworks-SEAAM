"""
SEAAM LLM Gateway

Abstraction layer for LLM providers (Ollama, Gemini).

Features:
- Provider abstraction
- Retry logic with validation
- Code cleaning
- Rate limiting ready
"""

import os
import re
import time
import requests
import json
from typing import Any, Optional, Union, List

from seaam.core.logging import get_logger
from seaam.core.config import config
from seaam.core.exceptions import (
    GatewayError,
    ProviderUnavailableError,
    InvalidResponseError,
)
from seaam.cortex.prompt_loader import prompt_loader

logger = get_logger("gateway")


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
    
    def generate_code(self, module_name: str, description: str) -> Optional[str]:
        """
        Generate Python code for an organ.
        
        Uses structured prompt template and validates output.
        """
        # Build prompt from template
        try:
            prompt = prompt_loader.render(
                "agent_factory",
                module_name=module_name,
                description=description,
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
        Generate code with validation and retry logic.
        
        Validates that the code contains a start() function.
        """
        current_prompt = prompt
        
        for attempt in range(max_retries):
            logger.info(f"Generating code for {module_name} [Attempt {attempt + 1}/{max_retries}]")
            
            response = self._generate(current_prompt, validate_code=True)
            
            if not response:
                logger.warning(f"No response on attempt {attempt + 1}")
                continue
            
            # Clean the code
            code = self._clean_code(response)
            
            # Validate start() function
            if not self._validate_start_function(code):
                logger.warning(f"Validation FAILED: Missing 'def start():'")
                
                # Add error feedback to prompt
                try:
                    feedback = prompt_loader.render(
                        "error_feedback",
                        error_message="The code you wrote is MISSING the global 'def start():' function.",
                        additional_instruction="You MUST include 'def start():' at the end of the file.",
                    )
                except FileNotFoundError:
                    feedback = "\n\nCRITICAL ERROR: Missing 'def start():' function. Add it at the end of the file."
                
                current_prompt = prompt + feedback
                continue
            
            logger.info(f"✓ Generated valid code for {module_name}")
            return code
        
        logger.error(f"Failed to generate valid code after {max_retries} attempts")
        return None
    
    def _validate_start_function(self, code: str) -> bool:
        """Check if code contains a valid start() function."""
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
        1. Use `from seaam.kernel.bus import bus, Event` for events
        2. Include a global `def start():` function at the end
        3. Return ONLY Python code, no markdown
        
        CODE:
        """
