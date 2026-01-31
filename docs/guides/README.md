# Getting Started Guides

Step-by-step guides to install and use SEAA.

## Files

### [INSTALL.md](INSTALL.md)
**Complete installation guide** (Start here!)
- One-command installation: `./install.sh`
- Manual installation steps
- LLM provider setup (Ollama, Gemini, custom)
- Troubleshooting & platform-specific notes
- Environment variables reference

### [QUICK_START.md](QUICK_START.md)
**Quick 5-minute start**
- Installation
- Running the agent
- Basic commands
- Common tasks

### [START_HERE.md](START_HERE.md)
**Recommended learning path**
- What to read first
- How to navigate docs
- How to get help

## Installation Options

### For Users
```bash
./install.sh
```

### For Developers
```bash
./install.sh --dev
```

### With CLI (Interactive Mode)
```bash
./install.sh --with-cli
```

### Manual pip Installation
```bash
pip install -r requirements.txt
pip install .
```

## After Installation

1. **Check Health**: `python3 main.py status`
2. **List Organs**: `python3 main.py organs`
3. **Interactive Mode**: `python3 main.py -i`
4. **View Commands**: `python3 main.py --help`

## Next Steps

- Architecture details: [docs/architecture/](../architecture/)
- Design & implementation: [docs/design/](../design/)
- Status & evolution: [docs/evolution/](../evolution/)
