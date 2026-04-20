"""Combat calculation utilities.

Pure functions for damage, dodge, and critical-hit resolution.
No side effects — all randomness is contained here so the rest of the
combat system can stay deterministic given the same RNG state.
"""

import random


def check_dodge(attacker, defender) -> bool:
    """Determine whether the defender dodges an incoming attack.

    Dodge chance is based on the defender's SPD stat plus any temporary
    bonuses (streak-based or flat modifiers).

    Args:
        attacker: The entity performing the attack (unused directly, kept
                  for symmetry and potential future attacker-accuracy stats).
        defender: The entity attempting to dodge.

    Returns:
        bool: True if the dodge succeeds.
    """
    # Base dodge chance: 2% per point of SPD
    base_chance = defender.spd * 0.02

    # Streak-based bonus (MainCharacter only)
    if hasattr(defender, "streak_dodge_bonus"):
        base_chance += defender.streak_dodge_bonus()

    # Flat modifier from items/status effects (e.g. Vulnerable debuff)
    if hasattr(defender, "dodge_modifier"):
        base_chance += defender.dodge_modifier

    return random.random() < base_chance


def check_critical(attacker) -> bool:
    """Determine whether the attacker lands a critical hit.

    Consumes any accumulated momentum bonus (set by the Momentum passive)
    after the check so it only applies once.

    Args:
        attacker: The entity attacking.

    Returns:
        bool: True if this attack is a critical hit.
    """
    # Pull any one-time momentum bonus then reset it immediately
    bonus = getattr(attacker, "_momentum_bonus", 0)
    attacker._momentum_bonus = 0

    return random.random() < (attacker.crit_chance + bonus)


def calculate_damage(
    attacker,
    defender,
    variance_low: int = -2,
    variance_high: int = 2,
) -> tuple:
    """Calculate the final damage dealt from attacker to defender.

    Damage formula (applied in order):
        1. Base ATK (+ streak bonus for player)
        2. Multiply by wisdom scaling:    1 + (WIS * 0.01)
        3. Multiply by mastery scaling:   1 + (total_mastery * 0.002)
        4. Add random variance in [variance_low, variance_high]
        5. Subtract defender's defense (minimum 1 damage)
        6. If critical hit: multiply by attacker's crit_multiplier

    Args:
        attacker:       The entity dealing damage.
        defender:       The entity receiving damage.
        variance_low:   Minimum random variance added to raw damage.
        variance_high:  Maximum random variance added to raw damage.

    Returns:
        tuple[int, bool]: (final_damage, is_critical)
    """
    # --- Step 1: Raw attack (+ streak bonus if player) ---
    raw = attacker.atk
    if hasattr(attacker, "streak_attack_bonus"):
        raw += attacker.streak_attack_bonus()

    # --- Step 2: Wisdom scaling ---
    wisdom       = getattr(attacker, "wisdom", 0)
    wisdom_bonus = 1 + (wisdom * 0.01)

    # --- Step 3: Mastery scaling (long-term progression bonus) ---
    mastery_bonus = 1.0
    if hasattr(attacker, "mastery"):
        total_mastery  = sum(attacker.mastery.values())
        mastery_bonus += total_mastery * 0.002

    # --- Step 4: Random variance ---
    variance = random.randint(variance_low, variance_high)

    # --- Step 5: Apply defense, floor at 1 ---
    base = max(1, raw - defender.defense + variance)
    base = int(base * wisdom_bonus * mastery_bonus)

    # --- Step 6: Critical hit check and multiplier ---
    is_crit = check_critical(attacker)
    if is_crit:
        base = int(base * attacker.crit_multiplier)

    return base, is_crit