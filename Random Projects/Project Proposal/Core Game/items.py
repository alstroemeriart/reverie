# items.py
from statusEffects import StatusEffect
from ui import typewriter
import random

class Item:
    """Base class for items."""
    name = "Generic Item"
    price = 10  # default shop price

    def use(self, user, target=None):
        return f"{user.name} used {self.name}, but nothing happened."

# =========================
# HEALING ITEMS
# =========================

class HealingPotion(Item):
    name = "Healing Potion"
    price = 15

    def __init__(self, heal_amount=20):
        self.heal_amount = heal_amount

    def use(self, user, target=None):
        user.heal(self.heal_amount)
        return f"{user.name} heals {self.heal_amount} HP!"

class MegaHealingPotion(Item):
    name = "Mega Healing Potion"
    price = 35

    def __init__(self, heal_amount=50):
        self.heal_amount = heal_amount

    def use(self, user, target=None):
        user.heal(self.heal_amount)
        return f"{user.name} restores {self.heal_amount} HP!"
    
# =========================
# BUFF ITEMS
# =========================

class AttackBoost(Item):
    name = "Attack Boost"
    price = 25

    def __init__(self, boost_amount=5, duration=3):
        self.boost_amount = boost_amount
        self.duration = duration

    def use(self, user, target=None):
        from statusEffects import AttackBuff
        buff = AttackBuff(self.boost_amount, self.duration)
        user.status_effects.append(buff)
        buff.on_apply(user)
        return f"ATK +{self.boost_amount} for {self.duration} turns!"

class DefenseBoost(Item):
    name = "Defense Boost"
    price = 25

    def __init__(self, boost_amount=5, duration=3):
        self.boost_amount = boost_amount
        self.duration = duration

    def use(self, user, target=None):
        from statusEffects import DefenseBuff
        buff = DefenseBuff(self.boost_amount, self.duration)
        user.status_effects.append(buff)
        buff.on_apply(user)
        return f"DEF +{self.boost_amount} for {self.duration} turns!"

class SpeedBoost(Item):
    name = "Speed Boost"
    price = 30

    def __init__(self, boost_amount=3, duration=3):
        self.boost_amount = boost_amount
        self.duration = duration

    def use(self, user, target=None):
        from statusEffects import SpeedBuff
        buff = SpeedBuff(self.boost_amount, self.duration)
        user.status_effects.append(buff)
        buff.on_apply(user)
        return f"SPD +{self.boost_amount} for {self.duration} turns!"

# =========================
# DEBUFF ITEMS (Require New Status Effects)
# =========================

class PoisonBomb(Item):
    name = "Poison Bomb"
    price = 30

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

class FreezeScroll(Item):
    name = "Freeze Scroll"
    price = 35

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

class WeaknessCurse(Item):
    name = "Weakness Curse"
    price = 30

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

class HintPotion(Item):
    name = "Hint Potion"
    price = 20

    def use(self, user, target=None):
        user.hint_active = True
        return "Your next question will be easier!"

class DoubleGoldCharm(Item):
    name = "Double Gold Charm"
    price = 40

    def __init__(self, duration=3):
        self.duration = duration

    def use(self, user, target=None):
        from statusEffects import DoubleGold
        buff = DoubleGold(self.duration)
        user.status_effects.append(buff)
        buff.on_apply(user)
        return f"Gold rewards doubled for {self.duration} turns!"

class RevivalStone(Item):
    name = "Revival Stone"
    price = 50

    def use(self, user, target=None):
        if user.hp <= 0:
            user.hp = user.max_hp // 2
            return f"{user.name} is revived with {user.hp} HP!"
        return "Nothing happened."
    
AllItems = [
    {"class": HealingPotion, "name": "Healing Potion", "rarity": "common"},
    {"class": MegaHealingPotion, "name": "Mega Healing Potion", "rarity": "uncommon"},
    {"class": AttackBoost, "name": "Attack Boost", "rarity": "uncommon"},
    {"class": DefenseBoost, "name": "Defense Boost", "rarity": "uncommon"},
    {"class": SpeedBoost, "name": "Speed Boost", "rarity": "uncommon"},
    {"class": PoisonBomb, "name": "Poison Bomb", "rarity": "rare"},
    {"class": FreezeScroll, "name": "Freeze Scroll", "rarity": "rare"},
    {"class": WeaknessCurse, "name": "Weakness Curse", "rarity": "rare"},
    {"class": HintPotion, "name": "Hint Potion", "rarity": "common"},
    {"class": DoubleGoldCharm, "name": "Double Gold Charm", "rarity": "rare"},
    {"class": RevivalStone, "name": "Revival Stone", "rarity": "legendary"},
]