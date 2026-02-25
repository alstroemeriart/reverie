import random
from Spawns import Enemy

# -------------------------
# TIER 1 – Early Game
# -------------------------
TIER_1 = [
    {"name": "Squid", "hp": 50, "atk": 10, "defense": 3, "speed": 2, "crit_chance": 0.05},
    {"name": "Goblin", "hp": 40, "atk": 12, "defense": 2, "speed": 5, "crit_chance": 0.10},
    {"name": "Wild Rat", "hp": 30, "atk": 8, "defense": 1, "speed": 6, "crit_chance": 0.08},
    {"name": "Bandit", "hp": 45, "atk": 11, "defense": 3, "speed": 4, "crit_chance": 0.12}
]

# -------------------------
# TIER 2 – Mid Game
# -------------------------
TIER_2 = [
    {"name": "Stone Golem", "hp": 80, "atk": 8, "defense": 6, "speed": 1, "crit_chance": 0.03},
    {"name": "Shadow Sprite", "hp": 35, "atk": 9, "defense": 2, "speed": 8, "crit_chance": 0.20},
    {"name": "Orc Brute", "hp": 90, "atk": 14, "defense": 4, "speed": 2, "crit_chance": 0.07},
    {"name": "Dark Mage", "hp": 55, "atk": 16, "defense": 3, "speed": 4, "crit_chance": 0.15}
]

# -------------------------
# TIER 3 – Late Game
# -------------------------
TIER_3 = [
    {"name": "Executioner", "hp": 120, "atk": 20, "defense": 5, "speed": 3, "crit_chance": 0.18},
    {"name": "Phantom Assassin", "hp": 75, "atk": 22, "defense": 3, "speed": 9, "crit_chance": 0.25},
    {"name": "Ancient Guardian", "hp": 160, "atk": 15, "defense": 10, "speed": 2, "crit_chance": 0.05}
]

# -------------------------
# ELITE POOL
# -------------------------
ELITES = [
    {"name": "Cursed Knight", "hp": 140, "atk": 24, "defense": 8, "speed": 4, "crit_chance": 0.20},
    {"name": "Void Reaper", "hp": 110, "atk": 28, "defense": 5, "speed": 7, "crit_chance": 0.30}
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
        else:
            template = random.choice(TIER_3)

    return Enemy(
        template["name"],
        template["hp"],
        template["atk"],
        template["defense"],
        template["speed"],
        template["crit_chance"]
    )