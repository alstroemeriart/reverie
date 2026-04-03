# COMBAT CALCULATIONS

import random

def check_dodge(attacker, defender):
    """Return True if defender dodges the attack (includes streak bonus)."""
    base_chance = defender.spd * 0.02

    if hasattr(defender, "streak_dodge_bonus"):
        base_chance += defender.streak_dodge_bonus()

    if hasattr(defender, "dodge_modifier"):
        base_chance += defender.dodge_modifier

    return random.random() < base_chance


def check_critical(attacker):
    """Return True if attack is a critical hit."""
    bonus = getattr(attacker, "_momentum_bonus", 0)
    attacker._momentum_bonus = 0
    return random.random() < (attacker.crit_chance + bonus)


def calculate_damage(attacker, defender, variance_low=-2, variance_high=2):
    """Calculate damage, considering crits, variance, and streak buffs."""

    # Base attack, boosted by streak if attacker is MainCharacter
    raw = attacker.atk
    if hasattr(attacker, "streak_attack_bonus"):
        raw += attacker.streak_attack_bonus()

    # Wisdom scales damage
    wisdom = getattr(attacker, "wisdom", 0)
    wisdom_bonus = 1 + (wisdom * 0.01)

    # Mastery gives a small long-term bonus
    mastery_bonus = 1.0
    if hasattr(attacker, "mastery"):
        total_mastery = sum(attacker.mastery.values())
        mastery_bonus += total_mastery * 0.002

    variance = random.randint(variance_low, variance_high)
    base = max(1, raw - defender.defense + variance)
    base = int(base * wisdom_bonus * mastery_bonus)

    is_crit = check_critical(attacker)
    if is_crit:
        base = int(base * attacker.crit_multiplier)

    return base, is_crit

