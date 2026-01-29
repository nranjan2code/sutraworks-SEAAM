# SEAAM: Self-Evolving Autonomous Agent Mesh

> "The code that writes itself."

SEAAM is an experimental AI substrate designed to be **Autopoietic** (self-creating). Starting from a minimal immutable kernel, it reasons about its goals, designs its own architecture, generates the necessary Python code, installs its own dependencies, and hot-loads the new capabilities—all without human intervention.

## 🚀 Key Features

*   **Tabula Rasa Evolution**: Can rebuild its entire body (Perception, Memory, Interface) from a blank JSON manifest.
*   **The Genesis Loop**: A continuous OODA loop (Observe-Orient-Decide-Act) applied to source code generation.
*   **Immunity System**: Detects runtime `ImportError`, auto-installs missing PyPI packages, and self-reboots.
*   **The Nervous System**: A global Event Bus that allows evolved organs to communicate and coordinate actions.
*   **Evolutionary Feedback**: The system learns from runtime failures (e.g., buggy code), feeding errors back to the Architect to trigger self-correction cycles.
*   **The Architect**: An internal agent that recursively modifies the system's blueprints based on high-level persistent goals.

## 📂 Documentation

*   [**Architecture**](docs/ARCHITECTURE.md): The Kernel, Cortex, and Genesis Protocols.
*   [**Design**](docs/DESIGN.md): DNA Blueprints and Assimilation logic.
*   [**Operations**](docs/OPERATIONS.md): How to run, configure, and reset the system.

## ⚡ Quick Start

1.  **Install Ollama** and pull the coding model:
    ```bash
    ollama pull qwen2.5-coder:14b
    ```

2.  **Clone & Run**:
    ```bash
    git clone https://github.com/your-repo/seaam.git
    cd seaam
    python3 main.py
    ```

3.  **Watch it Grow**:
    The system will immediately begin writing files to `seaam/perception`, `seaam/memory`, etc.
    Eventually, it will launch a dashboard (usually at `http://localhost:8501`).

## 🧠 The "Robinson Crusoe" Test

We verify this system by effectively stranding it on a desert island:
1.  We wipe its memory (`dna.json`).
2.  We destroy its body (delete all sub-modules).
3.  We uninstall its tools (`pip uninstall streamlit watchdog`).

**Result**: It wakes up, realizes it is blind and tool-less, re-architects itself, re-writes its code, re-installs its tools, and resumes operation.

---
*Created by SutraWorks - January 2026*
