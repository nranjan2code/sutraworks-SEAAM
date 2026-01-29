# SEAAM Architecture

The **Self-Evolving Autonomous Agent Mesh (SEAAM)** is a recursive, bio-mimetic software substrate designed to achieve operational autonomy through continuous self-improvement.

## The Layered Topology

The system is organized into concentric layers of responsibility, mimicking a biological organism.

### Level 0: The Immutable Kernel (Substrate)
**Location**: `seaam/kernel/`
*   **Role**: The "Brain Stem". It is the only part of the system that is manually written and immutable (mostly).
*   **Protocols**:
    *   **Genesis**: The logic for bootstrapping the system from a DNA blueprint.
    *   **Assimilation**: The ability to dynamically load, instantiate, and execute Python modules generated at runtime.
    *   **Immunity**: The self-healing mechanism that detects `ImportError`, installs missing dependencies (via `pip`), and restarts the process.
    *   **The Bus**: A global Event Bus (Nervous System) allowing decoupled modules to act and react to stimuli.

### Level 1: The Cognition Mesh (Cortex)
**Location**: `seaam/cortex/`
*   **Role**: The "Mind".
*   **Component**: `Architect`
*   **Function**: Recursively analyzes the system's state against high-level goals. It does not write code; it writes **Blueprints**. It modifies the `dna.json` to reflect what the system *needs* to become.
*   **Learning**: It reads runtime failures from the DNA to correct faulty blueprints in the next cycle.

### Level 2: The Sensory Peripheral (Perception)
**Location**: `seaam/perception/` (Generated)
*   **Role**: The "Senses".
*   **Function**: Observes the environment and publishes events to the **Bus**.
*   **Standard Module**: `Observer` (FileSystemWatcher) - Allows the system to react to file changes.

### Level 3: The Evolutionary Registry (Memory)
**Location**: `seaam/memory/` (Generated)
*   **Role**: The "Memory".
*   **Function**: Persists state.
*   **Standard Module**: `Journal` - Logs events to `events.log`.

### Level 4: The Interface (Skin)
**Location**: `seaam/interface/` (Generated)
*   **Role**: The "Face".
*   **Standard Module**: `Dashboard` - A web interface (Flask/Streamlit) to visualize the internal state (`dna.json`, logs).

### Level 5: The Action Layer (Behaviors)
**Location**: `seaam/behavior/` (Generated)
*   **Role**: The "Reflexes".
*   **Function**: Subscribes to the **Bus** and triggers actions (Voice, API calls, etc.).

---

## The Protocols

### 1. The Genesis Loop (Autopoiesis)
1.  **Awakening**: The Kernel starts.
2.  **Reflection**: The `Architect` consults the LLM to identify gaps between "Goals" and "Current DNA". It also reviews **Failures** to fix broken code.
3.  **Mutation**: The `Architect` adds a new module requirement or updates an existing blueprint in `dna.json`.
4.  **Materialization**: The `Genesis` engine detects the new requirement, asks the LLM for implementation, and writes the code to disk.
5.  **Assimilation**: The Kernel imports the new module and spins it up.

### 2. The Immunity Protocol
1.  **Detection**: The Kernel detects an `ImportError` during Assimilation.
2.  **Identification**: It parses the error to find the missing package name.
3.  **Intervention**: It runs `pip install <package>`.
4.  **Reincarnation**: It executes `os.execv` to restart the entire process, reloading the environment.

### 3. The Evolutionary Feedback Loop
1.  **Failure**: A generated module crashes or fails a contract (e.g., missing `start()` function).
2.  **Reporting**: `Genesis` catches the error and writes it to the `failures` list in `dna.json`.
3.  **Learning**: On the next cycle, the `Architect` reads the failure.
4.  **Correction**: The `Architect` refines the blueprint with specific fix instructions.
5.  **Regeneration**: `Genesis` rebuilds the module.
