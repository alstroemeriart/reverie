# Combat system and player actions
import random, time
from ui import typewriter
from Spawns import Spawn

# -----------------------------
# Combat States
# -----------------------------
CONTINUE = "continue"
ESCAPED = "escaped"
WIN = "win"
DEATH = "death"

# -----------------------------
# Combat mechanics
# -----------------------------
def check_dodge(attacker, defender):
    """Return True if defender dodges the attack (includes streak bonus)."""
    base_chance = defender.spd * 0.02

    # Streak bonus
    if hasattr(defender, "streak_dodge_bonus"):
        base_chance += defender.streak_dodge_bonus()

    # Vulnerable / other modifiers
    if hasattr(defender, "dodge_modifier"):
        base_chance += defender.dodge_modifier  # can be negative

    return random.random() < base_chance

def check_critical(attacker):
    """Return True if attack is a critical hit."""
    return random.random() < attacker.crit_chance

def calculate_damage(attacker, defender, variance_low=-2, variance_high=2):
    """Calculate damage, considering crits, variance, and streak buffs."""
    raw = attacker.atk
    # Add streak attack bonus if attacker is a MainCharacter
    if hasattr(attacker, "streak_attack_bonus"):
        raw += attacker.streak_attack_bonus()

    variance = random.randint(variance_low, variance_high)
    base = max(1, raw - defender.defense + variance)

    is_crit = check_critical(attacker)
    if is_crit:
        base = int(base * attacker.crit_multiplier)

    return base, is_crit


# -----------------------------
# Display stats function
# -----------------------------
def display_entity_stats(entity):
    typewriter(f"\n--- {entity.name} ---")
    typewriter(f"HP: {entity.hp}/{entity.max_hp}")
    typewriter(f"ATK: {entity.atk} | DEF: {entity.defense} | SPD: {entity.spd}")
    typewriter(f"CRIT: {int(entity.crit_chance*100)}%")
    if hasattr(entity, "streak"):
        typewriter(f"Streak: {entity.streak} (Longest: {entity.longest_streak})")
    if hasattr(entity, "gold"):
        typewriter(f"Gold: {entity.gold}")
    if entity.status_effects:
        typewriter("Status Effects:")
        for effect in entity.status_effects:
            typewriter(f" - {effect.name} ({effect.duration} turns)")
    else:
        typewriter("Status Effects: None")
    time.sleep(0.5)


