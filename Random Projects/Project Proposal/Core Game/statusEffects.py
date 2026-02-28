from ui import typewriter

class StatusEffect:
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration

    # Called once when applied
    def on_apply(self, entity):
        pass

    # Called at start of entity's turn
    def on_turn_start(self, entity):
        pass

    # Called at end of entity's turn
    def on_turn_end(self, entity):
        self.duration -= 1

    # Called once when effect expires
    def on_expire(self, entity):
        pass

    def is_expired(self):
        return self.duration <= 0


# ==========================================
# ATTACK BUFF
# ==========================================
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


# ==========================================
# DEFENSE BUFF
# ==========================================
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


# ==========================================
# POISON (Damage Over Time)
# ==========================================
class Poison(StatusEffect):
    def __init__(self, damage, duration):
        super().__init__("Poison", duration)
        self.damage = damage

    def on_turn_start(self, entity):
        entity.take_dmg(self.damage)
        typewriter(f"{entity.name} takes {self.damage} poison damage!")

    def on_expire(self, entity):
        typewriter(f"{entity.name} is no longer poisoned!")


# ==========================================
# BURN (Damage Over Time)
# ==========================================
class Burn(StatusEffect):
    def __init__(self, damage, duration):
        super().__init__("Burn", duration)
        self.damage = damage

    def on_turn_start(self, entity):
        entity.take_dmg(self.damage)
        typewriter(f"{entity.name} takes {self.damage} burn damage!")

    def on_expire(self, entity):
        typewriter(f"{entity.name} is no longer burning!")


# ==========================================
# REGENERATION (Heal Over Time)
# ==========================================
class Regen(StatusEffect):
    def __init__(self, amount, duration):
        super().__init__("Regeneration", duration)
        self.amount = amount

    def on_turn_start(self, entity):
        entity.hp = min(entity.max_hp, entity.hp + self.amount)
        typewriter(f"{entity.name} regenerates {self.amount} HP!")

    def on_expire(self, entity):
        typewriter(f"{entity.name}'s regeneration faded.")


# ==========================================
# SHIELD (Absorbs Damage)
# ==========================================
class Shield(StatusEffect):
    def __init__(self, amount, duration):
        super().__init__("Shield", duration)
        self.amount = amount

    def on_apply(self, entity):
        entity.shield += self.amount
        typewriter(f"{entity.name} gains a shield of {self.amount}!")

    def on_expire(self, entity):
        entity.shield = max(0, entity.shield - self.amount)
        typewriter(f"{entity.name}'s shield expired.")


# ==========================================
# STUN (Skip Turn)
# ==========================================
class Stun(StatusEffect):
    def __init__(self, duration):
        super().__init__("Stun", duration)

    def on_apply(self, entity):
        entity.is_stunned = True

    def on_expire(self, entity):
        entity.is_stunned = False
        typewriter(f"{entity.name} is no longer stunned!")


# ==========================================
# GOLD BOOST (Utility)
# ==========================================
class GoldBoost(StatusEffect):
    def __init__(self, multiplier, duration):
        super().__init__("Gold Boost", duration)
        self.multiplier = multiplier

    def on_apply(self, entity):
        entity.gold_multiplier *= self.multiplier
        typewriter(f"{entity.name}'s gold gain increased!")

    def on_expire(self, entity):
        entity.gold_multiplier /= self.multiplier
        typewriter("Gold boost has expired.")


# ==========================================
# STREAK GUARD (One-Time Protection)
# ==========================================
class StreakGuard(StatusEffect):
    def __init__(self):
        super().__init__("Streak Guard", 1)

    def on_apply(self, entity):
        entity.has_streak_guard = True
        typewriter("Your next streak loss will be prevented!")

    def on_expire(self, entity):
        entity.has_streak_guard = False
        typewriter("Streak Guard has been used.")

# ==========================================
# SPEED BUFF (Turn Priority / Dodge / Future Scaling)
# ==========================================
class SpeedBuff(StatusEffect):
    def __init__(self, amount, duration):
        super().__init__("Speed Buff", duration)
        self.amount = amount

    def on_apply(self, entity):
        entity.speed += self.amount
        typewriter(f"{entity.name}'s Speed increased by {self.amount}!")

    def on_expire(self, entity):
        entity.speed -= self.amount
        typewriter(f"{entity.name}'s Speed Buff has worn off!")


# ==========================================
# FREEZE (Stronger Stun Variant)
# Skips turn AND reduces defense temporarily
# ==========================================
class Freeze(StatusEffect):
    def __init__(self, duration, defense_reduction=2):
        super().__init__("Freeze", duration)
        self.defense_reduction = defense_reduction

    def on_apply(self, entity):
        entity.is_stunned = True
        entity.defense -= self.defense_reduction
        typewriter(f"{entity.name} is frozen solid!")

    def on_expire(self, entity):
        entity.is_stunned = False
        entity.defense += self.defense_reduction
        typewriter(f"{entity.name} thawed out!")


# ==========================================
# ATTACK DEBUFF (Opposite of Attack Buff)
# ==========================================
class AttackDebuff(StatusEffect):
    def __init__(self, amount, duration):
        super().__init__("Attack Down", duration)
        self.amount = amount

    def on_apply(self, entity):
        entity.atk -= self.amount
        typewriter(f"{entity.name}'s ATK decreased by {self.amount}!")

    def on_expire(self, entity):
        entity.atk += self.amount
        typewriter(f"{entity.name}'s Attack returned to normal!")


# ==========================================
# DOUBLE GOLD (Stronger Version of GoldBoost)
# Always x2
# ==========================================
class DoubleGold(StatusEffect):
    def __init__(self, duration):
        super().__init__("Double Gold", duration)

    def on_apply(self, entity):
        entity.gold_multiplier *= 2
        typewriter(f"{entity.name} will earn DOUBLE gold!")

    def on_expire(self, entity):
        entity.gold_multiplier /= 2
        typewriter("Double Gold has expired.")