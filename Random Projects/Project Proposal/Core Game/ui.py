# ui.py
import os
import time
import random


def clear_screen():
    """Clear the screen. In GUI mode this fires a bus event instead."""
    if _gui_active():
        bus.game_event("clear_log")
    else:
        os.system("cls" if os.name == "nt" else "clear")


def typewriter(text, delay=0.005):
    """
    Print text character-by-character in terminal mode,
    or emit it through the event bus in GUI mode.
    All game modules call this function directly — no patching needed.
    """
    if _gui_active():
        bus.say(str(text))
    else:
        try:
            for char in str(text):
                print(char, end="", flush=True)
                time.sleep(delay)
        except UnicodeEncodeError:
            # Fallback for systems that don't support Unicode in console
            for char in str(text):
                try:
                    print(char, end="", flush=True)
                except UnicodeEncodeError:
                    # Replace problematic characters with ASCII alternatives
                    replacements = {'→': '->', '←': '<-', '█': '#', '▓': '%', '░': '=', '♥': '*', '★': '*'}
                    safe_char = replacements.get(char, '?')
                    print(safe_char, end="", flush=True)
                time.sleep(delay)
        print()


def hp_bar(current, maximum, length=20):
    if maximum <= 0:
        return "[--------------------] 0/0"
    filled = max(0, min(length, int((current / maximum) * length)))
    bar = "#" * filled + "-" * (length - filled)
    ratio = current / maximum
    status = "healthy" if ratio > 0.5 else ("wounded" if ratio > 0.25 else "critical")
    return f"[{bar}] {current}/{maximum} ({status})"


# ── Event bus ────────────────────────────────────────────────────────────────

class EventBus:
    def __init__(self):
        self._listeners = []

    def subscribe(self, fn):
        if fn not in self._listeners:
            self._listeners.append(fn)

    def unsubscribe(self, fn):
        self._listeners = [l for l in self._listeners if l is not fn]

    def emit(self, event_type, **data):
        event = {"type": event_type, **data}
        for fn in list(self._listeners):
            try:
                fn(event)
            except Exception:
                pass

    def say(self, text):
        self.emit("text", content=str(text))

    def stat_update(self, **data):
        self.emit("stat_update", **data)

    def combat_event(self, name, **data):
        self.emit("combat", name=name, **data)

    def game_event(self, name, **data):
        self.emit("game", name=name, **data)


def _terminal_listener(event):
    """Default listener — prints text events to the terminal."""
    if event["type"] == "text":
        content = event.get("content", "")
        for char in str(content):
            print(char, end="", flush=True)
            time.sleep(0.005)
        print()


bus = EventBus()
bus.subscribe(_terminal_listener)


# ── GUI mode flag ─────────────────────────────────────────────────────────────

def _gui_active():
    """Returns True once the GUI has been initialised."""
    return input_handler.gui_mode


# ── Input handler ─────────────────────────────────────────────────────────────

class InputHandler:
    """
    Single point for ALL player input in the game.
    Terminal mode : calls input() directly.
    GUI mode      : blocks until push_answer() is called from the GUI thread.
    """

    def __init__(self):
        self._pending = None
        self.gui_mode = False
        self.auto_play_mode = False
        self.in_combat_question = False

    def _wait_for_pending(self):
        while self._pending is None:
            time.sleep(0.02)
        result = self._pending
        self._pending = None
        return result

    def ask(self, prompt=""):
        if not self.gui_mode:
            return input(prompt).strip()
        bus.game_event("hide_choices")
        if prompt:
            bus.game_event("waiting_for_input", prompt=str(prompt))
        return self._wait_for_pending()

    def ask_choice(self, choices, prompt=""):
        if not self.gui_mode:
            return input(prompt).strip()

        normalized = []
        for choice in choices:
            if isinstance(choice, dict):
                label = str(choice.get("label", choice.get("value", "")))
                value = str(choice.get("value", label))
                log = str(choice.get("log", label))
            elif isinstance(choice, (tuple, list)) and len(choice) >= 2:
                label = str(choice[0])
                value = str(choice[1])
                log = label
            else:
                label = str(choice)
                value = label
                log = label
            normalized.append({"label": label, "value": value, "log": log})

        if not normalized:
            return self.ask(prompt)

        # Auto-play mode: randomly select (unless in combat question)
        if self.auto_play_mode and not self.in_combat_question:
            selected = random.choice(normalized)
            bus.game_event("show_choices", options=normalized, auto_selected=selected)
            time.sleep(0.3)  # Brief delay for visibility
            return selected["value"]

        bus.game_event("show_choices", options=normalized)
        return self._wait_for_pending()

    def push_answer(self, answer):
        self._pending = str(answer)

    def toggle_auto_play(self):
        """Toggle auto-play mode on/off and broadcast the state."""
        self.auto_play_mode = not self.auto_play_mode
        bus.game_event("auto_play_toggled", enabled=self.auto_play_mode)
        return self.auto_play_mode

    def set_in_combat_question(self, in_question: bool):
        """Set whether we're currently asking a question in combat."""
        self.in_combat_question = in_question


