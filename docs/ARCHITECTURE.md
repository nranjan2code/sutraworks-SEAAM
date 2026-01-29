# 🧬 System Architecture

SEAAM is fundamentally different from traditional software architectures. Instead of a static codebase, it is a dynamic biological system designed to grow and heal.

## 🗺 High-Level Map

```mermaid
graph TD
    User((User)) -->|Queries| Interface[Interface Organ]
    Interface -->|Events| Bus[Nervous System]
    Bus -->|Events| Cortex[Cortex / Memory]
    
    subgraph KERNEL [The Immutable Soul]
        Genesis[Genesis Cycle]
        Bus
    end
    
    subgraph CORTEX [The Mind]
        Architect[Architect] -->|Reflects| DNA[(DNA.json)]
        Architect -->|Designs| Blueprints
    end
    
    subgraph SOMA [The Body]
        Perception
        Memory
        Interface
    end
    
    Genesis -->|Reads| DNA
    Genesis -->|Builds| SOMA
    Blueprints -.->|Guide| Genesis
```

## 1. The Kernel (Immutable)
The Kernel is the only "hard-coded" part of the system. It enables life but does not dictate form.

### `seaam.kernel.genesis`
The "Will to Live". This is the main loop.
- **Awakening**: Loads DNA, initializes the Architect.
- **Evolution**: Asks Architect for blueprints, uses Gateway to generate code.
- **Assimilation**: Hot-loads the new Python modules (`active_modules`).
- **Metabolic Loop**: Once awake, the system enters a continuous loop where it periodically reconsider its goals, evolves new organs, and hot-loads them *while the system is running*.
- **Immunity**: If a module crashes due to missing libraries, Genesis installs them via `pip` and reboots. For internal `seaam` dependencies, it adds them to the blueprint.

### `seaam.connectors.llm_gateway`
The "Voice of God".
- **LLM Abstraction**: Connects to Ollama or Gemini.
- **Code Validation**: Every generated organ is validated for the mandatory `start()` entry point.
- **Auto-Retry**: If the LLM generates invalid code, the Gateway rejects it and re-prompts the LLM with the specific error (e.g., "Missing start() function").

## 2. The Cortex (The Mind)
### `seaam.cortex.architect`
 The intelligent agent responsible for system design.
- **Reflect**: Looks at `failures` and `goals` in `dna.json`.
- **Design**: Generates a JSON implementation plan (Thought) for the next necessary module.
- **Example Thought**:
  ```json
  {
    "module_name": "seaam.perception.file_watcher",
    "description": "A module that uses watchdog to monitor..."
  }
  ```

## 3. The Soma (The Body)
These are **not present** at start. They are written by the system itself.
Common evolved organs include:
- `soma.perception.observer`: Watches the filesystem.
- `soma.memory.journal`: Logs events to a database or file.
- `soma.interface.dashboard`: A Streamlit or Terminal UI.

## 4. The Nervous System (Synaptic Bus)
The `seaam.kernel.bus` is the connective tissue. Organs do not call each other directly; they communicate via events:
- **`bus.publish(event_name, data)`**: Fires a signal.
- **`bus.subscribe(event_name, callback)`**: Listens for a signal.
This decoupling allows the system to add or remove organs (e.g. swap a Voice Speaker for a Dashboard) without breaking the core logic.
