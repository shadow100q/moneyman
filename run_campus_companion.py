"""
Root runner for Campus AI Companion.
Run with: python run_campus_companion.py
"""

import sys
from pathlib import Path

# Add campus_ai_companion directory to python sys.path
companion_dir = Path(__file__).resolve().parent / "campus_ai_companion"
sys.path.insert(0, str(companion_dir))

from campus_ai_companion.app import create_app

if __name__ == "__main__":
    app = create_app()
    port = app.config.get("PORT", 5050)
    print("=" * 65)
    print("[CAMPUS AI COMPANION] - College Workshop Edition")
    print("=" * 65)
    print(f"Server is running at: http://127.0.0.1:{port}")
    print("Tabs available:")
    print("  1. ASK AI (General Educational Q&A)")
    print("  2. CAMPUS KNOWLEDGE (Keyword-based RAG)")
    print("  3. TAKE ACTION (Gemini Tool & Function Calling)")
    print("=" * 65)
    app.run(host="127.0.0.1", port=port, debug=True)
