"""
Unit tests for the Assimilator
"""

import pytest
import sys
import time
import threading
from pathlib import Path
from seaam.kernel.assimilator import Assimilator
from seaam.core.exceptions import ValidationFailedError, ImportFailedError


@pytest.fixture
def valid_organ_module(temp_dir):
    """Create a valid organ module for testing."""
    soma_dir = temp_dir / "soma" / "test"
    soma_dir.mkdir(parents=True)
    (soma_dir.parent / "__init__.py").write_text("# Soma\n")
    (soma_dir / "__init__.py").write_text("# Test package\n")
    
    organ_code = '''
from seaam.kernel.bus import bus, Event

class ValidOrgan:
    def __init__(self):
        self.started = True

_started = False

def start():
    global _started
    _started = True
    organ = ValidOrgan()
    # Just set flag and return, don't block
'''
    
    (soma_dir / "valid.py").write_text(organ_code)
    
    # Add to sys.path
    sys.path.insert(0, str(temp_dir))
    
    yield "soma.test.valid"
    
    # Cleanup
    sys.path.remove(str(temp_dir))
    # Remove from sys.modules if loaded
    for key in list(sys.modules.keys()):
        if key.startswith("soma"):
            del sys.modules[key]


@pytest.fixture
def invalid_organ_no_start(temp_dir):
    """Create an organ without start() function."""
    soma_dir = temp_dir / "soma" / "test"
    soma_dir.mkdir(parents=True, exist_ok=True)
    (soma_dir.parent / "__init__.py").write_text("# Soma\n")
    (soma_dir / "__init__.py").write_text("# Test package\n")
    
    organ_code = '''
class NoStartOrgan:
    pass
'''
    
    (soma_dir / "nostart.py").write_text(organ_code)
    
    sys.path.insert(0, str(temp_dir))
    
    yield "soma.test.nostart"
    
    sys.path.remove(str(temp_dir))
    for key in list(sys.modules.keys()):
        if key.startswith("soma"):
            del sys.modules[key]


class TestAssimilator:
    """Tests for the Assimilator class."""
    
    def test_integrate_valid_module(self, valid_organ_module, reset_event_bus):
        """Test integrating a valid organ."""
        assimilator = Assimilator()
        
        result = assimilator.integrate(valid_organ_module)
        
        assert result == True
        assert assimilator.is_running(valid_organ_module)
        
        # Wait a bit for thread to start
        time.sleep(0.1)
        
        status = assimilator.get_organ_status(valid_organ_module)
        assert status["status"] in ["running", "stopped"]  # May have completed
    
    def test_reject_missing_start(self, invalid_organ_no_start, reset_event_bus):
        """Test that modules without start() are rejected."""
        failures = []
        
        def on_fail(module, error_type, message):
            failures.append((module, error_type, message))
        
        assimilator = Assimilator(on_failure=on_fail)
        
        with pytest.raises(ValidationFailedError):
            assimilator.integrate(invalid_organ_no_start)
        
        assert not assimilator.is_running(invalid_organ_no_start)
        assert len(failures) == 1
        assert "start()" in failures[0][2]
    
    def test_reject_nonexistent_module(self, reset_event_bus):
        """Test handling of non-existent modules."""
        assimilator = Assimilator()
        
        with pytest.raises(ImportFailedError):
            assimilator.integrate("soma.nonexistent.module")
    
    def test_double_integration_prevention(self, valid_organ_module, reset_event_bus):
        """Test that same module isn't integrated twice."""
        assimilator = Assimilator()
        
        result1 = assimilator.integrate(valid_organ_module)
        result2 = assimilator.integrate(valid_organ_module)
        
        assert result1 == True
        assert result2 == True  # Returns True but doesn't re-integrate
        
        # Should only be tracked once
        assert len(assimilator.get_running_organs()) == 1
    
    def test_stop_organ(self, valid_organ_module, reset_event_bus):
        """Test stopping/untracking an organ."""
        assimilator = Assimilator()
        
        assimilator.integrate(valid_organ_module)
        assert assimilator.is_running(valid_organ_module)
        
        result = assimilator.stop_organ(valid_organ_module)
        
        assert result == True
        assert not assimilator.is_running(valid_organ_module)
    
    def test_batch_integration(self, valid_organ_module, reset_event_bus):
        """Test integrating multiple organs."""
        assimilator = Assimilator()
        
        results = assimilator.integrate_batch([
            valid_organ_module,
            "soma.nonexistent.module"
        ])
        
        assert results[valid_organ_module] == True
        assert results["soma.nonexistent.module"] == False
