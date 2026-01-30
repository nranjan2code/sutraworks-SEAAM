"""
SEAA Custom Exceptions

Typed exception hierarchy for proper error handling and classification.
"""

from typing import Optional
class SEAAError(Exception):
    """Base exception for all SEAA errors."""
    
    def __init__(self, message: str, context: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.context = context or {}
    
    def __str__(self):
        if self.context:
            return f"{self.message} | context={self.context}"
        return self.message


# DNA Errors
class DNAError(SEAAError):
    """Errors related to DNA loading, saving, or validation."""
    pass


class DNAValidationError(DNAError):
    """DNA failed schema validation."""
    pass


class DNANotFoundError(DNAError):
    """DNA file does not exist."""
    pass


class DNACorruptedError(DNAError):
    """DNA file exists but contains invalid JSON."""
    pass


# Evolution Errors
class EvolutionError(SEAAError):
    """Errors during the evolution/code generation process."""
    pass


class BlueprintError(EvolutionError):
    """Error creating or validating a blueprint."""
    pass


class CodeGenerationError(EvolutionError):
    """LLM failed to generate valid code."""
    pass


class MaterializationError(EvolutionError):
    """Failed to write code to filesystem."""
    pass


# Assimilation Errors
class AssimilationError(SEAAError):
    """Errors during module loading and activation."""
    pass


class ImportFailedError(AssimilationError):
    """Failed to import a module."""
    
    def __init__(self, module_name: str, original_error: Exception):
        super().__init__(
            f"Failed to import module: {module_name}",
            context={"module": module_name, "error": str(original_error)}
        )
        self.module_name = module_name
        self.original_error = original_error


class ValidationFailedError(AssimilationError):
    """Module imported but failed validation (e.g., missing start())."""
    
    def __init__(self, module_name: str, reason: str):
        super().__init__(
            f"Module validation failed: {module_name} - {reason}",
            context={"module": module_name, "reason": reason}
        )
        self.module_name = module_name
        self.reason = reason


class ActivationFailedError(AssimilationError):
    """Module's start() function raised an exception."""
    
    def __init__(self, module_name: str, original_error: Exception):
        super().__init__(
            f"Module activation failed: {module_name}",
            context={"module": module_name, "error": str(original_error)}
        )
        self.module_name = module_name
        self.original_error = original_error


# Immunity/Healing Errors
class ImmunityError(SEAAError):
    """Errors during the healing/recovery process."""
    pass


class DependencyResolutionError(ImmunityError):
    """Failed to resolve a missing dependency."""
    pass


class KernelProtectionError(ImmunityError):
    """Attempted to modify protected kernel code."""
    
    def __init__(self, target: str):
        super().__init__(
            f"Kernel protection violation: Cannot modify {target}",
            context={"target": target}
        )
        self.target = target


# LLM/Gateway Errors
class GatewayError(SEAAError):
    """Errors communicating with LLM providers."""
    pass


class ProviderUnavailableError(GatewayError):
    """No LLM provider is available."""
    pass


class RateLimitError(GatewayError):
    """LLM provider rate limit exceeded."""
    pass


class InvalidResponseError(GatewayError):
    """LLM returned an unparseable response."""
    pass
