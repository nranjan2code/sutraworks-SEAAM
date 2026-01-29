import os
import requests
import json

class ProviderGateway:
    """
    The Voice of the System. 
    Connects to an LLM provider (Ollama or Gemini) to generate code based on blueprints.
    """
    def __init__(self):
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
        self.ollama_model = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:14b") # Great for coding tasks

    def generate_code(self, module_name, description):
        """
        Asks the LLM to write a Python module based on the description.
        Prioritizes Ollama if available, otherwise falls back to Gemini.
        """
        # Try Ollama first (User Preference)
        code = self._generate_ollama(module_name, description)
        if code:
            return code

        # Fallback to Gemini
        if self.gemini_key:
            return self._generate_gemini(module_name, description)
            
        print("CRITICAL: No active LLM provider found. Ensure Ollama is running or GEMINI_API_KEY is set.")
        return None

    def think(self, prompt):
        """
        Used for non-code generation (e.g. Architect thoughts).
        Bypasses code cleaning and validation.
        """
        data = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.5} # More creative reflection
        }
        
        try:
            print(f"[GATEWAY] Contacting Ollama ({self.ollama_model}) [THOUGHT]...")
            response = requests.post(self.ollama_url, json=data)
            response.raise_for_status()
            result = response.json()
            return result['response']
        except Exception as e:
            print(f"[GATEWAY] Ollama unreachable: {e}")
            return None
    def _generate_ollama(self, module_name, description):
        prompt = self._construct_prompt(module_name, description)
        
        data = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1 # Precise code generation
            }
        }
        
        # RETRY LOOP: Enforce viability
        max_retries = 3
        current_try = 0
        
        while current_try < max_retries:
            try:
                print(f"[GATEWAY] Contacting Ollama ({self.ollama_model}) [Attempt {current_try+1}/{max_retries}]...")
                response = requests.post(self.ollama_url, json=data)
                response.raise_for_status()
                result = response.json()
                code = self._clean_code(result['response'])
                
                # VALIDATION: Must have start() (Only for actual organs)
                if module_name != "ARCHITECT_THOUGHT":
                    if "def start():" not in code and "def start(self):" not in code:
                         print(f"[GATEWAY] Validation FAILED for {module_name}: Missing 'def start():'. Retrying...")
                         current_try += 1
                         # Feed the error back to the LLM
                         data["prompt"] += "\n\nCRITICAL ERROR: The code you wrote is MISSING the global 'def start():' function. You MUST include 'def start():' at the end of the file. Rewrite the code now."
                         continue
                
                return code                
            except Exception as e:
                print(f"[GATEWAY] Ollama unreachable: {e}")
                return None
        
        print("[GATEWAY] Failed to generate viable organ after retries.")
        return None

    def _generate_gemini(self, module_name, description):
        # TODO: Implement similar retry logic for Gemini
        prompt = self._construct_prompt(module_name, description)
        model = "gemini-1.5-flash"
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_key}"
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        try:
            print(f"[GATEWAY] Contacting Gemini ({model})...")
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            result = response.json()
            text = result['candidates'][0]['content']['parts'][0]['text']
            return self._clean_code(text)
        except Exception as e:
            print(f"[GATEWAY] Gemini failed: {e}")
            return None

    def _construct_prompt(self, module_name, description):
        return f"""
        You are the 'Agent Factory' for a recursive self-improving system.
        
        TASK: Write a complete, working Python module for: '{module_name}'.
        DESCRIPTION: {description}
        
        REQUIREMENTS:
        1. Return ONLY the raw Python code. No markdown formatting, no backticks, no explanatory text.
        2. Steps: Imports -> Class Definition -> Methods.
        3. The code must be production-ready and error-free.
        4. CRITICAL: You MUST define a global 'start()' function at the end of the file. This is the entry point.
        
        EXAMPLE FORMAT:
        import some_lib
        
        class MyOrgan:
            def do_something(self):
                pass
                
        # REQUIRED ENTRY POINT
        def start():
            organ = MyOrgan()
            organ.do_something()
        
        CODE:
        """

    def _clean_code(self, text):
        # Remove markdown code blocks
        if "```" in text:
            lines = text.splitlines()
            cleaned_lines = []
            in_block = False
            for line in lines:
                if line.strip().startswith("```"):
                    in_block = not in_block
                    continue
                cleaned_lines.append(line)
            text = "\n".join(cleaned_lines)
        
        return text.strip()