# -----------------------------
# Player turn
# -----------------------------
def player_turn(player, enemy, learning_engine):

    while True:
        typewriter(f"\n{player.name}'s turn! Choose your action:")
        typewriter("1. Attack")
        typewriter("2. Ask")
        typewriter("3. Aid")
        typewriter("4. Abstain")

        choice = input("> ").strip()

        if choice == "1":
            choice_attack(player, enemy)
            return CONTINUE

        elif choice == "2":
            choice_ask(player, enemy, learning_engine)
            return CONTINUE

        elif choice == "3":
            choice_item(player)
            return CONTINUE

        elif choice == "4":
            return choice_run(player, enemy)

        else:
            typewriter("Invalid choice. Enter 1-4.")

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
    typewriter(f"{player.name} deals {dmg} dmg!")
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

    # True/False
    if q_type == "TF":
        player_answer = input(f"{question} (True/False) > ").strip()
        correct = player_answer.lower() == answer.lower()
    # Multiple Choice
    elif q_type == "MC":
        options = question_data["options"]
        typewriter(question)
        for i, opt in enumerate(options, 1):
            typewriter(f"{i}. {opt}")
        try:
            choice = int(input("> ").strip())
            correct = options[choice-1] == answer
        except:
            correct = False
    # Arithmetic or Identification
    else:
        player_answer = input(f"{question} > ").strip()
        correct = player_answer.lower() == answer.lower()

    if player.focus >= 100:
        typewriter("Focus Ability Ready!")
        typewriter("1. Massive Strike (2x dmg)")
        typewriter("2. Heal 20% HP")
        typewriter("3. Protect Streak")
        ability = input("> ")

        if ability == "1":
            dmg, _ = calculate_damage(player, enemy, 1, 5)
            dmg *= 2
            enemy.take_dmg(dmg)
            player.focus = 0
            typewriter(f"Massive Strike deals {dmg} dmg!")
            return True

        elif ability == "2":
            heal = int(player.max_hp * 0.2)
            player.hp = min(player.max_hp, player.hp + heal)
            player.focus = 0
            typewriter(f"You healed {heal} HP!")
            return True

        elif ability == "3":
            player.streak_protected = True
            player.focus = 0
            typewriter("Your next wrong answer will not reduce streak.")
            return True

    # Resolve damage or counterattack
    if correct:
        typewriter("Correct!")

        # -----------------------------
        # STREAK + FOCUS LOGIC
        # -----------------------------
        player.streak += 1
        player.longest_streak = max(player.longest_streak, player.streak)

        # Increase mastery (make sure q_type exists earlier in function)
        if hasattr(player, "mastery") and q_type in player.mastery:
            player.mastery[q_type] += 1

        # Focus gain scales with wisdom
        focus_gain = 10 + int(player.wisdom * 0.2)
        player.focus = min(player.max_focus, player.focus + focus_gain)

        typewriter(f"Streak: {player.streak}")
        typewriter(f"Focus: {player.focus}/{player.max_focus}")

        # -----------------------------
        # DAMAGE PHASE
        # -----------------------------
        if not check_dodge(player, enemy):

            dmg, is_crit = calculate_damage(player, enemy, 1, 5)

            # Apply streak multiplier again if you want empowered strike feel
            # (Remove this line if streak already handled fully inside calculate_damage)
            dmg = int(dmg)

            enemy.take_dmg(dmg)

            if is_crit:
                typewriter("CRITICAL HIT!")

            typewriter(f"{enemy.name} takes {dmg} dmg!")

        else:
            typewriter(f"{enemy.name} dodged the empowered strike!")

    else:
        typewriter("Incorrect!")

        # -----------------------------
        # STREAK PENALTY
        # -----------------------------
        if player.streak_protected:
            typewriter("Your streak was protected!")
            player.streak_protected = False
        else:
            player.streak = player.streak // 2

        # Focus penalty
        player.focus = max(0, player.focus - 15)

        typewriter(f"Streak reduced to {player.streak}")
        typewriter(f"Focus: {player.focus}/{player.max_focus}")

        # -----------------------------
        # ENEMY PUNISHMENT ATTACK
        # -----------------------------
        if not check_dodge(enemy, player):

            dmg, is_crit = calculate_damage(enemy, player, 0, 3)

            player.take_dmg(dmg)

            if is_crit:
                typewriter("Enemy CRITICAL HIT!")

            typewriter(f"You take {dmg} dmg!")

        else:
            typewriter("You dodged the punishment attack!")

        time.sleep(1)
        return True

def choice_item(player):
    if not player.inventory:
        typewriter("You have no aid!")
        return True

    typewriter("\nYour Inventory:")
    for i, aid in enumerate(player.inventory, 1):
        typewriter(f"{i}. {aid.name}")
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

def choice_run(player, enemy):
    typewriter(f"\n{player.name} attempts to abstain away...")
    time.sleep(1)

    run_chance = 0.5 + (player.spd - enemy.spd) * 0.03
    run_chance = min(0.9, max(0.1, run_chance))

    if random.random() < run_chance:
        typewriter("You successfully escaped, but at a cost!")
        time.sleep(1)

        # Penalty
        lost_gold = min(player.gold, random.randint(5, 15))
        player.gold -= lost_gold
        player.streak = max(0, player.streak // 2)

        # Apply temporary debuffs
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

        # Enemy attacks immediately
        if not check_dodge(enemy, player):
            dmg, is_crit = calculate_damage(enemy, player, 0, 3)
            player.take_dmg(dmg)
            if is_crit:
                typewriter("Enemy CRITICAL HIT!")
            typewriter(f"{enemy.name} hits you for {dmg} dmg!")
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

    if check_dodge(enemy, player):
        typewriter(f"{player.name} dodged the attack!")
        return CONTINUE

    dmg, is_crit = calculate_damage(enemy, player, -1, 2)
    player.take_dmg(dmg)

    if is_crit:
        typewriter("Enemy lands a CRITICAL HIT!")

    typewriter(f"{enemy.name} attacks {player.name} for {dmg} dmg!")
    time.sleep(1)

    return CONTINUE

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