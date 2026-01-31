# SEAA Installation Guide

Self-Evolving Autonomous Agent - Easy setup for any system.

## Quick Start (Recommended)

### 1. One-Command Installation

```bash
# Clone or download the repository
git clone https://github.com/sutraworks/seaa.git
cd seaa

# Run the installation script
./install.sh
```

The script will:
- Check Python version (3.9+)
- Create a virtual environment
- Install dependencies
- Set up LLM provider (Ollama or Gemini)
- Verify installation
- Run tests

### 2. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 3. Start the Agent

```bash
python3 main.py
```

## Manual Installation

If you prefer to install manually:

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- LLM provider (Ollama or Google Gemini)

### Step 1: Clone Repository

```bash
git clone https://github.com/sutraworks/seaa.git
cd seaa
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

**Core only:**
```bash
pip install -r requirements.txt
```

**With CLI (interactive mode):**
```bash
pip install -r requirements.txt
pip install rich prompt-toolkit
```

**Development:**
```bash
pip install -r requirements-dev.txt
```

### Step 4: Install SEAA

```bash
# Standard installation
pip install .

# OR development mode (editable):
pip install -e .
```

## LLM Provider Setup

### Option A: Ollama (Local, Recommended for Development)

1. **Install Ollama**: https://ollama.ai

2. **Download model**:
   ```bash
   ollama pull qwen2.5-coder:14b
   ```

3. **Start Ollama**:
   ```bash
   ollama serve
   ```

4. **SEAA is pre-configured** for Ollama at `http://localhost:11434`

### Option B: Google Gemini (Cloud)

1. **Get API Key**: https://aistudio.google.com/app/apikeys

2. **Set environment variable**:
   ```bash
   export GOOGLE_API_KEY=your_key_here
   ```

3. **Or create .env file**:
   ```bash
   echo "GOOGLE_API_KEY=your_key_here" > .env
   ```

4. **Update config.yaml**:
   ```yaml
   llm:
     provider: gemini
     model: gemini-1.5-flash
   ```

### Option C: Custom LLM Provider

Edit `config.yaml`:
```yaml
llm:
  provider: custom
  model: your_model
  custom_url: http://your_llm_endpoint/api/generate
```

## Installation Options

### Development Installation

```bash
./install.sh --dev
```

Includes:
- pytest for testing
- black, flake8, mypy for code quality
- Additional development tools

### Minimal Installation (Skip LLM Setup)

```bash
./install.sh --skip-llm
```

Use when:
- LLM is already configured
- You only want to query system state
- Testing without LLM interaction

### Custom Virtual Environment Path

```bash
./install.sh --venv /path/to/custom/venv
```

### With CLI (Interactive Mode)

```bash
./install.sh --with-cli
```

Installs additional dependencies:
- rich (terminal UI)
- prompt-toolkit (interactive REPL)

## Environment Variables

### Install Script Variables

```bash
# Use specific Python command
PYTHON_CMD=python3.11 ./install.sh

# Skip virtual environment (use system Python)
SEAA_SKIP_VENV=1 ./install.sh

# Skip tests after installation
SEAA_SKIP_TESTS=1 ./install.sh
```

### Runtime Variables

```bash
# Ollama endpoint
OLLAMA_URL=http://custom-host:11434/api/generate

# Google Gemini API key
GOOGLE_API_KEY=your_key

# Log level
SEAA_LOG_LEVEL=DEBUG

# Config file location
SEAA_CONFIG=./custom-config.yaml
```

## Verification

### Check Installation

```bash
# System status
python3 main.py status

# List organs
python3 main.py organs

# Show identity
python3 main.py identity

# View configuration
cat config.yaml
```

### Run Tests

```bash
# Activate virtual environment first
source venv/bin/activate

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=seaa --cov-report=html
```

## Troubleshooting

### Python Version Error

```
Python 3.9+ not found
```

**Solution**: Install Python 3.9 or higher from https://www.python.org

### Virtual Environment Issues

```bash
# Recreate virtual environment
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### LLM Not Accessible

```
Error: Cannot reach LLM provider
```

**For Ollama**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve
```

**For Gemini**:
```bash
# Verify API key
echo $GOOGLE_API_KEY

# Check config
grep provider config.yaml
```

### Permission Denied on install.sh

```bash
chmod +x install.sh
./install.sh
```

### Import Errors

```
ModuleNotFoundError: No module named 'seaa'
```

**Solution**:
```bash
# Make sure you're in virtual environment
source venv/bin/activate

# Reinstall SEAA
pip install -e .
```

## Next Steps

After installation:

1. **Interactive Mode**:
   ```bash
   python3 main.py -i
   ```

2. **Read Documentation**:
   ```bash
   cat QUICK_START.md
   cat ARCHITECTURE_FINAL.md
   ```

3. **Check Health**:
   ```bash
   python3 main.py status
   ```

4. **Watch Evolution**:
   ```bash
   python3 main.py watch
   ```

## Platform-Specific Notes

### macOS

- Use `python3` command (not `python`)
- May need to accept Xcode command line tools
- If using Ollama, ensure Docker Desktop is running

### Linux

- Works on Ubuntu, Debian, Fedora, CentOS
- Some systems may need `python3-venv`: `sudo apt-get install python3-venv`
- Ollama supports native installation

### Windows

- Use Windows Subsystem for Linux (WSL2) recommended
- Or use Git Bash for bash commands
- Activate venv with: `venv\Scripts\activate`
- Use python instead of python3

## Getting Help

- **Issues**: https://github.com/sutraworks/seaa/issues
- **Documentation**: See DOCUMENTATION_INDEX.md
- **Quick Start**: See QUICK_START.md
- **Architecture**: See ARCHITECTURE_FINAL.md

## Uninstallation

```bash
# Remove virtual environment
rm -rf venv/

# Remove SEAA package
pip uninstall seaa

# Clean up (optional)
rm -rf .dna_backups/
rm dna.json
rm .identity.json
```

## What's Installed

After installation, you'll have:

| Component | Location | Purpose |
|-----------|----------|---------|
| Core kernel | `seaa/kernel/` | Immutable system core |
| Configuration | `seaa/core/`, `seaa/cortex/` | Logging, config, prompts |
| CLI tools | `seaa/cli/` | Interactive REPL |
| Core organs | `soma/` | Perception, memory, interface |
| Configuration | `config.yaml` | System settings |
| Tests | `tests/` | Unit and integration tests |
| Documentation | `*.md` | Architecture, guides |

