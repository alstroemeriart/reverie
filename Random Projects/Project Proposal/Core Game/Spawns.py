from dataclasses import dataclass, field
from typing import List
import random, time
from statusEffects import StatusEffect

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

    def take_dmg(self, dmg: int):
        """Apply damage, accounting for defense, minimum 1."""
        self.hp -= max(0, dmg - self.defense)
        
    def is_alive(self) -> bool:
        return self.hp > 0
    
    def heal(self, amount: int):
        self.hp = min(self.max_hp, self.hp + amount)

from items import HealingPotion, AttackBoost, HintPotion

class MainCharacter(Spawn):
    def __init__(self, name, max_hp, atk, defense, speed, wisdom, crit_chance, crit_multiplier):
        super().__init__(name, max_hp, atk, defense, speed, 0)
        self.wisdom = wisdom
        self.crit_chance = crit_chance
        self.crit_multiplier = crit_multiplier

        # Leveling and progression
        self.lvl = 1
        self.exp = 0
        self.gain_xp = self.exp
        self.xp_to_next = 100

        self.inventory = [HealingPotion(), AttackBoost(), HintPotion()]

        self.status_effects = []

        def is_alive(self):
            return self.hp > 0
        
        def gain_xp(self, amount):
            self.xp += amount
            print(f"Gained {amount} XP!")

            while self.xp >= self.xp_to_next:
                self.level_up()

        def level_up(self):
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = int(self.xp_to_next * 1.3)

            # Stat scaling per level
            self.max_hp += 10
            self.atk += 2
            self.defense += 1
            self.spd += 1

            self.hp = self.max_hp

            print(f"\nLEVEL UP! You are now level {self.level}!")
        

class Enemy(Spawn):
    def __init__(self, name, hp, atk, defense, speed, crit_chance):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.defense = defense

        self.spd = speed
        self.crit_chance = crit_chance
        self.crit_multiplier = 1.5

        self.status_effects = []

    def is_alive(self):
        return self.hp > 0
    
