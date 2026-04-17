"""Character and entity spawning system.

Defines the base Spawn class and MainCharacter entity with stats, inventory,
progression tracking, and class-specific mechanics.
"""

import random
from dataclasses import dataclass, field
from typing import List
from statusEffects import StatusEffect
from items import HealingPotion, AttackBoost, HintPotion
from ui import typewriter, input_handler, emit_player_stats


@dataclass
class Spawn:
    """Base entity class for characters and enemies.
    
    Attributes:
        name: Entity's display name.
        max_hp: Maximum hit points.
        atk: Attack damage stat.
        defense: Damage reduction stat.
        spd: Speed/dodge chance stat.
        gold: Currency/reward amount.
        hp: Current hit points (initialized to max_hp).
        status_effects: List of active status effects.
        shield: Amount of damage that can be absorbed before HP loss.
    """
    name: str
    max_hp: int
    atk: int
    defense: int
    spd: int
    gold: int

    hp: int = field(init=False)
    status_effects: List["StatusEffect"] = field(default_factory=list)

    def __post_init__(self):
        """Initialize derived fields after dataclass construction."""
        self.hp = self.max_hp
        self.shield = 0

    def take_dmg(self, dmg: int):
        """Reduce HP by damage, applying shield absorption first.
        
        Args:
            dmg: Damage amount to apply.
        """
        if self.shield > 0:
            absorbed = min(self.shield, dmg)
            self.shield -= absorbed
            dmg -= absorbed
            if absorbed > 0:
                typewriter(f"{self.name}'s shield absorbs {absorbed} damage!")
        self.hp = max(0, self.hp - dmg)

    def is_alive(self) -> bool:
        """Check if entity is still alive.
        
        Returns:
            True if hp > 0, False otherwise.
        """
        return self.hp > 0

    def heal(self, amount: int):
        """Restore hit points up to maximum.
        
        Args:
            amount: HP to restore.
        """
        self.hp = min(self.max_hp, self.hp + amount)


