"""
SEAA DNA Schema

Strongly-typed Pydantic models for DNA validation.
Ensures data integrity and provides clear structure.
"""

from datetime import datetime
from typing import Any, Optional, Union, List, Dict
from dataclasses import dataclass, field, asdict
from enum import Enum
import fnmatch
import json


class FailureType(str, Enum):
    """Classification of failure types for better error handling."""
    IMPORT = "import"           # ImportError during assimilation
    VALIDATION = "validation"   # Missing start() or signature issues
    RUNTIME = "runtime"         # Exception during start() execution
    GENERATION = "generation"   # LLM failed to generate valid code
    MATERIALIZATION = "materialization"  # Failed to write to disk


@dataclass
class Failure:
    """
    A recorded failure for learning and correction.

    Structured format replaces the old string-based format.
    Includes circuit breaker state for repeated failures.
    """
    module_name: str
    error_type: FailureType
    error_message: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    attempt_count: int = 1
    context: Dict[str, Any] = field(default_factory=dict)
    # Circuit breaker fields
    circuit_open: bool = False
    circuit_opened_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "module_name": self.module_name,
            "error_type": self.error_type.value if isinstance(self.error_type, FailureType) else self.error_type,
            "error_message": self.error_message,
            "timestamp": self.timestamp,
            "attempt_count": self.attempt_count,
            "context": self.context,
            "circuit_open": self.circuit_open,
            "circuit_opened_at": self.circuit_opened_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Failure":
        error_type = data.get("error_type", "runtime")
        if isinstance(error_type, str):
            try:
                error_type = FailureType(error_type)
            except ValueError:
                error_type = FailureType.RUNTIME

        return cls(
            module_name=data["module_name"],
            error_type=error_type,
            error_message=data.get("error_message", "Unknown error"),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat() + "Z"),
            attempt_count=data.get("attempt_count", 1),
            context=data.get("context", {}),
            circuit_open=data.get("circuit_open", False),
            circuit_opened_at=data.get("circuit_opened_at"),
        )
    
    @classmethod
    def from_legacy_string(cls, legacy: str) -> "Failure":
        """Convert old format 'module: error' to new structured format."""
        if ": " in legacy:
            module_name, error_message = legacy.split(": ", 1)
        else:
            module_name = "unknown"
            error_message = legacy
        
        return cls(
            module_name=module_name,
            error_type=FailureType.RUNTIME,
            error_message=error_message,
        )


@dataclass
class OrganBlueprint:
    """
    Blueprint for an organ to be evolved.
    
    Contains all information needed to generate the organ.
    """
    name: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    version: int = 1
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "dependencies": self.dependencies,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, name: str, data: Union[Dict[str, Any], str]) -> "OrganBlueprint":
        """Create from dict or legacy string description."""
        if isinstance(data, str):
            # Legacy format: just a description string
            return cls(name=name, description=data)
        
        return cls(
            name=name,
            description=data.get("description", ""),
            dependencies=data.get("dependencies", []),
            version=data.get("version", 1),
            created_at=data.get("created_at", datetime.utcnow().isoformat() + "Z"),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat() + "Z"),
        )


@dataclass
class Goal:
    """
    A goal that drives system evolution.

    Goals can have required_organs patterns for automatic satisfaction checking.
    Patterns support wildcards: "soma.perception.*" matches any perception organ.
    """
    description: str
    priority: int = 1  # 1 = highest priority
    satisfied: bool = False
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    required_organs: List[str] = field(default_factory=list)  # e.g., ["soma.perception.*"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "priority": self.priority,
            "satisfied": self.satisfied,
            "created_at": self.created_at,
            "required_organs": self.required_organs,
        }

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], str]) -> "Goal":
        """Create from dict or legacy string."""
        if isinstance(data, str):
            return cls(description=data)

        return cls(
            description=data.get("description", ""),
            priority=data.get("priority", 1),
            satisfied=data.get("satisfied", False),
            created_at=data.get("created_at", datetime.utcnow().isoformat() + "Z"),
            required_organs=data.get("required_organs", []),
        )


@dataclass
class DNAMetadata:
    """Metadata about the DNA itself."""
    last_modified: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    total_evolutions: int = 0
    total_failures: int = 0
    last_successful_organ: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DNAMetadata":
        return cls(
            last_modified=data.get("last_modified", datetime.utcnow().isoformat() + "Z"),
            total_evolutions=data.get("total_evolutions", 0),
            total_failures=data.get("total_failures", 0),
            last_successful_organ=data.get("last_successful_organ"),
        )


