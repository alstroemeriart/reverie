from ui import typewriter

class StatusEffect:
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration

    def on_apply(self, entity):
        """Runs once when effect is applied."""
        pass

    def on_turn_start(self, entity):
        """Runs at start of entity's turn."""
        pass

    def on_turn_end(self, entity):
        """Runs at end of entity's turn."""
        self.duration -= 1

    def on_expire(self, entity):
        """Runs once when effect expires."""
        pass

    def is_expired(self):
        return self.duration <= 0


# -----------------------------------
# Attack Buff
# -----------------------------------
class AttackBuff(StatusEffect):
    def __init__(self, amount, duration):
        super().__init__("Attack Buff", duration)
        self.amount = amount

    def on_apply(self, entity):
        entity.atk += self.amount
        typewriter(f"{entity.name}'s ATK increased by {self.amount}!")

    def on_expire(self, entity):
        entity.atk -= self.amount
        typewriter(f"{entity.name}'s Attack Buff has worn off!")


# -----------------------------------
# Defense Buff
# -----------------------------------
class DefenseBuff(StatusEffect):
    def __init__(self, amount, duration):
        super().__init__("Defense Buff", duration)
        self.amount = amount

    def on_apply(self, entity):
        entity.defense += self.amount
        typewriter(f"{entity.name}'s DEF increased by {self.amount}!")

    def on_expire(self, entity):
        entity.defense -= self.amount
        typewriter(f"{entity.name}'s Defense Buff has worn off!")


# -----------------------------------
# Poison Debuff
# -----------------------------------
class Poison(StatusEffect):
    def __init__(self, damage, duration):
        super().__init__("Poison", duration)
        self.damage = damage

    def on_turn_start(self, entity):
        entity.take_damage(self.damage)
        typewriter(f"{entity.name} takes {self.damage} poison damage!")

    def on_expire(self, entity):
        typewriter(f"{entity.name} is no longer poisoned!")