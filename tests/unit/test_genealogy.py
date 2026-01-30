import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from seaa.kernel.genealogy import Genealogy

@pytest.fixture
def temp_soma(tmp_path):
    """Create a temporary directory for soma."""
    soma_dir = tmp_path / "soma"
    soma_dir.mkdir()
    return soma_dir

@pytest.fixture
def mock_config():
    """Mock configuration."""
    with patch("seaa.kernel.genealogy.config") as mock:
        mock.genealogy.enabled = True
        mock.genealogy.user_name = "Test User"
        mock.genealogy.user_email = "test@example.com"
        mock.paths.soma = Path("./soma")
        yield mock

class TestGenealogy:
    
    def test_init_repo(self, temp_soma, mock_config):
        """Test repository initialization."""
        gen = Genealogy(temp_soma)
        assert gen.init_repo() is True
        
        # Check if .git exists
        assert (temp_soma / ".git").is_dir()
        assert (temp_soma / "README.md").exists()
        
        # Check if initial commit was made
        log = gen._run_git(["log", "--oneline"], capture_output=True)
        assert "Genesis: Initial Awakening" in log

    def test_commit_flow(self, temp_soma, mock_config):
        """Test committing changes."""
        gen = Genealogy(temp_soma)
        gen.init_repo()
        
        # Create a new organ
        organ_file = temp_soma / "organ.py"
        organ_file.write_text("print('Hello')")
        
        # Commit
        assert gen.commit("Evolved organ") is True
        
        # Verify log
        log = gen._run_git(["log", "--oneline"], capture_output=True)
        assert "Evolved organ" in log
        
        # Verify status is clean
        status = gen._run_git(["status", "--porcelain"], capture_output=True)
        assert status.strip() == ""

    def test_revert_last(self, temp_soma, mock_config):
        """Test reverting to previous state."""
        gen = Genealogy(temp_soma)
        gen.init_repo() # Commit 1
        
        # Evolution 1
        (temp_soma / "organ.py").write_text("v1")
        gen.commit("Evolution 1") # Commit 2
        
        # Evolution 2 (Bad one)
        (temp_soma / "organ.py").write_text("v2")
        gen.commit("Evolution 2") # Commit 3
        
        assert (temp_soma / "organ.py").read_text() == "v2"
        
        # Revert!
        assert gen.revert_last() is True
        
        # Should be back to v1
        assert (temp_soma / "organ.py").read_text() == "v1"
        
        # Log should allow show Commit 2 as HEAD
        log = gen._run_git(["log", "-n", "1"], capture_output=True)
        assert "Evolution 1" in log

    def test_disabled(self, temp_soma, mock_config):
        """Test that nothing happens if disabled."""
        mock_config.genealogy.enabled = False
        gen = Genealogy(temp_soma)
        
        assert gen.init_repo() is False
        assert (temp_soma / ".git").exists() is False
