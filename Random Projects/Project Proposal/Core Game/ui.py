# UI

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

class EventBus:
    """
    Collects game events as structured data instead of printing directly.
    The terminal reads from it immediately.
    A future GUI reads from it to update widgets.
    """
    def __init__(self):
        self._listeners = []
        self._use_typewriter = True    # set False when GUI takes over

    def subscribe(self, fn):
        self._listeners.append(fn)

    def emit(self, event_type, **data):
        event = {"type": event_type, **data}
        for listener in self._listeners:
            listener(event)

    def say(self, text):
        """Emit a text message event."""
        self.emit("text", content=text)

    def stat_update(self, entity_name, hp, max_hp, **extras):
        """Emit a stat update event."""
        self.emit("stat_update", name=entity_name, hp=hp, max_hp=max_hp, **extras)

    def combat_event(self, event_name, **data):
        """Emit a combat-specific event."""
        self.emit("combat", name=event_name, **data)

# Global bus — import this everywhere instead of calling typewriter directly
bus = EventBus()

def _terminal_listener(event):
    """Default listener: prints events to the terminal."""
    if event["type"] == "text":
        typewriter(event["content"])
    elif event["type"] == "stat_update":
        pass    # terminal already shows stats via display_entity_stats
    elif event["type"] == "combat":
        pass    # combat events are narrated via text events

bus.subscribe(_terminal_listener)

class InputHandler:
    """
    Wraps input() so a GUI can intercept it later.
    Terminal mode: calls input() directly.
    GUI mode: waits for GUI to push an answer.
    """
    def __init__(self):
        self._pending = None
        self._gui_mode = False

    def ask(self, prompt=""):
        if self._gui_mode:
            # GUI will set self._pending when player clicks/types
            import time
            while self._pending is None:
                time.sleep(0.05)
            result = self._pending
            self._pending = None
            return result
        else:
            return input(prompt).strip()

    def push_answer(self, answer):
        """Called by GUI when player submits an answer."""
        self._pending = answer

input_handler = InputHandler()

