"""Achievement tracking and management.

Loads, saves, checks, and displays player achievements based on gameplay
milestones and cumulative stats across runs.
"""

import json
import os

ACHIEVEMENTS_FILE = "achievements.json"

# Master list of all achievement definitions.
# Each entry has: id (unique key), name (display name), desc (description).
ACHIEVEMENT_DEFINITIONS = [
    {"id": "first_win",     "name": "First Blood",           "desc": "Win your first battle."},
    {"id": "streak_10",     "name": "On a Roll",             "desc": "Reach a streak of 10."},
    {"id": "streak_25",     "name": "Unstoppable",           "desc": "Reach a streak of 25."},
    {"id": "beat_boss",     "name": "Scholar's Victory",     "desc": "Defeat the final boss."},
    {"id": "no_damage",     "name": "Untouchable",           "desc": "Win a battle without taking damage."},
    {"id": "mastery_tf_20", "name": "True Scholar",          "desc": "Reach 20 TF mastery."},
    {"id": "mastery_mc_20", "name": "Process of Elimination","desc": "Reach 20 MC mastery."},
    {"id": "all_types",     "name": "Well Rounded",          "desc": "Answer all 6 question types correctly in one run."},
    {"id": "full_clear",    "name": "Completionist",         "desc": "Clear 15 nodes in a single run."},
    {"id": "broke",         "name": "Penny Pincher",         "desc": "Enter a shop with 0 gold."},
]


def load_achievements() -> set:
    """Load previously unlocked achievements from disk.

    Reads the achievements JSON file and returns a set of unlocked
    achievement IDs. Returns an empty set if the file doesn't exist
    or is corrupted.

    Returns:
        set: Achievement IDs (strings) that have been unlocked.
    """
    if not os.path.exists(ACHIEVEMENTS_FILE):
        return set()
    try:
        with open(ACHIEVEMENTS_FILE, "r") as f:
            data = json.load(f)
        return set(data.get("unlocked", []))
    except (IOError, OSError, json.JSONDecodeError):
        # Return empty set on any file/parsing error
        return set()


def save_achievements(unlocked: set) -> None:
    """Persist the set of unlocked achievement IDs to disk.

    Silently ignores write errors so a save failure never crashes the game.

    Args:
        unlocked: Set of achievement ID strings to save.
    """
    try:
        with open(ACHIEVEMENTS_FILE, "w") as f:
            json.dump({"unlocked": list(unlocked)}, f, indent=2)
    except (IOError, OSError):
        pass  # Non-fatal: achievements just won't persist this session


def check_achievements(player, context: dict, unlocked: set) -> list:
    """Check all achievement conditions and unlock newly earned ones.

    Evaluates every achievement's condition against the current player state
    and run context. Achievements that are newly satisfied get added to the
    ``unlocked`` set (mutated in place) and their display names returned.

    Args:
        player:   The MainCharacter instance (used for streak, mastery, etc.).
        context:  Dict with run-level info. Expected keys:
                    - ``battles_won``         (int)
                    - ``beat_boss``           (bool)
                    - ``no_damage_battle``    (bool)
                    - ``nodes_cleared``       (int)
                    - ``visited_shop_broke``  (bool)
        unlocked: Mutable set of already-unlocked achievement IDs.
                  New unlocks are added directly to this set.

    Returns:
        list[str]: Display names of achievements newly unlocked this call.
    """
    newly_unlocked = []

    # Map each achievement ID to its unlock condition (bool expression).
    # Only evaluate conditions for achievements not yet unlocked.
    checks = {
        "first_win":     context.get("battles_won", 0) >= 1,
        "streak_10":     player.longest_streak >= 10,
        "streak_25":     player.longest_streak >= 25,
        "beat_boss":     context.get("beat_boss", False),
        "no_damage":     context.get("no_damage_battle", False),
        "mastery_tf_20": player.mastery.get("TF", 0) >= 20,
        "mastery_mc_20": player.mastery.get("MC", 0) >= 20,
        # "Well Rounded": player must have answered every question type at least once
        "all_types":     all(player.mastery.get(t, 0) > 0
                             for t in ["TF", "MC", "AR", "ID", "FB", "OD"]),
        "full_clear":    context.get("nodes_cleared", 0) >= 15,
        "broke":         context.get("visited_shop_broke", False),
    }

    for ach_id, condition in checks.items():
        if condition and ach_id not in unlocked:
            unlocked.add(ach_id)
            # Look up display name; fall back to raw ID if definition is missing
            name = next(
                (a["name"] for a in ACHIEVEMENT_DEFINITIONS if a["id"] == ach_id),
                ach_id,
            )
            newly_unlocked.append(name)

    return newly_unlocked


def print_achievements(unlocked: set) -> None:
    """Print all achievements to the console, marking which are unlocked.

    Args:
        unlocked: Set of unlocked achievement IDs to compare against.
    """
    from ui import typewriter

    typewriter("\n--- Achievements ---")
    for ach in ACHIEVEMENT_DEFINITIONS:
        # [X] = unlocked, [ ] = still locked
        status = "X" if ach["id"] in unlocked else " "
        typewriter(f"  [{status}] {ach['name']} — {ach['desc']}")