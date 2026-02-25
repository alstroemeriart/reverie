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
    def __init__(self, name: str, max_hp: int = 100, atk: int = 10, defense: int = 5, spd: int = 5, int = 10, gold: int = 0):
        # If the name is "DEBUG" (or any keyword you choose), create OP stats
        if name.upper() == "Rynier143":
            super().__init__(name, max_hp=999, atk=999, defense=999, spd=999, gold=999)
            self.exp = 999
            self.LVL = 99
            self.crit_chance = 1
            self.crit_multiplier = 3
            self.inventory = ["Ultra Potion", "Mega Elixir", "Debug Scroll"]
        else:
            super().__init__(name, max_hp, atk, defense, spd, gold)
            self.exp = 0
            self.LVL = 1
            self.crit_chance = 0.5
            self.crit_multiplier = 1.5
            self.inventory = []

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
    
