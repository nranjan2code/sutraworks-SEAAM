import os
import sys

# Ensure we can import modules from current directory
sys.path.append(os.getcwd())

from seaam.kernel.genesis import Genesis

def main():
    if not os.environ.get("GEMINI_API_KEY"):
        print("WARNING: GEMINI_API_KEY is not set. The system will probably fail to evolve.")
        # Optional: Ask user for key? For now, we assume environment.
    
    # Initialize the Will
    app = Genesis()
    
    # Start the Cycle
    app.awaken()

if __name__ == "__main__":
    main()
