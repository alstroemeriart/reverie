# CONFIG

import json
import os
from ui import typewriter

# Always resolves to the folder this file lives in
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")


def load_config():
    """
    Load config.json. If it doesn't exist or has no notes,
    run the setup wizard to create it.
    """
    if not os.path.exists(CONFIG_FILE):
        print("[Config] No config.json found — running setup wizard.")
        return setup_wizard()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[Config] config.json has a formatting error: {e}")
        print("Delete config.json and restart to run setup again.")
        input("Press Enter to exit.")
        raise SystemExit

    # If notes section is empty, re-run wizard
    if not config.get("notes"):
        print("[Config] No notes files configured — running setup wizard.")
        return setup_wizard()

    return config


def resolve_path(relative_path):
    return os.path.join(BASE_DIR, relative_path)


def get_notes_paths(config):
    paths = {}
    notes = config.get("notes", {})
    for qtype, relative_path in notes.items():
        absolute = resolve_path(relative_path)
        if not os.path.exists(absolute):
            print(f"[Config] Warning: notes file not found — {absolute}")
        paths[qtype] = absolute
    return paths


def get_save_path(config):
    return resolve_path(config.get("save_file", "savegame.json"))


def get_last_run_path(config):
    return resolve_path(config.get("last_run_file", "last_run.txt"))

def browse_for_file(prompt):
    """
    Ask the user to type or paste a file path.
    Keeps asking until a valid file is given or they skip.
    Returns the absolute path string, or None if skipped.
    """
    typewriter(prompt)
    typewriter("(Press Enter without typing to skip this question type)")

    while True:
        raw = input("> ").strip().strip('"').strip("'")

        if raw == "":
            return None

        # Normalize path separators
        path = os.path.normpath(raw)

        if os.path.isfile(path):
            return path
        else:
            typewriter(f"File not found: {path}")
            typewriter("Please check the path and try again, or press Enter to skip.")


def setup_wizard():
    """
    Interactive setup screen that asks the user to locate their
    notes files and saves the result to config.json.
    Runs automatically when config.json is missing or incomplete.
    """
    print("\n" + "="*50)
    print("  GAME-ON LEARNING — FIRST TIME SETUP")
    print("="*50)
    print("\nThis wizard will help you load your study notes.")
    print("You can paste full file paths, or drag-and-drop")
    print("the file into the terminal window on most systems.\n")

    question_types = {
        "TF": {
            "label": "True/False questions",
            "format": "Each line: Statement = True  or  Statement = False",
            "difficulty": 1,
        },
        "MC": {
            "label": "Multiple Choice questions",
            "format": 'Each line: {"question":"...","options":["A","B","C"],"answer":"A"}',
            "difficulty": 2,
        },
        "AR": {
            "label": "Arithmetic / Short Answer questions",
            "format": "Each line: Question = Answer",
            "difficulty": 2,
        },
        "ID": {
            "label": "Identification questions",
            "format": "Each line: Question = Answer",
            "difficulty": 3,
        },
    }

    notes_config = {}

    for qtype, info in question_types.items():
        print(f"\n--- {info['label']} ({qtype}) ---")
        print(f"Expected format: {info['format']}")
        path = browse_for_file(f"Path to your {info['label']} file:")

        if path:
            # Store relative to project folder if possible, else store absolute
            try:
                rel = os.path.relpath(path, BASE_DIR)
                notes_config[qtype] = rel
            except ValueError:
                # relpath fails across drives on Windows — store absolute
                notes_config[qtype] = path
            print(f"Loaded: {path}")
        else:
            print(f"Skipped {qtype}.")

    if not notes_config:
        print("\nNo files were loaded. The game needs at least one notes file.")
        print("Re-run the game to try again.")
        input("Press Enter to exit.")
        raise SystemExit

    # Build and save the config
    config = {
        "notes": notes_config,
        "save_file": "savegame.json",
        "last_run_file": "last_run.txt",
    }

    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        print(f"\nSetup saved to {CONFIG_FILE}")
        print("You can edit this file directly any time to change your notes.\n")
    except Exception as e:
        print(f"Could not save config: {e}")
        input("Press Enter to exit.")
        raise SystemExit

    return config

