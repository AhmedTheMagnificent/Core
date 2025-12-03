import sys
import os

print("--- DIAGNOSTIC MODE ---")

def check_import(module_name, code_to_run):
    try:
        exec(code_to_run)
        print(f"[OK] {module_name}")
    except ImportError as e:
        print(f"[FAIL] {module_name} -> {e}")
    except Exception as e:
        print(f"[FAIL] {module_name} -> {e}")

# 1. Check Environment
print("\n1. CHECKING LIBRARIES...")
check_import("LangChain", "import langchain")
check_import("LangGraph", "import langgraph")
check_import("ChromaDB", "import chromadb")
check_import("Google GenAI", "import langchain_google_genai")
check_import("Tavily", "import tavily")
check_import("Playwright", "import playwright")
check_import("Rich", "import rich")

# 2. Check Playwright specifically (Common failure point)
print("\n2. CHECKING PLAYWRIGHT BROWSERS...")
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        print("[OK] Playwright Browser launched successfully.")
        browser.close()
except Exception as e:
    print(f"[FAIL] Playwright Browser -> {e}")
    print("       (Did you run 'playwright install' in terminal?)")

# 3. Check Internal Files
print("\n3. CHECKING YOUR CODE...")
sys.path.append(os.getcwd())

check_import("src/memory.py", "from src.memory import save_to_memory")
check_import("src/tools.py", "from src.tools import get_core_tools")
check_import("src/brain.py", "from src.brain import build_core_brain")

print("\n--- END OF DIAGNOSTIC ---")
