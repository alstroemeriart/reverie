# ACHIEVEMENTS

import json
import os

ACHIEVEMENTS_FILE = "achievements.json"

ACHIEVEMENT_DEFINITIONS = [
    {"id": "first_win",      "name": "First Blood",        "desc": "Win your first battle."},
    {"id": "streak_10",      "name": "On a Roll",          "desc": "Reach a streak of 10."},
    {"id": "streak_25",      "name": "Unstoppable",        "desc": "Reach a streak of 25."},
    {"id": "beat_boss",      "name": "Scholar's Victory",  "desc": "Defeat the final boss."},
    {"id": "no_damage",      "name": "Untouchable",        "desc": "Win a battle without taking damage."},
    {"id": "mastery_tf_20",  "name": "True Scholar",       "desc": "Reach 20 TF mastery."},
    {"id": "mastery_mc_20",  "name": "Process of Elimination", "desc": "Reach 20 MC mastery."},
    {"id": "all_types",      "name": "Well Rounded",       "desc": "Answer all 4 question types correctly in one run."},
    {"id": "full_clear",     "name": "Completionist",      "desc": "Clear 15 nodes in a single run."},
    {"id": "broke",          "name": "Penny Pincher",      "desc": "Enter a shop with 0 gold."},
]

def load_achievements():
    if not os.path.exists(ACHIEVEMENTS_FILE):
        return set()
    try:
        with open(ACHIEVEMENTS_FILE, "r") as f:
            data = json.load(f)
        return set(data.get("unlocked", []))
    except Exception:
        return set()

def save_achievements(unlocked):
    try:
        with open(ACHIEVEMENTS_FILE, "w") as f:
            json.dump({"unlocked": list(unlocked)}, f, indent=2)
    except Exception:
        pass

def check_achievements(player, context, unlocked):
    """
    Check all achievement conditions and unlock new ones.
    context = dict with run-level info like battles_won, nodes_cleared etc.
    Returns list of newly unlocked achievement names.
    """
    newly_unlocked = []

    checks = {
        "first_win":     context.get("battles_won", 0) >= 1,
        "streak_10":     player.longest_streak >= 10,
        "streak_25":     player.longest_streak >= 25,
        "beat_boss":     context.get("beat_boss", False),
        "no_damage":     context.get("no_damage_battle", False),
        "mastery_tf_20": player.mastery.get("TF", 0) >= 20,
        "mastery_mc_20": player.mastery.get("MC", 0) >= 20,
        "all_types":     all(player.mastery.get(t, 0) > 0 for t in ["TF","MC","AR","ID"]),
        "full_clear":    context.get("nodes_cleared", 0) >= 15,
        "broke":         context.get("visited_shop_broke", False),
    }

    for ach_id, condition in checks.items():
        if condition and ach_id not in unlocked:
            unlocked.add(ach_id)
            name = next((a["name"] for a in ACHIEVEMENT_DEFINITIONS if a["id"] == ach_id), ach_id)
            newly_unlocked.append(name)

    return newly_unlocked

def print_achievements(unlocked):
    from ui import typewriter
    typewriter("\n--- Achievements ---")
    for ach in ACHIEVEMENT_DEFINITIONS:
        status = "X" if ach["id"] in unlocked else " "
        typewriter(f"  [{status}] {ach['name']} — {ach['desc']}")

        