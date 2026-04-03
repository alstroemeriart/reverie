# progression.py

# -----------------------------
# MASTERY SYSTEM
# -----------------------------
def gain_mastery(player, q_type, amount=1):
    if q_type not in player.mastery:
        return

    player.mastery[q_type] += amount


def mastery_multiplier(player, q_type):
    # BALANCED scaling (important)
    # 50 mastery = +75% power (not broken)
    return 1 + (player.mastery.get(q_type, 0) * 0.015)


# -----------------------------
# SKILL SYSTEM
# -----------------------------
class Skill:
    def __init__(self, name, tree, effect, condition):
        self.name = name
        self.tree = tree
        self.effect = effect
        self.condition = condition
        self.unlocked = False


def apply_skills(player, context):
    """
    context = {
        "type": "attack" / "dodge" / "heal",
        "q_type": "TF/MC/AR/ID",
        "damage": int,
        "correct": bool
    }
    """
    for skill in player.skills:
        if skill.unlocked:
            skill.effect(player, context)


# -----------------------------
# SKILL DEFINITIONS
# -----------------------------

def reflex_dodge_effect(player, context):
    if context["type"] == "dodge" and context["correct"]:
        player.dodge_modifier = getattr(player, "dodge_modifier", 0) + 0.1


def mc_eliminate_effect(player, context):
    if context["q_type"] == "MC":
        player.mc_eliminate = 1


def ar_bonus_damage(player, context):
    if context["type"] == "attack" and context["q_type"] == "AR" and context["correct"]:
        context["damage"] = int(context["damage"] * 1.2)


def id_heal_bonus(player, context):
    if context["type"] == "heal" and context["q_type"] == "ID":
        context["heal"] = int(context["heal"] * 1.2)


def create_skill_pool():
    return [
        Skill(
            "Reflex Dodge",
            "TF",
            reflex_dodge_effect,
            lambda p: p.mastery["TF"] >= 5
        ),
        Skill(
            "Eliminate One",
            "MC",
            mc_eliminate_effect,
            lambda p: p.mastery["MC"] >= 5
        ),
        Skill(
            "Bonus Damage",
            "AR",
            ar_bonus_damage,
            lambda p: p.mastery["AR"] >= 5
        ),
        Skill(
            "Efficient Healing",
            "ID",
            id_heal_bonus,
            lambda p: p.mastery["ID"] >= 5
        ),
    ]


def unlock_skills(player):
    if not hasattr(player, "skills"):
        return

    for skill in player.skills:
        if not skill.unlocked and skill.condition(player):
            skill.unlocked = True