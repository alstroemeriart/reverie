# combatSystem.py
import random, time
from ui import typewriter
from Spawns import Spawn

# -----------------------------
# Combat mechanics
# -----------------------------
def check_dodge(attacker, defender):
    """Return True if defender dodges the attack."""
    dodge_chance = defender.spd * 0.02
    return random.random() < dodge_chance

def check_critical(attacker):
    """Return True if attack is a critical hit."""
    return random.random() < attacker.crit_chance

def calculate_damage(attacker, defender, variance_low=-2, variance_high=2):
    """Calculate damage, considering crits and variance."""
    base = max(1, attacker.atk - defender.defense + random.randint(variance_low, variance_high))
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
        typewriter("3. Item")
        typewriter("4. Run")
        choice = input("> ").strip()

        if choice == "1":
            return choice_attack(player, enemy)
        elif choice == "2":
            return choice_ask(player, enemy, learning_engine)
        elif choice == "3":
            return choice_item(player)
        elif choice == "4":
            return choice_run(player, enemy)
        else:
            typewriter("Invalid choice. Enter 1-4.", 0.03)
            time.sleep(0.5)

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

    # Resolve damage or counterattack
    if correct:
        typewriter("Correct!")
        if not check_dodge(player, enemy):
            dmg, is_crit = calculate_damage(player, enemy, 1, 5)
            dmg *= 2
            enemy.take_dmg(dmg)
            if is_crit:
                typewriter("CRITICAL HIT!")
            typewriter(f"{enemy.name} takes {dmg} dmg!")
        else:
            typewriter(f"{enemy.name} dodged the empowered strike!")
    else:
        typewriter("Incorrect!")
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
        typewriter("You have no items!")
        return True

    typewriter("\nYour Inventory:")
    for i, item in enumerate(player.inventory, 1):
        typewriter(f"{i}. {item.name}")
    typewriter(f"{len(player.inventory)+1}. Cancel")

    try:
        choice = int(input("Choose an item: ").strip())
    except:
        typewriter("Invalid choice.")
        return True

    if choice == len(player.inventory)+1:
        typewriter("Cancelled.")
        return True

    if choice < 1 or choice > len(player.inventory):
        typewriter("Invalid choice.")
        return True

    item = player.inventory.pop(choice-1)
    typewriter(item.use(player))
    return True

def choice_run(player, enemy):
    typewriter(f"\n{player.name} attempts to run away...")
    time.sleep(1)

    run_chance = 0.5 + (player.spd - enemy.spd) * 0.03
    if random.random() < run_chance:
        typewriter("You successfully escaped!")
        time.sleep(1)
        return False
    else:
        typewriter("Failed to escape!")
        if not check_dodge(enemy, player):
            dmg, is_crit = calculate_damage(enemy, player, 0, 3)
            player.take_dmg(dmg)
            if is_crit:
                typewriter("Enemy CRITICAL HIT!")
            typewriter(f"{enemy.name} hits you for {dmg} dmg!")
        else:
            typewriter("You dodged the punishment attack!")
        time.sleep(1)
        return True

# -----------------------------
# Enemy turn
# -----------------------------
def enemy_turn(enemy, player):
    typewriter(f"\n{enemy.name}'s turn...")
    time.sleep(1)

    if check_dodge(enemy, player):
        typewriter(f"{player.name} dodged the attack!")
        return True

    dmg, is_crit = calculate_damage(enemy, player, -1, 2)
    player.take_dmg(dmg)
    if is_crit:
        typewriter("Enemy lands a CRITICAL HIT!")
    typewriter(f"{enemy.name} attacks {player.name} for {dmg} dmg!")
    time.sleep(1)
    return True

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