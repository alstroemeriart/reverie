import random

def check_dodge(attacker, defender):
    # Simple dodge formula
    dodge_chance = defender.speed * 0.02  # 2% per speed point

    if random.random() < dodge_chance:
        return True
    return False


def check_critical(attacker):
    if random.random() < attacker.crit_chance:
        return True
    return False


def calculate_damage(attacker, defender):
    base_damage = attacker.attack - defender.defense
    if base_damage < 1:
        base_damage = 1

    # Critical hit?
    is_crit = check_critical(attacker)
    if is_crit:
        base_damage *= attacker.crit_multiplier

    return int(base_damage), is_crit