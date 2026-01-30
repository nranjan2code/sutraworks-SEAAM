import pytest
from unittest.mock import MagicMock, patch
from seaa.kernel.immunity import Immunity
from seaa.dna.schema import FailureType

class TestAutoImmuneResponse:
    
    @pytest.fixture
    def mock_genealogy(self):
        genealogy = MagicMock()
        genealogy.revert_last.return_value = True
        return genealogy
    
    @pytest.fixture
    def immunity(self, mock_genealogy):
        return Immunity(
            root_dir="/tmp/test",
            genealogy=mock_genealogy,
            on_failure_report=MagicMock(),
        )
    
    def test_trigger_revert_success(self, immunity, mock_genealogy):
        """Test that trigger_revert calls genealogy.revert_last."""
        success = immunity.trigger_revert("soma.bad_organ", "SyntaxError")
        
        assert success is True
        mock_genealogy.revert_last.assert_called_once()
        immunity.on_failure_report.assert_called_with(
            "soma.bad_organ", 
            FailureType.RUNTIME, 
            "Auto-Reverted due to critical failure: SyntaxError"
        )

    def test_trigger_revert_no_genealogy(self):
        """Test behavior when genealogy is not enabled/passed."""
        immunity = Immunity(root_dir="/tmp/test", genealogy=None)
        
        success = immunity.trigger_revert("soma.bad_organ", "Error")
        
        assert success is False

    def test_trigger_revert_failure(self, immunity, mock_genealogy):
        """Test when git revert fails."""
        mock_genealogy.revert_last.return_value = False
        
        success = immunity.trigger_revert("soma.bad_organ", "Error")
        
        assert success is False
        mock_genealogy.revert_last.assert_called_once()
