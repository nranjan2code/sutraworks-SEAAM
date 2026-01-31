#!/bin/bash

#============================================================================
# SEAA Installation Script
# Self-Evolving Autonomous Agent - One-step setup for any system
#
# Usage:
#   ./install.sh               # Interactive setup
#   ./install.sh --help        # Show help
#   ./install.sh --dev         # Development mode
#   ./install.sh --skip-llm    # Skip LLM setup (use existing config)
#============================================================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PYTHON_MIN_VERSION="3.9"
SEAA_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SEAA_HOME}/venv"
CLI_DEPS=false
DEV_MODE=false
SKIP_LLM=false

#============================================================================
# Helper Functions
#============================================================================

print_header() {
    echo -e "\n${BLUE}===================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

show_help() {
    cat << EOF
SEAA Installation Script

Usage:
  ./install.sh [OPTIONS]

Options:
  --help              Show this help message
  --dev               Install in development mode (editable)
  --skip-llm          Skip LLM provider setup
  --with-cli          Install CLI dependencies (rich, prompt_toolkit)
  --venv PATH         Custom virtual environment path

Environment Variables:
  PYTHON_CMD          Override Python command (default: python3)
  SEAA_SKIP_TESTS     Skip running tests after installation
  SEAA_SKIP_VENV      Skip virtual environment creation (use system Python)

Examples:
  ./install.sh                    # Standard installation
  ./install.sh --dev              # Development installation
  ./install.sh --with-cli         # Include interactive CLI
  ./install.sh --skip-llm         # Use existing LLM config

EOF
}

check_python() {
    print_info "Checking Python version..."

    # Try different Python commands
    local python_cmd=""
    for cmd in python3 python; do
        if command -v "$cmd" &> /dev/null; then
            local version=$("$cmd" -c 'import sys; print(".".join(map(str, sys.version_info[:2])))' 2>/dev/null || echo "0.0")
            if (( $(echo "$version >= $PYTHON_MIN_VERSION" | bc -l) )); then
                python_cmd="$cmd"
                break
            fi
        fi
    done

    if [ -z "$python_cmd" ]; then
        print_error "Python $PYTHON_MIN_VERSION+ not found"
        echo "  Install from: https://www.python.org/downloads/"
        exit 1
    fi

    local version=$("$python_cmd" --version 2>&1 | awk '{print $2}')
    print_success "Found Python $version"

    # Export for use in script
    export PYTHON_CMD="${PYTHON_CMD:-$python_cmd}"
}

setup_venv() {
    if [ "$SEAA_SKIP_VENV" = "1" ]; then
        print_warning "Skipping virtual environment (using system Python)"
        return 0
    fi

    print_info "Setting up virtual environment at $VENV_DIR..."

    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists"
        read -p "  Recreate it? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_DIR"
        else
            print_info "Using existing virtual environment"
            return 0
        fi
    fi

    "$PYTHON_CMD" -m venv "$VENV_DIR"
    print_success "Virtual environment created"

    # Export activation command
    source "$VENV_DIR/bin/activate"
    export PYTHON_CMD="${VENV_DIR}/bin/python"
}

install_dependencies() {
    print_header "Installing Dependencies"

    print_info "Upgrading pip, setuptools, wheel..."
    "$PYTHON_CMD" -m pip install --upgrade pip setuptools wheel > /dev/null 2>&1
    print_success "Pip upgraded"

    # Core dependencies
    print_info "Installing core dependencies..."
    local core_deps=(
        "pyyaml>=6.0"
        "pydantic>=2.0"
        "watchdog>=3.0"
    )

    for dep in "${core_deps[@]}"; do
        "$PYTHON_CMD" -m pip install "$dep" > /dev/null 2>&1
        print_success "Installed $dep"
    done

    # CLI dependencies (optional)
    if [ "$CLI_DEPS" = true ]; then
        print_info "Installing CLI dependencies..."
        local cli_deps=(
            "rich>=13.0"
            "prompt-toolkit>=3.0"
        )

        for dep in "${cli_deps[@]}"; do
            "$PYTHON_CMD" -m pip install "$dep" > /dev/null 2>&1
            print_success "Installed $dep"
        done
    fi

    # Development dependencies
    if [ "$DEV_MODE" = true ]; then
        print_info "Installing development dependencies..."
        local dev_deps=(
            "pytest>=7.0"
            "pytest-cov>=4.0"
            "black>=23.0"
            "flake8>=6.0"
            "mypy>=1.0"
        )

        for dep in "${dev_deps[@]}"; do
            "$PYTHON_CMD" -m pip install "$dep" > /dev/null 2>&1
            print_success "Installed $dep"
        done
    fi
}

install_seaa() {
    print_header "Installing SEAA"

    cd "$SEAA_HOME"

    if [ "$DEV_MODE" = true ]; then
        print_info "Installing SEAA in editable mode..."
        "$PYTHON_CMD" -m pip install -e . > /dev/null 2>&1
    else
        print_info "Installing SEAA..."
        "$PYTHON_CMD" -m pip install . > /dev/null 2>&1
    fi

    print_success "SEAA installed"
}

setup_llm() {
    if [ "$SKIP_LLM" = true ]; then
        print_warning "Skipping LLM setup (using existing config)"
        return 0
    fi

    print_header "LLM Provider Setup"

    echo -e "Choose LLM provider:"
    echo -e "  1) Ollama (local, recommended for development)"
    echo -e "  2) Google Gemini (cloud, requires API key)"
    echo -e "  3) Skip (use existing config)"

    read -p "Enter choice (1-3): " -n 1 -r
    echo

    case $REPLY in
        1)
            configure_ollama
            ;;
        2)
            configure_gemini
            ;;
        3)
            print_warning "Using existing config"
            ;;
        *)
            print_error "Invalid choice"
            setup_llm
            ;;
    esac
}

