import py_compile
import sys

files = [
    "src/bot.py",
    "src/config.py",
    "src/handlers/message_handler.py",
    "src/handlers/callback_handler.py",
    "src/services/ai_service.py",
    "src/services/scraper.py",
    "src/services/database.py"
]

for f in files:
    try:
        py_compile.compile(f, doraise=True)
        print(f"OK: {f}")
    except Exception as e:
        print(f"ERROR: {f} - {e}")
        sys.exit(1)

print("\nAll files OK!")