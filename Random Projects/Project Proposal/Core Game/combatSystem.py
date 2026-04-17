"""Combat system module.

Manages turn-based combat flow including player/enemy turns, damage
calculation, status effect processing, and question resolution in combat.
"""

import random
import time

from ui import (
    typewriter, clear_screen, hp_bar, bus,
    input_handler, emit_player_stats
)
from combatCalc import calculate_damage, check_dodge, check_critical
from progression import (
    gain_mastery, mastery_multiplier, apply_skills, unlock_skills
)

# ─────────────────────────────────────────────
# Combat state constants
# ─────────────────────────────────────────────
CONTINUE = "continue"
ESCAPED  = "escaped"
WIN      = "win"
DEATH    = "death"

CATEGORY_NAMES = {
    "TF": "True/False",
    "MC": "Multiple Choice",
    "AR": "Arithmetic",
    "ID": "Identification",
    "FB": "Fill in the Blanks",
    "OD": "Ordering",
}


def _set_action_ui(action=False, boss=False):
    """Enable or disable action buttons in the GUI.
    
    Args:
        action: Whether to enable standard action buttons.
        boss: Whether to enable boss-specific action buttons.
    """
    bus.game_event("action_buttons", enabled=action)
    bus.game_event("boss_actions", enabled=boss)


def _emit_enemy_panel(entity, role="enemy"):
    """Send enemy stats to GUI for display in enemy panel.
    
    Args:
        entity: The entity (enemy or boss) to display.
        role: Entity type label ('enemy', 'boss', 'elite', etc).
    """
    bus.game_event(
        "enemy_update",
        target_name=entity.name,
        role=role,
        hp=entity.hp,
        max_hp=entity.max_hp,
        atk=entity.atk,
        defense=entity.defense,
        spd=entity.spd,
        crit_chance=getattr(entity, "crit_chance", 0),
        shield=getattr(entity, "shield", 0),
        behavior=getattr(entity, "behavior", ""),
        status_effects=[e.name for e in getattr(entity, "status_effects", [])],
    )


def _clear_enemy_panel():
    """Clear the enemy panel display on the GUI."""
    bus.game_event("enemy_clear")


# ─────────────────────────────────────────────
# Display helpers
# ─────────────────────────────────────────────

def damage_line(attacker_name, target, dmg):
    """Display damage result and classify severity.
    
    Args:
        attacker_name: Name of the attacker.
        target: Target entity taking damage.
        dmg: Damage amount dealt.
    """
    ratio = dmg / max(1, target.max_hp)
    if ratio >= 0.25:
        msg = f"HEAVY HIT! {attacker_name} deals {dmg} damage!"
    elif ratio >= 0.10:
        msg = f"{attacker_name} deals {dmg} damage."
    else:
        msg = f"{attacker_name} grazes for {dmg} damage."
    bus.say(msg)
    bus.combat_event("damage", attacker=attacker_name,
                     target=target.name, amount=dmg,
                     severity="heavy" if ratio >= 0.25 else "normal")
    if not hasattr(target, "streak"):
        _emit_enemy_panel(target, role=getattr(target, "_panel_role", "enemy"))


def display_entity_stats(entity, role=None):
    """Print entity stats and optionally update GUI panel.
    
    Args:
        entity: Character or enemy to display.
        role: Optional role label for GUI panel update.
    """
    typewriter(f"\n--- {entity.name} ---")
    typewriter(f"HP:  {hp_bar(entity.hp, entity.max_hp)}")
    if entity.shield > 0:
        typewriter(f"Shield: {entity.shield}")
    typewriter(f"ATK: {entity.atk} | DEF: {entity.defense} | SPD: {entity.spd}")
    typewriter(f"CRIT: {int(entity.crit_chance * 100)}%")
    if hasattr(entity, "streak"):
        typewriter(f"Streak: {entity.streak} (Longest: {entity.longest_streak})")
        typewriter(f"Focus:  {hp_bar(entity.focus, entity.max_focus, length=10)}")
    if hasattr(entity, "gold"):
        typewriter(f"Gold: {entity.gold}")
    if entity.status_effects:
        effects = ", ".join(f"{e.name}({e.duration})" for e in entity.status_effects)
        typewriter(f"Status: {effects}")
    else:
        typewriter("Status: None")
    if role is not None:
        setattr(entity, "_panel_role", role)
        _emit_enemy_panel(entity, role=role)
    time.sleep(0.3)