class MainCharacter(Spawn):
    """Player character entity with progression, inventory, and specialized mechanics.
    
    Handles player stats, inventory management, skill/mastery progression, focus buildup,
    streaks, and special class-based mechanics.
    """
    def __init__(self, name, max_hp, atk, defense, spd,
                 wisdom, crit_chance, crit_multiplier):
        super().__init__(name, max_hp, atk, defense, spd, 0)
        self.wisdom         = wisdom
        self.crit_chance    = crit_chance
        self.crit_multiplier = crit_multiplier
        self.class_name     = ""
        self.class_passive  = ""
        self.run_modifier   = ""

        # Progression
        self.lvl         = 1
        self.exp         = 0
        self.xp_to_next  = 100

        # Starting inventory
        self.inventory = [HealingPotion(), AttackBoost(), HintPotion()]
        self.gold = 10

        # Combat
        self.streak          = 0
        self.longest_streak  = 0
        self.focus           = 0
        self.max_focus       = 100
        self.streak_protected = False
        self.action_points    = 2
        self.max_action_points = 2
        self.bloodlust_stacks  = 0
        self.dodge_next        = False
        self._momentum_bonus   = 0.0

        # Mastery / skills
        self.mastery = {"TF": 0, "MC": 0, "AR": 0, "ID": 0, "FB": 0, "OD": 0}
        self.skills  = []

        # Status
        self.hint_active     = False
        self.status_effects  = []
        self.is_stunned      = False
        self.gold_multiplier = 1.0
        self.has_streak_guard = False
        self.mc_eliminate    = 0
        self.debug_mode      = False

        # GUI references
        self.engine_ref    = None
        self.session_stats = None

    # ── Streak bonuses ──────────────────────────────────────────────────

    def streak_attack_bonus(self) -> int:
        """Calculate additional ATK from current streak.
        
        Returns:
            Bonus attack damage based on streak counter.
        """
        return int(self.atk * 0.01 * self.streak)

    def streak_dodge_bonus(self) -> float:
        """Calculate dodge bonus from current streak, capped at 25%.
        
        Returns:
            Additional dodge chance (0.0 to 0.25) based on streak.
        """
        return min(0.005 * self.streak, 0.25)

    def shop_discount(self, base_price: int) -> int:
        """Calculate discounted price based on streak, capped at 25% off.
        
        Args:
            base_price: Original item price.
        
        Returns:
            Discounted price.
        """
        discount = min(0.01 * (self.streak // 5), 0.25)
        return int(base_price * (1 - discount))

    def apply_gold(self, amount: int) -> int:
        """Add gold to inventory, applying multiplier.
        
        Args:
            amount: Base gold amount.
        
        Returns:
            Actual gold added (after multiplier applied).
        """
        actual = int(amount * self.gold_multiplier)
        self.gold += actual
        return actual

    def puzzle_bonus(self) -> float:
        """Calculate puzzle difficulty bonus from streak, capped at 30%.
        
        Returns:
            Difficulty reduction (0.0 to 0.30) based on streak.
        """
        return min(0.02 * self.streak, 0.30)

    # ── Progression ─────────────────────────────────────────────────────

    def is_alive(self):
        return self.hp > 0

    def gain_xp(self, amount: int):
        """Add experience points and handle level-up progression.
        
        Args:
            amount: XP to add. Triggers level_up() if threshold exceeded.
        """
        self.exp += amount
        typewriter(f"Gained {amount} XP! ({self.exp}/{self.xp_to_next})")
        while self.exp >= self.xp_to_next:
            self.level_up()
        emit_player_stats(self)   # refresh GUI after XP gain

    def level_up(self):
        """Advance to next level and grant stat boost choice.
        
        Increases max HP, resets XP counter, scales XP threshold, and
        prompts player to choose a stat to increase.
        """
        self.exp -= self.xp_to_next
        self.lvl += 1
        self.xp_to_next = int(self.xp_to_next * 1.3)
        self.max_hp += 5
        self.hp = self.max_hp

        typewriter(f"\n*** LEVEL UP! You are now Level {self.lvl}! ***")
        typewriter("Choose a stat to boost:")
        typewriter("1. ATK +3")
        typewriter("2. DEF +3")
        typewriter("3. SPD +2")
        typewriter("4. WIS +5")

        # Uses input_handler so the GUI can intercept
        choice = input_handler.ask_choice(
            [
                {"label": "1. ATK +3", "value": "1"},
                {"label": "2. DEF +3", "value": "2"},
                {"label": "3. SPD +2", "value": "3"},
                {"label": "4. WIS +5", "value": "4"},
            ],
            "> ",
        )
        boosts = {"1": ("atk", 3), "2": ("defense", 3),
                  "3": ("spd", 2),  "4": ("wisdom", 5)}
        stat, amt = boosts.get(choice, ("atk", 3))
        setattr(self, stat, getattr(self, stat) + amt)
        typewriter(f"{stat.upper()} increased by {amt}!")
        emit_player_stats(self)


class Enemy(Spawn):
    """NPC enemy entity with combat behavior.
    
    Attributes:
        crit_chance: Probability of critical hit (0.0-1.0).
        crit_multiplier: Damage multiplier on critical hits.
        behavior: AI behavior type (e.g., 'neutral', 'aggressive').
        defense_bonus: Temporary defense increase.
        dodge_modifier: Temporary dodge chance modification.
        is_stunned: Whether enemy is currently stunned.
    """
    def __init__(self, name, hp, atk, defense, spd,
                 crit_chance, behavior="neutral"):
        super().__init__(name, hp, atk, defense, spd, gold=0)
        self.crit_chance    = crit_chance
        self.crit_multiplier = 1.5
        self.behavior       = behavior
        self.defense_bonus  = 0
        self.dodge_modifier = 0.0
        self.is_stunned     = False


@dataclass
class RunState:
    """Tracks state and progress for a single game run.
    
    Attributes:
        tier: Current difficulty tier (1-5 typically).
        battles_won: Number of enemies defeated.
        nodes_cleared: Number of map nodes explored.
    """
    tier: int = 1
    battles_won: int = 0
    nodes_cleared: int = 0
