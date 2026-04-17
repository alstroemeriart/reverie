"""Status effects and status system.

Defines all status effects (buffs, debuffs, damage-over-time) and the base
StatusEffect class with hooks for apply, turn-start, turn-end, and expire events.
"""

from ui import typewriter


class StatusEffect:
    """Base class for all status effects (buffs, debuffs, DOT effects).
    
    Provides lifecycle hooks for apply, turn-start, turn-end, and expire events.
    All subclasses should override the appropriate hooks for their behavior.
    
    Attributes:
        name (str): Display name of the effect.
        duration (int): Remaining turns this effect is active.
    """
    def __init__(self, name, duration):
        """Initialize a status effect.
        
        Args:
            name (str): Display name for the effect.
            duration (int): Number of turns the effect lasts.
        """
        self.name = name
        self.duration = duration

    def on_apply(self, entity):
        """Called once when the effect is first applied to an entity.
        
        Args:
            entity: The entity receiving this effect.
        """
        pass

    def on_turn_start(self, entity):
        """Called at the start of the entity's turn.
        
        Args:
            entity: The entity with this effect.
        """
        pass

    def on_turn_end(self, entity):
        """Called at the end of the entity's turn. Default decrements duration.
        
        Args:
            entity: The entity with this effect.
        """
        self.duration -= 1

    def on_expire(self, entity):
        """Called once when the effect expires (duration reaches 0).
        
        Args:
            entity: The entity no longer affected.
        """
        pass

    def is_expired(self):
        """Check if this effect has expired.
        
        Returns:
            bool: True if duration <= 0, False otherwise.
        """
        return self.duration <= 0


# ==========================================
# ATTACK BUFF
# ==========================================
class AttackBuff(StatusEffect):
    """Status effect that increases entity's attack damage.
    
    Attributes:
        amount (int): Attack points added to entity.
    """
    def __init__(self, amount, duration):
        """Initialize attack buff.
        
        Args:
            amount (int): Attack points to gain.
            duration (int): Turns the buff lasts.
        """
        super().__init__("Attack Buff", duration)
        self.amount = amount

    def on_apply(self, entity):
        """Increase entity's attack stat and notify."""
        entity.atk += self.amount
        typewriter(f"{entity.name}'s ATK increased by {self.amount}!")

    def on_expire(self, entity):
        """Decrease entity's attack stat back to normal."""
        entity.atk -= self.amount
        typewriter(f"{entity.name}'s Attack Buff has worn off!")


# ==========================================
# DEFENSE BUFF
# ==========================================
class DefenseBuff(StatusEffect):
    """Status effect that increases entity's defense.
    
    Attributes:
        amount (int): Defense points added to entity.
    """
    def __init__(self, amount, duration):
        """Initialize defense buff.
        
        Args:
            amount (int): Defense points to gain.
            duration (int): Turns the buff lasts.
        """
        super().__init__("Defense Buff", duration)
        self.amount = amount

    def on_apply(self, entity):
        """Increase entity's defense stat and notify."""
        entity.defense += self.amount
        typewriter(f"{entity.name}'s DEF increased by {self.amount}!")

    def on_expire(self, entity):
        """Decrease entity's defense stat back to normal."""
        entity.defense -= self.amount
        typewriter(f"{entity.name}'s Defense Buff has worn off!")


# ==========================================
# POISON (Damage Over Time)
# ==========================================
class Poison(StatusEffect):
    """Status effect that deals damage at the start of entity's turn.
    
    Attributes:
        damage (int): Damage dealt per turn.
    """
    def __init__(self, damage, duration):
        """Initialize poison effect.
        
        Args:
            damage (int): Damage to deal each turn.
            duration (int): Turns the poison lasts.
        """
        super().__init__("Poison", duration)
        self.damage = damage

    def on_turn_start(self, entity):
        """Deal poison damage at start of entity's turn."""
        entity.take_dmg(self.damage)
        typewriter(f"{entity.name} takes {self.damage} poison damage!")

    def on_expire(self, entity):
        """Notify poison has expired."""
        typewriter(f"{entity.name} is no longer poisoned!")


