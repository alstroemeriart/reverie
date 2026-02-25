# items.py
from statusEffects import StatusEffect
from ui import typewriter

class Item:
    """Base class for items."""
    name = "Generic Item"

    def use(self, user, target=None):
        """Apply the item's effect. Must return a string description."""
        return f"{user.name} used {self.name}, but nothing happened."

# Healing Potion
class HealingPotion(Item):
    name = "Healing Potion"

    def __init__(self, heal_amount=20):
        self.heal_amount = heal_amount

    def use(self, user, target=None):
        user.heal(self.heal_amount)
        return f"{user.name} uses Healing Potion and heals {self.heal_amount} HP!"

# Attack Boost (temporary buff)
class AttackBoost(Item):
    name = "Attack Boost"

    def __init__(self, boost_amount=5, duration=3):
        self.boost_amount = boost_amount
        self.duration = duration

    def use(self, user, target=None):
        from statusEffects import AttackBuff
        buff = AttackBuff(self.boost_amount, self.duration)
        user.status_effects.append(buff)
        buff.on_apply(user)
        return f"{user.name} uses Attack Boost! ATK +{self.boost_amount} for {self.duration} turns!"

# Hint Potion (affects questions)
class HintPotion(Item):
    name = "Hint Potion"

    def use(self, user, target=None):
        user.hint_active = True
        return f"{user.name} uses Hint Potion! Your next question will be easier!"