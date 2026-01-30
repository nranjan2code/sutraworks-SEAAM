"""
Unit tests for DNA Schema
"""

import pytest
import json
from datetime import datetime
from seaa.dna.schema import (
    DNA,
    OrganBlueprint,
    Failure,
    Goal,
    FailureType,
    DNAMetadata,
)


class TestFailure:
    """Tests for the Failure class."""
    
    def test_failure_creation(self):
        """Test basic failure creation."""
        failure = Failure(
            module_name="soma.test.organ",
            error_type=FailureType.IMPORT,
            error_message="Module not found"
        )
        
        assert failure.module_name == "soma.test.organ"
        assert failure.error_type == FailureType.IMPORT
        assert failure.error_message == "Module not found"
        assert failure.attempt_count == 1
    
    def test_failure_to_dict(self):
        """Test failure serialization."""
        failure = Failure(
            module_name="test",
            error_type=FailureType.VALIDATION,
            error_message="Missing start()"
        )
        
        data = failure.to_dict()
        assert data["module_name"] == "test"
        assert data["error_type"] == "validation"
        assert data["error_message"] == "Missing start()"
    
    def test_failure_from_legacy_string(self):
        """Test parsing legacy failure format."""
        legacy = "soma.perception.observer: Missing start() function"
        failure = Failure.from_legacy_string(legacy)
        
        assert failure.module_name == "soma.perception.observer"
        assert failure.error_message == "Missing start() function"
        assert failure.error_type == FailureType.RUNTIME


class TestOrganBlueprint:
    """Tests for OrganBlueprint class."""
    
    def test_blueprint_creation(self):
        """Test basic blueprint creation."""
        bp = OrganBlueprint(
            name="soma.perception.observer",
            description="Watches filesystem"
        )
        
        assert bp.name == "soma.perception.observer"
        assert bp.description == "Watches filesystem"
        assert bp.version == 1
        assert bp.dependencies == []
    
    def test_blueprint_from_legacy_string(self):
        """Test parsing legacy string format."""
        bp = OrganBlueprint.from_dict(
            "soma.test",
            "A simple test organ"  # Old format was just a string
        )
        
        assert bp.name == "soma.test"
        assert bp.description == "A simple test organ"


class TestGoal:
    """Tests for Goal class."""
    
    def test_goal_creation(self):
        """Test basic goal creation."""
        goal = Goal(description="I must perceive")
        
        assert goal.description == "I must perceive"
        assert goal.priority == 1
        assert goal.satisfied == False
    
    def test_goal_from_legacy_string(self):
        """Test parsing legacy string format."""
        goal = Goal.from_dict("I must have memory")
        
        assert goal.description == "I must have memory"


class TestDNA:
    """Tests for DNA class."""
    
    def test_dna_creation(self):
        """Test basic DNA creation."""
        dna = DNA()
        
        assert dna.system_version == "1.0.0"
        assert dna.blueprint == {}
        assert dna.goals == []
        assert dna.active_modules == []
        assert dna.failures == []
    
    def test_dna_tabula_rasa(self):
        """Test creating fresh DNA."""
        dna = DNA.create_tabula_rasa()
        
        assert dna.system_name == "SEAA-TabulaRasa"
        assert len(dna.goals) == 3
        assert dna.goals[0].description == "I must be able to perceive the file system."
    
    def test_dna_add_blueprint(self):
        """Test adding a blueprint."""
        dna = DNA()
        bp = dna.add_blueprint("soma.test", "A test organ")
        
        assert "soma.test" in dna.blueprint
        assert bp.description == "A test organ"
        assert bp.version == 1
    
    def test_dna_update_blueprint(self):
        """Test updating existing blueprint."""
        dna = DNA()
        dna.add_blueprint("soma.test", "Version 1")
        dna.add_blueprint("soma.test", "Version 2")
        
        bp = dna.blueprint["soma.test"]
        assert bp.description == "Version 2"
        assert bp.version == 2
    
    def test_dna_add_failure(self):
        """Test recording failures."""
        dna = DNA()
        dna.add_failure(
            "soma.test",
            FailureType.IMPORT,
            "Module not found"
        )
        
        assert len(dna.failures) == 1
        assert dna.failures[0].module_name == "soma.test"
        assert dna.metadata.total_failures == 1
    
    def test_dna_failure_increment(self):
        """Test that repeated failures increment count."""
        dna = DNA()
        dna.add_failure("soma.test", FailureType.IMPORT, "Error 1")
        dna.add_failure("soma.test", FailureType.IMPORT, "Error 2")
        
        assert len(dna.failures) == 1
        assert dna.failures[0].attempt_count == 2
        assert dna.failures[0].error_message == "Error 2"
    
    def test_dna_clear_failure(self):
        """Test clearing failures for a module."""
        dna = DNA()
        dna.add_failure("soma.test", FailureType.IMPORT, "Error")
        dna.clear_failure("soma.test")
        
        assert len(dna.failures) == 0
    
    def test_dna_mark_active(self):
        """Test marking a module as active."""
        dna = DNA()
        dna.mark_active("soma.test")
        
        assert "soma.test" in dna.active_modules
        assert dna.metadata.total_evolutions == 1
        assert dna.metadata.last_successful_organ == "soma.test"
    
    def test_dna_pending_blueprints(self):
        """Test getting pending blueprints."""
        dna = DNA()
        dna.add_blueprint("soma.pending", "Not yet built")
        dna.add_blueprint("soma.active", "Already built")
        dna.mark_active("soma.active")
        
        pending = dna.get_pending_blueprints()
        assert "soma.pending" in pending
        assert "soma.active" not in pending
    
    def test_dna_serialization(self):
        """Test DNA to/from dict."""
        dna = DNA.create_tabula_rasa()
        dna.add_blueprint("soma.test", "Test organ")
        dna.add_failure("soma.test", FailureType.VALIDATION, "Missing start()")
        
        # Serialize
        data = dna.to_dict()
        json_str = json.dumps(data)
        
        # Deserialize
        loaded = DNA.from_dict(json.loads(json_str))
        
        assert loaded.system_name == dna.system_name
        assert len(loaded.goals) == len(dna.goals)
        assert "soma.test" in loaded.blueprint
        assert len(loaded.failures) == 1
    
    def test_dna_legacy_format_migration(self):
        """Test loading DNA with legacy format."""
        legacy_data = {
            "system_version": "0.0.1",
            "system_name": "OldSEAA",
            "blueprint": {
                "soma.test": "Just a description string"  # Old format
            },
            "goals": [
                "I must perceive",  # Old format: just strings
                "I must remember"
            ],
            "active_modules": ["soma.test"],
            "failures": [
                "soma.test: Some error"  # Old format: just strings
            ]
        }
        
        dna = DNA.from_dict(legacy_data)
        
        assert dna.system_name == "OldSEAA"
        assert dna.blueprint["soma.test"].description == "Just a description string"
        assert dna.goals[0].description == "I must perceive"
        assert dna.failures[0].module_name == "soma.test"
