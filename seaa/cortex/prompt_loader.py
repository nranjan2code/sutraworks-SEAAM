"""
SEAA Prompt Loader

Loads and renders prompt templates from YAML files.

Features:
- YAML-based prompt templates
- Jinja2 template rendering
- Prompt caching
- Version tracking
"""

import json
from pathlib import Path
from typing import Any, Optional, Union, List, Dict

from seaa.core.logging import get_logger
from seaa.core.config import config

logger = get_logger("prompt_loader")

# Try to import yaml, fall back to manual parsing
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    logger.warning("PyYAML not installed, prompt loading will be limited")


class PromptTemplate:
    """A loaded prompt template."""
    
    def __init__(
        self,
        name: str,
        version: int,
        description: str,
        template: str,
        variables: List[str],
    ):
        self.name = name
        self.version = version
        self.description = description
        self.template = template
        self.variables = variables
    
    def render(self, **kwargs: Any) -> str:
        """
        Render the template with provided variables.
        
        Uses simple string replacement (Jinja2-lite) to avoid dependency.
        """
        result = self.template
        
        for var in self.variables:
            placeholder = "{{ " + var + " }}"
            alt_placeholder = "{{" + var + "}}"
            json_placeholder = "{{ " + var + " | tojson }}"
            
            if var in kwargs:
                value = kwargs[var]
                
                # Handle tojson filter
                if json_placeholder in result:
                    result = result.replace(json_placeholder, json.dumps(value, indent=2))
                
                # Handle regular placeholder
                if isinstance(value, (dict, list)):
                    str_value = json.dumps(value, indent=2)
                else:
                    str_value = str(value)
                
                result = result.replace(placeholder, str_value)
                result = result.replace(alt_placeholder, str_value)
        
        return result


class PromptLoader:
    """
    Loads and caches prompt templates.
    
    Templates are loaded from YAML files in the configured prompts directory.
    """
    
    def __init__(self, prompts_dir: Optional[Union[Path, str]] = None):
        """
        Args:
            prompts_dir: Directory containing prompt YAML files
        """
        self.prompts_dir = Path(prompts_dir) if prompts_dir else config.paths.prompts
        self._cache: Dict[str, PromptTemplate] = {}
    
    def load(self, name: str) -> PromptTemplate:
        """
        Load a prompt template by name.
        
        Args:
            name: Template name (without .yaml extension)
        
        Returns:
            PromptTemplate instance
        
        Raises:
            FileNotFoundError: If template file doesn't exist
            ValueError: If template is invalid
        """
        # Check cache first
        if name in self._cache:
            return self._cache[name]
        
        # Load from file
        file_path = self.prompts_dir / f"{name}.yaml"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt template not found: {file_path}")
        
        template = self._load_yaml(file_path)
        self._cache[name] = template
        
        logger.debug(f"Loaded prompt: {name} (v{template.version})")
        return template
    
    def _load_yaml(self, path: Path) -> PromptTemplate:
        """Load and parse a YAML prompt file."""
        content = path.read_text()
        
        if HAS_YAML:
            data = yaml.safe_load(content)
        else:
            # Fallback: simple parsing for the structure we use
            data = self._simple_yaml_parse(content)
        
        return PromptTemplate(
            name=data.get("name", path.stem),
            version=data.get("version", 1),
            description=data.get("description", ""),
            template=data.get("template", ""),
            variables=data.get("variables", []),
        )
    
    def _simple_yaml_parse(self, content: str) -> dict:
        """
        Simple YAML parser for our specific format.
        
        Only handles the structure we use in prompt files.
        """
        result = {}
        current_key = None
        current_value = []
        in_multiline = False
        
        for line in content.split("\n"):
            # Check for key: value
            if not in_multiline and line and not line.startswith(" ") and ":" in line:
                # Save previous key if exists
                if current_key and current_value:
                    result[current_key] = "\n".join(current_value).strip()
                
                key, value = line.split(":", 1)
                current_key = key.strip()
                value = value.strip()
                
                if value == "|":
                    # Start multiline
                    in_multiline = True
                    current_value = []
                elif value.startswith("["):
                    # List
                    result[current_key] = [
                        v.strip().strip("'\"")
                        for v in value.strip("[]").split(",")
                        if v.strip()
                    ]
                    current_key = None
                else:
                    result[current_key] = value.strip("'\"")
                    if current_key == "version":
                        result[current_key] = int(result[current_key])
                    current_key = None
            elif in_multiline:
                if line and not line.startswith(" "):
                    # End of multiline
                    result[current_key] = "\n".join(current_value)
                    in_multiline = False
                    current_value = []
                    # Re-process this line
                    if ":" in line:
                        key, value = line.split(":", 1)
                        result[key.strip()] = value.strip()
                else:
                    # Continue multiline
                    current_value.append(line[2:] if line.startswith("  ") else line)
        
        # Save last key
        if current_key and current_value:
            result[current_key] = "\n".join(current_value).strip()
        
        return result
    
    def render(self, name: str, **kwargs: Any) -> str:
        """
        Load and render a prompt in one step.
        
        Args:
            name: Template name
            **kwargs: Variables to pass to template
        
        Returns:
            Rendered prompt string
        """
        template = self.load(name)
        return template.render(**kwargs)
    
    def clear_cache(self) -> None:
        """Clear the template cache."""
        self._cache.clear()
    
    def list_templates(self) -> List[str]:
        """List all available template names."""
        if not self.prompts_dir.exists():
            return []
        
        return [f.stem for f in self.prompts_dir.glob("*.yaml")]


# Global instance
prompt_loader = PromptLoader()
