import json
import os
from ui import typewriter

SAVE_FILE = "savegame.json"

def save_game(player, run_state, save_path="savegame.json"):
    """Save current run to a JSON file."""
    data = {
        "player": {
            "name": player.name,
            "max_hp": player.max_hp,
            "hp": player.hp,
            "atk": player.atk,
            "defense": player.defense,
            "spd": player.spd,
            "wisdom": player.wisdom,
            "crit_chance": player.crit_chance,
            "crit_multiplier": player.crit_multiplier,
            "lvl": player.lvl,
            "exp": player.exp,
            "xp_to_next": player.xp_to_next,
            "gold": player.gold,
            "streak": player.streak,
            "longest_streak": player.longest_streak,
            "focus": player.focus,
            "max_focus": player.max_focus,
            "mastery": player.mastery,
            "action_points": player.max_action_points,
            "inventory": [
                {"name": item.name, "price": item.price}
                for item in player.inventory
            ],
        },
        "run": {
            "tier": run_state["tier"],
            "battles_won": run_state["battles_won"],
            "nodes_cleared": run_state["nodes_cleared"],
        }
    }

    try:
        with open(save_path, "w") as f:
            json.dump(data, f, indent=2)
        typewriter("Game saved.")
    except Exception as e:
        typewriter(f"Save failed: {e}")


def load_game(save_path="savegame.json"):
    """
    Load a saved run. Returns (player_data, run_data) dicts or (None, None).
    The caller reconstructs the player object from player_data.
    """
    if not os.path.exists(save_path):
        return None, None

    try:
        with open(save_path, "r") as f:
            data = json.load(f)
        typewriter("Save file found.")
        return data["player"], data["run"]
    except Exception as e:
        typewriter(f"Load failed: {e}")
        return None, None


def delete_save(save_path="savegame.json"):
    """Remove the save file after a run ends."""
    if os.path.exists(save_path):
        os.remove(save_path)


def save_exists(save_path="savegame.json"):
    return os.path.exists(save_path)

