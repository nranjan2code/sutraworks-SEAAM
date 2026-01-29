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
        failures = self.dna.get("failures", [])
        
        # PRIORITIZE FIXING FAILURES:
        # If we have failures, we MUST reflect to fix them, even if the body is busy.
        # Otherwise, we might get stuck in a loop of generating the same broken code.
        if not failures:
            # Quick heuristic: If we have pending blueprints (not yet active), wait for Genesis to build them.
            # This prevents the Architect from panicking while the Body is still growing.
            if len(blueprint) > len(active_modules):
                print("[ARCHITECT] Waiting for Body to catch up with Blueprint...")
                return
        else:
            print(f"[ARCHITECT] Critical failures detected ({len(failures)}). Intervening...")

        print("[ARCHITECT] Reflecting on existence...")
        
        prompt = f"""
        You are the 'Architect' of a self-evolving AI system.
        
        GOALS:
        {json.dumps(self.goals, indent=2)}
        
        CURRENT DNA BLUEPRINT:
        {json.dumps(blueprint, indent=2)}
        
        PREVIOUS FAILURES (LEARN FROM THIS):
        {json.dumps(failures, indent=2)}
        
        TASK:
        1. ANALYZE PREVIOUS FAILURES. If an organ is failing, your #1 priority is to REDEFINE its blueprint with a fix.
        2. EVALUATE ALL GOALS vs BLUEPRINT. Compare the existing organs against ALL system goals.
        3. PROPOSE NEXT GROWTH: Identify the single most important component that is MISSING to satisfy the remaining goals. Be proactive!
        
        CRITICAL KERNEL CONTRACT: 
        - The system HAS a nervous system: `seaam.kernel.bus`. 
        - **EVENT BUS API**:
          * `from seaam.kernel.bus import bus, Event`
          * `bus.subscribe(event_type: str, callback: Callable[[Event], None])`
          * `bus.publish(Event(event_type: str, data: Any))`
        - **EVERY MODULE MUST HAVE A GLOBAL `start()` FUNCTION.**
        
        SOMA ATLAS (Internal Package Paths):
        - Perception: `soma.perception.observer`
        - Memory: `soma.memory.journal` (Class name must be `Journal`)
        - Dashboard: `soma.interface.dashboard`
        - Behavior: `soma.behavior.reflex`
        
        - **DECOUPLING & IMPORTS**:
          * **NO DIRECT IMPORTS BETWEEN SOMA ORGANS**. Use the Event Bus to communicate.
          * **FORBIDDEN**: `import soma.memory.journal` inside `soma.perception.observer`.
          * **CORRECT**: Publish an event from `observer` and subscribe in `journal`.
          * **NO REDUNDANT PREFIXES**: 
            - CORRECT: `from seaam.kernel.bus import bus`
            - INCORRECT: `import soma.seaam.kernel.bus`
        
        If a component is missing OR NEEDS FIXING, return a JSON object (and ONLY JSON) with:
        {
            "module_name": "soma.behavior.reflex",
            "description": "Detailed description of the python module. Focus on logic. Remind Genesis not to import other organs directly."
        }
}
        """
        
        response = self.gateway.think(prompt) 
        
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
                print(f"[ARCHITECT] No JSON found in response.")
                if response:
                    print(f"[ARCHITECT] Raw response snippet: {response[:100]}...")
                return

            plan = json.loads(json_str) 
            
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
