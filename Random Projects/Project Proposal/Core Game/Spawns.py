# SPAWNS

import random
from dataclasses import dataclass, field
from typing import List
from statusEffects import StatusEffect
from items import HealingPotion, AttackBoost, HintPotion
from ui import typewriter

# -----------------------------
# Base Spawn Class
# -----------------------------
@dataclass
class Spawn:
    name: str
    max_hp: int
    atk: int
    defense: int
    spd: int
    gold: int

    hp: int = field(init=False)
    status_effects: List["StatusEffect"] = field(default_factory=list)

    def __post_init__(self):
        self.hp = self.max_hp
        self.shield = 0

    def take_dmg(self, dmg: int):
        if self.shield > 0:
            absorbed = min(self.shield, dmg)
            self.shield -= absorbed
            dmg -= absorbed
            if absorbed > 0:
                typewriter(f"{self.name}'s shield absorbs {absorbed} damage!")
        self.hp = max(0, self.hp - dmg)


    def is_alive(self) -> bool:
        return self.hp > 0

    def heal(self, amount: int):
        self.hp = min(self.max_hp, self.hp + amount)


# -----------------------------
# Player Character
# -----------------------------
class MainCharacter(Spawn):
    def __init__(self, name, max_hp, atk, defense, spd, wisdom, crit_chance, crit_multiplier):
        super().__init__(name, max_hp, atk, defense, spd, 0)
        self.wisdom = wisdom
        self.crit_chance = crit_chance
        self.crit_multiplier = crit_multiplier
        self.class_name = ""
        self.class_passive = ""

        # Progression
        self.lvl = 1
        self.exp = 0
        self.xp_to_next = 100

        # Inventory
        self.inventory = [HealingPotion(), AttackBoost(), HintPotion()]
        self.gold = 10 

        # Combat systems
        self.streak = 0
        self.longest_streak = 0
        self.focus = 0
        self.max_focus = 100
        self.streak_protected = False
        self.action_points = 2
        self.max_action_points = 2

        # Mastery tracking
        self.mastery = {"TF": 0, "MC": 0, "AR": 0, "ID": 0}

        # Hint system
        self.hint_active = False

        self.status_effects = []
        self.shield = 0
        self.is_stunned = False
        self.gold_multiplier = 1.0
        self.has_streak_guard = False

        self.skills = []

    # --- RPG Buffs from Streak ---
    def streak_attack_bonus(self):
        """Extra attack power based on streak."""
        return int(self.atk * (0.01 * self.streak))

    def streak_dodge_bonus(self):
        """Extra dodge chance based on streak."""
        return min(0.005 * self.streak, 0.25)  # cap at +25%

    def shop_discount(self, base_price):
        """Discount in shops based on streak."""
        discount = min(0.01 * (self.streak // 5), 0.25)  # 1% per 5 streak, max 25%
        return int(base_price * (1 - discount))
    
    def apply_gold(self, amount):
        """Apply gold with multiplier from active buffs."""
        actual = int(amount * self.gold_multiplier)
        self.gold += actual
        return actual

    def puzzle_bonus(self):
        """Bonus chance to solve puzzles based on streak."""
        return min(0.02 * self.streak, 0.30)  # up to +30% success chance

    # --- Progression ---
    def is_alive(self):
        return self.hp > 0

    def gain_xp(self, amount):
        self.exp += amount
        typewriter(f"Gained {amount} XP!")
        while self.exp >= self.xp_to_next:
            self.level_up()

    def level_up(self):
        self.exp -= self.xp_to_next
        self.lvl += 1
        self.xp_to_next = int(self.xp_to_next * 1.3)
        self.max_hp += 5
        self.hp = self.max_hp
        typewriter(f"\nLEVEL UP! You are now Level {self.lvl}!")
        typewriter("Choose a stat to boost:")
        typewriter("1. ATK +3")
        typewriter("2. DEF +3")
        typewriter("3. SPD +2")
        typewriter("4. WIS +5 (more focus gain per correct answer)")
        choice = input("> ").strip()
        boosts = {"1": ("atk", 3), "2": ("defense", 3), "3": ("spd", 2), "4": ("wisdom", 5)}
        stat, amount = boosts.get(choice, ("atk", 3))
        setattr(self, stat, getattr(self, stat) + amount)
        typewriter(f"{stat.upper()} increased by {amount}!")

# -----------------------------
# Enemy
# -----------------------------
class Enemy(Spawn):
    def __init__(self, name, hp, atk, defense, spd, crit_chance, behavior="neutral"):
        super().__init__(name, hp, atk, defense, spd, gold=0)
        self.crit_chance = crit_chance
        self.crit_multiplier = 1.5
        self.behavior = behavior

# ------------------------------
# RunState
# ------------------------------
@dataclass
class RunState:
    tier: int = 1
    battles_won: int = 0
    nodes_cleared: int = 0