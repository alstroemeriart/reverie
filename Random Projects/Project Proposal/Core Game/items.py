"""Item and aid system.

Defines all consumable and utility items including healing potions, stat boosts,
status effect items, and special utility items used in combat and exploration.
"""

from statusEffects import StatusEffect
from ui import typewriter
import random

class Aid:
    """Base class for consumable and utility items.
    
    Attributes:
        name: Display name of the item.
        description: Short description of the item's effect.
        price: Gold cost to purchase from shop.
        flavor_texts: List of drop message templates.
    """
    name = "Generic Aid"
    description = "Does something."
    price = 10
    flavor_texts = ["You found a {name}!"]  # Drop messages

    def use(self, user, target=None) -> str:
        """Apply the item's effect to the user.
        
        Args:
            user: Character using the item.
            target: Optional target for the item effect.
        
        Returns:
            Message describing the item usage.
        """
        return ""
    
    def get_drop_message(self):
        """Get a flavor text message for when item is dropped."""
        message = random.choice(self.flavor_texts)
        return message.format(name=self.name)


# =========================
# HEALING ITEMS
# =========================

class HealingPotion(Aid):
    """Consumable item that restores 20 HP.
    
    Standard healing potion. Entry-level aid item for early runs.
    Attributes:
        heal_amount (int): HP to restore. Defaults to 20.
    """
    name = "Healing Potion"
    description = "Restores 20 HP."
    price = 15
    flavor_texts = [
        "The air smells of herbs. A {name} materializes.",
        "A glowing vial of {name} drops before you.",
        "Lucky! A {name} appears!"
    ]

    def __init__(self, heal_amount=20):
        self.heal_amount = heal_amount

    def use(self, user, target=None):
        """Restore hit points to the user."""
        user.heal(self.heal_amount)
        return f"{user.name} heals {self.heal_amount} HP!"

class MegaHealingPotion(Aid):
    """Consumable item that restores 50 HP (stronger healing).
    
    Rare higher-tier healing potion for mid/late game runs.
    Restores 2.5x HP of standard HealingPotion.
    
    Attributes:
        heal_amount (int): HP to restore. Defaults to 50.
    """
    name = "Mega Healing Potion"
    description = "Restores 50 HP."
    price = 35
    flavor_texts = [
        "A surge of magical energy! {name} materializes!",
        "You feel incredibly lucky... {name} drops!",
        "The gods smile upon you. {name} appears!"
    ]

    def __init__(self, heal_amount=50):
        self.heal_amount = heal_amount

    def use(self, user, target=None):
        """Restore hit points to the user."""
        user.heal(self.heal_amount)
        return f"{user.name} restores {self.heal_amount} HP!"

# =========================
# BUFF ITEMS
# =========================

class AttackBoost(Aid):
    """Consumable item that grants temporary ATK +5 buff for 3 turns.
    
    Applies a temporary stat buff via status effect system. Useful for
    burst damage on difficult enemies. Stacks with skill bonuses.
    
    Attributes:
        boost_amount (int): ATK increase. Defaults to 5.
        duration (int): Turns the buff lasts. Defaults to 3.
    """
    name = "Attack Boost"
    description = "ATK +5 for 3 turns."
    price = 25
    flavor_texts = [
        "Your muscles tingle... {name} drops.",
        "Power surges through the air. {name} appears!",
        "A fierce aura materializes. {name} emerges!"
    ]

    def __init__(self, boost_amount=5, duration=3):
        self.boost_amount = boost_amount
        self.duration = duration

    def use(self, user, target=None):
        """Apply a temporary attack buff via status effect.
        
        Args:
            user: The character using the item (receives buff)
            target: Unused (kept for interface compatibility)
            
        Returns:
            str: Message describing the buff application
        """
        from statusEffects import AttackBuff
        buff = AttackBuff(self.boost_amount, self.duration)
        user.status_effects.append(buff)
        buff.on_apply(user)
        return f"ATK +{self.boost_amount} for {self.duration} turns!"

class DefenseBoost(Aid):
    """Consumable item that grants temporary DEF +5 buff for 3 turns.
    
    Applies a temporary defense buff via status effect system. Useful for
    surviving heavy enemy attacks. Reduces damage taken by damage reduction %.
    
    Attributes:
        boost_amount (int): DEF increase. Defaults to 5.
        duration (int): Turns the buff lasts. Defaults to 3.
    """
    name = "Defense Boost"
    description = "DEF +5 for 3 turns."
    price = 25
    flavor_texts = [
        "A barrier crystallizes before you. {name} appears!",
        "Stone and steel shimmer... {name} drops.",
        "An impenetrable aura surrounds you. {name} materializes!"
    ]

    def __init__(self, boost_amount=5, duration=3):
        self.boost_amount = boost_amount
        self.duration = duration

    def use(self, user, target=None):
        """Apply a temporary defense buff via status effect.
        
        Args:
            user: The character using the item (receives buff)
            target: Unused (kept for interface compatibility)
            
        Returns:
            str: Message describing the buff application
        """
        from statusEffects import DefenseBuff
        buff = DefenseBuff(self.boost_amount, self.duration)
        user.status_effects.append(buff)
        buff.on_apply(user)
        return f"DEF +{self.boost_amount} for {self.duration} turns!"

