"""Enemy generation and spawning system.

Defines enemy templates grouped by tier, generates random enemies,
and scales their stats to the player's run progression.
"""

import random
from Spawns import Enemy

# ---------------------------------------------------------------------------
# ENEMY TEMPLATES
# Each dict mirrors Enemy.__init__ keyword args (name, hp, atk, defense,
# speed, crit_chance, behavior). Behavior options: neutral | aggressive |
# evasive | defensive.
# ---------------------------------------------------------------------------

# ── Tier 1 — Early Game ────────────────────────────────────────────────────
TIER_1 = [
    {"name": "Squid",   "hp": 50, "atk": 10, "defense": 3, "speed": 2, "crit_chance": 0.05, "behavior": "neutral"},
    {"name": "Goblin",  "hp": 40, "atk": 12, "defense": 2, "speed": 5, "crit_chance": 0.10, "behavior": "aggressive"},
    {"name": "Wild Rat","hp": 30, "atk":  8, "defense": 1, "speed": 6, "crit_chance": 0.08, "behavior": "evasive"},
    {"name": "Bandit",  "hp": 45, "atk": 11, "defense": 3, "speed": 4, "crit_chance": 0.12, "behavior": "defensive"},
]

# ── Tier 2 — Mid Game ──────────────────────────────────────────────────────
TIER_2 = [
    {"name": "Stone Golem",   "hp": 80, "atk":  8, "defense": 6, "speed": 1, "crit_chance": 0.03, "behavior": "defensive"},
    {"name": "Shadow Sprite", "hp": 35, "atk":  9, "defense": 2, "speed": 8, "crit_chance": 0.20, "behavior": "evasive"},
    {"name": "Orc Brute",     "hp": 90, "atk": 14, "defense": 4, "speed": 2, "crit_chance": 0.07, "behavior": "aggressive"},
    {"name": "Dark Mage",     "hp": 55, "atk": 16, "defense": 3, "speed": 4, "crit_chance": 0.15, "behavior": "neutral"},
]

# ── Tier 3 — Late Game ─────────────────────────────────────────────────────
TIER_3 = [
    {"name": "Executioner",      "hp": 120, "atk": 20, "defense":  5, "speed": 3, "crit_chance": 0.18, "behavior": "aggressive"},
    {"name": "Phantom Assassin", "hp":  75, "atk": 22, "defense":  3, "speed": 9, "crit_chance": 0.25, "behavior": "evasive"},
    {"name": "Ancient Guardian", "hp": 160, "atk": 15, "defense": 10, "speed": 2, "crit_chance": 0.05, "behavior": "defensive"},
]

# ── Elite Pool — Used for elite and boss encounters ────────────────────────
ELITES = [
    {"name": "Cursed Knight", "hp": 140, "atk": 24, "defense": 8, "speed": 4, "crit_chance": 0.20, "behavior": "defensive"},
    {"name": "Void Reaper",   "hp": 110, "atk": 28, "defense": 5, "speed": 7, "crit_chance": 0.30, "behavior": "evasive"},
]

# Tier number → pool mapping (used in generate_random_enemy)
_TIER_POOLS = {1: TIER_1, 2: TIER_2, 3: TIER_3}


def generate_random_enemy(tier: int = 1, elite_chance: float = 0.1) -> Enemy:
    """Pick a random enemy template and return a new Enemy instance.

    With probability ``elite_chance`` the enemy is drawn from the ELITES
    pool regardless of tier, simulating a mini-boss surprise.

    Args:
        tier:         Enemy tier (1–3). Controls which pool is sampled.
        elite_chance: Probability (0.0–1.0) of spawning an elite enemy.

    Returns:
        Enemy: Freshly constructed enemy from the chosen template.

    Raises:
        ValueError: If ``tier`` is not 1, 2, or 3.
    """
    if tier not in _TIER_POOLS and random.random() >= elite_chance:
        raise ValueError(f"Invalid tier {tier!r}. Must be 1, 2, or 3.")

    # Roll for elite spawn first
    if random.random() < elite_chance:
        template = random.choice(ELITES)
    else:
        pool = _TIER_POOLS.get(tier)
        if pool is None:
            raise ValueError(f"Invalid tier {tier!r}. Must be 1, 2, or 3.")
        template = random.choice(pool)

    return Enemy(
        template["name"],
        template["hp"],
        template["atk"],
        template["defense"],
        template["speed"],
        template["crit_chance"],
        template.get("behavior", "neutral"),
    )


def scale_enemy(enemy: Enemy, nodes_cleared: int, tier: int) -> Enemy:
    """Scale an enemy's stats based on how far the player is through the run.

    Prevents early-game enemies from feeling trivial in later nodes.
    Defense is scaled more conservatively than HP/ATK to avoid unkillable enemies.

    Scaling formula:
        scaling = 1 + (nodes_cleared * 0.03) + (tier * 0.1)

    Args:
        enemy:         The Enemy to modify (mutated in place).
        nodes_cleared: Number of nodes already completed in this run.
        tier:          Current difficulty tier (affects base scaling).

    Returns:
        Enemy: The same enemy instance with updated stats.
    """
    # Overall scaling multiplier grows with both nodes and tier
    scaling = 1 + (nodes_cleared * 0.03) + (tier * 0.1)

    enemy.max_hp  = int(enemy.max_hp * scaling)
    enemy.hp      = enemy.max_hp          # Reset HP to scaled maximum
    enemy.atk     = int(enemy.atk * scaling)

    # Defense uses a gentler curve (nodes only, no tier multiplier)
    enemy.defense = int(enemy.defense * (1 + nodes_cleared * 0.01))

    return enemy