"""
Tests for SEAA Observability Layer

Tests for:
- Identity: creation, persistence, corruption handling, thread-safety
- Beacon: vitals, organs, caching, DNA availability
- Observer: timeline, system summary
"""

import json
import pytest
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import patch

from seaa.kernel.identity import (
    IdentityManager,
    InstanceIdentity,
    IdentityCorruptedError,
    get_identity_manager,
)
from seaa.kernel.beacon import Beacon, get_beacon
from seaa.kernel.observer import Observer
from seaa.kernel.protocols import OrganHealth


class TestIdentity:
    """Tests for InstanceIdentity and IdentityManager."""

    def test_create_new_identity(self, temp_dir):
        """Test that new identity is created when none exists."""
        IdentityManager.reset_instance()
        identity_path = temp_dir / ".identity.json"
        dna_path = temp_dir / "dna.json"

        manager = IdentityManager(identity_path, dna_path)
        identity = manager.get_identity()

        assert identity is not None
        assert len(identity.id) == 36  # UUID format
        assert identity.name.startswith("SEAA-")
        assert identity.genesis_time is not None
        assert identity_path.exists()

    def test_load_existing_identity(self, temp_dir):
        """Test that existing identity is loaded from file."""
        IdentityManager.reset_instance()
        identity_path = temp_dir / ".identity.json"
        dna_path = temp_dir / "dna.json"

        # Create identity data
        identity_data = {
            "id": "test-uuid-1234",
            "name": "TestInstance",
            "genesis_time": "2024-01-01T00:00:00Z",
            "lineage": "abc123",
        }
        with open(identity_path, "w") as f:
            json.dump(identity_data, f)

        manager = IdentityManager(identity_path, dna_path)
        identity = manager.get_identity()

        assert identity.id == "test-uuid-1234"
        assert identity.name == "TestInstance"

    def test_identity_persists_after_reload(self, temp_dir):
        """Test that identity persists across manager reloads."""
        IdentityManager.reset_instance()
        identity_path = temp_dir / ".identity.json"
        dna_path = temp_dir / "dna.json"

        # Create first manager and get identity
        manager1 = IdentityManager(identity_path, dna_path)
        identity1 = manager1.get_identity()
        original_id = identity1.id

        # Reset and create new manager
        IdentityManager.reset_instance()
        manager2 = IdentityManager(identity_path, dna_path)
        identity2 = manager2.get_identity()

        assert identity2.id == original_id

    def test_corrupted_identity_raises_error(self, temp_dir):
        """Test that corrupted identity file raises IdentityCorruptedError."""
        IdentityManager.reset_instance()
        identity_path = temp_dir / ".identity.json"
        dna_path = temp_dir / "dna.json"

        # Create corrupted identity file
        with open(identity_path, "w") as f:
            f.write("not valid json {{{")

        manager = IdentityManager(identity_path, dna_path)

        with pytest.raises(IdentityCorruptedError):
            manager.get_identity()

    def test_force_recreate_backs_up_corrupted(self, temp_dir):
        """Test that force_recreate backs up corrupted identity."""
        IdentityManager.reset_instance()
        identity_path = temp_dir / ".identity.json"
        dna_path = temp_dir / "dna.json"

        # Create corrupted identity file
        with open(identity_path, "w") as f:
            f.write("corrupted data")

        manager = IdentityManager(identity_path, dna_path)
        new_identity = manager.force_recreate()

        assert new_identity is not None
        assert (temp_dir / ".identity.json.bak").exists()

    def test_set_name_updates_identity(self, temp_dir):
        """Test that set_name updates the identity name."""
        IdentityManager.reset_instance()
        identity_path = temp_dir / ".identity.json"
        dna_path = temp_dir / "dna.json"

        manager = IdentityManager(identity_path, dna_path)
        original = manager.get_identity()
        original_id = original.id

        updated = manager.set_name("NewName")

        assert updated.name == "NewName"
        assert updated.id == original_id  # ID should not change

    def test_short_id(self, temp_dir):
        """Test that short_id returns first 8 chars."""
        identity = InstanceIdentity(
            id="12345678-1234-1234-1234-123456789012",
            name="Test",
            genesis_time="2024-01-01T00:00:00Z",
            lineage="abc",
        )

        assert identity.short_id() == "12345678"


