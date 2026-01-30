"""
SEAA Architect - The Mind

The intelligent agent responsible for system design.
Uses externalized prompt templates for flexibility.

Responsibilities:
- Reflect on DNA state (goals, failures, blueprint)
- Design new organs
- Propose goal evolution
"""

import json
import re
from typing import Callable, Optional

from seaa.core.logging import get_logger
from seaa.core.config import config
from seaa.dna.schema import DNA, Goal
from seaa.cortex.prompt_loader import prompt_loader

# Security: Strict module name pattern - only valid Python identifiers under soma.*
MODULE_NAME_PATTERN = re.compile(r'^soma(\.[a-z_][a-z0-9_]*)+$', re.IGNORECASE)

logger = get_logger("architect")


class Architect:
    """
    The Mind of SEAA.
    
    Analyzes the current system state and designs the next evolution step.
    """
    
    def __init__(
        self,
        dna: DNA,
        gateway,  # ProviderGateway - avoid circular import
        save_callback: Callable[[], None],
    ):
        """
        Args:
            dna: The DNA instance to reflect on
            gateway: LLM gateway for thinking
            save_callback: Function to call when DNA is modified
        """
        self.dna = dna
        self.gateway = gateway
        self.save_dna = save_callback
    
    def reflect(self) -> bool:
        """
        Reflect on the current state and propose evolution.
        
        Returns:
            True if a new blueprint was added/modified
        """
        # Check if we should reflect
        if not self._should_reflect():
            return False
        
        logger.info("Reflecting on existence...")
        
        # Build prompt using template
        try:
            prompt = self._build_reflect_prompt()
        except FileNotFoundError:
            # Fallback to inline prompt if template not found
            logger.warning("Prompt template not found, using inline fallback")
            prompt = self._build_fallback_prompt()
        
        # Ask the gateway
        response = self.gateway.think(prompt)
        
        if not response:
            logger.warning("No response from Overmind")
            return False
        
        # Parse and apply the response
        return self._process_response(response)
    
    def _should_reflect(self) -> bool:
        """
        Determine if reflection is needed.
        
        Prioritizes fixing failures over waiting for body to catch up.
        """
        failures = self.dna.failures
        blueprint = self.dna.blueprint
        active = self.dna.active_modules
        
        # Always reflect if there are failures
        if failures:
            logger.info(f"Critical failures detected ({len(failures)}). Intervening...")
            return True
        
        # If we have pending blueprints, wait for Genesis to build them
        pending = len(blueprint) - len(active)
        if pending > 0:
            logger.debug(f"Waiting for Body to catch up ({pending} pending)...")
            return False
        
        return True
    
    def _build_reflect_prompt(self) -> str:
        """Build the reflection prompt from template."""
        # Prepare data for template
        goals = [g.description for g in self.dna.goals if not g.satisfied]

        blueprint = {
            name: bp.description
            for name, bp in self.dna.blueprint.items()
        }

        failures = [
            f"{f.module_name}: {f.error_message} (attempts: {f.attempt_count})"
            for f in self.dna.failures
        ]

        # Include active modules so LLM knows what's running
        active_modules = self.dna.active_modules

        return prompt_loader.render(
            "architect_reflect",
            goals=goals,
            blueprint=blueprint,
            failures=failures,
            active_modules=active_modules,
        )
    
    def _build_fallback_prompt(self) -> str:
        """Fallback inline prompt if template loading fails."""
        goals = [g.description for g in self.dna.goals if not g.satisfied]
        blueprint = {name: bp.description for name, bp in self.dna.blueprint.items()}
        failures = [f"{f.module_name}: {f.error_message}" for f in self.dna.failures]
        
        return f"""
        You are the 'Architect' of a self-evolving AI system.
        
        GOALS: {json.dumps(goals, indent=2)}
        BLUEPRINT: {json.dumps(blueprint, indent=2)}
        FAILURES: {json.dumps(failures, indent=2)}
        
        Analyze the goals vs blueprint. Propose the next organ as JSON:
        {{"module_name": "soma.category.name", "description": "..."}}
        
        Or return {{"module_name": "COMPLETE"}} if satisfied.
        """
    
    def _validate_module_name(self, module_name: str) -> bool:
        """
        SECURITY: Validate module name from LLM response.

        Prevents path traversal and injection attacks via malicious module names.

        Returns:
            True if module name is valid, False otherwise
        """
        if not module_name or not isinstance(module_name, str):
            return False

        # Special case for completion signal
        if module_name == "COMPLETE":
            return True

        # Must start with soma.
        if not module_name.startswith("soma."):
            logger.warning(f"Security: Rejected module name not starting with 'soma.': {module_name}")
            return False

        # Check against strict pattern
        if not MODULE_NAME_PATTERN.match(module_name):
            logger.warning(f"Security: Rejected invalid module name format: {module_name}")
            return False

        # No path traversal attempts
        if ".." in module_name:
            logger.warning(f"Security: Path traversal detected in module name: {module_name}")
            return False

        # Check each part is a valid Python identifier
        parts = module_name.split(".")
        for part in parts:
            if not part.isidentifier():
                logger.warning(f"Security: Invalid identifier '{part}' in module name: {module_name}")
                return False

        return True

    def _process_response(self, response: str) -> bool:
        """
        Parse and apply the Architect's response.

        SECURITY: Validates module names from LLM to prevent injection attacks.

        Returns:
            True if DNA was modified
        """
        try:
            # Extract JSON from response
            json_data = self._extract_json(response)

            if not json_data:
                if "COMPLETE" in response.upper():
                    logger.info("Content with current form")
                else:
                    logger.warning(f"Unstructured thought: {response[:100]}...")
                return False

            # Parse the plan
            module_name = json_data.get("module_name")
            description = json_data.get("description")
            new_goal = json_data.get("new_goal")

            # SECURITY: Validate module name before using it
            if module_name and not self._validate_module_name(module_name):
                logger.error(f"Security: Rejected invalid module name from LLM: {module_name}")
                return False
            
            # Check for completion
            if module_name == "COMPLETE":
                logger.info("Purpose fulfilled for now")
                return False
            
            modified = False
            
            # Handle goal evolution
            if new_goal:
                existing_goals = [g.description for g in self.dna.goals]
                if new_goal not in existing_goals:
                    logger.info(f"Purpose Evolved: {new_goal}")
                    self.dna.goals.append(Goal(description=new_goal))
                    modified = True
            
            # Handle blueprint
            if module_name and description:
                # Check if this is a new organ or a fix for failing one
                is_failing = any(
                    module_name in f.module_name
                    for f in self.dna.failures
                )
                
                if module_name not in self.dna.blueprint:
                    logger.info(f"Decided to evolve: {module_name}")
                    self.dna.add_blueprint(module_name, description)
                    modified = True
                elif is_failing:
                    logger.info(f"Refining blueprint for failing organ: {module_name}")
                    self.dna.add_blueprint(module_name, description)
                    modified = True
                else:
                    logger.debug(f"{module_name} is already operational")
            
            if modified:
                self.save_dna()

            # Check if any goals are now satisfied
            newly_satisfied = self.dna.check_goal_satisfaction()
            if newly_satisfied > 0:
                logger.info(f"✓ {newly_satisfied} goal(s) auto-satisfied by active modules")
                self.save_dna()

            return modified

        except Exception as e:
            logger.error(f"Failed to process response: {e}")
            logger.debug(f"Raw response: {response[:200]}...")
            return False
    
    def _extract_json(self, text: str) -> Optional[dict]:
        """
        Extract JSON object from text response.

        Handles LLMs that include extra text around JSON.
        SECURITY: Uses proper depth tracking instead of first/last brace matching.
        """
        # Find first complete JSON object using proper depth tracking
        depth = 0
        start_idx = -1
        in_string = False
        escape_next = False

        for i, char in enumerate(text):
            if escape_next:
                escape_next = False
                continue

            if char == '\\' and in_string:
                escape_next = True
                continue

            if char == '"' and not escape_next:
                in_string = not in_string
                continue

            if in_string:
                continue

            if char == '{':
                if depth == 0:
                    start_idx = i
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0 and start_idx != -1:
                    json_str = text[start_idx:i + 1]
                    try:
                        result = json.loads(json_str)
                        if isinstance(result, dict):
                            return result
                    except json.JSONDecodeError:
                        # Try cleaning and parsing again
                        cleaned = self._clean_json_string(json_str)
                        try:
                            result = json.loads(cleaned)
                            if isinstance(result, dict):
                                return result
                        except json.JSONDecodeError:
                            pass
                    # Reset and try to find next JSON object
                    start_idx = -1

        return None
    
    def _clean_json_string(self, text: str) -> str:
        """
        Clean common JSON issues from LLM output.
        """
        # Remove markdown code fences if present - keep content INSIDE fences
        if "```" in text:
            lines = []
            in_fence = False
            for line in text.split("\n"):
                if line.strip().startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    lines.append(line)
            # Only use extracted lines if we found fenced content
            if lines:
                text = "\n".join(lines)

        # Remove trailing commas (common LLM error)
        import re
        text = re.sub(r",\s*}", "}", text)
        text = re.sub(r",\s*]", "]", text)

        return text
