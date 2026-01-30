"""
SEAA Test Configuration

Pytest fixtures and helpers for testing.
"""

import pytest
import sys
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_dna_dict():
    """Sample DNA data in dictionary format."""
    return {
        "system_version": "1.0.0",
        "system_name": "SEAA-Test",
        "blueprint": {
            "soma.perception.observer": {
                "name": "soma.perception.observer",
                "description": "Watches the filesystem",
                "dependencies": [],
                "version": 1,
            }
        },
        "goals": [
            {"description": "Test goal 1", "priority": 1, "satisfied": False},
            {"description": "Test goal 2", "priority": 2, "satisfied": False},
        ],
        "active_modules": [],
        "failures": [],
        "metadata": {
            "total_evolutions": 0,
            "total_failures": 0,
        },
    }


@pytest.fixture
def temp_dna_file(temp_dir, sample_dna_dict):
    """Create a temporary DNA file."""
    dna_path = temp_dir / "dna.json"
    with open(dna_path, "w") as f:
        json.dump(sample_dna_dict, f)
    return dna_path


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for code generation."""
    return '''
from seaa.kernel.bus import bus, Event

class TestOrgan:
    def __init__(self):
        bus.subscribe("test.event", self.handle)
    
    def handle(self, event):
        print(f"Received: {event.data}")

def start():
    organ = TestOrgan()
    import time
    while True:
        time.sleep(1)
'''


@pytest.fixture
def mock_gateway(mock_llm_response):
    """Mock LLM gateway that returns valid code."""
    gateway = Mock()
    gateway.generate_code.return_value = mock_llm_response
    gateway.think.return_value = json.dumps({
        "module_name": "soma.test.organ",
        "description": "A test organ"
    })
    return gateway


@pytest.fixture
def reset_event_bus():
    """Reset the EventBus singleton between tests."""
    from seaa.kernel.bus import EventBus
    EventBus.reset_instance()
    yield
    EventBus.reset_instance()


@pytest.fixture
def sample_organ_code():
    """Sample valid organ code."""
    return '''
from seaa.kernel.bus import bus, Event

class SampleOrgan:
    def __init__(self):
        self.running = True
        bus.subscribe("sample.event", self.on_event)
    
    def on_event(self, event):
        print(f"Sample received: {event.data}")

def start():
    organ = SampleOrgan()
'''


@pytest.fixture
def temp_soma_dir(temp_dir):
    """Create a temporary soma directory structure."""
    soma_dir = temp_dir / "soma"
    soma_dir.mkdir()
    (soma_dir / "__init__.py").write_text("# Soma package\n")
    
    perception_dir = soma_dir / "perception"
    perception_dir.mkdir()
    (perception_dir / "__init__.py").write_text("# Perception package\n")
    
    return soma_dir
