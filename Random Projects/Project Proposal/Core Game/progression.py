"""Character progression and skill system.

Manages mastery progression, skill unlocking and application, skill trees,
mastery multipliers, and progression milestones.
"""

# ─────────────────────────────
# MASTERY SYSTEM
# ─────────────────────────────
def gain_mastery(player, q_type, amount=1):
    """Increase mastery for a specific question type.
    
    Args:
        player: Player character object with mastery dict.
        q_type (str): Question type key (e.g., 'TF', 'MC', 'AR').
        amount (int): Mastery points to gain (default: 1).
    """
    if q_type not in player.mastery:
        return

    player.mastery[q_type] += amount


def mastery_multiplier(player, q_type):
    """Calculate damage multiplier based on mastery level.
    
    Uses balanced scaling: 50 mastery = +75% damage.
    
    Args:
        player: Player character object.
        q_type (str): Question type to check mastery for.
    
    Returns:
        float: Damage multiplier (1.0 + mastery contribution).
    """
    # BALANCED scaling (important)
    # 50 mastery = +75% power (not broken)
    return 1 + (player.mastery.get(q_type, 0) * 0.015)


# -----------------------------
# SKILL SYSTEM
# -----------------------------
class Skill:
    """Represents a learnable skill that modifies combat behavior.
    
    Attributes:
        name (str): Skill name displayed to player.
        tree (str): Associated question type tree (e.g., 'TF').
        effect (callable): Function that applies skill effect.
        condition (callable): Function that returns True when skill is unlockable.
        unlocked (bool): Whether skill has been unlocked yet.
    """
    def __init__(self, name, tree, effect, condition):
        """Initialize a skill with name, tree, effect, and unlock condition.
        
        Args:
            name (str): Display name of the skill.
            tree (str): Question type this skill is associated with.
            effect (callable): Function(player, context) to apply skill effect.
            condition (callable): Function(player) that returns unlock status.
        """
        self.name = name
        self.tree = tree
        self.effect = effect
        self.condition = condition
        self.unlocked = False


def apply_skills(player, context):
    """Apply all unlocked skills to current combat context.
    
    Args:
        player: Player character with skills list.
        context (dict): Combat context with keys like:
            - 'type': 'attack', 'dodge', or 'heal'
            - 'q_type': Question type (e.g., 'TF', 'MC')
            - 'damage': Damage value (int)
            - 'correct': Whether answer was correct (bool)
    """
    for skill in player.skills:
        if skill.unlocked:
            skill.effect(player, context)


# -----------------------------
# SKILL DEFINITIONS
# -----------------------------

def reflex_dodge_effect(player, context):
    """Skill effect: Increase dodge chance when True/False question is answered correctly.
    
    Args:
        player: Player character object.
        context (dict): Combat context dict (checked for type and correct).
    """
    if context["type"] == "dodge" and context["correct"]:
        player.dodge_modifier = getattr(player, "dodge_modifier", 0) + 0.1


def mc_eliminate_effect(player, context):
    """Skill effect: Unlock ability to eliminate one wrong answer on Multiple Choice.
    
    Args:
        player: Player character object.
        context (dict): Combat context dict (checked for q_type).
    """
    if context["q_type"] == "MC":
        player.mc_eliminate = 1


def ar_bonus_damage(player, context):
    """Skill effect: Increase damage by 20% on correct Arrange answers.
    
    Args:
        player: Player character object.
        context (dict): Combat context dict with 'damage' key to modify.
    """
    if context["type"] == "attack" and context["q_type"] == "AR" and context["correct"]:
        context["damage"] = int(context["damage"] * 1.2)


def id_heal_bonus(player, context):
    """Skill effect: Increase healing by 20% on correct Identify answers.
    
    Args:
        player: Player character object.
        context (dict): Combat context dict with 'heal' key to modify.
    """
    if context["type"] == "heal" and context["q_type"] == "ID":
        context["heal"] = int(context["heal"] * 1.2)


def create_skill_pool():
    """Create a pool of all available skills.
    
    Returns:
        list: List of Skill objects with unlock conditions based on mastery levels.
    """
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
    """Unlock skills whose conditions have been met.
    
    Iterates through player's skill list and unlocks any skills whose
    unlock condition function returns True.
    
    Args:
        player: Player character object with skills list attribute.
    """
    if not hasattr(player, "skills"):
        return

    for skill in player.skills:
        if not skill.unlocked and skill.condition(player):
            skill.unlocked = True