@dataclass
class DNA:
    """
    The complete DNA structure for SEAA.
    
    This is the single source of truth for the organism's state.
    """
    system_version: str = "1.0.0"
    system_name: str = "SEAA"
    blueprint: Dict[str, OrganBlueprint] = field(default_factory=dict)
    goals: List[Goal] = field(default_factory=list)
    active_modules: List[str] = field(default_factory=list)
    failures: List[Failure] = field(default_factory=list)
    metadata: DNAMetadata = field(default_factory=DNAMetadata)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON storage."""
        return {
            "system_version": self.system_version,
            "system_name": self.system_name,
            "blueprint": {
                name: bp.to_dict() for name, bp in self.blueprint.items()
            },
            "goals": [g.to_dict() if isinstance(g, Goal) else g for g in self.goals],
            "active_modules": self.active_modules,
            "failures": [f.to_dict() for f in self.failures],
            "metadata": self.metadata.to_dict(),
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DNA":
        """Deserialize from dictionary."""
        # Parse blueprint
        blueprint = {}
        raw_blueprint = data.get("blueprint", {})
        for name, bp_data in raw_blueprint.items():
            blueprint[name] = OrganBlueprint.from_dict(name, bp_data)
        
        # Parse goals (handle both legacy string list and new object list)
        goals = []
        for goal_data in data.get("goals", []):
            goals.append(Goal.from_dict(goal_data))
        
        # Parse failures (handle legacy string format)
        failures = []
        for failure_data in data.get("failures", []):
            if isinstance(failure_data, str):
                failures.append(Failure.from_legacy_string(failure_data))
            else:
                failures.append(Failure.from_dict(failure_data))
        
        # Parse metadata
        metadata_data = data.get("metadata", {})
        metadata = DNAMetadata.from_dict(metadata_data)
        
        return cls(
            system_version=data.get("system_version", "1.0.0"),
            system_name=data.get("system_name", "SEAA"),
            blueprint=blueprint,
            goals=goals,
            active_modules=data.get("active_modules", []),
            failures=failures,
            metadata=metadata,
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "DNA":
        """Deserialize from JSON string."""
        return cls.from_dict(json.loads(json_str))
    
    def add_failure(self, module_name: str, error_type: FailureType, message: str, context: Optional[dict] = None) -> None:
        """Record a failure, incrementing count if it already exists."""
        # Check for existing failure for this module
        for failure in self.failures:
            if failure.module_name == module_name:
                failure.attempt_count += 1
                failure.error_type = error_type
                failure.error_message = message
                failure.timestamp = datetime.utcnow().isoformat() + "Z"
                if context:
                    failure.context.update(context)
                return
        
        # New failure
        self.failures.append(Failure(
            module_name=module_name,
            error_type=error_type,
            error_message=message,
            context=context or {},
        ))
        self.metadata.total_failures += 1
    
    def clear_failure(self, module_name: str) -> None:
        """Remove failures for a module (after successful fix)."""
        self.failures = [f for f in self.failures if f.module_name != module_name]
    
    def add_blueprint(self, name: str, description: str, dependencies: Optional[List[str]] = None) -> OrganBlueprint:
        """Add or update a blueprint."""
        if name in self.blueprint:
            # Update existing
            bp = self.blueprint[name]
            bp.description = description
            bp.version += 1
            bp.updated_at = datetime.utcnow().isoformat() + "Z"
            if dependencies:
                bp.dependencies = dependencies
        else:
            # New blueprint
            bp = OrganBlueprint(
                name=name,
                description=description,
                dependencies=dependencies or [],
            )
            self.blueprint[name] = bp
        
        return bp
    
    def get_pending_blueprints(self) -> Dict[str, OrganBlueprint]:
        """Get blueprints that are not yet active."""
        return {
            name: bp for name, bp in self.blueprint.items()
            if name not in self.active_modules
        }
    
    def get_failed_modules(self) -> List[str]:
        """Get list of module names that have failures."""
        return [f.module_name for f in self.failures]

    def should_attempt(self, module_name: str, max_attempts: int = 3, cooldown_minutes: int = 30) -> bool:
        """
        Check if we should attempt to evolve/fix this module.

        Returns False if:
        - Circuit is open and cooldown hasn't passed
        - Attempt count >= max_attempts and circuit is open

        Args:
            module_name: The module to check
            max_attempts: Maximum attempts before circuit opens
            cooldown_minutes: Minutes to wait before retrying after circuit opens
        """
        for failure in self.failures:
            if failure.module_name == module_name:
                if failure.circuit_open:
                    # Check if cooldown has passed
                    if failure.circuit_opened_at:
                        opened_at = datetime.fromisoformat(failure.circuit_opened_at.rstrip('Z'))
                        now = datetime.utcnow()
                        elapsed = (now - opened_at).total_seconds() / 60
                        if elapsed < cooldown_minutes:
                            return False
                        # Cooldown passed, close circuit and allow retry
                        failure.circuit_open = False
                        failure.circuit_opened_at = None
                        return True
                    return False
                # Circuit not open, check attempt count
                if failure.attempt_count >= max_attempts:
                    # Too many attempts, open the circuit
                    self.open_circuit(module_name)
                    return False
                return True
        # No failure record, safe to attempt
        return True

    def open_circuit(self, module_name: str) -> None:
        """Open the circuit breaker for a module."""
        for failure in self.failures:
            if failure.module_name == module_name:
                failure.circuit_open = True
                failure.circuit_opened_at = datetime.utcnow().isoformat() + "Z"
                return

    def is_circuit_open(self, module_name: str) -> bool:
        """Check if circuit breaker is open for a module."""
        for failure in self.failures:
            if failure.module_name == module_name:
                return failure.circuit_open
        return False

    def reset_circuit(self, module_name: str) -> None:
        """Manually reset the circuit breaker for a module."""
        for failure in self.failures:
            if failure.module_name == module_name:
                failure.circuit_open = False
                failure.circuit_opened_at = None
                failure.attempt_count = 0
                return

    def check_goal_satisfaction(self) -> int:
        """
        Check and update goal satisfaction based on active modules.

        For each goal with required_organs patterns, checks if all patterns
        match at least one active module. If so, marks the goal as satisfied.

        Returns:
            Number of goals newly satisfied
        """
        newly_satisfied = 0

        for goal in self.goals:
            if goal.satisfied:
                continue

            if not goal.required_organs:
                # No required organs specified, can't auto-satisfy
                continue

            # Check if all required patterns are matched
            all_matched = True
            for pattern in goal.required_organs:
                pattern_matched = False
                for module in self.active_modules:
                    if fnmatch.fnmatch(module, pattern):
                        pattern_matched = True
                        break
                if not pattern_matched:
                    all_matched = False
                    break

            if all_matched:
                goal.satisfied = True
                newly_satisfied += 1

        return newly_satisfied
    
    def mark_active(self, module_name: str) -> None:
        """Mark a module as active."""
        if module_name not in self.active_modules:
            self.active_modules.append(module_name)
        self.metadata.total_evolutions += 1
        self.metadata.last_successful_organ = module_name
        self.metadata.last_modified = datetime.utcnow().isoformat() + "Z"
    
    def mark_inactive(self, module_name: str) -> None:
        """Mark a module as inactive (failed)."""
        if module_name in self.active_modules:
            self.active_modules.remove(module_name)
    
    @classmethod
    def create_tabula_rasa(cls, goals: Optional[List[Dict[str, Any]]] = None) -> "DNA":
        """
        Create a fresh DNA with default measurable goals.

        Args:
            goals: Optional list of goal dicts with 'description' and optional 'required_organs'
        """
        default_goals = goals or [
            {
                "description": "I must be able to perceive the file system.",
                "required_organs": ["soma.perception.*"],
            },
            {
                "description": "I must have a memory.",
                "required_organs": ["soma.memory.*"],
            },
            {
                "description": "I must have a visual dashboard.",
                "required_organs": ["soma.interface.*"],
            },
        ]

        parsed_goals = []
        for g in default_goals:
            if isinstance(g, str):
                parsed_goals.append(Goal(description=g))
            else:
                parsed_goals.append(Goal(
                    description=g.get("description", ""),
                    required_organs=g.get("required_organs", []),
                ))

        return cls(
            system_version="1.0.0",
            system_name="SEAA-TabulaRasa",
            goals=parsed_goals,
        )
