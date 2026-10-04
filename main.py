"""
SafeHer Application Launcher
Allows launching the Django development server directly from PyCharm's 'Run main.py' button.
"""
import os
import sys
from pathlib import Path


def main():
    safety_dir = Path(__file__).resolve().parent / "Safety_For_Woman"
    sys.path.insert(0, str(safety_dir))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "safeher.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Please ensure your virtual environment (.venv) is activated."
        ) from exc

    # Default to running the web server if no arguments are provided
    if len(sys.argv) <= 1:
        print("\n" + "=" * 65)
        print("🛡️  SafeHer: Crowd-Sourced Safety Network & Panic Response")
        print("🌍  Launching local development server at: http://127.0.0.1:8000/")
        print("👤  Demo login: username='sarah' | password='SafeHerPassword2026!'")
        print("=" * 65 + "\n")
        execute_from_command_line([sys.argv[0], "runserver", "127.0.0.1:8000"])
    else:
        execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
