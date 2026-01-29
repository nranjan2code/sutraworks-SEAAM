import json
import os
from seaam.connectors.llm_gateway import ProviderGateway

class Architect:
    """
    The Mind.
    It decides WHAT the system should be.
    """
    def __init__(self, dna, save_callback):
        self.dna = dna
        self.save_dna = save_callback
        self.gateway = ProviderGateway()
        
        # Load goals from DNA (Cognitive Persistence)
        # If no goals exist, seed them with defaults
        if "goals" not in self.dna:
            self.dna["goals"] = [
                "I must be able to perceive the file system to understand the user's project.",
                "I must have a memory of past events to learn from mistakes.",
                "I must have a visual dashboard to communicate my state to the user."
            ]
            self.save_dna()
            
        self.goals = self.dna["goals"]

    def reflect(self):
        """
        Analyzes the current DNA against Goal.
        """
        active_modules = self.dna.get("active_modules", [])
        blueprint = self.dna.get("blueprint", {})
        
        # Quick heuristic: If we have pending blueprints (not yet active), wait for Genesis to build them.
        # This prevents the Architect from panicking while the Body is still growing.
        if len(blueprint) > len(active_modules):
            print("[ARCHITECT] Waiting for Body to catch up with Blueprint...")
            return

        print("[ARCHITECT] Reflecting on existence...")
        
        failures = self.dna.get("failures", [])
        
        prompt = f"""
        You are the 'Architect' of a self-evolving AI system.
        
        GOALS:
        {json.dumps(self.goals, indent=2)}
        
        CURRENT DNA BLUEPRINT:
        {json.dumps(blueprint, indent=2)}
        
        PREVIOUS FAILURES (LEARN FROM THIS):
        {json.dumps(failures, indent=2)}
        
        TASK:
        1. REVIEW PREVIOUS FAILURES. If a module failed (e.g. missing start()), you MUST output a JSON to REDEFINE that module with specific instructions to fix the error.
        2. Identify the single most critical MISSING component to achieve the GOALS.
        
        If the system is complete and healthy (no failures), return "COMPLETE".

        CRITICAL KERNEL CONTRACT: 
        - The system HAS a nervous system: `seaam.kernel.bus`. 
        - Modules can import `bus` and use `bus.subscribe("file_modified", callback)` or `bus.publish(Event("file_modified", path))`.
        - **EVERY MODULE MUST HAVE A GLOBAL `start()` FUNCTION.** This is how the kernel launches it.
        - If you have an Observer and a Speaker but no sound, you probably need a "Reflex" or "Behavior" module to wire them together.
        
        If a component is missing OR NEEDS FIXING, return a JSON object (and ONLY JSON) with:
        {{
            "module_name": "seaam.behavior.reflex",
            "description": "Detailed description of the python module. It should import seaam.kernel.bus, seaam.voice.speaker, etc..."
        }}
        
        Note:
        - For Perception/Observer, use 'seaam.perception.observer'.
        - For Memory/Journal, use 'seaam.memory.journal'.
        - For Dashboard, use 'seaam.interface.dashboard'.
        """
        
        response = self.gateway.generate_code("ARCHITECT_THOUGHT", prompt) # Reusing generate_code for text gen
        
        if not response or "COMPLETE" in response:
            print("[ARCHITECT] Content with current form.")
            return

        try:
            # Gateway now cleans code, so we can try to parse directly
            # But sometimes LLMs are chatty, so we try to find the first '{'
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx+1]
            else:
                # If no JSON found
                return

            plan = json.loads(response)
            
            module_name = plan.get("module_name")
            desc = plan.get("description")
            
            if module_name and desc:
                # EVOLUTION LOGIC:
                # 1. New Organ: if not in blueprint
                # 2. Iteration: if in blueprint BUT in failures (Refinement)
                
                is_failing = any(module_name in f for f in failures)
                
                # Check for "Reflex" or "Behavior" specifically as per instructions
                if module_name == "seaam.behavior.reflex":
                     # Ensure we don't accidentally ignore it if it's critical
                     pass
                
                if module_name not in blueprint:
                    print(f"[ARCHITECT] Decided to evolve: {module_name}")
                    self.dna["blueprint"][module_name] = desc
                    self.save_dna()
                elif is_failing:
                    print(f"[ARCHITECT] Refining blueprint for failing organ: {module_name}")
                    self.dna["blueprint"][module_name] = desc
                    self.save_dna() 
                else:
                    print(f"[ARCHITECT] {module_name} already in blueprint.")
                    
        except json.JSONDecodeError as e:
            print(f"[ARCHITECT] Failed to structure thought: {e}")
            print(f"[ARCHITECT] Raw Response: {response}")
            pass
