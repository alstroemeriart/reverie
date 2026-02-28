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

    # -----------------------------
    # 1. Base Damage
    # -----------------------------
    base_damage = attacker.atk - defender.defense
    base_damage = max(1, base_damage)

    # -----------------------------
    # 2. Streak Scaling (Soft Cap)
    # -----------------------------
    streak = getattr(attacker, "streak", 0)

    # Soft scaling formula to prevent runaway damage
    # Early streak feels strong, later streak scales slower
    streak_multiplier = 1 + (streak * 0.05) / (1 + streak * 0.02)

    # -----------------------------
    # 3. Wisdom Scaling
    # -----------------------------
    wisdom = getattr(attacker, "wisdom", 0)
    wisdom_bonus = 1 + (wisdom * 0.01)

    # -----------------------------
    # 4. Mastery Bonus (Future Expansion Ready)
    # -----------------------------
    mastery_bonus = 1.0
    if hasattr(attacker, "mastery"):
        total_mastery = sum(attacker.mastery.values())
        mastery_bonus += total_mastery * 0.002  # small long-term scaling

    # -----------------------------
    # 5. Final Calculation
    # -----------------------------
    damage = base_damage * streak_multiplier * wisdom_bonus * mastery_bonus

    base_damage = attacker.attack - defender.defense
    if base_damage < 1:
        base_damage = 1

    # Critical hit?
    is_crit = check_critical(attacker)
    if is_crit:
        base_damage *= attacker.crit_multiplier

    return int(base_damage), is_crit