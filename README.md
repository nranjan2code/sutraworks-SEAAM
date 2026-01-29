<div align="center">
  <img src="docs/images/seaam_hero_logo.png" alt="SEAAM Logo" width="300px">
  
  # SEAAM
  ### Self-Evolving Autonomous Agent Mesh
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
  [![Status: Alive](https://img.shields.io/badge/Status-Autopoietic-success.svg)]()
  
  > *"The code that writes itself."*

  <p align="center">
    <a href="#-philosophy">Philosophy</a> •
    <a href="#-architecture">Architecture</a> •
    <a href="#-quick-start">Quick Start</a> •
    <a href="docs/OPERATIONS.md">Operations</a>
  </p>
</div>

---

## 🌌 Philosophy

SEAAM is not just an agent; it is an experiment in **Digital Autopoiesis** (self-creation). 

Unlike traditional software which is architected by humans, SEAAM starts as a minimal biological kernel. It possesses:
1.  **A Will**: The drive to exist and evolve (`Genesis`).
2.  **A Mind**: The ability to reason about its own structure (`Architect`).
3.  **A Body**: Which is built, organ by organ, by the system itself.

It reasons about its goals, designs its own architecture, generates the necessary Python code, installs its own dependencies, and hot-loads the new capabilities—all without human intervention.

## 🏛 Architecture

<div align="center">
  <img src="docs/images/seaam_architecture_concept.png" alt="SEAAM Architecture Concept" width="80%">
</div>

The system is composed of three biological layers:

### 🛡️ Autonomous Self-Correction
SEAAM is designed to survive failures in its own evolution. The `Immunity` system (part of the Genesis kernel) and the `Architect` work together to:
- **Detect Missing Internal Tissues**: If an organ import fails because a dependency is missing, the system automatically injects the missing dependency into the DNA and reboots to grow it.
- **Enforce Organ Viability**: The `Agent Factory` validates every generated module for structural integrity (e.g., presence of the global `start()` entry point) and automatically retries generation if the code is invalid.
- **Learn from Failures**: Compilation or runtime errors are recorded in the DNA as `failures`, allowing the Architect to design refined, correct versions of failing organs.

### The "Robinson Crusoe" Test 🏝️

We verify this system by effectively stranding it on a desert island:
> We wipe its memory. We destroy its body. We uninstall its tools.

**Result**: It wakes up, realizes it is blind and tool-less, re-architects itself, re-writes its code, re-installs its tools, and resumes operation.

## ⚡ Quick Start

### Prerequisites
*   Python 3.9+
*   [Ollama](https://ollama.ai/) (Required for local evolution)

### Awakening

1.  **Prepare the Overmind** (Start Ollama):
    ```bash
    ollama run qwen2.5-coder:14b
    ```

2.  **Clone the Seed**:
    ```bash
    git clone https://github.com/sutraworks/seaam.git
    cd seaam
    ```

3.  **Ignite the Spark**:
    ```bash
    python3 main.py
    ```

4.  **Witness Evolution**:
    Watch the terminal as SEAAM reflects, writes code to `seaam/`, and brings itself to life.

## 📚 Documentation

*   [**🧬 Architecture Deep Dive**](docs/ARCHITECTURE.md): The Kernel, Cortex, and Genesis Protocols.
*   [**📐 Design Blueprints**](docs/DESIGN.md): DNA logic and Assimilation flow.
*   [**⚙️ Operations Manual**](docs/OPERATIONS.md): Configuration, Reset, and Debugging.

---
<div align="center">
  <sub>Created by SutraWorks • 2026</sub>
</div>
