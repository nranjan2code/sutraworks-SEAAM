"""
Integration tests for SEAA refactored features.

Tests:
- Code validation (syntax, forbidden imports, start() signature)
- Circuit breaker functionality
- Goal satisfaction
- Configuration validation
"""

import pytest
from datetime import datetime, timedelta

from seaa.connectors.llm_gateway import ProviderGateway
from seaa.dna.schema import DNA, Goal, Failure, FailureType
from seaa.core.config import SEAAConfig, LLMConfig, MetabolismConfig, CircuitBreakerConfig


class TestCodeValidation:
    """Tests for the code validation in ProviderGateway."""

    @pytest.fixture
    def gateway(self):
        return ProviderGateway()

    def test_syntax_error_rejected(self, gateway):
        """Code with syntax errors should be rejected."""
        code = """
def start()
    print("missing colon")
"""
        is_valid, error = gateway.validate_code(code, "test_module")
        assert not is_valid
        assert "Syntax error" in error

    def test_forbidden_import_pip_rejected(self, gateway):
        """Code importing pip should be rejected."""
        code = """
import pip
def start():
    pip.main(['install', 'something'])
"""
        is_valid, error = gateway.validate_code(code, "test_module")
        assert not is_valid
        assert "Forbidden" in error
        assert "pip" in error

    def test_forbidden_import_subprocess_rejected(self, gateway):
        """Code importing subprocess should be rejected."""
        code = """
import subprocess
def start():
    subprocess.run(['ls'])
"""
        is_valid, error = gateway.validate_code(code, "test_module")
        assert not is_valid
        assert "Forbidden" in error

    def test_forbidden_os_system_rejected(self, gateway):
        """Code using os.system should be rejected."""
        code = """
import os
def start():
    os.system('rm -rf /')
"""
        is_valid, error = gateway.validate_code(code, "test_module")
        assert not is_valid
        assert "Forbidden" in error

    def test_forbidden_eval_rejected(self, gateway):
        """Code using eval should be rejected."""
        code = """
def start():
    eval('__import__("os").system("ls")')
"""
        is_valid, error = gateway.validate_code(code, "test_module")
        assert not is_valid
        assert "Forbidden" in error

    def test_missing_start_rejected(self, gateway):
        """Code without start() function should be rejected."""
        code = """
class MyClass:
    def run(self):
        pass
"""
        is_valid, error = gateway.validate_code(code, "test_module")
        assert not is_valid
        assert "start()" in error

    def test_start_with_required_args_rejected(self, gateway):
        """start() with required arguments should be rejected."""
        code = """
def start(required_arg):
    print(required_arg)
"""
        is_valid, error = gateway.validate_code(code, "test_module")
        assert not is_valid
        assert "required argument" in error

    def test_start_with_default_args_accepted(self, gateway):
        """start() with only default arguments should be accepted."""
        code = """
def start(optional_arg=None):
    print(optional_arg)
"""
        is_valid, error = gateway.validate_code(code, "test_module")
        assert is_valid
        assert error is None

    def test_valid_code_accepted(self, gateway):
        """Valid code with proper start() should be accepted."""
        code = """
from seaa.kernel.bus import bus, Event

class MyOrgan:
    def __init__(self):
        pass

def start():
    organ = MyOrgan()
"""
        is_valid, error = gateway.validate_code(code, "test_module")
        assert is_valid
        assert error is None


class TestCircuitBreaker:
    """Tests for circuit breaker functionality in DNA."""

    @pytest.fixture
    def dna(self):
        return DNA.create_tabula_rasa()

    def test_should_attempt_no_failures(self, dna):
        """Should allow attempts when no failures exist."""
        assert dna.should_attempt("soma.test.module") is True

    def test_should_attempt_under_max(self, dna):
        """Should allow attempts when under max_attempts."""
        dna.add_failure("soma.test.module", FailureType.RUNTIME, "Test error")
        assert dna.should_attempt("soma.test.module", max_attempts=3) is True

    def test_circuit_opens_after_max_attempts(self, dna):
        """Circuit should open after max_attempts failures."""
        # Add failures up to max
        for i in range(3):
            dna.add_failure("soma.test.module", FailureType.RUNTIME, f"Error {i}")

        # Should trigger circuit open on the check
        assert dna.should_attempt("soma.test.module", max_attempts=3) is False
        assert dna.is_circuit_open("soma.test.module") is True

    def test_circuit_respects_cooldown(self, dna):
        """Circuit should respect cooldown period."""
        # Add failure and open circuit
        dna.add_failure("soma.test.module", FailureType.RUNTIME, "Error")
        dna.open_circuit("soma.test.module")

        # Should not allow during cooldown
        assert dna.should_attempt("soma.test.module", cooldown_minutes=30) is False

    def test_circuit_resets_after_cooldown(self, dna):
        """Circuit should reset after cooldown expires."""
        # Add failure and open circuit with past timestamp
        dna.add_failure("soma.test.module", FailureType.RUNTIME, "Error")
        dna.open_circuit("soma.test.module")

        # Manually set circuit opened in the past
        for failure in dna.failures:
            if failure.module_name == "soma.test.module":
                past_time = datetime.utcnow() - timedelta(minutes=60)
                failure.circuit_opened_at = past_time.isoformat() + "Z"

        # Should allow after cooldown
        assert dna.should_attempt("soma.test.module", cooldown_minutes=30) is True
        assert dna.is_circuit_open("soma.test.module") is False

    def test_reset_circuit_manual(self, dna):
        """Manual circuit reset should work."""
        dna.add_failure("soma.test.module", FailureType.RUNTIME, "Error")
        dna.open_circuit("soma.test.module")
        assert dna.is_circuit_open("soma.test.module") is True

        dna.reset_circuit("soma.test.module")
        assert dna.is_circuit_open("soma.test.module") is False


