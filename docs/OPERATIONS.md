# SEAAM Operations Guide

## Prerequisites

*   **Python 3.9+**
*   **Ollama**: Installed and running (`ollama serve`).
*   **Model**: `qwen2.5-coder:14b` (Recommended).
    ```bash
    ollama pull qwen2.5-coder:14b
    ```

## Environment Variables

| Variable | Description | Default |
| :--- | :--- | :--- |
| `OLLAMA_URL` | URL of the Ollama API | `http://localhost:11434/api/generate` |
| `OLLAMA_MODEL` | Model to use for code/reasoning | `qwen2.5-coder:14b` |
| `GEMINI_API_KEY`| (Optional) Fallback cloud provider | `None` |

## Running the System

To start the Genesis Loop:

```bash
python3 main.py
```

## What to Expect

1.  **Awakening**: You will see logs indicating the system is starting.
2.  **Reflection**: The Architect will pause to "think".
3.  **Generation**: Files will be created in `seaam/` in real-time.
4.  **Self-Healing**: You may see the system **restart** abruptly. This is normal; it likely installed a dependency (like `streamlit` or `watchdog`).
5.  **Dashboard**: Once evolved, a web dashboard will be available (usually `http://localhost:8501` for Streamlit or `:5000` for Flask).

## Resetting (The "Robinson Crusoe" Scenario)

To verify the system's ability to rebuild from scratch:

```bash
# 1. Kill the loop
pkill -f main.py

# 2. Upload "Tabula Rasa" DNA (Goals only, no blueprints/active modules)
echo '{
  "system_version": "0.0.1",
  "system_name": "SEAAM-TabulaRasa",
  "blueprint": {},
  "goals": [
    "I must be able to perceive the file system to understand the user's project.",
    "I must have a memory of past events to learn from mistakes.",
    "I must have a visual dashboard to communicate my state to the user."
  ],
  "active_modules": [],
  "failures": []
}' > dna.json

# 3. Wipe the Body (delete generated modules)
rm -rf seaam/perception seaam/memory seaam/interface seaam/voice seaam/behavior

# 4. Sabotage Environment (Optional)
# pip uninstall streamlit watchdog pyttsx3 espeak-ng

# 5. Run the Second Genesis
python3 main.py
```
