# ui.py
import os, time

# -----------------------------
# Utilities
# -----------------------------
def clear_screen():
    """Clears the terminal screen."""
    if os.name == "nt":  # Windows
        os.system("cls")
    else:  # macOS / Linux
        os.system("clear")

def typewriter(text, delay=0.005):
    """Prints text one character at a time for a typewriter effect."""
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()  # newline at the end

# -----------------------------
# ASCII Titles
# -----------------------------
game_title = r"""
   _____                              ____          _                           _             
  / ____|                            / __ \        | |                         (_)            
 | |  __  __ _ _ __ ___   ___ ______| |  | |_ __   | |     ___  __ _ _ __ _ __  _ _ __   __ _ 
 | | |_ |/ _` | '_ ` _ \ / _ \______| |  | | '_ \  | |    / _ \/ _` | '__| '_ \| | '_ \ / _` |
 | |__| | (_| | | | | | |  __/      | |__| | | | | | |___|  __/ (_| | |  | | | | | | | | (_| |
  \_____|\__,_|_| |_| |_|\___|       \____/|_| |_| |______\___|\__,_|_|  |_| |_|_|_| |_|\__, |
                                                                                         __/ |
                                                                                        |___/ 
"""

game_over_art = r"""
   ____                        ___                 
  / ___| __ _ _ __ ___   ___  / _ \__   _____ _ __ 
 | |  _ / _` | '_ ` _ \ / _ \| | | \ \ / / _ \ '__|
 | |_| | (_| | | | | | |  __/| |_| |\ V /  __/ |   
  \____|\__,_|_| |_| |_|\___| \___/  \_/ \___|_|   
"""

# -----------------------------
# Title Screen
# -----------------------------
def title_screen(last_run_path="last_run.txt"):
    """Displays the title screen and returns True if start, False if exit."""
    while True:
        clear_screen()
        print("=" * 60)
        print(game_title)
        print("=" * 60)

        if os.path.exists(last_run_path):
            try:
                with open(last_run_path, "r") as f:
                    content = f.read().strip()
                print("\n--- Last Run ---")
                print(content)
                print()
            except Exception:
                pass

        typewriter("\n1. Start Game", 0.03)
        typewriter("2. Practice Mode", 0.03)
        typewriter("3. Change Notes Files", 0.03)
        typewriter("4. View Achievements", 0.03)
        typewriter("5. Exit\n", 0.03)
        print("=" * 60)

        choice = input("Enter your choice: ").strip()
        if choice == "1":
            return "start"
        elif choice == "2":
            return "practice"
        elif choice == "3":
            return "reconfigure"
        elif choice == "4":
            return "achievements"
        elif choice == "5":
            return "exit"
        else:
            typewriter("Invalid choice. Please enter 1, 2, or 3.", 0.03)
            time.sleep(1)

# -----------------------------
# Game Over Screen
# -----------------------------
def game_over_screen():
    """Displays the game over screen and returns True to restart, False to exit."""
    while True:
        clear_screen()
        print("=" * 60)
        print(game_over_art)
        print("=" * 60)
        typewriter("\n1. Restart", 0.03)
        typewriter("2. Exit\n", 0.03)
        print("=" * 60)

        choice = input("Enter your choice: ").strip()
        if choice == "1":
            return True
        elif choice == "2":
            return False
        else:
            typewriter("Invalid choice. Please enter 1 or 2.", 0.03)
            time.sleep(1)

def hp_bar(current, maximum, length=20):
    """Returns a visual HP bar string."""
    filled = int((current / maximum) * length)
    filled = max(0, min(length, filled))
    bar = "#" * filled + "-" * (length - filled)

    if current / maximum > 0.5:
        status = "healthy"
    elif current / maximum > 0.25:
        status = "wounded"
    else:
        status = "critical"

    return f"[{bar}] {current}/{maximum} ({status})"