# COMBAT SYSTEM

import random, time
from ui import typewriter, clear_screen, hp_bar
from Spawns import Spawn
from combatCalc import calculate_damage, check_dodge, check_critical
from items import Aid
from progression import gain_mastery, mastery_multiplier, apply_skills, unlock_skills

# -----------------------------
# Combat States
# -----------------------------
CONTINUE = "continue"
ESCAPED = "escaped"
WIN = "win"
DEATH = "death"

# -----------------------------
# Damage line helper
# -----------------------------
def damage_line(attacker_name, target, dmg):
    ratio = dmg / target.max_hp
    if ratio >= 0.25:
        typewriter(f"HEAVY HIT! {attacker_name} deals {dmg} damage!")
    elif ratio >= 0.10:
        typewriter(f"{attacker_name} deals {dmg} damage.")
    else:
        typewriter(f"{attacker_name} grazes for {dmg} damage.")


# -----------------------------
# Display stats function
# -----------------------------
def display_entity_stats(entity):
    clear_screen()
    typewriter(f"\n--- {entity.name} ---")
    typewriter(f"HP:  {hp_bar(entity.hp, entity.max_hp)}")
    if hasattr(entity, "shield") and entity.shield > 0:
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
    time.sleep(0.5)


# -----------------------------
# Player turn
# -----------------------------
def player_turn(player, enemy, learning_engine):

    if getattr(player, "is_stunned", False):
        typewriter(f"{player.name} is stunned and cannot act!")
        player.action_points = 0
        return CONTINUE

    # Refresh action points at the start of the turn
    player.action_points = player.max_action_points

    while player.action_points > 0:
        typewriter(f"\n{player.name}'s turn! AP: {player.action_points}/{player.max_action_points}")
        typewriter("1. Attack  (costs 2 AP — uses whole turn)")
        typewriter("2. Ask     (costs 1 AP — can act again after)")
        typewriter(f"3. Aid     (costs 1 AP) [{len(player.inventory)} aids available]")
        typewriter("4. Abstain (costs 0 AP — ends turn, with penalty)")
        typewriter("5. Abilities (costs 0 AP — view unlocked abilities)")

        choice = input("> ").strip()

        if choice == "1":
            if player.action_points < 2:
                typewriter("Not enough AP for a full attack! (need 2)")
                continue
            choice_attack(player, enemy)
            player.action_points = 0          # uses the whole turn

        elif choice == "2":
            choice_ask(player, enemy, learning_engine)
            player.action_points -= 1         # can still act if AP remains

        elif choice == "3":
            choice_aid(player)
            player.action_points -= 1

        elif choice == "4":
            return choice_abstain(player, enemy)  # run can still escape mid-turn

        elif choice == "5":
            _view_skills(player)
            continue

        else:
            typewriter("Invalid choice. Enter 1-4.")
            continue

        # Check if combat ended mid-turn
        if enemy.hp <= 0 or player.hp <= 0:
            break

    return CONTINUE

# -----------------------------
# Player actions
# -----------------------------
def choice_attack(player, enemy):
    typewriter(f"\n{player.name} attacks {enemy.name}!")
    time.sleep(0.5)

    if check_dodge(player, enemy):
        typewriter(f"{enemy.name} dodged the attack!")
        return True

    dmg, is_crit = calculate_damage(player, enemy)
    enemy.take_dmg(dmg)

    if is_crit:
        typewriter("CRITICAL HIT!")
    damage_line(player.name, enemy, dmg)

    time.sleep(1)
    return True