class SpeedBoost(Aid):
    """Consumable item that grants temporary SPD +3 buff for 3 turns.
    
    Applies a temporary speed buff via status effect system. Improves dodge
    chance and turn order priority. Useful for kiting difficult enemies.
    
    Attributes:
        boost_amount (int): SPD increase. Defaults to 3.
        duration (int): Turns the buff lasts. Defaults to 3.
    """
    name = "Speed Boost"
    description = "SPD +3 for 3 turns. Improves dodge."
    price = 30
    flavor_texts = [
        "Everything blurs into motion. {name} appears!",
        "Wind swirls around you... {name} drops!",
        "The world slows down. {name} materializes!"
    ]

    def __init__(self, boost_amount=3, duration=3):
        self.boost_amount = boost_amount
        self.duration = duration

    def use(self, user, target=None):
        """Apply a temporary speed buff via status effect.
        
        Args:
            user: The character using the item (receives buff)
            target: Unused (kept for interface compatibility)
            
        Returns:
            str: Message describing the buff application
        """
        from statusEffects import SpeedBuff
        buff = SpeedBuff(self.boost_amount, self.duration)
        user.status_effects.append(buff)
        buff.on_apply(user)
        return f"SPD +{self.boost_amount} for {self.duration} turns!"

# =========================
# DEBUFF ITEMS
# =========================

class PoisonBomb(Aid):
    name = "Poison Bomb"
    description = "Poisons enemy for 4 turns (5 dmg/turn)."
    price = 30
    flavor_texts = [
        "A sickly purple haze settles... {name} drops!",
        "The stench of corruption fills the air. {name} appears!",
        "Toxic fumes swirl about. {name} materializes!"
    ]

    def __init__(self, damage_per_turn=5, duration=4):
        self.damage_per_turn = damage_per_turn
        self.duration = duration

    def use(self, user, target=None):
        if target is None:
            return "No target selected!"
        from statusEffects import Poison
        poison = Poison(self.damage_per_turn, self.duration)
        target.status_effects.append(poison)
        poison.on_apply(target)
        return f"{target.name} is poisoned for {self.duration} turns!"

class FreezeScroll(Aid):
    name = "Freeze Scroll"
    description = "Stuns enemy and lowers their DEF for 1 turn."
    price = 35
    flavor_texts = [
        "Ice crystals form before you. {name} appears!",
        "Everything freezes in an instant... {name} drops!",
        "A chilling wind blows. {name} materializes!"
    ]

    def __init__(self, duration=1):
        self.duration = duration

    def use(self, user, target=None):
        if target is None:
            return "No target selected!"
        from statusEffects import Freeze
        freeze = Freeze(self.duration)
        target.status_effects.append(freeze)
        freeze.on_apply(target)
        return f"{target.name} is frozen and skips {self.duration} turn(s)!"

class WeaknessCurse(Aid):
    name = "Weakness Curse"
    description = "Reduces enemy ATK by 5 for 3 turns."
    price = 30
    flavor_texts = [
        "A dark curse spreads... {name} drops!",
        "Weakness seeps into your enemy. {name} appears!",
        "The enemy's strength fades. {name} materializes!"
    ]

    def __init__(self, reduction=5, duration=3):
        self.reduction = reduction
        self.duration = duration

    def use(self, user, target=None):
        if target is None:
            return "No target selected!"
        from statusEffects import AttackDebuff
        debuff = AttackDebuff(self.reduction, self.duration)
        target.status_effects.append(debuff)
        debuff.on_apply(target)
        return f"{target.name}'s ATK reduced by {self.reduction} for {self.duration} turns!"

# =========================
# SPECIAL ITEMS
# =========================

class HintPotion(Aid):
    name = "Hint Potion"
    description = "Gives a hint on your next question."
    price = 20
    flavor_texts = [
        "Clarity shines brightly... {name} drops!",
        "Knowledge whispers around you. {name} appears!",
        "The path forward becomes clear. {name} materializes!"
    ]

    def use(self, user, target=None):
        user.hint_active = True
        return "Your next question will come with a hint!"

class DoubleGoldCharm(Aid):
    name = "Double Gold Charm"
    description = "Doubles gold earned for 3 turns."
    price = 40
    flavor_texts = [
        "Gold glimmers in the light... {name} drops!",
        "Prosperity blooms around you. {name} appears!",
        "Riches are yours to claim! {name} materializes!"
    ]

    def __init__(self, duration=3):
        self.duration = duration

    def use(self, user, target=None):
        from statusEffects import DoubleGold
        buff = DoubleGold(self.duration)
        user.status_effects.append(buff)
        buff.on_apply(user)
        return f"Gold rewards doubled for {self.duration} turns!"

class RevivalStone(Aid):
    name = "Revival Stone"
    description = "Fully restores your HP."
    price = 50
    flavor_texts = [
        "A legendary stone of resurrection appears!",
        "The gods grant you a second chance. {name} materializes!",
        "Rebirth energy flows... {name} drops!"
    ]

    def use(self, user, target=None):
        healed = user.max_hp - user.hp
        user.hp = user.max_hp
        return f"{user.name} is fully restored! ({healed} HP recovered)"


AllItems = [
    {"class": HealingPotion,    "name": "Healing Potion",    "rarity": "common"},
    {"class": MegaHealingPotion,"name": "Mega Healing Potion","rarity": "uncommon"},
    {"class": AttackBoost,      "name": "Attack Boost",       "rarity": "uncommon"},
    {"class": DefenseBoost,     "name": "Defense Boost",      "rarity": "uncommon"},
    {"class": SpeedBoost,       "name": "Speed Boost",        "rarity": "uncommon"},
    {"class": PoisonBomb,       "name": "Poison Bomb",        "rarity": "rare"},
    {"class": FreezeScroll,     "name": "Freeze Scroll",      "rarity": "rare"},
    {"class": WeaknessCurse,    "name": "Weakness Curse",     "rarity": "rare"},
    {"class": HintPotion,       "name": "Hint Potion",        "rarity": "common"},
    {"class": DoubleGoldCharm,  "name": "Double Gold Charm",  "rarity": "rare"},
    {"class": RevivalStone,     "name": "Revival Stone",      "rarity": "legendary"},
]

