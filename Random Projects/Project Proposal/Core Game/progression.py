"""Character progression and skill system.

Handles mastery growth, mastery-based damage multipliers, skill definitions,
skill unlocking, and applying skill effects during combat.
"""


# ─────────────────────────────────────────────────────────────────────────────
# MASTERY SYSTEM
# ─────────────────────────────────────────────────────────────────────────────

def gain_mastery(player, q_type: str, amount: int = 1) -> None:
    """Increase the player's mastery in a specific question type.

    Does nothing if ``q_type`` is not already a key in player.mastery,
    preventing accidental creation of unknown categories.

    Args:
        player: MainCharacter instance with a ``mastery`` dict attribute.
        q_type: Question-type key, e.g. ``"TF"``, ``"MC"``, ``"AR"``.
        amount: Mastery points to add (default 1).
    """
    if q_type not in player.mastery:
        return  # Unknown question type — ignore silently
    player.mastery[q_type] += amount


def mastery_multiplier(player, q_type: str) -> float:
    """Calculate the damage multiplier granted by mastery in a given question type.

    Uses balanced linear scaling: every mastery point adds 1.5% damage.
    At 50 mastery this yields a +75% multiplier.

    Args:
        player: MainCharacter with a ``mastery`` dict.
        q_type: Question-type key to look up.

    Returns:
        float: Multiplier ≥ 1.0 (e.g. 1.75 at 50 mastery).
    """
    return 1 + (player.mastery.get(q_type, 0) * 0.015)


# ─────────────────────────────────────────────────────────────────────────────
# SKILL SYSTEM
# ─────────────────────────────────────────────────────────────────────────────

class Skill:
    """A learnable combat skill tied to a specific question-type mastery tree.

    Skills are created locked and become available once the player's mastery
    in the skill's ``tree`` reaches the required threshold.

    Attributes:
        name      (str):      Display name shown to the player.
        tree      (str):      Associated question type (e.g. ``"TF"``).
        effect    (callable): ``effect(player, context)`` — modifies combat context.
        condition (callable): ``condition(player) -> bool`` — unlock check.
        unlocked  (bool):     Whether this skill has been unlocked yet.
    """

    def __init__(self, name: str, tree: str, effect, condition) -> None:
        """Create a new (locked) Skill.

        Args:
            name:      Display name.
            tree:      Question-type mastery tree this skill belongs to.
            effect:    Callable applied during combat via apply_skills().
            condition: Callable that returns True when the skill can be unlocked.
        """
        self.name      = name
        self.tree      = tree
        self.effect    = effect
        self.condition = condition
        self.unlocked  = False   # All skills start locked


# ── Skill effect functions ────────────────────────────────────────────────────

def reflex_dodge_effect(player, context: dict) -> None:
    """Skill: Reflex Dodge — boost dodge chance on correct TF answers.

    Adds 0.10 to the player's dodge modifier when the combat context is
    a dodge action and the answer was correct.

    Args:
        player:  MainCharacter instance.
        context: Combat context dict (expects ``type`` and ``correct`` keys).
    """
    if context.get("type") == "dodge" and context.get("correct"):
        # Initialise dodge_modifier if the attribute doesn't exist yet
        player.dodge_modifier = getattr(player, "dodge_modifier", 0) + 0.1


def mc_eliminate_effect(player, context: dict) -> None:
    """Skill: Eliminate One — flag to remove a wrong MC option on next question.

    Sets player.mc_eliminate to 1 whenever a Multiple Choice question is
    being processed. The question-asking code reads and resets this flag.

    Args:
        player:  MainCharacter instance.
        context: Combat context dict (expects ``q_type`` key).
    """
    if context.get("q_type") == "MC":
        player.mc_eliminate = 1


def ar_bonus_damage(player, context: dict) -> None:
    """Skill: Bonus Damage — +20% damage on correct Arithmetic answers.

    Modifies ``context["damage"]`` in place so the caller applies the
    boosted value automatically.

    Args:
        player:  MainCharacter instance (unused but kept for interface consistency).
        context: Combat context dict (expects ``type``, ``q_type``, ``correct``,
                 and ``damage`` keys).
    """
    if (
        context.get("type") == "attack"
        and context.get("q_type") == "AR"
        and context.get("correct")
    ):
        context["damage"] = int(context["damage"] * 1.2)


def id_heal_bonus(player, context: dict) -> None:
    """Skill: Efficient Healing — +20% healing on correct Identification answers.

    Modifies ``context["heal"]`` in place.

    Args:
        player:  MainCharacter instance (unused but kept for interface consistency).
        context: Combat context dict (expects ``type``, ``q_type``, and ``heal`` keys).
    """
    if context.get("type") == "heal" and context.get("q_type") == "ID":
        context["heal"] = int(context["heal"] * 1.2)


# ── Public API ────────────────────────────────────────────────────────────────

def apply_skills(player, context: dict) -> None:
    """Run every unlocked skill's effect against the current combat context.

    Called once per combat action so skills can modify damage, healing,
    dodge chance, etc. before the result is applied.

    Args:
        player:  MainCharacter instance with a ``skills`` list.
        context: Mutable dict describing the current action. Common keys:
                   - ``type``    – ``"attack"``, ``"dodge"``, or ``"heal"``
                   - ``q_type`` – Question type that triggered the action
                   - ``damage`` – Damage amount (may be modified by skills)
                   - ``correct``– Whether the answer was correct
    """
    for skill in player.skills:
        if skill.unlocked:
            skill.effect(player, context)


def unlock_skills(player) -> None:
    """Unlock any skills whose mastery conditions are now met.

    Iterates the full skill list and flips ``unlocked = True`` for any
    skill whose condition returns True and isn't already unlocked.
    Safe to call after every mastery gain.

    Args:
        player: MainCharacter instance with a ``skills`` list attribute.
    """
    if not hasattr(player, "skills"):
        return

    for skill in player.skills:
        if not skill.unlocked and skill.condition(player):
            skill.unlocked = True


def create_skill_pool() -> list:
    """Build and return the full list of available Skill objects.

    All skills start locked; their conditions reference player.mastery
    thresholds (≥ 5 mastery in the tree to unlock).

    Returns:
        list[Skill]: Fresh skill pool for a new run.
    """
    return [
        Skill(
            name="Reflex Dodge",
            tree="TF",
            effect=reflex_dodge_effect,
            condition=lambda p: p.mastery["TF"] >= 5,
        ),
        Skill(
            name="Eliminate One",
            tree="MC",
            effect=mc_eliminate_effect,
            condition=lambda p: p.mastery["MC"] >= 5,
        ),
        Skill(
            name="Bonus Damage",
            tree="AR",
            effect=ar_bonus_damage,
            condition=lambda p: p.mastery["AR"] >= 5,
        ),
        Skill(
            name="Efficient Healing",
            tree="ID",
            effect=id_heal_bonus,
            condition=lambda p: p.mastery["ID"] >= 5,
        ),
    ]