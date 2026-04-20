"""Status effects system.

Defines the base StatusEffect class and all concrete effect types
(buffs, debuffs, damage-over-time, utility effects).

Lifecycle hooks (called by combatSystem.process_status_effects):
    on_apply     → called once when first applied
    on_turn_start→ called at the beginning of the affected entity's turn
    on_turn_end  → called at the end of the turn; default decrements duration
    on_expire    → called once when duration reaches 0
"""

from ui import typewriter


class StatusEffect:
    """Base class for all status effects.

    Subclasses override the lifecycle hooks they need.  Any hook not
    overridden is a no-op so subclasses only implement relevant behaviour.

    Attributes:
        name     (str): Display name shown to the player.
        duration (int): Remaining turns; decremented each turn_end.
    """

    def __init__(self, name: str, duration: int) -> None:
        self.name     = name
        self.duration = duration

    # ── Lifecycle hooks ───────────────────────────────────────────────────

    def on_apply(self, entity) -> None:
        """Called once when the effect is applied to ``entity``."""
        pass

    def on_turn_start(self, entity) -> None:
        """Called at the start of ``entity``'s turn."""
        pass

    def on_turn_end(self, entity) -> None:
        """Called at the end of ``entity``'s turn.  Decrements duration by 1."""
        self.duration -= 1

    def on_expire(self, entity) -> None:
        """Called once when duration reaches 0, before removal from entity."""
        pass

    def is_expired(self) -> bool:
        """Return True if this effect has run out of turns."""
        return self.duration <= 0


# ─────────────────────────────────────────────────────────────────────────────
# BUFFS
# ─────────────────────────────────────────────────────────────────────────────

class AttackBuff(StatusEffect):
    """Temporarily increase an entity's ATK stat.

    Args:
        amount   (int): ATK points to add.
        duration (int): Turns the buff lasts.
    """

    def __init__(self, amount: int, duration: int) -> None:
        super().__init__("Attack Buff", duration)
        self.amount = amount

    def on_apply(self, entity) -> None:
        entity.atk += self.amount
        typewriter(f"{entity.name}'s ATK increased by {self.amount}!")

    def on_expire(self, entity) -> None:
        entity.atk -= self.amount
        typewriter(f"{entity.name}'s Attack Buff has worn off!")


class DefenseBuff(StatusEffect):
    """Temporarily increase an entity's DEF stat.

    Args:
        amount   (int): DEF points to add.
        duration (int): Turns the buff lasts.
    """

    def __init__(self, amount: int, duration: int) -> None:
        super().__init__("Defense Buff", duration)
        self.amount = amount

    def on_apply(self, entity) -> None:
        entity.defense += self.amount
        typewriter(f"{entity.name}'s DEF increased by {self.amount}!")

    def on_expire(self, entity) -> None:
        entity.defense -= self.amount
        typewriter(f"{entity.name}'s Defense Buff has worn off!")


class SpeedBuff(StatusEffect):
    """Temporarily increase an entity's SPD stat.

    Args:
        amount   (int): SPD points to add.
        duration (int): Turns the buff lasts.
    """

    def __init__(self, amount: int, duration: int) -> None:
        super().__init__("Speed Buff", duration)
        self.amount = amount

    def on_apply(self, entity) -> None:
        entity.spd += self.amount
        typewriter(f"{entity.name}'s Speed increased by {self.amount}!")

    def on_expire(self, entity) -> None:
        entity.spd -= self.amount
        typewriter(f"{entity.name}'s Speed Buff has worn off!")


class Regen(StatusEffect):
    """Restore HP at the start of each turn (heal-over-time).

    Args:
        amount   (int): HP restored per turn.
        duration (int): Turns the regeneration lasts.
    """

    def __init__(self, amount: int, duration: int) -> None:
        super().__init__("Regeneration", duration)
        self.amount = amount

    def on_turn_start(self, entity) -> None:
        entity.hp = min(entity.max_hp, entity.hp + self.amount)
        typewriter(f"{entity.name} regenerates {self.amount} HP!")

    def on_expire(self, entity) -> None:
        typewriter(f"{entity.name}'s regeneration faded.")


class Shield(StatusEffect):
    """Grant a shield that absorbs damage before HP is reduced.

    Args:
        amount   (int): Shield points granted.
        duration (int): Turns before the shield expires.
    """

    def __init__(self, amount: int, duration: int) -> None:
        super().__init__("Shield", duration)
        self.amount = amount

    def on_apply(self, entity) -> None:
        entity.shield += self.amount
        typewriter(f"{entity.name} gains a shield of {self.amount}!")

    def on_expire(self, entity) -> None:
        # Clamp to 0 in case the shield was partially consumed
        entity.shield = max(0, entity.shield - self.amount)
        typewriter(f"{entity.name}'s shield expired.")


class GoldBoost(StatusEffect):
    """Multiply gold earned by ``multiplier`` for the duration.

    Args:
        multiplier (float): Gold multiplier, e.g. 1.5 for +50%.
        duration   (int):   Turns the boost lasts.
    """

    def __init__(self, multiplier: float, duration: int) -> None:
        super().__init__("Gold Boost", duration)
        self.multiplier = multiplier

    def on_apply(self, entity) -> None:
        entity.gold_multiplier *= self.multiplier
        typewriter(f"{entity.name}'s gold gain increased!")

    def on_expire(self, entity) -> None:
        # Undo the multiplier with division to avoid floating-point drift
        entity.gold_multiplier /= self.multiplier
        typewriter("Gold boost has expired.")