class TestBeacon:
    """Tests for Beacon health observation."""

    def test_get_vitals_basic(self, temp_dir, sample_dna_dict):
        """Test that get_vitals returns correct structure."""
        dna_path = temp_dir / "dna.json"
        with open(dna_path, "w") as f:
            json.dump(sample_dna_dict, f)

        # Create identity file
        identity_path = temp_dir / ".identity.json"
        identity_data = {
            "id": "test-uuid",
            "name": "TestBeacon",
            "genesis_time": "2024-01-01T00:00:00Z",
            "lineage": "abc",
        }
        with open(identity_path, "w") as f:
            json.dump(identity_data, f)

        # Reset identity manager to use temp path
        IdentityManager.reset_instance()
        from seaa.kernel import identity as identity_module
        identity_module._manager = None

        with patch.object(IdentityManager, '__new__', return_value=IdentityManager.__new__(IdentityManager)):
            IdentityManager.reset_instance()
            beacon = Beacon(dna_path)
            vitals = beacon.get_vitals()

        assert vitals.alive is True
        assert vitals.organ_count == 0  # No active modules in sample
        assert vitals.goals_total == 2  # Two goals in sample

    def test_beacon_dna_unavailable(self, temp_dir):
        """Test beacon handles missing DNA gracefully."""
        dna_path = temp_dir / "nonexistent.json"

        beacon = Beacon(dna_path)
        vitals = beacon.get_vitals()

        assert vitals.alive is True
        assert beacon.is_dna_available() is False

    def test_beacon_caching(self, temp_dir, sample_dna_dict):
        """Test that beacon caches DNA loads."""
        dna_path = temp_dir / "dna.json"
        with open(dna_path, "w") as f:
            json.dump(sample_dna_dict, f)

        beacon = Beacon(dna_path, cache_ttl=10.0)  # Long TTL

        # First call loads DNA
        vitals1 = beacon.get_vitals()

        # Modify file (should not affect cached result)
        sample_dna_dict["goals"].append({"description": "New goal", "priority": 3, "satisfied": False})
        with open(dna_path, "w") as f:
            json.dump(sample_dna_dict, f)

        vitals2 = beacon.get_vitals()

        # Should still return cached value
        assert vitals2.goals_total == 2  # Not 3

        # Invalidate and reload
        beacon.invalidate_cache()
        vitals3 = beacon.get_vitals()
        assert vitals3.goals_total == 3

    def test_beacon_dna_hash(self, temp_dir, sample_dna_dict):
        """Test that beacon computes DNA hash correctly."""
        dna_path = temp_dir / "dna.json"
        with open(dna_path, "w") as f:
            json.dump(sample_dna_dict, f)

        beacon = Beacon(dna_path)
        vitals = beacon.get_vitals()

        assert vitals.dna_hash != "no-file"
        assert vitals.dna_hash != "error"
        assert len(vitals.dna_hash) == 16  # First 16 chars of SHA-256

    def test_get_organs_empty(self, temp_dir, sample_dna_dict):
        """Test get_organs with no active modules."""
        dna_path = temp_dir / "dna.json"
        with open(dna_path, "w") as f:
            json.dump(sample_dna_dict, f)

        beacon = Beacon(dna_path)
        organs = beacon.get_organs()

        assert organs == []

    def test_get_organs_with_active(self, temp_dir, sample_dna_dict):
        """Test get_organs with active modules."""
        sample_dna_dict["active_modules"] = ["soma.perception.observer"]
        dna_path = temp_dir / "dna.json"
        with open(dna_path, "w") as f:
            json.dump(sample_dna_dict, f)

        beacon = Beacon(dna_path)
        organs = beacon.get_organs()

        assert len(organs) == 1
        assert organs[0].name == "soma.perception.observer"
        assert organs[0].health == OrganHealth.HEALTHY
        assert organs[0].active is True


