"""
Unit tests for the Materializer
"""

import pytest
from pathlib import Path
from seaa.kernel.materializer import Materializer
from seaa.core.exceptions import KernelProtectionError, MaterializationError


class TestMaterializer:
    """Tests for the Materializer class."""
    
    def test_materialize_basic(self, temp_dir, sample_organ_code):
        """Test basic code materialization."""
        materializer = Materializer(root_dir=temp_dir)
        
        path = materializer.materialize("soma.test.organ", sample_organ_code)
        
        assert path.exists()
        assert path.name == "organ.py"
        assert path.read_text() == sample_organ_code
    
    def test_creates_package_structure(self, temp_dir, sample_organ_code):
        """Test that package directories and __init__.py are created."""
        materializer = Materializer(root_dir=temp_dir)
        
        materializer.materialize("soma.deep.nested.organ", sample_organ_code)
        
        # Check directory structure
        assert (temp_dir / "soma").is_dir()
        assert (temp_dir / "soma" / "__init__.py").exists()
        assert (temp_dir / "soma" / "deep").is_dir()
        assert (temp_dir / "soma" / "deep" / "__init__.py").exists()
        assert (temp_dir / "soma" / "deep" / "nested").is_dir()
        assert (temp_dir / "soma" / "deep" / "nested" / "__init__.py").exists()
        assert (temp_dir / "soma" / "deep" / "nested" / "organ.py").exists()
    
    def test_kernel_protection(self, temp_dir, sample_organ_code):
        """Test that seaa.* modules are protected."""
        materializer = Materializer(root_dir=temp_dir)
        
        with pytest.raises(KernelProtectionError):
            materializer.materialize("seaa.kernel.bus", sample_organ_code)
    
    def test_soma_prefix_required(self, temp_dir, sample_organ_code):
        """Test that non-soma modules are rejected."""
        materializer = Materializer(root_dir=temp_dir)
        
        with pytest.raises(MaterializationError):
            materializer.materialize("other.module", sample_organ_code)
    
    def test_exists_check(self, temp_dir, sample_organ_code):
        """Test checking if organ exists."""
        materializer = Materializer(root_dir=temp_dir)
        
        assert not materializer.exists("soma.test.organ")
        
        materializer.materialize("soma.test.organ", sample_organ_code)
        
        assert materializer.exists("soma.test.organ")
    
    def test_read_organ(self, temp_dir, sample_organ_code):
        """Test reading organ source code."""
        materializer = Materializer(root_dir=temp_dir)
        
        materializer.materialize("soma.test.organ", sample_organ_code)
        
        code = materializer.read("soma.test.organ")
        assert code == sample_organ_code
    
    def test_delete_organ(self, temp_dir, sample_organ_code):
        """Test deleting an organ."""
        materializer = Materializer(root_dir=temp_dir)
        
        materializer.materialize("soma.test.organ", sample_organ_code)
        assert materializer.exists("soma.test.organ")
        
        result = materializer.delete("soma.test.organ")
        assert result == True
        assert not materializer.exists("soma.test.organ")
    
    def test_list_organs(self, temp_dir, sample_organ_code):
        """Test listing all materialized organs."""
        materializer = Materializer(root_dir=temp_dir)
        
        materializer.materialize("soma.perception.observer", sample_organ_code)
        materializer.materialize("soma.memory.journal", sample_organ_code)
        
        organs = materializer.list_organs()
        
        assert "soma.perception.observer" in organs
        assert "soma.memory.journal" in organs
        assert len(organs) == 2
    
    def test_atomic_write(self, temp_dir, sample_organ_code):
        """Test that writes are atomic (no partial files)."""
        materializer = Materializer(root_dir=temp_dir)
        
        # Materialize
        path = materializer.materialize("soma.test.organ", sample_organ_code)
        
        # Check no temp files left
        temp_files = list(temp_dir.rglob("*.tmp"))
        assert len(temp_files) == 0
        
        # Check content is complete
        assert path.read_text() == sample_organ_code