class TestGoalSatisfaction:
    """Tests for measurable goal satisfaction."""

    def test_goal_auto_satisfied_by_pattern(self):
        """Goal should be auto-satisfied when required organs match."""
        dna = DNA(
            goals=[
                Goal(
                    description="Must have perception",
                    required_organs=["soma.perception.*"],
                )
            ],
            active_modules=["soma.perception.observer"],
        )

        satisfied = dna.check_goal_satisfaction()
        assert satisfied == 1
        assert dna.goals[0].satisfied is True

    def test_goal_not_satisfied_without_organs(self):
        """Goal should not be satisfied without matching organs."""
        dna = DNA(
            goals=[
                Goal(
                    description="Must have perception",
                    required_organs=["soma.perception.*"],
                )
            ],
            active_modules=["soma.memory.journal"],
        )

        satisfied = dna.check_goal_satisfaction()
        assert satisfied == 0
        assert dna.goals[0].satisfied is False

    def test_goal_multiple_patterns_all_required(self):
        """All patterns must match for goal satisfaction."""
        dna = DNA(
            goals=[
                Goal(
                    description="Must have full pipeline",
                    required_organs=["soma.perception.*", "soma.memory.*"],
                )
            ],
            active_modules=["soma.perception.observer"],
        )

        # Only one pattern matched
        satisfied = dna.check_goal_satisfaction()
        assert satisfied == 0
        assert dna.goals[0].satisfied is False

        # Now add the missing organ
        dna.active_modules.append("soma.memory.journal")
        satisfied = dna.check_goal_satisfaction()
        assert satisfied == 1
        assert dna.goals[0].satisfied is True

    def test_goal_without_required_organs_not_auto_satisfied(self):
        """Goals without required_organs should not be auto-satisfied."""
        dna = DNA(
            goals=[Goal(description="Abstract goal")],
            active_modules=["soma.perception.observer"],
        )

        satisfied = dna.check_goal_satisfaction()
        assert satisfied == 0
        assert dna.goals[0].satisfied is False

    def test_already_satisfied_goals_skipped(self):
        """Already satisfied goals should not be recounted."""
        dna = DNA(
            goals=[
                Goal(
                    description="Already done",
                    required_organs=["soma.perception.*"],
                    satisfied=True,
                )
            ],
            active_modules=["soma.perception.observer"],
        )

        satisfied = dna.check_goal_satisfaction()
        assert satisfied == 0  # Not newly satisfied


class TestConfigValidation:
    """Tests for configuration validation."""

    def test_valid_config_passes(self):
        """Valid configuration should pass validation."""
        config = SEAAConfig()
        errors = config.validate()
        assert errors == []

    def test_invalid_temperature_rejected(self):
        """Temperature outside 0-2 should be rejected."""
        config = SEAAConfig()
        config.llm.temperature = 3.0
        errors = config.validate()
        assert any("temperature" in e.lower() for e in errors)

    def test_negative_temperature_rejected(self):
        """Negative temperature should be rejected."""
        config = SEAAConfig()
        config.llm.temperature = -0.5
        errors = config.validate()
        assert any("temperature" in e.lower() for e in errors)

    def test_short_timeout_rejected(self):
        """Too short timeout should be rejected."""
        config = SEAAConfig()
        config.llm.timeout_seconds = 5
        errors = config.validate()
        assert any("timeout" in e.lower() for e in errors)

    def test_invalid_resource_limits_rejected(self):
        """max_total_organs < max_concurrent_organs should be rejected."""
        config = SEAAConfig()
        config.metabolism.max_total_organs = 10
        config.metabolism.max_concurrent_organs = 20
        errors = config.validate()
        assert any("max_total_organs" in e for e in errors)

    def test_zero_max_organs_per_cycle_rejected(self):
        """Zero organs per cycle should be rejected."""
        config = SEAAConfig()
        config.metabolism.max_organs_per_cycle = 0
        errors = config.validate()
        assert any("max_organs_per_cycle" in e for e in errors)

    def test_zero_circuit_breaker_attempts_rejected(self):
        """Zero circuit breaker attempts should be rejected."""
        config = SEAAConfig()
        config.circuit_breaker.max_attempts = 0
        errors = config.validate()
        assert any("max_attempts" in e for e in errors)

    def test_zero_retries_rejected(self):
        """Zero LLM retries should be rejected."""
        config = SEAAConfig()
        config.llm.max_retries = 0
        errors = config.validate()
        assert any("max_retries" in e for e in errors)
