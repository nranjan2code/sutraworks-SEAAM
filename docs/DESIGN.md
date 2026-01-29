# SEAAM System Design

## The System DNA (`dna.json`)

The heart of SEAAM is its "Genetic Code". This file is the single source of truth for what the system *believes* it is.

```json
{
  "system_version": "0.0.1",
  "system_name": "SEAAM-Genesis",
  "blueprint": {
    "seaam.perception.observer": "Description of the module logic...",
    "seaam.interface.dashboard": "Description of the dashboard..."
  },
  "active_modules": [
    "seaam.perception.observer"
  ]
}
```


*   **Blueprint**: A dictionary of `"module.path": "Description"`. The Architect writes to this.
*   **Active Modules**: A list of modules that have been successfully built and likely assimilated.
*   **Failures**: A registry of runtime errors (e.g., "Missing start()"). Used by the Architect to self-correct.

## The Architect (Decision Engine)

The Architect does not know *how* to code. It only knows *what* is needed.
It uses a recursive prompt loop:
1.  **Review**: Checks `failures` list. If valid, prioritized fixing them.
2.  **Reflect**: "My goal is [X]. My blueprint has [Y]. What is missing?"
3.  **Decide**: "I need [Z]."
4.  **Update**: Writes [Z] to `dna.json`.

This separation of concerns (Architect = Design, Genesis = Build) allows the system to be extremely flexible.

## The Nervous System (Connectivity)

To avoid "Organs in a Jar" (isolated code), SEAAM uses a global Event Bus.
*   **Observer**: Publishes events (e.g., `file_modified`).
*   **Cortex/Reflex**: Subscribes to events.
*   **Effectors**: Act on events.

This allows the system to exhibit complex, coordinated behaviors without tight coupling.

## The Connector (LLM Gateway)

The `ProviderGateway` abstracts the AI model.
*   **Default**: Ollama (`qwen2.5-coder:14b`) - Optimized for local, private, gratuitous code generation.
*   **Fallback**: Google Gemini (`gemini-1.5-flash`) - For high-reasoning tasks if enabled.

## Self-Healing Design

The system assumes code generation is imperfect and dependencies are unknown.
*   **Import Traps**: Usage of `try/except ImportError` blocks around dynamic imports.
*   **subprocess pip**: Direct usage of pip to satisfy requirements at runtime.
*   **Feedback Loops**: Runtime failures (AttributeError, etc.) are caught and fed back to the design phase.
*   **Process Replacement**: Using `os.execv` ensures a clean state without memory leaks or stale modules.