def choice_ask(player, enemy, engine):
    """Ask a random question from the learning engine."""

    question_data = engine.get_random_question()
    if not question_data:
        typewriter("No questions loaded.")
        return True

    q_type = question_data["type"]
    question = question_data["question"]
    answer = question_data["answer"]

    # Show category and mastery before the question
    category_names = {
        "TF": "True/False",
        "MC": "Multiple Choice",
        "AR": "Arithmetic",
        "ID": "Identification"
    }
    mastery_val = player.mastery.get(q_type, 0)

    next_milestone = ((mastery_val // 5) + 1) * 5
    typewriter(f"\n[{category_names.get(q_type, q_type)} | Mastery: {mastery_val} → next skill at {next_milestone}]")

    correct = False

    # -----------------------------
    # Ask the question (hint applied inside each branch)
    # -----------------------------
    if q_type == "TF":
        if player.hint_active:
            typewriter(f"[Hint: the answer has {len(answer)} characters]")
            typewriter("[Hint: think carefully about whether this is always true]")
            player.hint_active = False
        player_answer = input(f"{question} (True/False) > ").strip()
        correct = player_answer.lower() == answer.lower()

    elif q_type == "MC":
        options = question_data["options"]
        if hasattr(player, "mc_eliminate") and player.mc_eliminate > 0:
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
        try:
            choice = int(input("> ").strip())
            correct = options[choice - 1] == answer
        except (ValueError, IndexError):
            correct = False

    elif q_type in ["AR", "ID"]:
        # AR or ID
        if player.hint_active:
            typewriter(f"[Hint: the answer starts with '{answer[0]}' and has {len(answer)} character(s)]")
            player.hint_active = False
        player_answer = input(f"{question} > ").strip()
        correct = player_answer.lower() == answer.lower()

    elif q_type == "OD":
        items = question_data["items"]
        typewriter(question)
        shuffled = items[:]
        random.shuffle(shuffled)
        for i, item in enumerate(shuffled, 1):
            typewriter(f"  {i}. {item}")
        typewriter("Enter the correct order as numbers (e.g. 3,1,4,2):")
        try:
            raw = input("> ").strip()
            order = [int(x.strip()) - 1 for x in raw.split(",")]
            if len(order) != len(items):
                correct = False
            else:
                player_sequence = [shuffled[i] for i in order]
                # answer is "1,2,3,4" = positions in original items list (1-indexed)
                correct_sequence = [items[int(i) - 1] for i in question_data["answer"].split(",")]
                correct = player_sequence == correct_sequence
        except (ValueError, IndexError):
            correct = False

    passive = getattr(player, "class_passive", "")

    # -----------------------------
    # Resolve correct answer
    # -----------------------------
    if correct:
        typewriter("Correct!") 
        gain_mastery(player, q_type)

        player.streak += 1
        player.longest_streak = max(player.longest_streak, player.streak)

        unlock_skills(player)

        focus_gain = 10 + int(player.wisdom * 0.2)
        player.focus = min(player.max_focus, player.focus + focus_gain)

        typewriter(f"Streak: {player.streak} | Focus: {player.focus}/{player.max_focus}")

        if passive == "bloodlust":
            if not hasattr(player, "bloodlust_stacks"):
                player.bloodlust_stacks = 0
            if player.bloodlust_stacks < 10:
                player.atk += 1
                player.bloodlust_stacks += 1
                typewriter(f"[Bloodlust] ATK permanently increased to {player.atk}!")

        elif passive == "momentum":
            bonus_crit = min(0.02 * player.streak, 0.30)
            player.crit_chance += bonus_crit
            typewriter(f"[Momentum] Crit chance this strike: {int((player.crit_chance + bonus_crit)*100)}%")

        elif passive == "luck":
            if random.random() < 0.05:
                gold_found = random.randint(5, 30)
                player.gold += gold_found
                typewriter(f"[Luck] It rained gold! You collected {gold_found} gold.")
            if random.random() < 0.03:
                player.hint_active = True
                typewriter("[Luck] You feel lucky! Your next question will have a hint.")
            if random.random() < 0.02:
                player.streak += 1
                typewriter("[Luck] Your luck spiked intellect! Streak increased by 1.")
            if random.random() < 0.01:
                player.focus = min(player.max_focus, player.focus + 20)
                typewriter("[Luck] A surge of insight fills you! Focus increased by 20.")
            if random.random() < 0.005:
                typewriter("[Luck] The forces of chance fights for you!")
                enemy.take_dmg(int(enemy.max_hp * 0.05))

        # --- DAMAGE PHASE ---
        if not check_dodge(player, enemy):
            dmg, is_crit = calculate_damage(player, enemy, 1, 5)

            # APPLY MASTERY SCALING
            dmg = int(dmg * mastery_multiplier(player, q_type))

            # APPLY SKILLS
            context = {
                "type": "attack",
                "q_type": q_type,
                "damage": dmg,
                "correct": True
            }

            apply_skills(player, context)
            dmg = context["damage"]

            # Scholar modifier
            if getattr(player, "run_modifier", "") == "scholar":
                dmg = int(dmg * 2)
                typewriter("[Scholar's Burden] Knowledge empowers your strike!")

            enemy.take_dmg(dmg)

            if is_crit:
                typewriter("CRITICAL HIT!")

            damage_line(player.name, enemy, dmg)

    # -----------------------------
    # Resolve incorrect answer
    # -----------------------------
    else:
        typewriter("Incorrect!")

        if passive == "fortress":
            typewriter("[Fortress] Your defenses hold — no punishment attack.")
        else:
            if getattr(player, "run_modifier", "") == "cursed":
                player.take_dmg(10)
                typewriter("[Cursed Knowledge] You take 10 HP from the wrong answer!")

            if player.streak_protected:
                typewriter("Your streak was protected!")
                player.streak_protected = False
            else:
                player.streak = player.streak // 2

            player.focus = max(0, player.focus - 15)

            typewriter(f"Streak reduced to {player.streak}")
            typewriter(f"Focus: {player.focus}/{player.max_focus}")

            if not check_dodge(enemy, player):
                dmg, is_crit = calculate_damage(enemy, player, 0, 3)
                player.take_dmg(dmg)
                if is_crit:
                    typewriter("Enemy CRITICAL HIT!")
                damage_line(enemy.name, player, dmg)
            else:
                typewriter("You dodged the punishment attack!")

            time.sleep(1)
            return True

    # -----------------------------
    # Focus ability (only triggers after a correct answer)
    # -----------------------------
    if player.focus >= player.max_focus:
        typewriter("\nFocus Ability Ready!")
        typewriter("1. Massive Strike (2x dmg)")
        typewriter("2. Heal 20% HP")
        typewriter("3. Protect Streak")
        ability = input("> ").strip()

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

    return True

def choice_aid(player):
    if not player.inventory:
        typewriter("You have no aid!")
        return True

    typewriter("\nYour Inventory:")
    for i, aid in enumerate(player.inventory, 1):
        typewriter(f"{i}. {aid.name} — {aid.description}")
    typewriter(f"{len(player.inventory)+1}. Cancel")

    try:
        choice = int(input("Choose an aid: ").strip())
    except:
        typewriter("Invalid choice.")
        return True

    if choice == len(player.inventory)+1:
        typewriter("Cancelled.")
        return True

    if choice < 1 or choice > len(player.inventory):
        typewriter("Invalid choice.")
        return True

    aid = player.inventory.pop(choice-1)
    typewriter(aid.use(player))
    return True

def choice_abstain(player, enemy):
    typewriter(f"\nAbstaining has consequences:")
    typewriter(f"  - Lose 5-15 gold")
    typewriter(f"  - Streak is halved")
    typewriter(f"  - Vulnerable and Attack Down for 2 turns")
    typewriter("Are you sure you want to abstain? (y/n)")
    confirm = input("> ").strip().lower()

    if confirm != "y":
        typewriter("You hold your ground.")
        return CONTINUE

    typewriter(f"\n{player.name} attempts to abstain away...")
    time.sleep(1)

    if getattr(player, "run_modifier", "") == "ironwill":
        typewriter("[Iron Will] You cannot escape. Face your enemy!")
        return CONTINUE

    run_chance = 0.5 + (player.spd - enemy.spd) * 0.03
    run_chance = min(0.9, max(0.1, run_chance))

    if random.random() < run_chance:
        typewriter("You successfully escaped, but at a cost!")
        time.sleep(1)

        lost_gold = min(player.gold, random.randint(5, 15))
        player.gold -= lost_gold
        player.streak = max(0, player.streak // 2)

        from statusEffects import AttackDebuff, Vulnerable

        attack_debuff = AttackDebuff(amount=5, duration=2)
        attack_debuff.on_apply(player)
        player.status_effects.append(attack_debuff)

        vulnerable = Vulnerable(duration=2)
        vulnerable.on_apply(player)
        player.status_effects.append(vulnerable)

        typewriter(f"You lost {lost_gold} Gold!")
        typewriter("Your streak is halved!")
        typewriter("You feel vulnerable and weaker for 2 turns!")
        time.sleep(1)

        return ESCAPED

    else:
        typewriter("Failed to escape!")
        time.sleep(0.5)

        if not check_dodge(enemy, player):
            dmg, is_crit = calculate_damage(enemy, player, 0, 3)
            player.take_dmg(dmg)
            if is_crit:
                typewriter("Enemy CRITICAL HIT!")
            damage_line(enemy.name, player, dmg)
        else:
            typewriter("You dodged the enemy's counterattack!")

        time.sleep(1)
        return CONTINUE

# -----------------------------
# Enemy turn
# -----------------------------
def enemy_turn(enemy, player):
    typewriter(f"\n{enemy.name}'s turn...")
    time.sleep(1)

    # Reset temporary modifiers from last turn
    if hasattr(enemy, "defense_bonus") and enemy.defense_bonus > 0:
        enemy.defense -= enemy.defense_bonus
        enemy.defense_bonus = 0

    if getattr(enemy, "behavior", "normal") == "evasive":
        if hasattr(enemy, "dodge_modifier") and enemy.dodge_modifier > 0:
            enemy.dodge_modifier = max(0, enemy.dodge_modifier - 0.2)

    # Stun check
    if getattr(enemy, "is_stunned", False):
        typewriter(f"{enemy.name} is stunned and cannot act!")
        return CONTINUE

    behavior = getattr(enemy, "behavior", "normal")

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
        return CONTINUE

    elif behavior == "evasive":
        if random.random() < 0.3:
            typewriter(f"{enemy.name} shifts into a defensive stance!")
            if not hasattr(enemy, "dodge_modifier"):
                enemy.dodge_modifier = 0
            enemy.dodge_modifier += 0.2
            return CONTINUE

    elif behavior == "defensive":
        if random.random() < 0.4:
            typewriter(f"{enemy.name} braces for impact!")
            enemy.defense += 3
            enemy.defense_bonus = 3
            # Still attacks after bracing

    # Default attack (shared by normal, defensive after bracing, evasive if no dodge)
    if check_dodge(enemy, player):
        typewriter(f"{player.name} dodged the attack!")
        return CONTINUE

    dmg, is_crit = calculate_damage(enemy, player, -1, 2)
    player.take_dmg(dmg)

    if is_crit:
        typewriter("Enemy lands a CRITICAL HIT!")
    damage_line(enemy.name, player, dmg)
    time.sleep(1)
    return CONTINUE

# -----------------------------
# Elite combat
# -----------------------------
def elite_combat(player, enemy, learning_engine):
    """
    Elite encounter: same loop as start_combat but the enemy has phases.
    At 66% and 33% HP the elite gains stat boosts and announces a phase shift.
    The player's streak bonus is doubled (handled inside calculate_damage via
    streak_attack_bonus, which already scales with streak).
    """
    phase = 1
    typewriter(f"\n*** ELITE ENCOUNTER: {enemy.name}! ***")
    typewriter("This enemy is stronger than usual. Watch for phase shifts!")
    time.sleep(1)

    while enemy.is_alive() and player.is_alive():

        # Phase transitions
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
        display_entity_stats(enemy)

        result = player_turn(player, enemy, learning_engine)

        if result == ESCAPED:
            typewriter("You escaped the elite battle!")
            return ESCAPED

        if enemy.hp <= 0:
            typewriter(f"{enemy.name} defeated!")
            time.sleep(1)
            return WIN

        if player.hp <= 0:
            typewriter("You were defeated...")
            time.sleep(1)
            return DEATH

        process_status_effects(player)

        if enemy.hp <= 0:
            return WIN
        if player.hp <= 0:
            return DEATH

        enemy_turn(enemy, player)
        process_status_effects(enemy)

        if player.hp <= 0:
            return DEATH
        if enemy.hp <= 0:
            return WIN

    return DEATH if not player.is_alive() else WIN


# -----------------------------
# Boss combat
# -----------------------------
def boss_combat(player, boss, learning_engine):
    """
    Main boss encounter.
    The player cannot act freely — every action (attack, dodge, heal, focus)
    requires answering a question first.
    Correct answer = the action succeeds.
    Wrong answer   = the action fails AND the boss immediately counterattacks.
    The boss also has three phases triggered by HP thresholds.
    """
    typewriter(f"\n{'='*50}")
    typewriter(f"  BOSS ENCOUNTER: {boss.name}")
    typewriter(f"{'='*50}")
    typewriter("You cannot act freely. Every move requires knowledge.")
    typewriter("Answer correctly to act. Answer wrong — face the consequences.")
    time.sleep(2)

    phase = 1
    player.dodge_next = False   # flag for the evade action

    while boss.is_alive() and player.is_alive():

        # Phase transitions
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

        # --- Boss telegraphs its next move ---
        BOSS_TELLS = [
            ("The boss winds up for a devastating blow...", "2"),   # evade
            ("The boss looks exposed and off-balance...",  "1"),    # strike
            ("Dark energy charges around the boss...",     "1"),    # strike
            ("The boss begins to slowly regenerate...",    "1"),    # strike fast
            ("The boss locks eyes on you, unblinking...",  "2"),    # evade
            ("The boss staggers — now is your chance!",    "1"),    # strike
        ]
        tell_text, ideal_action = random.choice(BOSS_TELLS)
        typewriter(f"\n{tell_text}")
        time.sleep(0.5)

        display_entity_stats(player)
        display_entity_stats(boss)

        # --- Player chooses an action ---
        typewriter(f"\n{player.name}'s turn — choose an action:")
        typewriter("1. Strike  — answer to deal damage")
        typewriter("2. Evade   — answer to dodge the boss's next attack")
        typewriter("3. Restore — answer to heal 15% max HP")
        typewriter("4. Focus   — answer to charge Focus ability (if ready, fires first)")

        choice = input("> ").strip()
        if choice not in ("1", "2", "3", "4"):
            typewriter("Invalid choice. You hesitate — boss attacks!")
            _boss_attack(boss, player)
            continue

        # --- Ask a difficulty-3 question ---
        q = learning_engine.get_question(difficulty=3)
        if q is None:
            q = learning_engine.get_question()  # fallback if no d3 questions exist yet
        if q is None:
            typewriter("No questions loaded. Boss attacks by default.")
            _boss_attack(boss, player)
            continue

        correct = _ask_boss_question(q, player)
        tell_matched = (choice == ideal_action)

        # --- Resolve the chosen action ---
        if choice == "1":
            if correct:
                # Damage scales with difficulty — boss questions hit harder when right
                dmg, is_crit = calculate_damage(player, boss, variance_low=2, variance_high=6)
                dmg = int(dmg * 1.5)   # bonus for answering correctly under pressure
                if tell_matched:
                    dmg = int(dmg * 1.3)
                boss.take_dmg(dmg)
                if is_crit:
                    typewriter("CRITICAL STRIKE!")
                damage_line(player.name, boss, dmg)
            else:
                typewriter("Your strike misses! The boss punishes you.")
                if tell_matched:
                    typewriter("(You read the opening right, but fumbled the answer.)")
                _boss_attack(boss, player)

        elif choice == "2":
            if correct:
                player.dodge_next = True
                if tell_matched:
                    typewriter("Perfect read! You're completely prepared.")
                    typewriter("Next attack will be dodged!")
                else:
                    typewriter("You prepare a dodge — but was this the right moment?")
            else:
                typewriter("You misread the opening. No dodge!")
                if tell_matched:
                    typewriter("(You saw the opening, but couldn't answer in time.)")

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
                    typewriter("Focus ability activated!")
                    typewriter("1. Massive Strike (2x dmg)")
                    typewriter("2. Full Heal")
                    typewriter("3. Protect Streak")
                    ability = input("> ").strip()
                    if ability == "1":
                        dmg, _ = calculate_damage(player, boss, 2, 6)
                        dmg = int(dmg * 2)
                        boss.take_dmg(dmg)
                        damage_line("Massive Strike", boss, dmg)
                    elif ability == "2":
                        player.hp = player.max_hp
                        typewriter("Fully healed!")
                    elif ability == "3":
                        player.streak_protected = True
                        typewriter("Streak protected!")
                    player.focus = 0
                else:
                    typewriter("Focus broken! No ability.")
            else:
                typewriter(f"Focus not ready ({player.focus}/{player.max_focus}). Turn wasted!")

        if boss.hp <= 0:
            typewriter(f"\n{boss.name} has been defeated!")
            time.sleep(1)
            return WIN

        if player.hp <= 0:
            typewriter("\nYou were defeated by the boss...")
            time.sleep(1)
            return DEATH

        # Process player status effects
        process_status_effects(player)

        if player.hp <= 0:
            return DEATH
        if boss.hp <= 0:
            return WIN

        # --- Boss attacks (unless player has dodge flag) ---
        _boss_attack(boss, player)
        process_status_effects(boss)

        if player.hp <= 0:
            return DEATH

    return DEATH if not player.is_alive() else WIN


def _ask_boss_question(q, player):
    """Helper: ask one boss question, return True if correct."""
    q_type = q["type"]
    question = q["question"]
    answer = q["answer"]

    typewriter(f"\nBoss Challenge: {question}")

    if q_type == "TF":
        player_answer = input("(True/False) > ").strip()
        correct = player_answer.lower() == answer.lower()
    elif q_type == "MC":
        options = q.get("options", [])
        for i, opt in enumerate(options, 1):
            typewriter(f"  {i}. {opt}")
        try:
            idx = int(input("> ").strip()) - 1
            correct = options[idx] == answer
        except (ValueError, IndexError):
            correct = False
    else:
        player_answer = input("> ").strip()
        correct = player_answer.lower() == answer.lower()

    if correct:
        player.streak += 1
        player.longest_streak = max(player.longest_streak, player.streak)
        focus_gain = 10 + int(player.wisdom * 0.2)
        player.focus = min(player.max_focus, player.focus + focus_gain)
        typewriter(f"Correct! Streak: {player.streak} | Focus: {player.focus}/{player.max_focus}")
    else:
        typewriter(f"Wrong! The answer was: {answer}")
        if player.streak_protected:
            typewriter("Streak protected!")
            player.streak_protected = False
        else:
            player.streak = player.streak // 2
        player.focus = max(0, player.focus - 10)

    return correct


def _boss_attack(boss, player):
    """Helper: boss attacks the player, respecting dodge_next flag."""
    if getattr(player, "dodge_next", False):
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
    time.sleep(0.5)

def _view_skills(player):
    """Display the player's skill tree and unlock status."""
    typewriter("\n--- Your Skills ---")
    if not hasattr(player, "skills") or not player.skills:
        typewriter("No skills available.")
        return
    for skill in player.skills:
        if skill.unlocked:
            typewriter(f"  [UNLOCKED] {skill.name} ({skill.tree} tree)")
        else:
            current = player.mastery.get(skill.tree, 0)
            typewriter(f"  [locked]   {skill.name} ({skill.tree} mastery: {current}/5)")
    time.sleep(0.5)

# -----------------------------
# Status effects
# -----------------------------
def process_status_effects(entity):
    for effect in entity.status_effects[:]:
        effect.on_turn_start(entity)
        effect.on_turn_end(entity)
        if effect.is_expired():
            effect.on_expire(entity)
            entity.status_effects.remove(effect)