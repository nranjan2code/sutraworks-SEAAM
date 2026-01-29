import os
import json
import time
import importlib
import subprocess
import sys
import threading
import inspect
from seaam.connectors.llm_gateway import ProviderGateway
from seaam.cortex.architect import Architect

class Genesis:
    """
    The Primal Will.
    It exists to ensure the System exists.
    """
    def __init__(self):
        self.root_dir = os.getcwd()
        self.dna_path = os.path.join(self.root_dir, "dna.json")
        self.gateway = ProviderGateway()
        self.dna = self._load_dna()
        self.architect = Architect(self.dna, self._save_dna)
        self.running_organs = set() # Track what is already active to prevent double-integration

    def _load_dna(self):
        try:
            with open(self.dna_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("CRITICAL: DNA not found. The organism is dead.")
            return None

    def _save_dna(self):
        with open(self.dna_path, 'w') as f:
            json.dump(self.dna, f, indent=2)

    def awaken(self):
        print(f"--- SEAAM v{self.dna.get('system_version')} AWAKENING ---")
        
        # 1. Self-Audit & Evolution (Architect decides, Genesis builds)
        while True:
            # The Architect thinks about what is needed
            self.architect.reflect()
            
            # The Genesis Loop checks if there are pending blueprints to build
            missing = self._audit()
            if not missing:
                break
            
            # Build what the Architect designed
            self._evolve_step(missing)

        # 2. Assimilation (Integration)
        self._assimilate()

        # 3. Life (The Run Loop)
        self._live()

    def _live(self):
        print("[LIFE] Entering metabolic stasis with continuous evolution (Ctrl+C to stop)...")
        try:
            while True:
                # PERIODIC METABOLISM: Think and Grow
                print("\n[METABOLISM] Periodic reflection cycle...")
                
                # 1. Reflect
                self.architect.reflect()
                
                # 2. Audit
                missing = self._audit()
                
                # 3. Evolve (if needed)
                if missing:
                    print(f"[METABOLISM] New needs detected: {list(missing.keys())}")
                    self._evolve_step(missing)
                    
                    # 4. Integrate new growth
                    self._assimilate()
                
                # Wait before next cycle (e.g. 30 seconds for demonstration)
                # In production this might be longer or event-driven.
                time.sleep(30)
                
        except KeyboardInterrupt:
            print("[LIFE] Shutting down.")

    def _assimilate(self):
        """
        Dynamically imports and activates the grown organs.
        """
        active_modules = self.dna.get("active_modules", [])
        
        # Only integrate what isn't already running
        to_integrate = [m for m in active_modules if m not in self.running_organs]
        
        if not to_integrate:
            return

        print(f"[ASSIMILATION] Integrating {len(to_integrate)} new organs...")
        
        for module_name in to_integrate:
            try:
                # seaam.perception.observer -> from seaam.perception.observer import *
                module = importlib.import_module(module_name)
                print(f"  - Loaded: {module_name}")
                
                # Heuristic: Find a class that matches the module name loosely or just pick the first class?
                # For this prototype, we rely on the specific blueprints asking for specific hooks.
                
                # GENERIC PROTOCOL: If the module has a 'start' function, run it.
                if hasattr(module, "start"):
                    # Check signature to see if we can call it without args
                    sig = inspect.signature(module.start)
                    if len(sig.parameters) == 0:
                        t = threading.Thread(target=module.start, daemon=True)
                        t.start()
                    else:
                        print(f"  - [WARNING] {module_name}.start() requires arguments: {list(sig.parameters.keys())}. Skipping auto-start.")
                        # Could report failure, but let's see if we can make it zero-args
                        self._report_failure(module_name, f"start() requires arguments: {list(sig.parameters.keys())}. Must be zero-args.")
                        continue
                    
                    print(f"  - [STARTED] {module_name} (Thread)")
                    self.running_organs.add(module_name)
                else:
                    # FEEDBACK LOOP: Report failure to DNA so Architect can fix it.
                    error_msg = f"Module {module_name} rejected: Missing global start() function."
                    print(f"  - [REJECTED] {error_msg}")
                    
                    self._report_failure(module_name, error_msg)
                    
            except ImportError as e:
                print(f"  - [CRITICAL] Body rejected organ {module_name} due to missing tissue: {e}")
                # e.name might be the package name, or we parse str(e) "No module named 'x'"
                missing_package = str(e).split("'")[-2]
                self._heal(missing_package)
                
            except Exception as e:
                print(f"  - [REJECTED] {module_name}: {e}")
                self._report_failure(module_name, str(e))

    def _report_failure(self, module_name, error_reason):
        """
        Feeds the error back into the DNA so the Architect can learn.
        """
        # 1. Remove from active modules (it's dead)
        if module_name in self.dna["active_modules"]:
            self.dna["active_modules"].remove(module_name)
        
        # 2. Add to failures list
        if "failures" not in self.dna:
            self.dna["failures"] = []
        
        # Avoid duplicate failures
        failure_entry = f"{module_name}: {error_reason}"
        if failure_entry not in self.dna["failures"]:
            self.dna["failures"].append(failure_entry)
            
        self._save_dna()
        print(f"[GENESIS] Failure recorded in DNA: {failure_entry}")

    def _heal(self, package_name):
        """
        The Immunity System.
        Installs missing dependencies and REBOOTS the system.
        """
        # CHECK INTERNAL: Is this a missing ORGAN or external TISSUE?
        # We assume any package starting with 'seaam' or 'soma' is an internal organ.
        is_internal = package_name.startswith("seaam") or package_name.startswith("soma")
        
        # HEURISTIC: Even if it doesn't start with soma/seaam, it might be an internal sub-package
        # example: 'perception.observer' (if LLM forgot the soma prefix)
        if not is_internal:
            # Check if this name exists as a directory in soma/
            soma_path = os.path.join(self.root_dir, "soma")
            if os.path.exists(soma_path):
                # Check for first part of package name as directory in soma/
                root_pkg = package_name.split('.')[0]
                if root_pkg == "seaam": # NEVER over-heal the SEED
                    is_internal = True
                elif os.path.isdir(os.path.join(soma_path, root_pkg)):
                    is_internal = True
                    print(f"[IMMUNITY] Identified {package_name} as internal tissue (missing prefix).")
        
        # DOUBLE CHECK: If it's something in seaam/, it is SEED.
        # We must NOT try to grow something that is already hardcoded.
        if package_name.startswith("seaam."):
            # Does the file exist on disk?
            parts = package_name.split('.')
            seed_path = os.path.join(self.root_dir, *parts)
            # Check for directory or .py file
            if os.path.exists(seed_path) or os.path.exists(seed_path + ".py"):
                print(f"[IMMUNITY] {package_name} is a SEED component. Immersion failed due to internal API mismatch.")
                # Report failure to Architect instead of healing
                self._report_failure(package_name, f"Internal API mismatch: {package_name} is part of the SEED. Check your class/function names.")
                return

        if is_internal:
            print(f"[IMMUNITY] Detected missing internal tissue: {package_name}")
            
            # Check if we already know about this need
            # If it's a sub-part (e.g. perception.observer), find parent organ in blueprint
            found_in_blueprint = False
            for bp_name in self.dna.get("blueprint", {}):
                if bp_name == package_name or bp_name.endswith("." + package_name):
                    found_in_blueprint = True
                    break

            if not found_in_blueprint:
                print(f"[IMMUNITY] Injecting new blueprint for: {package_name}")
                
                # Add to blueprint with a prompt-friendly description
                if "blueprint" not in self.dna:
                    self.dna["blueprint"] = {}
                
                # Use soma. prefix for the new blueprint entry
                full_name = package_name if package_name.startswith("soma.") else f"soma.{package_name}"
                self.dna["blueprint"][full_name] = (
                    "Critical system component required by other organs. "
                    "This organ was discovered as a missing dependency. "
                    "Please implement it with a global start() function."
                )
                
                # Ensure it's not marked as active (so Genesis picks it up)
                if full_name in self.dna.get("active_modules", []):
                    self.dna["active_modules"].remove(full_name)
                
                self._save_dna()
                print("[IMMUNITY] Blueprint updated. REBOOTING SYSTEM for Genesis to take over...")
                
                # Restart
                os.execv(sys.executable, [sys.executable] + sys.argv)
                return
            
            else:
                # It is in blueprint, but we still got an ImportError?
                # This usually means the module exists but doesn't have the specific attribute (e.g. class)
                # OR the file is corrupted/empty/missing prefix.
                print(f"[IMMUNITY] Internal organ {package_name} exists in blueprint but caused ImportError.")
                print(f"[IMMUNITY] Marking as FAILED so Architect can fix it.")
                
                # Try to report failure for the fully qualified name
                full_name = next((n for n in self.dna["blueprint"] if n == package_name or n.endswith("." + package_name)), package_name)
                self._report_failure(full_name, f"ImportError detected: No module named '{package_name}'. Likely missing 'soma.' prefix in internal imports.")
                return

        # EXTERNAL: Use pip
        print(f"[IMMUNITY] Auto-Installing missing dependency: {package_name}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print("[IMMUNITY] Installation successful. REBOOTING SYSTEM...")
            
            # Restart the process
            os.execv(sys.executable, [sys.executable] + sys.argv)
            
        except Exception as e:
            print(f"[IMMUNITY] FAILED to install {package_name}: {e}")

    def _evolve_step(self, missing_organs):
        for organ_name, blueprint_desc in missing_organs.items():
            print(f"[GENESIS] Missing Organ: {organ_name}")
            print(f"[GENESIS] Consultling the Overmind for blueprint...")
            
            code = self.gateway.generate_code(organ_name, blueprint_desc)
            
            if code:
                self._materialize(organ_name, code)
                self.dna['active_modules'].append(organ_name)
                
                # CLEAR FAILURES: We have just evolved a fix. Forget past mistakes for this organ.
                if "failures" in self.dna:
                    self.dna["failures"] = [f for f in self.dna["failures"] if not f.startswith(organ_name + ":")]
                
                self._save_dna()
                print(f"[GENESIS] Organ '{organ_name}' GROWN.")
            else:
                print(f"[GENESIS] Failed to grow {organ_name}. Retrying in next epoch.")

    def _audit(self):
        """
        Checks what organs are in the blueprint but not in active_modules.
        """
        blueprint = self.dna.get("blueprint", {})
        active = self.dna.get("active_modules", [])
        
        missing = {}
        for organ, desc in blueprint.items():
            if organ not in active:
                missing[organ] = desc
        
        return missing

    def _materialize(self, organ_name, code):
        """
        Writes the code to the file system.
        organ_name example: 'soma.perception.observer'
        """
        # Convert dot notation to path
        parts = organ_name.split('.')
        # parts = ['soma', 'perception', 'observer']
        
        # Ensure directories exist and are valid packages
        current_path = self.root_dir
        for i in range(len(parts) - 1):
            current_path = os.path.join(current_path, parts[i])
            if not os.path.exists(current_path):
                os.makedirs(current_path, exist_ok=True)
                # Every new directory in soma must be a package
                init_file = os.path.join(current_path, "__init__.py")
                if not os.path.exists(init_file):
                    with open(init_file, 'w') as f:
                        f.write("# Soma package part\n")
        
        # File name
        file_name = parts[-1] + ".py"
        file_path = os.path.join(current_path, file_name)
        
        # Write
        with open(file_path, 'w') as f:
            f.write(code)
            
        print(f"[GENESIS] Wrote code to {file_path}")