def _view_skills(player):
    typewriter("\n--- Your Skills ---")
    if not player.skills:
        typewriter("No skills available.")
        return
    for skill in player.skills:
        if skill.unlocked:
            typewriter(f"  [UNLOCKED] {skill.name} ({skill.tree} tree)")
        else:
            current = player.mastery.get(skill.tree, 0)
            typewriter(f"  [locked]   {skill.name} ({skill.tree} mastery: {current}/5)")
    time.sleep(0.3)


# ─────────────────────────────────────────────
# Question asking  (shared logic)
# ─────────────────────────────────────────────

def _ask_question(question_data, player):
    """
    Present one question to the player.
    Returns True if correct, False otherwise.
    """
    # Disable auto-play during combat questions
    input_handler.set_in_combat_question(True)
    
    q_type   = question_data["type"]
    question = question_data["question"]
    answer   = question_data["answer"]
    
    # Debug mode: auto-answer all questions correctly
    if getattr(player, "debug_mode", False):
        diff_label = {1: "easy", 2: "medium", 3: "hard"}.get(
            question_data.get("difficulty", 1), "?")
        mastery_val = player.mastery.get(q_type, 0)
        next_ms = ((mastery_val // 5) + 1) * 5
        typewriter(f"\n[{CATEGORY_NAMES.get(q_type, q_type)} | "
                   f"Mastery: {mastery_val} → {next_ms} | {diff_label}]")
        typewriter(f"[DEBUG AUTO-ANSWER] {question}")
        typewriter(f"[Correct Answer: {answer}]")
        input_handler.set_in_combat_question(False)
        return True

    diff_label = {1: "easy", 2: "medium", 3: "hard"}.get(
        question_data.get("difficulty", 1), "?")
    mastery_val = player.mastery.get(q_type, 0)
    next_ms = ((mastery_val // 5) + 1) * 5
    typewriter(f"\n[{CATEGORY_NAMES.get(q_type, q_type)} | "
               f"Mastery: {mastery_val} → {next_ms} | {diff_label}]")

    correct = False

    if q_type == "TF":
        if player.hint_active:
            typewriter("[Hint: think carefully about whether this is always true]")
            player.hint_active = False
        typewriter(question)
        raw = input_handler.ask_choice(
            [
                {"label": "True", "value": "True"},
                {"label": "False", "value": "False"},
            ],
            "(True/False) > ",
        )
        correct = raw.lower() == answer.lower()

    elif q_type == "MC":
        options = list(question_data["options"])

        if getattr(player, "mc_eliminate", 0) > 0:
            wrong = [o for o in options if o != answer]
            if wrong:
                eliminated = random.choice(wrong)
                options.remove(eliminated)
                player.mc_eliminate = 0
                typewriter(f"[Skill] Eliminated: {eliminated}")

        if player.hint_active:
            wrong = [o for o in options if o != answer]
            if wrong:
                eliminated = random.choice(wrong)
                options = [o for o in options if o != eliminated]
                typewriter(f"[Hint: '{eliminated}' has been eliminated]")
            player.hint_active = False

        typewriter(question)
        for i, opt in enumerate(options, 1):
            typewriter(f"{i}. {opt}")
        raw = input_handler.ask_choice(
            [
                {"label": f"{i}. {opt}", "value": opt, "log": f"{i}. {opt}"}
                for i, opt in enumerate(options, 1)
            ],
            "> ",
        )
        if raw.isdigit():
            try:
                raw = options[int(raw) - 1]
            except (ValueError, IndexError):
                raw = ""
        correct = raw.lower() == answer.lower()

    elif q_type in ("AR", "ID"):
        if player.hint_active:
            typewriter(f"[Hint: starts with '{answer[0]}', {len(answer)} character(s)]")
            player.hint_active = False
        raw = input_handler.ask(f"{question} > ")
        correct = raw.lower() == answer.lower()

    elif q_type == "FB":
        if player.hint_active:
            typewriter(f"[Hint: starts with '{answer[0]}', {len(answer)} character(s)]")
            player.hint_active = False
        typewriter(question)
        raw = input_handler.ask("> ")
        correct = raw.lower() == answer.lower()

    elif q_type == "OD":
        items = question_data["items"]
        shuffled = items[:]
        random.shuffle(shuffled)
        typewriter(question)
        for i, item in enumerate(shuffled, 1):
            typewriter(f"  {i}. {item}")
        typewriter("Enter the correct order as numbers (e.g. 3,1,4,2):")
        try:
            raw   = input_handler.ask("> ")
            order = [int(x.strip()) - 1 for x in raw.split(",")]
            if len(order) != len(items):
                correct = False
            else:
                player_seq  = [shuffled[i] for i in order]
                correct_seq = [items[int(i) - 1] for i in answer.split(",")]
                correct = player_seq == correct_seq
        except (ValueError, IndexError):
            correct = False

    else:
        typewriter(f"[Warning] Unknown question type '{q_type}' — skipping.")
        input_handler.set_in_combat_question(False)
        return False

    # Re-enable auto-play after question is answered
    input_handler.set_in_combat_question(False)
    return correct


def _apply_correct(player, q_type, enemy, engine):
    """Handle streak, focus, mastery, passives, and damage after a correct answer."""
    typewriter("Correct!")

    gain_mastery(player, q_type)
    player.streak += 1
    player.longest_streak = max(player.longest_streak, player.streak)
    unlock_skills(player)

    focus_gain = 10 + int(player.wisdom * 0.2)
    player.focus = min(player.max_focus, player.focus + focus_gain)
    typewriter(f"Streak: {player.streak} | Focus: {player.focus}/{player.max_focus}")

    try:
        from narrative import show_streak_comment, show_correct_flavor
        show_streak_comment(player.streak)
        show_correct_flavor()
    except ImportError:
        pass

    passive = getattr(player, "class_passive", "")
    if passive == "bloodlust":
        if player.bloodlust_stacks < 10:
            player.atk += 1
            player.bloodlust_stacks += 1
            typewriter(f"[Bloodlust] ATK permanently increased to {player.atk}!")

    elif passive == "momentum":
        bonus = min(0.02 * player.streak, 0.30)
        player._momentum_bonus = bonus
        typewriter(f"[Momentum] Crit bonus this strike: +{int(bonus*100)}%")

    elif passive == "luck":
        if random.random() < 0.05:
            gold = random.randint(5, 30)
            player.gold += gold
            typewriter(f"[Luck] Found {gold} gold!")
        if random.random() < 0.03:
            player.hint_active = True
            typewriter("[Luck] Next question has a hint!")
        if random.random() < 0.02:
            player.streak += 1
            typewriter("[Luck] Streak +1!")
        if random.random() < 0.01:
            player.focus = min(player.max_focus, player.focus + 20)
            typewriter("[Luck] Focus +20!")
        if random.random() < 0.005 and enemy is not None and enemy.is_alive():
            typewriter("[Luck] Chance strikes your enemy!")
            enemy.take_dmg(max(1, int(enemy.max_hp * 0.05)))
            _emit_enemy_panel(enemy, role=getattr(enemy, "_panel_role", "enemy"))

    mastery_val = player.mastery.get(q_type, 0)
    if mastery_val > 0 and mastery_val % 5 == 0:
        typewriter(f"Mastery milestone! {CATEGORY_NAMES.get(q_type, q_type)}: {mastery_val}")

    emit_player_stats(player)

    if enemy is not None and not check_dodge(player, enemy):
        dmg, is_crit = calculate_damage(player, enemy, 1, 5)
        dmg = int(dmg * mastery_multiplier(player, q_type))

        ctx = {"type": "attack", "q_type": q_type, "damage": dmg, "correct": True}
        apply_skills(player, ctx)
        dmg = ctx["damage"]

        if getattr(player, "run_modifier", "") == "scholar":
            dmg = int(dmg * 2)
            typewriter("[Scholar's Burden] Knowledge empowers your strike!")

        enemy.take_dmg(dmg)
        if is_crit:
            typewriter("CRITICAL HIT!")
        damage_line(player.name, enemy, dmg)
    elif enemy is not None:
        typewriter(f"{enemy.name} dodged the empowered strike!")


def _apply_incorrect(player, q_type, enemy, engine, question_data):
    """Handle streak loss, focus loss, and punishment after a wrong answer."""
    typewriter("Incorrect!")

    if engine is not None:
        engine.record_wrong(question_data)
        repeat = engine.get_consecutive_wrong()
        if repeat:
            typewriter("\n[This question came up twice in a row.]")
            typewriter(f"  Q: {repeat['question']}")
            typewriter(f"  A: {repeat['correct_answer']}")
            typewriter("[Take a moment to remember it.]")
            time.sleep(1.5)

    try:
        from narrative import show_wrong_flavor
        show_wrong_flavor()
    except ImportError:
        pass

    passive = getattr(player, "class_passive", "")

    if passive == "fortress":
        typewriter("[Fortress] Your defenses hold — no punishment attack.")
    else:
        if getattr(player, "run_modifier", "") == "cursed":
            player.take_dmg(10)
            typewriter("[Cursed Knowledge] -10 HP for wrong answer!")

        if player.streak_protected:
            typewriter("Your streak was protected!")
            player.streak_protected = False
        else:
            player.streak = player.streak // 2

        player.focus = max(0, player.focus - 15)
        typewriter(f"Streak → {player.streak} | Focus → {player.focus}/{player.max_focus}")

        if enemy is not None and not check_dodge(enemy, player):
            dmg, is_crit = calculate_damage(enemy, player, 0, 3)
            player.take_dmg(dmg)
            if is_crit:
                typewriter("Enemy CRITICAL HIT!")
            damage_line(enemy.name, player, dmg)
        else:
            typewriter("You dodged the punishment attack!")

    emit_player_stats(player)

    stats = getattr(player, "session_stats", None)
    if stats:
        stats.record(q_type, False)


# ─────────────────────────────────────────────
# Player actions
# ─────────────────────────────────────────────

def choice_attack(player, enemy):
    typewriter(f"\n{player.name} attacks {enemy.name}!")
    time.sleep(0.5)
    if check_dodge(player, enemy):
        typewriter(f"{enemy.name} dodged the attack!")
        return
    dmg, is_crit = calculate_damage(player, enemy)
    enemy.take_dmg(dmg)
    if is_crit:
        typewriter("CRITICAL HIT!")
    damage_line(player.name, enemy, dmg)
    time.sleep(1)


def choice_ask(player, enemy, engine):
    """Ask a question and resolve all consequences."""
    question_data = engine.get_random_question()
    if not question_data:
        typewriter("No questions loaded.")
        return

    q_type  = question_data["type"]
    correct = _ask_question(question_data, player)

    if correct:
        _apply_correct(player, q_type, enemy, engine)
        stats = getattr(player, "session_stats", None)
        if stats:
            stats.record(q_type, True)
    else:
        _apply_incorrect(player, q_type, enemy, engine, question_data)

    if correct and player.focus >= player.max_focus:
        _use_focus_ability(player, enemy)


def _use_focus_ability(player, enemy):
    typewriter("\nFocus Ability Ready!")
    typewriter("1. Massive Strike (2x dmg)")
    typewriter("2. Heal 20% HP")
    typewriter("3. Protect Streak")
    
    # Auto-select for debug mode
    if getattr(player, "debug_mode", False):
        ability = "1"  # Always use Massive Strike
        typewriter("[DEBUG AUTO-PLAY] Choosing: 1. Massive Strike")
    else:
        ability = input_handler.ask_choice(
            [
                {"label": "1. Massive Strike (2x dmg)", "value": "1"},
                {"label": "2. Heal 20% HP", "value": "2"},
                {"label": "3. Protect Streak", "value": "3"},
            ],
            "> ",
        )
    if ability == "1":
        dmg, _ = calculate_damage(player, enemy, 1, 5)
        dmg *= 2
        enemy.take_dmg(dmg)
        player.focus = 0
        damage_line("Massive Strike", enemy, dmg)
    elif ability == "2":
        heal = int(player.max_hp * 0.2)
        player.hp = min(player.max_hp, player.hp + heal)
        player.focus = 0
        typewriter(f"You healed {heal} HP!")
    elif ability == "3":
        player.streak_protected = True
        player.focus = 0
        typewriter("Your next wrong answer will not reduce streak.")
    emit_player_stats(player)


def choice_aid(player):
    if not player.inventory:
        typewriter("You have no aid!")
        return
    typewriter("\nYour Inventory:")
    for i, aid in enumerate(player.inventory, 1):
        desc = getattr(aid, "description", "")
        typewriter(f"{i}. {aid.name} — {desc}")
    typewriter(f"{len(player.inventory)+1}. Cancel")
    try:
        choice = int(input_handler.ask_choice(
            [
                {"label": f"{i}. {aid.name}", "value": str(i)}
                for i, aid in enumerate(player.inventory, 1)
            ] + [
                {"label": f"{len(player.inventory) + 1}. Cancel", "value": str(len(player.inventory) + 1)}
            ],
            "Choose an aid: ",
        ))
    except ValueError:
        typewriter("Invalid choice.")
        return
    if choice == len(player.inventory) + 1:
        typewriter("Cancelled.")
        return
    if 1 <= choice <= len(player.inventory):
        aid = player.inventory.pop(choice - 1)
        typewriter(aid.use(player))
        emit_player_stats(player)
    else:
        typewriter("Invalid choice.")


def choice_abstain(player, enemy):
    typewriter("\nAbstaining has consequences:")
    typewriter("  - Lose 5-15 gold")
    typewriter("  - Streak is halved")
    typewriter("  - Vulnerable and Attack Down for 2 turns")
    confirm = input_handler.ask_choice(
        [
            {"label": "Yes", "value": "y"},
            {"label": "No", "value": "n"},
        ],
        "Are you sure? (y/n) > ",
    )
    if confirm.lower() != "y":
        typewriter("You hold your ground.")
        return CONTINUE

    if getattr(player, "run_modifier", "") == "ironwill":
        typewriter("[Iron Will] You cannot escape. Face your enemy!")
        return CONTINUE

    typewriter(f"\n{player.name} attempts to abstain away...")
    time.sleep(1)

    run_chance = min(0.9, max(0.1, 0.5 + (player.spd - enemy.spd) * 0.03))
    if random.random() < run_chance:
        typewriter("You escaped, but at a cost!")
        lost_gold = min(player.gold, random.randint(5, 15))
        player.gold -= lost_gold
        player.streak = max(0, player.streak // 2)
        from statusEffects import AttackDebuff, Vulnerable
        for effect in [AttackDebuff(5, 2), Vulnerable(2)]:
            effect.on_apply(player)
            player.status_effects.append(effect)
        typewriter(f"Lost {lost_gold} gold! Streak halved! Vulnerable for 2 turns.")
        emit_player_stats(player)
        time.sleep(1)
        return ESCAPED
    else:
        typewriter("Failed to escape!")
        if not check_dodge(enemy, player):
            dmg, is_crit = calculate_damage(enemy, player, 0, 3)
            player.take_dmg(dmg)
            if is_crit:
                typewriter("Enemy CRITICAL HIT!")
            damage_line(enemy.name, player, dmg)
        else:
            typewriter("You dodged the enemy's counterattack!")
        emit_player_stats(player)
        time.sleep(1)
        return CONTINUE


# ─────────────────────────────────────────────
# Player turn
# ─────────────────────────────────────────────

def player_turn(player, enemy, learning_engine):
    if getattr(player, "is_stunned", False):
        _set_action_ui(False, False)
        typewriter(f"{player.name} is stunned and cannot act!")
        return CONTINUE

    player.action_points = player.max_action_points

    while player.action_points > 0:
        typewriter(f"\n{player.name}'s turn! AP: {player.action_points}/{player.max_action_points}")
        typewriter("1. Attack  (costs 2 AP)")
        typewriter("2. Ask     (costs 1 AP — can act again after)")
        typewriter(f"3. Aid     (costs 1 AP) [{len(player.inventory)} available]")
        typewriter("4. Abstain (costs 0 AP — escape with penalty)")
        typewriter("5. Skills  (free — view unlocked abilities)")

        # Auto-play for debug mode
        if getattr(player, "debug_mode", False):
            # Alternate between Ask (to answer questions) and Attack
            choice = "2" if random.random() < 0.6 else "1"
            typewriter(f"[DEBUG AUTO-PLAY] Choosing: {choice}")
            time.sleep(0.3)
        else:
            _set_action_ui(True, False)
            choice = input_handler.ask("> ")
            _set_action_ui(False, False)

        if choice == "1":
            if player.action_points < 2:
                typewriter("Not enough AP! (need 2)")
                continue
            choice_attack(player, enemy)
            player.action_points = 0

        elif choice == "2":
            choice_ask(player, enemy, learning_engine)
            player.action_points -= 1

        elif choice == "3":
            choice_aid(player)
            player.action_points -= 1

        elif choice == "4":
            return choice_abstain(player, enemy)

        elif choice == "5":
            _view_skills(player)
            continue

        else:
            typewriter("Invalid choice. Enter 1-5.")
            continue

        if enemy.hp <= 0 or player.hp <= 0:
            break

    return CONTINUE


# ─────────────────────────────────────────────
# Enemy turn
# ─────────────────────────────────────────────

def enemy_turn(enemy, player):
    typewriter(f"\n{enemy.name}'s turn...")
    time.sleep(1)

    if enemy.defense_bonus > 0:
        enemy.defense -= enemy.defense_bonus
        enemy.defense_bonus = 0
    if enemy.behavior == "evasive" and enemy.dodge_modifier > 0:
        enemy.dodge_modifier = max(0.0, enemy.dodge_modifier - 0.2)

    if getattr(enemy, "is_stunned", False):
        typewriter(f"{enemy.name} is stunned and cannot act!")
        return CONTINUE

    behavior = enemy.behavior

    if behavior == "aggressive":
        typewriter(f"{enemy.name} attacks furiously!")
        for _ in range(2):
            if player.hp <= 0:
                break
            if not check_dodge(enemy, player):
                dmg, is_crit = calculate_damage(enemy, player, -1, 1)
                dmg = max(1, dmg // 2)
                player.take_dmg(dmg)
                if is_crit:
                    typewriter("CRITICAL HIT!")
                damage_line(enemy.name, player, dmg)
            else:
                typewriter(f"{player.name} sidesteps the flurry!")
        emit_player_stats(player)
        return CONTINUE

    if behavior == "evasive" and random.random() < 0.3:
        typewriter(f"{enemy.name} shifts into a defensive stance!")
        enemy.dodge_modifier += 0.2
        return CONTINUE

    if behavior == "defensive" and random.random() < 0.4:
        typewriter(f"{enemy.name} braces for impact!")
        enemy.defense += 3
        enemy.defense_bonus = 3

    if check_dodge(enemy, player):
        typewriter(f"{player.name} dodged the attack!")
        return CONTINUE

    dmg, is_crit = calculate_damage(enemy, player, -1, 2)
    player.take_dmg(dmg)
    if is_crit:
        typewriter("Enemy lands a CRITICAL HIT!")
    damage_line(enemy.name, player, dmg)
    emit_player_stats(player)
    time.sleep(1)
    return CONTINUE


# ─────────────────────────────────────────────
# Status effects processor
# ─────────────────────────────────────────────

def process_status_effects(entity):
    for effect in entity.status_effects[:]:
        effect.on_turn_start(entity)
        effect.on_turn_end(entity)
        if effect.is_expired():
            effect.on_expire(entity)
            entity.status_effects.remove(effect)


# ─────────────────────────────────────────────
# Combat loops
# ─────────────────────────────────────────────

def _combat_loop(player, enemy, learning_engine):
    hp_before = player.hp

    while True:
        display_entity_stats(player)
        display_entity_stats(enemy, role="enemy")

        result = player_turn(player, enemy, learning_engine)

        if result == ESCAPED:
            _set_action_ui(False, False)
            _clear_enemy_panel()
            return ESCAPED, False
        if enemy.hp <= 0 or player.hp <= 0:
            break

        process_status_effects(player)
        emit_player_stats(player)
        if enemy.hp <= 0 or player.hp <= 0:
            break

        enemy_turn(enemy, player)
        process_status_effects(enemy)
        if enemy.hp <= 0 or player.hp <= 0:
            break

    if player.hp <= 0:
        _set_action_ui(False, False)
        _clear_enemy_panel()
        typewriter("You were defeated...")
        time.sleep(1)
        return DEATH, False

    _set_action_ui(False, False)
    _clear_enemy_panel()
    typewriter(f"{enemy.name} defeated!")
    time.sleep(1)
    no_damage = player.hp >= hp_before
    typewriter(f"\n--- Battle Summary ---")
    typewriter(f"HP: {player.hp}/{player.max_hp} | Streak: {player.streak}")
    if no_damage:
        typewriter("Flawless victory! No damage taken.")
    time.sleep(0.5)
    return WIN, no_damage


def elite_combat(player, enemy, learning_engine, bestiary=None):
    phase = 1
    typewriter(f"\n*** ELITE ENCOUNTER: {enemy.name}! ***")
    typewriter("Watch for phase shifts!")
    time.sleep(1)

    while enemy.is_alive() and player.is_alive():
        hp_ratio = enemy.hp / enemy.max_hp
        if phase == 1 and hp_ratio <= 0.66:
            phase = 2
            enemy.atk += 4
            typewriter(f"\n{enemy.name} enters a RAGE! ATK increased!")
            time.sleep(1)
        elif phase == 2 and hp_ratio <= 0.33:
            phase = 3
            enemy.defense += 3
            typewriter(f"\n{enemy.name} is DESPERATE! Defense hardened!")
            time.sleep(1)

        display_entity_stats(player)
        display_entity_stats(enemy, role="elite")

        result = player_turn(player, enemy, learning_engine)
        emit_player_stats(player)
        if result == ESCAPED:
            _set_action_ui(False, False)
            _clear_enemy_panel()
            typewriter("You escaped the elite battle!")
            return ESCAPED
        if enemy.hp <= 0:
            _set_action_ui(False, False)
            _clear_enemy_panel()
            typewriter(f"{enemy.name} defeated!")
            if bestiary:
                bestiary.record_kill(enemy.name)
            time.sleep(1)
            return WIN
        if player.hp <= 0:
            _set_action_ui(False, False)
            _clear_enemy_panel()
            typewriter("You were defeated...")
            time.sleep(1)
            return DEATH

        if enemy.hp <= 0:
            _set_action_ui(False, False)
            _clear_enemy_panel()
            if bestiary:
                bestiary.record_kill(enemy.name)
            return WIN
        if player.hp <= 0:
            _set_action_ui(False, False)
            _clear_enemy_panel()
            return DEATH

        if enemy.hp <= 0:
            _set_action_ui(False, False)
            _clear_enemy_panel()
            if bestiary:
                bestiary.record_kill(enemy.name)
            return WIN

    _set_action_ui(False, False)
    _clear_enemy_panel()
    if enemy.hp <= 0 and bestiary:
        bestiary.record_kill(enemy.name)
    return WIN if enemy.hp <= 0 else DEATH


def boss_combat(player, boss, learning_engine, bestiary=None):
    typewriter(f"\n{'='*50}")
    typewriter(f"  BOSS ENCOUNTER: {boss.name}")
    typewriter(f"{'='*50}")
    typewriter("Every action requires answering a question.")
    typewriter("Answer correctly to act. Answer wrong — face the consequences.")
    time.sleep(2)

    BOSS_TELLS = [
        ("The boss winds up for a devastating blow...", "2"),
        ("The boss looks exposed and off-balance...",   "1"),
        ("Dark energy charges around the boss...",      "1"),
        ("The boss begins to slowly regenerate...",     "1"),
        ("The boss locks eyes on you, unblinking...",   "2"),
        ("The boss staggers — now is your chance!",     "1"),
    ]

    phase = 1
    player.dodge_next = False

    while boss.is_alive() and player.is_alive():
        hp_ratio = boss.hp / boss.max_hp
        if phase == 1 and hp_ratio <= 0.66:
            phase = 2
            boss.atk += 5
            typewriter(f"\n{boss.name} PHASE 2: grows more powerful!")
            time.sleep(1)
        elif phase == 2 and hp_ratio <= 0.33:
            phase = 3
            boss.atk += 5
            boss.crit_chance = min(boss.crit_chance + 0.15, 0.5)
            typewriter(f"\n{boss.name} PHASE 3: final form unleashed!")
            time.sleep(1)

        tell_text, ideal = random.choice(BOSS_TELLS)
        typewriter(f"\n{tell_text}")
        time.sleep(0.5)

        display_entity_stats(player)
        display_entity_stats(boss, role="boss")

        typewriter(f"\n{player.name}'s turn:")
        typewriter("1. Strike  — deal damage")
        typewriter("2. Evade   — dodge next attack")
        typewriter("3. Restore — heal 15% HP")
        typewriter("4. Focus   — use Focus ability")

        _set_action_ui(False, True)
        choice = input_handler.ask("> ")
        _set_action_ui(False, False)
        if choice not in ("1", "2", "3", "4"):
            typewriter("Invalid choice. You hesitate — boss attacks!")
            _boss_attack(boss, player)
            emit_player_stats(player)
            continue

        q = learning_engine.get_question(difficulty=3) or learning_engine.get_question()
        if q is None:
            typewriter("No questions loaded. Boss attacks.")
            _boss_attack(boss, player)
            emit_player_stats(player)
            continue

        correct = _ask_question(q, player)
        tell_matched = (choice == ideal)

        if correct:
            player.streak += 1
            player.longest_streak = max(player.longest_streak, player.streak)
            focus_gain = 10 + int(player.wisdom * 0.2)
            player.focus = min(player.max_focus, player.focus + focus_gain)
            typewriter(f"Correct! Streak: {player.streak} | Focus: {player.focus}/{player.max_focus}")
        else:
            typewriter(f"Wrong! The answer was: {q['answer']}")
            if player.streak_protected:
                typewriter("Streak protected!")
                player.streak_protected = False
            else:
                player.streak = player.streak // 2
            player.focus = max(0, player.focus - 10)

        emit_player_stats(player)

        if choice == "1":
            if correct:
                dmg, is_crit = calculate_damage(player, boss, variance_low=2, variance_high=6)
                dmg = int(dmg * 1.5)
                if tell_matched:
                    dmg = int(dmg * 1.3)
                    typewriter("Perfect read! Bonus damage!")
                boss.take_dmg(dmg)
                if is_crit: typewriter("CRITICAL STRIKE!")
                damage_line(player.name, boss, dmg)
            else:
                typewriter("Your strike misses!")
                if tell_matched: typewriter("(Good read, wrong answer.)")
                _boss_attack(boss, player)

        elif choice == "2":
            if correct:
                player.dodge_next = True
                typewriter("Perfect read! Next attack will be dodged!" if tell_matched
                           else "You prepare a dodge.")
            else:
                typewriter("No dodge!")
                if tell_matched: typewriter("(Good read, wrong answer.)")

        elif choice == "3":
            if correct:
                heal = int(player.max_hp * 0.15)
                player.heal(heal)
                typewriter(f"You recover {heal} HP! ({player.hp}/{player.max_hp})")
            else:
                typewriter("Your concentration breaks. No healing!")

        elif choice == "4":
            if player.focus >= player.max_focus:
                if correct:
                    _use_focus_ability(player, boss)
                else:
                    typewriter("Focus broken! No ability.")
            else:
                typewriter(f"Focus not ready ({player.focus}/{player.max_focus}).")

        emit_player_stats(player)

        if boss.hp <= 0:
            _clear_enemy_panel()
            typewriter(f"\n{boss.name} has been defeated!")
            if bestiary:
                bestiary.record_kill(boss.name)
            time.sleep(1)
            return WIN
        if player.hp <= 0:
            _clear_enemy_panel()
            typewriter("\nYou were defeated by the boss...")
            time.sleep(1)
            return DEATH

        process_status_effects(player)
        emit_player_stats(player)
        if player.hp <= 0:
            _clear_enemy_panel()
            return DEATH
        if boss.hp <= 0:
            _clear_enemy_panel()
            if bestiary:
                bestiary.record_kill(boss.name)
            return WIN

        _boss_attack(boss, player)
        emit_player_stats(player)
        process_status_effects(boss)
        if player.hp <= 0:
            _clear_enemy_panel()
            return DEATH

    _set_action_ui(False, False)
    _clear_enemy_panel()
    return WIN if boss.hp <= 0 else DEATH


def _boss_attack(boss, player):
    if player.dodge_next:
        typewriter(f"You dodge {boss.name}'s attack!")
        player.dodge_next = False
        return
    if check_dodge(boss, player):
        typewriter(f"You narrowly dodge {boss.name}'s strike!")
        return
    dmg, is_crit = calculate_damage(boss, player, variance_low=0, variance_high=4)
    player.take_dmg(dmg)
    if is_crit:
        typewriter(f"{boss.name} lands a CRITICAL HIT!")
    damage_line(boss.name, player, dmg)
    typewriter(f"({player.hp}/{player.max_hp} HP remaining)")
    emit_player_stats(player)
    time.sleep(0.5)