input_handler = InputHandler()


# ── Player stats broadcast ────────────────────────────────────────────────────

def emit_player_stats(player):
    """Broadcast full player state so the GUI can refresh every panel."""
    bus.stat_update(
        name=player.name,
        class_name=getattr(player, "class_name", ""),
        lvl=player.lvl,
        hp=player.hp,
        max_hp=player.max_hp,
        exp=player.exp,
        xp_to_next=player.xp_to_next,
        gold=player.gold,
        focus=player.focus,
        max_focus=player.max_focus,
        streak=player.streak,
        longest_streak=player.longest_streak,
        atk=player.atk,
        defense=player.defense,
        spd=player.spd,
        wisdom=player.wisdom,
        crit_chance=player.crit_chance,
        shield=getattr(player, "shield", 0),
        inventory=[getattr(i, "name", str(i)) for i in player.inventory],
        status_effects=[e.name for e in player.status_effects],
        run_modifier=getattr(player, "run_modifier", ""),
        class_passive=getattr(player, "class_passive", ""),
    )


# ── ASCII art ─────────────────────────────────────────────────────────────────

GAME_TITLE = r"""
  ____                        ___        _                           _
 / ___| __ _ _ __ ___   ___  / _ \ _ __ | |     ___  __ _ _ __ _ __ (_)_ __   __ _
| |  _ / _` | '_ ` _ \ / _ \| | | | '_ \| |    / _ \/ _` | '__| '_ \| | '_ \ / _` |
| |_| | (_| | | | | | |  __/| |_| | | | | |___|  __/ (_| | |  | | | | | | | | (_| |
 \____|\__,_|_| |_| |_|\___| \___/|_| |_|_____\___|\__,_|_|  |_| |_|_|_| |_|\__, |
                                                                               |___/
"""

GAME_OVER_ART = r"""
  ____                        ___
 / ___| __ _ _ __ ___   ___  / _ \__   _____ _ __
| |  _ / _` | '_ ` _ \ / _ \| | | \ \ / / _ \ '__|
| |_| | (_| | | | | | |  __/| |_| |\ V /  __/ |
 \____|\__,_|_| |_| |_|\___| \___/  \_/ \___|_|
"""


# ── Terminal screens ──────────────────────────────────────────────────────────

def title_screen(last_run_path="last_run.txt"):
    while True:
        clear_screen()
        print("=" * 60)
        print(GAME_TITLE)
        print("=" * 60)
        if os.path.exists(last_run_path):
            try:
                print("\n--- Last Run ---")
                print(open(last_run_path).read().strip())
                print()
            except Exception:
                pass
        typewriter("\n1. Start Game",       0.03)
        typewriter("2. Practice Mode",      0.03)
        typewriter("3. Change Notes Files", 0.03)
        typewriter("4. View Achievements",  0.03)
        typewriter("5. Exit\n",             0.03)
        print("=" * 60)
        m = {"1": "start", "2": "practice", "3": "reconfigure",
             "4": "achievements", "5": "exit"}
        c = input("Enter your choice: ").strip()
        if c in m:
            return m[c]
        typewriter("Invalid choice.", 0.03)
        time.sleep(1)


def game_over_screen():
    while True:
        clear_screen()
        print("=" * 60)
        print(GAME_OVER_ART)
        print("=" * 60)
        typewriter("\n1. Restart", 0.03)
        typewriter("2. Exit\n",   0.03)
        print("=" * 60)
        c = input("Enter your choice: ").strip()
        if c == "1": return True
        if c == "2": return False
        typewriter("Invalid choice.", 0.03)
        time.sleep(1)
