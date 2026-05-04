import os
import re
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

REPLACEMENTS = {
    "world": "world",
    "world": "world",
    "world": "world",
}

TARGET_FILES_EXT = {".py"}

def run_cmd(cmd):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    return result.returncode

def replace_in_file(file_path: Path):
    try:
        content = file_path.read_text()

        original = content

        for old, new in REPLACEMENTS.items():
            content = content.replace(old, new)

        if content != original:
            file_path.write_text(content)
            print(f"Updated: {file_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def scan_and_fix():
    print("🔍 Scanning backend for outdated app references...")

    for root, dirs, files in os.walk(BASE_DIR):
        # skip venv, cache
        if "migrations" in root and "__pycache__" in root:
            continue

        for file in files:
            path = Path(root) / file

            if path.suffix in TARGET_FILES_EXT:
                replace_in_file(path)

def validate_migrations():
    print("\n🧪 Validating Django migration graph...\n")
    return run_cmd("docker compose exec backend python manage.py showmigrations")

def main():
    print("🚀 Starting Django refactor cleanup...\n")

    scan_and_fix()

    print("\n🔄 Rebuilding migrations check...\n")
    validate_migrations()

    print("\n✅ Done. Now run:")
    print("docker compose down -v")
    print("docker compose up --build")
    print("docker compose exec backend python manage.py migrate")

if __name__ == "__main__":
    main()