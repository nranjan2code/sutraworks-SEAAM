"""
SEAAM Architect - The Mind

The intelligent agent responsible for system design.
Uses externalized prompt templates for flexibility.

Responsibilities:
- Reflect on DNA state (goals, failures, blueprint)
- Design new organs
- Propose goal evolution
"""

import json
from typing import Callable, Optional

from seaam.core.logging import get_logger
from seaam.core.config import config
from seaam.dna.schema import DNA, Goal
from seaam.cortex.prompt_loader import prompt_loader

logger = get_logger("architect")


class Architect:
    """
    The Mind of SEAAM.
    
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
        
        return prompt_loader.render(
            "architect_reflect",
            goals=goals,
            blueprint=blueprint,
            failures=failures,
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
    
    def _process_response(self, response: str) -> bool:
        """
        Parse and apply the Architect's response.
        
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
            
            return modified
            
        except Exception as e:
            logger.error(f"Failed to process response: {e}")
            logger.debug(f"Raw response: {response[:200]}...")
            return False
    
    def _extract_json(self, text: str) -> Optional[dict]:
        """
        Extract JSON object from text response.
        
        Handles LLMs that include extra text around JSON.
        """
        # Find JSON object
        start_idx = text.find("{")
        end_idx = text.rfind("}")
        
        if start_idx == -1 or end_idx == -1:
            return None
        
        json_str = text[start_idx:end_idx + 1]
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Try to clean up common issues
            cleaned = self._clean_json_string(json_str)
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                return None
    
    def _clean_json_string(self, text: str) -> str:
        """
        Clean common JSON issues from LLM output.
        """
        # Remove markdown code fences if present
        if "```" in text:
            lines = []
            in_fence = False
            for line in text.split("\n"):
                if line.strip().startswith("```"):
                    in_fence = not in_fence
                    continue
                if not in_fence:
                    lines.append(line)
            text = "\n".join(lines)
        
        # Remove trailing commas (common LLM error)
        import re
        text = re.sub(r",\s*}", "}", text)
        text = re.sub(r",\s*]", "]", text)
        
        return text