class TestObserver:
    """Tests for Observer local observation."""

    def test_get_timeline_empty(self, temp_dir, sample_dna_dict):
        """Test get_timeline with no events."""
        sample_dna_dict["blueprint"] = {}
        dna_path = temp_dir / "dna.json"
        with open(dna_path, "w") as f:
            json.dump(sample_dna_dict, f)

        observer = Observer(dna_path)
        timeline = observer.get_timeline()

        assert timeline == []

    def test_get_timeline_with_blueprint(self, temp_dir, sample_dna_dict):
        """Test get_timeline shows blueprint events."""
        sample_dna_dict["blueprint"]["soma.perception.observer"]["created_at"] = "2024-01-01T00:00:00Z"
        sample_dna_dict["blueprint"]["soma.perception.observer"]["updated_at"] = "2024-01-01T00:00:00Z"
        dna_path = temp_dir / "dna.json"
        with open(dna_path, "w") as f:
            json.dump(sample_dna_dict, f)

        observer = Observer(dna_path)
        timeline = observer.get_timeline()

        assert len(timeline) >= 1
        assert any(e["type"] == "designed" for e in timeline)

    def test_get_system_summary(self, temp_dir, sample_dna_dict):
        """Test get_system_summary returns comprehensive info."""
        dna_path = temp_dir / "dna.json"
        with open(dna_path, "w") as f:
            json.dump(sample_dna_dict, f)

        # Create identity file
        identity_path = temp_dir / ".identity.json"
        identity_data = {
            "id": "test-uuid",
            "name": "TestObserver",
            "genesis_time": "2024-01-01T00:00:00Z",
            "lineage": "abc",
        }
        with open(identity_path, "w") as f:
            json.dump(identity_data, f)

        IdentityManager.reset_instance()

        observer = Observer(dna_path)
        summary = observer.get_system_summary()

        assert "identity" in summary
        assert "vitals" in summary
        assert "health" in summary
        assert "evolution" in summary

    def test_observer_delegates_to_beacon(self, temp_dir, sample_dna_dict):
        """Test that observer correctly delegates to beacon."""
        dna_path = temp_dir / "dna.json"
        with open(dna_path, "w") as f:
            json.dump(sample_dna_dict, f)

        observer = Observer(dna_path)

        # These should work via delegation
        vitals = observer.get_vitals()
        organs = observer.get_organs()
        goals = observer.get_goals()
        failures = observer.get_failures()

        assert vitals is not None
        assert isinstance(organs, list)
        assert isinstance(goals, list)
        assert isinstance(failures, list)

    def test_search_events_by_type(self, temp_dir, sample_dna_dict):
        """Test searching events by type."""
        sample_dna_dict["blueprint"]["soma.perception.observer"]["created_at"] = "2024-01-01T00:00:00Z"
        sample_dna_dict["blueprint"]["soma.perception.observer"]["updated_at"] = "2024-01-01T00:00:00Z"
        sample_dna_dict["active_modules"] = ["soma.perception.observer"]
        dna_path = temp_dir / "dna.json"
        with open(dna_path, "w") as f:
            json.dump(sample_dna_dict, f)

        observer = Observer(dna_path)
        designed = observer.search_events(event_type="designed")
        integrated = observer.search_events(event_type="integrated")

        assert all(e["type"] == "designed" for e in designed)
        assert all(e["type"] == "integrated" for e in integrated)


class TestThreadSafety:
    """Tests for thread-safe singleton patterns."""

    def test_identity_manager_thread_safe(self, temp_dir):
        """Test that IdentityManager is thread-safe."""
        IdentityManager.reset_instance()
        identity_path = temp_dir / ".identity.json"
        dna_path = temp_dir / "dna.json"

        identities = []
        errors = []

        def get_identity_thread():
            try:
                manager = IdentityManager(identity_path, dna_path)
                identity = manager.get_identity()
                identities.append(identity.id)
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=get_identity_thread) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        # All threads should get the same identity
        assert len(set(identities)) == 1

    def test_beacon_cache_thread_safe(self, temp_dir, sample_dna_dict):
        """Test that Beacon cache is thread-safe."""
        dna_path = temp_dir / "dna.json"
        with open(dna_path, "w") as f:
            json.dump(sample_dna_dict, f)

        beacon = Beacon(dna_path, cache_ttl=0.001)  # Very short TTL
        errors = []

        def query_beacon():
            try:
                for _ in range(100):
                    beacon.get_vitals()
                    beacon.get_organs()
                    beacon.invalidate_cache()
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=query_beacon) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
