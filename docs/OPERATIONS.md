# ⚙️ Operations Manual

How to operate, configure, and maintain the SEAAM system.

## 🚀 Running the System

### 1. Requirements 📋
Ensure you have the following installed:
*   [Python 3.9+](https://www.python.org/getit/)
*   [Ollama](https://ollama.ai/) (Mac/Linux)

### 2. Environment Setup 🛠️
```bash
# Clone the repository
git clone https://github.com/sutraworks/seaam.git
cd seaam /Users/nisheethranjan/Projects/sutraworks-SEAAM

# Install dependencies (Minimal)
pip install -r requirements.txt
```

### 3. Ignition 🔥
```bash
# Start Ollama (in a separate terminal)
ollama run qwen2.5-coder:14b

# Start SEAAM
python3 main.py
```

---

## 🛑 Resetting the System (The "Robinson Crusoe" Protocol)

If you want to watch the system rebuild itself from scratch, perform a **hard reset**.

> ⚠️ **WARNING**: This will delete all evolved code and memory!

```bash
# 1. Stop the running process (Ctrl+C)

# 2. Delete the Body (Evolved Organs)
rm -rf seaam/perception seaam/memory seaam/interface seaam/behavior

# 3. Wipe the Mind (DNA) - KEEP THE FILE, CLEAR THE CONTENT
echo '{ "system_version": "0.0.1", "system_name": "SEAAM-TabulaRasa", "blueprint": {}, "goals": ["I must be able to perceive the file system.", "I must have a memory.", "I must have a visual dashboard."], "active_modules": [], "failures": [] }' > dna.json

# 4. Uninstall Tools (Optional, to text immunity)
pip uninstall watchdog streamlit
```

When you restart `python3 main.py`, the system will detect the damage and begin repairs immediately.

---

## 🕵️ Troubleshooting

### `[ARCHITECT] Failed to structure thought`
*   **Cause**: The LLM is outputting bad JSON or conversational text.
*   **Fix**: Ensure `seaam/connectors/llm_gateway.py` has the markdown cleaning fix (v0.0.2+).

### `[GATEWAY] Validation FAILED`
*   **Cause**: The LLM failed to include a `start()` function in the generated code after 3 retries.
*   **Fix**: Check `seaam/connectors/llm_gateway.py`. The LLM might be struggling with the prompt. Try switching to a more capable model (e.g., `qwen2.5-coder:14b`) or check the `_construct_prompt` for errors.

### `[ASSIMILATION] Rejected: Missing global start() function`
*   **Cause**: The module was imported successfully but does not have the standardized entry point.
*   **Fix**: This failure is reported to the DNA automatically. The Architect will attempt to redesign the organ in the next metabolic cycle. 