class DoubleGold(StatusEffect):
    """Double all gold earned for the duration (convenience x2 boost).

    Args:
        duration (int): Turns the bonus lasts.
    """

    def __init__(self, duration: int) -> None:
        super().__init__("Double Gold", duration)

    def on_apply(self, entity) -> None:
        entity.gold_multiplier *= 2
        typewriter(f"{entity.name} will earn DOUBLE gold!")

    def on_expire(self, entity) -> None:
        entity.gold_multiplier /= 2
        typewriter("Double Gold has expired.")


class StreakGuard(StatusEffect):
    """Protect the player's streak from the next wrong answer.

    Single-turn effect that sets a flag read by the combat system.
    """

    def __init__(self) -> None:
        super().__init__("Streak Guard", 1)

    def on_apply(self, entity) -> None:
        entity.has_streak_guard = True
        typewriter("Your next streak loss will be prevented!")

    def on_expire(self, entity) -> None:
        entity.has_streak_guard = False
        typewriter("Streak Guard has been used.")


# ─────────────────────────────────────────────────────────────────────────────
# DEBUFFS
# ─────────────────────────────────────────────────────────────────────────────

class Poison(StatusEffect):
    """Deal damage at the start of each turn (damage-over-time).

    Args:
        damage   (int): Damage dealt per turn.
        duration (int): Turns the poison lasts.
    """

    def __init__(self, damage: int, duration: int) -> None:
        super().__init__("Poison", duration)
        self.damage = damage

    def on_turn_start(self, entity) -> None:
        entity.take_dmg(self.damage)
        typewriter(f"{entity.name} takes {self.damage} poison damage!")

    def on_expire(self, entity) -> None:
        typewriter(f"{entity.name} is no longer poisoned!")


class Burn(StatusEffect):
    """Deal burn damage at the start of each turn.

    Args:
        damage   (int): Damage dealt per turn.
        duration (int): Turns the burn lasts.
    """

    def __init__(self, damage: int, duration: int) -> None:
        super().__init__("Burn", duration)
        self.damage = damage

    def on_turn_start(self, entity) -> None:
        entity.take_dmg(self.damage)
        typewriter(f"{entity.name} takes {self.damage} burn damage!")

    def on_expire(self, entity) -> None:
        typewriter(f"{entity.name} is no longer burning!")


class Stun(StatusEffect):
    """Prevent the entity from acting for the duration.

    Sets ``entity.is_stunned = True`` on apply; removes it on expire.

    Args:
        duration (int): Number of turns stunned.
    """

    def __init__(self, duration: int) -> None:
        super().__init__("Stun", duration)

    def on_apply(self, entity) -> None:
        entity.is_stunned = True

    def on_expire(self, entity) -> None:
        entity.is_stunned = False
        typewriter(f"{entity.name} is no longer stunned!")


class Freeze(StatusEffect):
    """Stun the entity AND temporarily lower its defense.

    Stronger variant of Stun for items like the Freeze Scroll.

    Args:
        duration          (int): Turns frozen.
        defense_reduction (int): DEF points removed while frozen (default 2).
    """

    def __init__(self, duration: int, defense_reduction: int = 2) -> None:
        super().__init__("Freeze", duration)
        self.defense_reduction = defense_reduction

    def on_apply(self, entity) -> None:
        entity.is_stunned   = True
        entity.defense     -= self.defense_reduction
        typewriter(f"{entity.name} is frozen solid!")

    def on_expire(self, entity) -> None:
        entity.is_stunned   = False
        entity.defense     += self.defense_reduction  # Restore reduced defense
        typewriter(f"{entity.name} thawed out!")


class AttackDebuff(StatusEffect):
    """Temporarily reduce an entity's ATK stat.

    Args:
        amount   (int): ATK points to remove.
        duration (int): Turns the debuff lasts.
    """

    def __init__(self, amount: int, duration: int) -> None:
        super().__init__("Attack Down", duration)
        self.amount = amount

    def on_apply(self, entity) -> None:
        entity.atk -= self.amount
        typewriter(f"{entity.name}'s ATK decreased by {self.amount}!")

    def on_expire(self, entity) -> None:
        entity.atk += self.amount  # Restore ATK on expire
        typewriter(f"{entity.name}'s Attack returned to normal!")


class Vulnerable(StatusEffect):
    """Reduce the entity's dodge chance, making it easier to hit.

    Args:
        duration      (int):   Turns the debuff lasts.
        dodge_penalty (float): Dodge chance reduction (default 0.2 = 20%).
    """

    def __init__(self, duration: int, dodge_penalty: float = 0.2) -> None:
        super().__init__("Vulnerable", duration)
        self.dodge_penalty = dodge_penalty

    def on_apply(self, entity) -> None:
        # Ensure dodge_modifier attribute exists before subtracting
        if not hasattr(entity, "dodge_modifier"):
            entity.dodge_modifier = 0
        entity.dodge_modifier -= self.dodge_penalty
        typewriter(
            f"{entity.name} feels exposed! "
            f"Dodge reduced by {int(self.dodge_penalty * 100)}% "
            f"for {self.duration} turns."
        )

    def on_expire(self, entity) -> None:
        entity.dodge_modifier += self.dodge_penalty
        typewriter(f"{entity.name} is no longer vulnerable.")