# ENEMY POOL

import random
from Spawns import Enemy

# -------------------------
# TIER 1 – Early Game
# -------------------------
TIER_1 = [
    {"name": "Squid", "hp": 50, "atk": 10, "defense": 3, "speed": 2, "crit_chance": 0.05, "behavior": "neutral"},
    {"name": "Goblin", "hp": 40, "atk": 12, "defense": 2, "speed": 5, "crit_chance": 0.10, "behavior": "aggressive"},
    {"name": "Wild Rat", "hp": 30, "atk": 8, "defense": 1, "speed": 6, "crit_chance": 0.08, "behavior": "evasive"},
    {"name": "Bandit", "hp": 45, "atk": 11, "defense": 3, "speed": 4, "crit_chance": 0.12, "behavior": "defensive"}
]

# -------------------------
# TIER 2 – Mid Game
# -------------------------
TIER_2 = [
    {"name": "Stone Golem", "hp": 80, "atk": 8, "defense": 6, "speed": 1, "crit_chance": 0.03, "behavior": "defensive"},
    {"name": "Shadow Sprite", "hp": 35, "atk": 9, "defense": 2, "speed": 8, "crit_chance": 0.20, "behavior": "evasive"},
    {"name": "Orc Brute", "hp": 90, "atk": 14, "defense": 4, "speed": 2, "crit_chance": 0.07, "behavior": "aggressive"},
    {"name": "Dark Mage", "hp": 55, "atk": 16, "defense": 3, "speed": 4, "crit_chance": 0.15, "behavior": "neutral"}
]

# -------------------------
# TIER 3 – Late Game
# -------------------------
TIER_3 = [
    {"name": "Executioner", "hp": 120, "atk": 20, "defense": 5, "speed": 3, "crit_chance": 0.18, "behavior": "aggressive"},
    {"name": "Phantom Assassin", "hp": 75, "atk": 22, "defense": 3, "speed": 9, "crit_chance": 0.25, "behavior": "evasive"},
    {"name": "Ancient Guardian", "hp": 160, "atk": 15, "defense": 10, "speed": 2, "crit_chance": 0.05, "behavior": "defensive"}
]

# -------------------------
# ELITE POOL
# -------------------------
ELITES = [
    {"name": "Cursed Knight", "hp": 140, "atk": 24, "defense": 8, "speed": 4, "crit_chance": 0.20, "behavior": "defensive"},
    {"name": "Void Reaper", "hp": 110, "atk": 28, "defense": 5, "speed": 7, "crit_chance": 0.30, "behavior": "evasive"}
]

# -------------------------
# Generate Enemy
# -------------------------
def generate_random_enemy(tier=1, elite_chance=0.1):
    """
    tier: 1, 2, or 3
    elite_chance: % chance to spawn elite
    """

    if random.random() < elite_chance:
        template = random.choice(ELITES)
    else:
        if tier == 1:
            template = random.choice(TIER_1)
        elif tier == 2:
            template = random.choice(TIER_2)
        elif tier == 3:
            template = random.choice(TIER_3)
        else:
            raise ValueError("Invalid tier. Tier be either 1, 2, or 3.")

    return Enemy(
        template["name"],
        template["hp"],
        template["atk"],
        template["defense"],
        template["speed"],
        template["crit_chance"],
        template.get("behavior", "neutral")
    )

def scale_enemy(enemy, nodes_cleared, tier):
    """
    Lightly scale enemy stats based on how far into the run we are.
    Prevents early enemies from feeling trivial late-game.
    """
    scaling = 1 + (nodes_cleared * 0.03) + (tier * 0.1)
    enemy.max_hp = int(enemy.max_hp * scaling)
    enemy.hp = enemy.max_hp
    enemy.atk = int(enemy.atk * scaling)
    # Defense scales slower — avoid making enemies unkillable
    enemy.defense = int(enemy.defense * (1 + (nodes_cleared * 0.01)))
    return enemy