configure_ollama() {
    print_info "Ollama Configuration"
    echo -e "  1. Install Ollama from https://ollama.ai"
    echo -e "  2. Run: ollama run qwen2.5-coder:14b"
    echo -e "  3. This script will configure SEAA to use it"

    read -p "Press Enter when Ollama is running (or Ctrl+C to skip)..."

    if command -v curl &> /dev/null; then
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            print_success "Ollama is running"
            # config.yaml already defaults to Ollama
            print_info "Updated config.yaml for Ollama (default)"
        else
            print_warning "Ollama not accessible at localhost:11434"
            echo "  Make sure Ollama is running: ollama serve"
        fi
    else
        print_warning "curl not found, skipping Ollama verification"
    fi
}

configure_gemini() {
    print_info "Google Gemini Configuration"
    echo -e "  1. Get API key from https://aistudio.google.com/app/apikeys"
    echo -e "  2. Set environment variable: export GOOGLE_API_KEY=your_key"
    echo -e "  3. Or add to .env file (will be created)"

    read -p "Enter your Google API key (or press Enter to skip): " api_key

    if [ -n "$api_key" ]; then
        echo "GOOGLE_API_KEY=$api_key" > "$SEAA_HOME/.env"
        print_success "Saved API key to .env"
    else
        print_warning "Skipped API key configuration"
    fi
}

verify_installation() {
    print_header "Verifying Installation"

    cd "$SEAA_HOME"

    # Check imports
    print_info "Checking imports..."
    if "$PYTHON_CMD" -c "from seaa.kernel import Genesis; from seaa.core.config import config" 2>/dev/null; then
        print_success "Core imports working"
    else
        print_error "Core imports failed"
        return 1
    fi

    # Check CLI (if installed)
    if [ "$CLI_DEPS" = true ]; then
        print_info "Checking CLI..."
        if "$PYTHON_CMD" -c "from seaa.cli import run_interactive" 2>/dev/null; then
            print_success "CLI imports working"
        else
            print_warning "CLI imports failed (optional)"
        fi
    fi

    # Check DNA
    print_info "Checking DNA state..."
    if [ -f "$SEAA_HOME/dna.json" ]; then
        print_success "DNA found at dna.json"
    else
        print_warning "DNA not initialized (will be created on first run)"
    fi

    # Check identity
    print_info "Checking identity..."
    if [ -f "$SEAA_HOME/.identity.json" ]; then
        local identity_name=$("$PYTHON_CMD" -c "import json; print(json.load(open('.identity.json'))['name'])" 2>/dev/null || echo "unknown")
        print_success "Instance identity: $identity_name"
    else
        print_warning "Identity not yet created (will be created on first run)"
    fi
}

run_tests() {
    if [ "$SEAA_SKIP_TESTS" = "1" ]; then
        print_warning "Skipping tests"
        return 0
    fi

    if ! command -v pytest &> /dev/null; then
        print_warning "pytest not installed, skipping tests"
        return 0
    fi

    print_header "Running Tests"

    cd "$SEAA_HOME"

    if "$PYTHON_CMD" -m pytest tests/ -v --tb=short 2>/dev/null; then
        print_success "All tests passed"
    else
        print_warning "Some tests failed (installation may still work)"
    fi
}

show_next_steps() {
    print_header "Installation Complete! 🎉"

    echo -e "Next steps:\n"

    if [ "$SEAA_SKIP_VENV" != "1" ]; then
        echo -e "${BLUE}1. Activate virtual environment:${NC}"
        echo -e "   source ${VENV_DIR}/bin/activate\n"
    fi

    echo -e "${BLUE}2. Start the agent:${NC}"
    echo -e "   python3 main.py\n"

    echo -e "${BLUE}3. Interactive mode:${NC}"
    echo -e "   python3 main.py -i\n"

    echo -e "${BLUE}4. Check system health:${NC}"
    echo -e "   python3 main.py status\n"

    echo -e "${BLUE}5. View commands:${NC}"
    echo -e "   python3 main.py --help\n"

    if [ "$SKIP_LLM" = true ]; then
        echo -e "${YELLOW}Note: LLM setup was skipped. Make sure your LLM provider is configured in config.yaml${NC}\n"
    fi

    echo -e "${GREEN}Documentation:${NC}"
    echo -e "   - Quick Start: cat QUICK_START.md"
    echo -e "   - Architecture: cat ARCHITECTURE_FINAL.md"
    echo -e "   - All Docs: cat DOCUMENTATION_INDEX.md\n"
}

#============================================================================
# Main Script
#============================================================================

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help)
                show_help
                exit 0
                ;;
            --dev)
                DEV_MODE=true
                shift
                ;;
            --skip-llm)
                SKIP_LLM=true
                shift
                ;;
            --with-cli)
                CLI_DEPS=true
                shift
                ;;
            --venv)
                VENV_DIR="$2"
                shift 2
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    print_header "SEAA Installation"
    print_info "This script will install the Self-Evolving Autonomous Agent"
    echo -e "Location: ${BLUE}${SEAA_HOME}${NC}\n"

    # Checks
    check_python

    # Setup
    setup_venv
    install_dependencies
    install_seaa
    setup_llm

    # Verification
    verify_installation
    run_tests
    show_next_steps
}

main "$@"