# ==========================================
# BURN (Damage Over Time)
# ==========================================
class Burn(StatusEffect):
    """Status effect that deals burn damage at the start of entity's turn.
    
    Attributes:
        damage (int): Burn damage dealt per turn.
    """
    def __init__(self, damage, duration):
        """Initialize burn effect.
        
        Args:
            damage (int): Damage to deal each turn.
            duration (int): Turns the burn lasts.
        """
        super().__init__("Burn", duration)
        self.damage = damage

    def on_turn_start(self, entity):
        """Deal burn damage at start of entity's turn."""
        entity.take_dmg(self.damage)
        typewriter(f"{entity.name} takes {self.damage} burn damage!")

    def on_expire(self, entity):
        """Notify burn has expired."""
        typewriter(f"{entity.name} is no longer burning!")


# ==========================================
# REGENERATION (Heal Over Time)
# ==========================================
class Regen(StatusEffect):
    """Status effect that heals entity at the start of their turn.
    
    Attributes:
        amount (int): Health points restored per turn.
    """
    def __init__(self, amount, duration):
        """Initialize regeneration effect.
        
        Args:
            amount (int): Health to restore each turn.
            duration (int): Turns the regen lasts.
        """
        super().__init__("Regeneration", duration)
        self.amount = amount

    def on_turn_start(self, entity):
        """Restore health at start of entity's turn."""
        entity.hp = min(entity.max_hp, entity.hp + self.amount)
        typewriter(f"{entity.name} regenerates {self.amount} HP!")

    def on_expire(self, entity):
        """Notify regeneration has expired."""
        typewriter(f"{entity.name}'s regeneration faded.")


# ==========================================
# SHIELD (Absorbs Damage)
# ==========================================
class Shield(StatusEffect):
    """Status effect that grants a protective shield that absorbs damage.
    
    Attributes:
        amount (int): Shield points granted to entity.
    """
    def __init__(self, amount, duration):
        """Initialize shield effect.
        
        Args:
            amount (int): Shield points to grant.
            duration (int): Turns the shield lasts.
        """
        super().__init__("Shield", duration)
        self.amount = amount

    def on_apply(self, entity):
        """Apply shield to entity."""
        entity.shield += self.amount
        typewriter(f"{entity.name} gains a shield of {self.amount}!")

    def on_expire(self, entity):
        """Remove shield from entity."""
        entity.shield = max(0, entity.shield - self.amount)
        typewriter(f"{entity.name}'s shield expired.")


# ==========================================
# STUN (Skip Turn)
# ==========================================
class Stun(StatusEffect):
    """Status effect that prevents entity from taking actions for the duration."""
    def __init__(self, duration):
        """Initialize stun effect.
        
        Args:
            duration (int): Number of turns the stun lasts.
        """
        super().__init__("Stun", duration)

    def on_apply(self, entity):
        """Mark entity as stunned."""
        entity.is_stunned = True

    def on_expire(self, entity):
        """Remove stunned status from entity."""
        entity.is_stunned = False
        typewriter(f"{entity.name} is no longer stunned!")


# ==========================================
# GOLD BOOST (Utility)
# ==========================================
class GoldBoost(StatusEffect):
    """Status effect that multiplies gold earned by entity.
    
    Attributes:
        multiplier (float): Gold earnings multiplier (e.g., 1.5 for +50%).
    """
    def __init__(self, multiplier, duration):
        """Initialize gold boost effect.
        
        Args:
            multiplier (float): Gold multiplier to apply.
            duration (int): Turns the boost lasts.
        """
        super().__init__("Gold Boost", duration)
        self.multiplier = multiplier

    def on_apply(self, entity):
        """Apply gold multiplier to entity."""
        entity.gold_multiplier *= self.multiplier
        typewriter(f"{entity.name}'s gold gain increased!")

    def on_expire(self, entity):
        """Remove gold multiplier from entity."""
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
        entity.spd += self.amount
        typewriter(f"{entity.name}'s Speed increased by {self.amount}!")

    def on_expire(self, entity):
        entity.spd -= self.amount
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

# -----------------------------------
# Vulnerable Debuff
# -----------------------------------
class Vulnerable(StatusEffect):
    def __init__(self, duration, dodge_penalty=0.2):
        super().__init__("Vulnerable", duration)
        self.dodge_penalty = dodge_penalty

    def on_apply(self, entity):
        if not hasattr(entity, "dodge_modifier"):
            entity.dodge_modifier = 0
        entity.dodge_modifier -= self.dodge_penalty
        typewriter(f"{entity.name} feels exposed! Dodge reduced by {int(self.dodge_penalty*100)}% for {self.duration} turns.")

    def on_expire(self, entity):
        entity.dodge_modifier += self.dodge_penalty
        typewriter(f"{entity.name} is no longer vulnerable.")

