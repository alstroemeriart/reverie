import random
from Spawns import Enemy

ENEMY_TEMPLATES = [
    {
        "name": "Squid",
        "hp": 50,
        "atk": 10,
        "defense": 3,
        "speed": 2,
        "crit_chance": 0.05
    },
    {
        "name": "Goblin",
        "hp": 40,
        "atk": 12,
        "defense": 2,
        "speed": 5,
        "crit_chance": 0.10
    },
    {
        "name": "Stone Golem",
        "hp": 80,
        "atk": 8,
        "defense": 6,
        "speed": 1,
        "crit_chance": 0.03
    },
    {
        "name": "Shadow Sprite",
        "hp": 35,
        "atk": 9,
        "defense": 2,
        "speed": 8,
        "crit_chance": 0.20
    }
]

def generate_random_enemy():
    template = random.choice(ENEMY_TEMPLATES)

    return Enemy(
        template["name"],
        template["hp"],
        template["atk"],
        template["defense"],
        template["speed"],
        template["crit_chance"]
    )