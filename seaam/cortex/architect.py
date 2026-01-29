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
        
        # Initial goals (If DNA is empty, the system waits for purpose)
        if "goals" not in self.dna:
            self.dna["goals"] = []
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
        4. EVOLVE PURPOSE: If current goals are largely satisfied, you MUST propose a NEW high-level goal to expand the system's intelligence, autonomy, or utility.
        
        CRITICAL KERNEL CONTRACT: 
        - The system HAS a nervous system: `seaam.kernel.bus`. 
        - **EVENT BUS API**:
          * `from seaam.kernel.bus import bus, Event`
          * `bus.subscribe(event_type: str, callback: Callable[[Event], None])`
          * `bus.publish(Event(event_type: str, data: Any))`
        - **EVERY MODULE MUST HAVE A GLOBAL `start()` FUNCTION.**
        
        - Purpose: Define your own organ names and paths under the `soma.` package.
        
        - **DECOUPLING & IMPORTS**:
          * **NO DIRECT IMPORTS BETWEEN SOMA ORGANS**. Use the Event Bus to communicate.
          * **FORBIDDEN**: `import soma.memory.journal` inside `soma.perception.observer`.
          * **CORRECT**: Publish an event from `observer` and subscribe in `journal`.
          * **NO REDUNDANT PREFIXES**: 
            - CORRECT: `from seaam.kernel.bus import bus`
            - INCORRECT: `import soma.seaam.kernel.bus`
        
        - **NO PLACEHOLDERS**: Every module must be FULLY IMPLEMENTED. No `pass`, no `TODO`.
        
        If a component is missing OR NEEDS FIXING, or if you are proposing a NEW GOAL, return a JSON object (and ONLY JSON) with:
        {{
            "module_name": "soma.your_category.your_organ",
            "description": "DETAILED description of the python module logic. Demands functional code without mocks. Describe exactly how it should interact with the Event Bus.",
            "new_goal": "Optional: A new high-level goal to add to the system's DNA (only if evolving purpose)."
        }}
        """
        
        response = self.gateway.think(prompt) 
        
        if not response:
            print("[ARCHITECT] No response from Overmind.")
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
            new_goal = plan.get("new_goal")
            
            # 0. GOAL EVOLUTION:
            if new_goal and new_goal not in self.dna["goals"]:
                print(f"[ARCHITECT] Purpose Evolved: {new_goal}")
                self.dna["goals"].append(new_goal)
                self.save_dna()

            if module_name and desc:
                # EVOLUTION LOGIC:
                # 1. New Organ: if not in blueprint
                # 2. Iteration: if in blueprint BUT in failures (Refinement)
                
                is_failing = any(module_name in f for f in failures)
                
                if module_name not in blueprint:
                    print(f"[ARCHITECT] Decided to evolve: {module_name}")
                    self.dna["blueprint"][module_name] = desc
                    self.save_dna()
                elif is_failing:
                    print(f"[ARCHITECT] Refining blueprint for failing organ: {module_name}")
                    self.dna["blueprint"][module_name] = desc
                    self.save_dna() 
                else:
                    # If it's already there and not failing, we might be looping.
                    # This happens if the Architect isn't creative enough.
                    pass
                    
        except json.JSONDecodeError as e:
            print(f"[ARCHITECT] Failed to structure thought: {e}")
            print(f"[ARCHITECT] Raw Response: {response}")
            pass
