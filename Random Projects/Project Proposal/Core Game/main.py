# Main game loop and character creation

import time, os, random
from Spawns import MainCharacter, Enemy, Spawn
from statusEffects import StatusEffect
from items import HealingPotion, AttackBoost, HintPotion
from progression import create_skill_pool
from combatSystem import (
    player_turn,
    enemy_turn,
    process_status_effects,
    display_entity_stats,
    ESCAPED, CONTINUE, WIN, DEATH
)
from ui import title_screen, game_over_screen, typewriter, clear_screen, hp_bar
from combatCalc import calculate_damage, check_dodge, check_critical
from enemyPool import generate_random_enemy, scale_enemy
from learningEngine import LearningEngine, quiz_trial, combat_item_drop, validate_notes
from shop import shop
from saveLoad import save_game, load_game, delete_save, save_exists
from config import load_config, get_notes_paths, get_save_path, get_last_run_path
from achievements import load_achievements, save_achievements, check_achievements, print_achievements
from narrative import (show_opening, show_node_flavor, show_streak_comment,
                       show_wrong_flavor, show_correct_flavor,
                       show_tier_narrative, show_death_narrative,
                       show_victory_narrative)

CONFIG = load_config()
NOTE_PATHS = get_notes_paths(CONFIG)
SAVE_PATH = get_save_path(CONFIG)
LAST_RUN_PATH = get_last_run_path(CONFIG)

# Difficulty assignment per question type
NOTE_DIFFICULTIES = {
    "TF": 1,
    "MC": 2,
    "AR": 2,
    "ID": 3,
}

# Validate and load notes
engine = LearningEngine()
for qtype, path in NOTE_PATHS.items():
    validate_notes(path, qtype)
    engine.load_notes(path, qtype=qtype, difficulty=NOTE_DIFFICULTIES.get(qtype, 1))

class PathNode:
    def __init__(self, node_type, tier=1):
        """
        node_type:
            "battle"
            "elite"
            "shop"
            "maze"
            "rest"
        """
        self.node_type = node_type
        self.tier = tier

    def describe(self):
        descriptions = {
            "battle": [
                "A hostile presence lurks ahead...",
                "You hear movement in the shadows.",
                "Something is waiting around the corner.",
                "The path ahead smells of danger.",
            ],
            "elite": [
                "A powerful elite enemy blocks your path.",
                "The air feels heavier here. Something strong is near.",
                "A fearsome silhouette stands between you and the exit.",
                "Your instincts scream at you to turn back.",
            ],
            "shop": [
                "A wandering merchant appears.",
                "The smell of a campfire and commerce drifts toward you.",
                "Someone has set up a makeshift stall ahead.",
            ],
            "maze": [
                "A mysterious maze entrance glows faintly.",
                "A labyrinth stretches before you, humming with energy.",
                "The walls here seem to shift when you're not looking.",
            ],
            "rest": [
                "A quiet sanctuary for recovery.",
                "A warm alcove offers a moment of peace.",
                "The fighting fades here. You can breathe.",
            ],
            "boss": [
                "An overwhelming darkness fills the corridor...",
                "The ground trembles faintly with each step forward.",
                "Everything here feels wrong. Something enormous is ahead.",
            ],
        }
        options = descriptions.get(self.node_type, ["An unknown path."])
        return random.choice(options)

def draw_run_map(nodes_cleared, current_tier, run_log, next_node_type=None):
    """Display a visual map of run progression."""
    clear_screen()
    typewriter(f"\n{'='*50}")
    typewriter(f"  RUN MAP  |  Tier {current_tier}/3  |  Node {nodes_cleared}")
    typewriter(f"{'='*50}")

    # Icon map for node types
    icons = {
        "battle": "[B]",
        "elite":  "[E]",
        "shop":   "[S]",
        "maze":   "[M]",
        "rest":   "[R]",
        "boss":   "[!]",
        "unknown":"[?]",
    }

    # Parse run_log to get past node types
    past_nodes = []
    for entry in run_log:
        if "Defeated enemy" in entry:
            past_nodes.append("battle")
        elif "ELITE" in entry:
            past_nodes.append("elite")
        elif "shop" in entry.lower():
            past_nodes.append("shop")
        elif "maze" in entry.lower():
            past_nodes.append("maze")
        elif "Rested" in entry:
            past_nodes.append("rest")
        elif "BOSS" in entry:
            past_nodes.append("boss")
        elif "Fled" in entry:
            past_nodes.append("battle")

    # Build the map line
    map_line = ""
    for i, node_type in enumerate(past_nodes):
        map_line += f"{icons.get(node_type, '[?]')}--"

    # Current position marker
    map_line += "[*]"

    # Next node preview
    if next_node_type:
        map_line += f"--{icons.get(next_node_type, '[?]')}?"

    typewriter(f"\n  {map_line}")

    # Legend
    typewriter("\n  Legend: [B]attle [E]lite [S]hop [M]aze [R]est [!]Boss [*]You")

    # Tier progress bar
    tier_fill = "#" * (nodes_cleared % 5) + "-" * (5 - (nodes_cleared % 5))
    nodes_to_next = 5 - (nodes_cleared % 5)
    typewriter(f"\n  Tier progress: [{tier_fill}] {nodes_to_next} nodes to Tier {min(current_tier+1, 3)}")
    typewriter(f"{'='*50}\n")
    time.sleep(0.5)

def _check_mastery_bonus_node(player):
    """If any mastery is high enough, offer a bonus knowledge trial node."""
    for q_type, val in player.mastery.items():
        if val >= 15:
            return True
    return False

def generate_next_nodes(current_tier, player, nodes_cleared=0):
    node_count = random.choice([2, 3])
    nodes = []

    for _ in range(node_count):
        # Boss only available from tier 3 onward AND after node 10
        # Never appears before node 10 regardless of tier
        boss_eligible = current_tier >= 3 and nodes_cleared >= 10

        if boss_eligible:
            types = ["battle", "elite", "shop", "maze", "rest", "boss"]
            weights = [35, 15, 15, 15, 10, 10]
        else:
            types = ["battle", "elite", "shop", "maze", "rest"]
            weights = [50, 10, 15, 15, 10]

        node_type = random.choices(types, weights=weights, k=1)[0]
        tier = current_tier
        if node_type in ("elite", "boss"):
            tier += 1

        if _check_mastery_bonus_node(player) and random.random() < 0.08:
            nodes.append(PathNode("trial", tier=current_tier))

        nodes.append(PathNode(node_type, tier=tier))

    return nodes

def choose_next_path(current_tier, player, nodes_cleared=0):
    nodes = generate_next_nodes(current_tier, player)

    typewriter("\nChoose your next destination:")
    typewriter("(Type 'c' to view your character sheet)")
    time.sleep(0.5)

    for i, node in enumerate(nodes, 1):
        typewriter(f"{i}. {node.describe()} ({node.node_type.upper()})")
        time.sleep(0.3)

    while True:
        choice = input("> ").strip().lower()

        if choice == "c":
            view_character(player)          # need to pass player in
            # reprint the options
            for i, node in enumerate(nodes, 1):
                typewriter(f"{i}. {node.describe()} ({node.node_type.upper()})")
            continue

        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(nodes):
                return nodes[choice - 1]

        typewriter("Invalid choice. Select a valid number or 'c' for character.")

class SessionStats:
    """Tracks learning statistics for the current run."""
    def __init__(self):
        self.correct = 0
        self.wrong = 0
        self.by_type = {t: {"correct": 0, "wrong": 0} for t in ["TF", "MC", "AR", "ID", "OD"]}

    def record(self, q_type, was_correct):
        if was_correct:
            self.correct += 1
            self.by_type.setdefault(q_type, {"correct": 0, "wrong": 0})["correct"] += 1
        else:
            self.wrong += 1
            self.by_type.setdefault(q_type, {"correct": 0, "wrong": 0})["wrong"] += 1

    def accuracy(self):
        total = self.correct + self.wrong
        return int((self.correct / total) * 100) if total > 0 else 0

    def print_summary(self):
        from ui import typewriter
        total = self.correct + self.wrong
        typewriter(f"\n--- Learning Summary ---")
        typewriter(f"  Questions answered: {total}")
        typewriter(f"  Correct: {self.correct} | Wrong: {self.wrong}")
        typewriter(f"  Accuracy: {self.accuracy()}%")
        typewriter(f"\n  By category:")
        for q_type, counts in self.by_type.items():
            t = counts["correct"] + counts["wrong"]
            if t == 0:
                continue
            acc = int((counts["correct"] / t) * 100)
            bar = "#" * (acc // 10) + "-" * (10 - acc // 10)
            category = {"TF": "True/False", "MC": "Multi-Choice",
                        "AR": "Arithmetic", "ID": "Identification",
                        "OD": "Ordering"}.get(q_type, q_type)
            typewriter(f"  {category:15} [{bar}] {acc}% ({t} answered)")

def create_character():
    typewriter("\n=== Character Creation ===")

    name = input("Enter your character name: ").strip()

    typewriter("\nChoose a GOL Class:")
    typewriter("1. Berserker (Glass Cannon) - High ATK, Low DEF")
    typewriter("2. Duelist (Speedy Rogue) - High SPD, High CRIT, Low ATK")
    typewriter("3. Sentinel (Average Sustain) - High HP, High DEF, Low SPD")
    typewriter("4. Arcanist (Learning Focus) - High WIS, High Crit)")
    typewriter("5. Gambler (High Risk/Reward) - Variance in all stats, Mismatch CRIT")
    typewriter("6. Custom Build - Distribute your own stat points")

    choice = input("> ").strip()
    # (name, hp, atk, def, spd, wisdom, crit_chance, crit_multiplier)

    if choice == "1":
        player = MainCharacter(name, 30, 15, 5, 10, 5, 0.3, 2.5)
        player.class_name = "Berserker"
        player.class_passive = "bloodlust"
        # On correct answer: gains +1 ATK permanently (up to +10 max)
        return player

    elif choice == "2":
        player = MainCharacter(name, 50, 5, 10, 10, 5, 0.8, 2.5)
        player.class_name = "Duelist"
        player.class_passive = "momentum"
        # Each consecutive correct answer increases crit chance by 2%
        return player

    elif choice == "3":
        player = MainCharacter(name, 80, 5, 15, 5, 5, 0.3, 1.5)
        player.class_name = "Sentinel"
        player.class_passive = "fortress"
        # Wrong answers don't trigger enemy punishment attacks
        return player

    elif choice == "4":
        player = MainCharacter(name, 40, 5, 5, 7, 30, 1, 3.0)
        player.class_name = "Arcanist"
        player.class_passive = "insight"
        # Always shows question category and mastery before asking
        # (already happens, but Arcanist also sees the difficulty rating)
        return player
    
    elif choice == "5":
        player = MainCharacter(name, random.randint(30, 100), random.randint(5, 40), random.randint(2, 15), random.randint(3, 20), random.randint(5, 25), random.randint(0, 1), random.uniform(0.5, 5)) #gambler
        player.class_name = "Gambler"
        player.class_passive = "luck"
        # Each stat is randomly determined at the start of the run
        return player

    elif choice == "6":
        return custom_build(name) # custom build
    
    elif choice == "143":
        typewriter("Welcome home, Rynier. Let's get you ready for testing.")
        return MainCharacter(name, 999, 999, 999, 999, 999, 1, 10) # testing god mode

    else:
        typewriter("Invalid choice. Defaulting to Berserker.")
        return MainCharacter(name, 30, 25, 2, 10, 5, 0.3, 2.5) # default berserker

def custom_build(name):
    typewriter("\nYou have 100 stat points to distribute.")
    points = 100

    def allocate(stat_name):
        nonlocal points
        while True:
            value = input(f"{stat_name} (Remaining points: {points}): ")
            try:
                value = int(value)
                if 0 <= value <= points:
                    points -= value
                    return value
            except:
                pass
            typewriter("Invalid amount.")

    max_hp = 20 + allocate("HP")
    atk = 5 + allocate("ATK")
    defense = 5 + allocate("DEF")
    spd = 5 + allocate("SPD")
    wisdom = 5 + allocate("WISDOM")
    crit_chance = 0 + allocate("CRIT_CHANCE") / 100
    crit_multiplier = 0 + allocate("CRIT_MULTIPLIER") / 10

    return MainCharacter(name, max_hp, atk, defense, spd, wisdom, crit_chance, crit_multiplier)

def view_character(player):
    """Display full character stats and progression."""
    clear_screen()
    typewriter(f"\n{'='*40}")
    typewriter(f"  {player.name}  |  Level {player.lvl}")
    typewriter(f"{'='*40}")
    typewriter(f"HP:      {hp_bar(player.hp, player.max_hp)}")
    typewriter(f"Focus:   {hp_bar(player.focus, player.max_focus, length=10)}")
    typewriter(f"Shield:  {player.shield}")
    typewriter(f"Gold:    {player.gold}")
    typewriter(f"EXP:     {player.exp}/{player.xp_to_next}")
    typewriter(f"\nStats:")
    typewriter(f"  ATK: {player.atk}  DEF: {player.defense}")
    typewriter(f"  SPD: {player.spd}  WIS: {player.wisdom}")
    typewriter(f"  CRIT: {int(player.crit_chance*100)}%  x{player.crit_multiplier}")
    typewriter(f"\nMastery:")
    for q_type, val in player.mastery.items():
        next_ms = ((val // 5) + 1) * 5
        category = {"TF": "True/False", "MC": "Multi-Choice",
                    "AR": "Arithmetic", "ID": "Identification"}.get(q_type, q_type)
        typewriter(f"  {category}: {val} (next skill at {next_ms})")
    typewriter(f"\nSkills:")
    if hasattr(player, "skills") and player.skills:
        for skill in player.skills:
            status = "UNLOCKED" if skill.unlocked else f"locked ({skill.tree} mastery 5)"
            typewriter(f"  {skill.name} [{skill.tree}] — {status}")
    else:
        typewriter("  No skills loaded.")
    typewriter(f"\nInventory ({len(player.inventory)} items):")
    if player.inventory:
        for item in player.inventory:
            desc = getattr(item, "description", "")
            typewriter(f"  {item.name} — {desc}")
    else:
        typewriter("  Empty.")
    typewriter(f"\nStreak: {player.streak} (Longest: {player.longest_streak})")
    typewriter(f"Action Points: {player.max_action_points}/turn")
    time.sleep(0.5)
    input("\nPress Enter to continue...")


def start_combat(player, learning_engine, tier, nodes_cleared=1):
    """Full combat loop handling turns, status effects, escape, and victory."""

    enemy = generate_random_enemy(tier=tier)
    enemy = scale_enemy(enemy, nodes_cleared, tier)
    typewriter(f"\nA wild {enemy.name} appears!")
    time.sleep(1)

    hp_before = player.hp

    while True:

        display_entity_stats(player)
        display_entity_stats(enemy)

        result = player_turn(player, enemy, learning_engine)

        if result == ESCAPED:
            typewriter("You successfully escaped the battle!")
            time.sleep(1)
            return ESCAPED, False          # tuple

        if enemy.hp <= 0:
            typewriter(f"{enemy.name} defeated!")
            time.sleep(1)
            typewriter(f"\n--- Battle Summary ---")
            typewriter(f"HP remaining: {player.hp}/{player.max_hp}")
            typewriter(f"Streak: {player.streak} | Focus: {player.focus}/{player.max_focus}")
            no_damage = (player.hp >= hp_before)
            if no_damage:
                typewriter("Flawless victory! No damage taken.")
            time.sleep(0.5)
            return WIN, no_damage          # tuple

        if player.hp <= 0:
            typewriter("You were defeated...")
            time.sleep(1)
            return DEATH, False            # tuple

        process_status_effects(player)

        if enemy.hp <= 0:
            typewriter(f"{enemy.name} defeated!")
            time.sleep(1)
            xp_gain = 20 + (tier * 10)
            player.gain_xp(xp_gain)
            typewriter(f"Gained {xp_gain} XP!")
            return WIN, False              # tuple

        if player.hp <= 0:
            typewriter("You were defeated...")
            time.sleep(1)
            return DEATH, False            # tuple

        enemy_turn(enemy, player)
        process_status_effects(enemy)

        if player.hp <= 0:
            typewriter("You were defeated...")
            time.sleep(1)
            return DEATH, False            # tuple

        if enemy.hp <= 0:
            typewriter(f"{enemy.name} defeated!")
            time.sleep(1)
            xp_gain = 20 + (tier * 10)
            player.gain_xp(xp_gain)
            typewriter(f"Gained {xp_gain} XP!")
            return WIN, False
        
def random_event(player):
    """Small random events that fire between nodes ~20% of the time."""
    roll = random.random()

    if roll < 0.07:
        typewriter("\nA wounded traveler shares their supplies with you.")
        heal = int(player.max_hp * 0.1)
        player.heal(heal)
        typewriter(f"Recovered {heal} HP.")

    elif roll < 0.13:
        typewriter("\nYou find a small coin pouch on the ground.")
        bonus = random.randint(5, 20)
        player.gold += bonus
        typewriter(f"Found {bonus} gold!")

    elif roll < 0.17:
        typewriter("\nA strange fog rolls in. You feel disoriented.")
        player.streak = max(0, player.streak - 2)
        typewriter("Streak reduced by 2.")
        time.sleep(1)

    elif roll < 0.20:
        typewriter("\nYou stumble upon an abandoned satchel.")
        from learningEngine import random_item_pool
        reward = random_item_pool(num_rewards=1)
        if reward:
            player.inventory.extend(reward)
            for item in reward:
                typewriter(f"Found: {item.name}!")
        time.sleep(1)

    # rolls 0.20-1.0 → nothing happens, which is intentional

def main_game():
    """Runs a full RPG loop until player dies or escapes."""

    unlocked_achievements = load_achievements()
    run_context = {
        "battles_won": 0,
        "nodes_cleared": 0,
        "beat_boss": False,
        "no_damage_battle": False,
        "visited_shop_broke": False,
    }

    current_tier = 1
    battles_won = 0
    nodes_cleared = 0
    run_log = []
    player = None

    if save_exists(SAVE_PATH):
        typewriter("A saved run was found. Continue? (y/n)")
        if input("> ").strip().lower() == "y":
            pdata, rdata = load_game(SAVE_PATH)
            if pdata and rdata:
                player = restore_player(pdata)
                current_tier = rdata["tier"]
                battles_won = rdata["battles_won"]
                nodes_cleared = rdata["nodes_cleared"]
                run_context["battles_won"] = battles_won
                run_context["nodes_cleared"] = nodes_cleared
                typewriter(f"Welcome back, {player.name}!")
                time.sleep(1)

    if player is None:
        player = create_character()
        player.gold = 50
        player.exp = 0
        player.streak = 0
        player.skills = create_skill_pool()
        engine.wrong_answers.clear()
        choose_run_modifier(player)
        show_opening(player.name, getattr(player, "class_name", "Adventurer"))

    typewriter("=" * 60)
    typewriter("\nWelcome to the Game-on Learning demo!")
    typewriter("Use knowledge and strategy to defeat enemies and gain rewards.")
    typewriter("Gold earned can be used in the shop to buy aid.")
    typewriter("=" * 60)
    time.sleep(2)
    typewriter("Loading Combat...")
    time.sleep(1)
    clear_screen()

    typewriter("=== ROGUELITE RUN STARTED ===")
    typewriter("\nYour goal: Clear 3 tiers and defeat the boss.")
    typewriter(f"Current Tier: {current_tier}/3")
    time.sleep(1)

    run_active = True
    while run_active and player.is_alive():

        nodes_cleared += 1

        # -------------------------
        # Determine next node
        # -------------------------
        # Guaranteed boss at node 15
        if nodes_cleared == 15:
            typewriter("\n" + "="*50)
            typewriter("  A darkness unlike anything before stirs ahead.")
            typewriter("  You sense this is where it all ends.")
            typewriter("="*50)
            time.sleep(2)
            next_node = PathNode("boss", tier=current_tier + 1)
        elif nodes_cleared == 1:
            next_node = PathNode("battle", tier=current_tier)
        elif nodes_cleared == 2:
            next_node = PathNode(random.choice(["battle", "rest"]), tier=current_tier)
        else:
            next_node = choose_next_path(current_tier, player)

        draw_run_map(nodes_cleared, current_tier, run_log, next_node.node_type)
        show_node_flavor(next_node.node_type)
        typewriter(f"You proceed toward: {next_node.node_type.upper()}")
        time.sleep(0.5)

        # -------------------------
        # Handle Node Types
        # -------------------------
        # Battle / Elite
        if next_node.node_type == "battle":
            result, no_damage = start_combat(player, engine, next_node.tier, nodes_cleared)
            if no_damage and result == WIN:
                run_context["no_damage_battle"] = True

            if result == DEATH:
                show_death_narrative(player.name, battles_won, player.longest_streak)
                typewriter("\n=== GAME OVER ===")
                game_over_screen()
                return

            elif result == ESCAPED:
                typewriter("You escaped the battle — no rewards gained!")
                lost_gold = min(player.gold, random.randint(5, 15))
                player.gold -= lost_gold
                typewriter(f"Running costs you {lost_gold} gold!")
                time.sleep(1)

                run_log.append(f"Node {nodes_cleared}: Fled from battle (lost gold)")
                continue

            else:
                battles_won += 1
                xp_reward = 20 + (current_tier * 5)
                gold_reward = 15 + (current_tier * 5)
                player.gain_xp(xp_reward)
                gold_earned = player.apply_gold(gold_reward)
                typewriter(f"You gained {xp_reward} XP and {gold_earned} Gold!")

                # Item drop
                drop = combat_item_drop(tier=current_tier)
                if drop:
                    player.inventory.append(drop)
                    typewriter(f"Item dropped: {drop.name}!")
                    typewriter(f"  ({getattr(drop, 'description', '')})")

                run_context["battles_won"] = battles_won
                run_context["nodes_cleared"] = nodes_cleared
                newly = check_achievements(player, run_context, unlocked_achievements)
                for name in newly:
                    typewriter(f"\n*** ACHIEVEMENT UNLOCKED: {name} ***")
                    time.sleep(0.5)
                save_achievements(unlocked_achievements)

                run_log.append(f"Node {nodes_cleared}: Defeated enemy at Tier {current_tier}")
                time.sleep(1)

        elif next_node.node_type == "elite":
            from enemyPool import generate_random_enemy
            from combatSystem import elite_combat
            elite_enemy = generate_random_enemy(tier=next_node.tier + 1, elite_chance=1.0)
            result = elite_combat(player, elite_enemy, engine)

            if result == DEATH:
                typewriter("\n=== GAME OVER ===")
                game_over_screen()
                return

            elif result == ESCAPED:
                typewriter("You escaped the elite — cowardly, but alive.")
                lost_gold = min(player.gold, random.randint(10, 25))
                player.gold -= lost_gold
                typewriter(f"You lost {lost_gold} gold fleeing!")
                time.sleep(1)
                continue

            else:
                battles_won += 1
                xp_reward = 50 + (current_tier * 10)
                gold_reward = 40 + (current_tier * 10)
                player.max_hp += 5
                typewriter("Permanent +5 Max HP for defeating an elite!")
                player.gain_xp(xp_reward)
                gold_earned = player.apply_gold(gold_reward)
                typewriter(f"You gained {xp_reward} XP and {gold_earned} Gold!")

                # Item drop
                drop = combat_item_drop(tier=current_tier)
                if drop:
                    player.inventory.append(drop)
                    typewriter(f"Item dropped: {drop.name}!")
                    typewriter(f"  ({getattr(drop, 'description', '')})")

                run_context["battles_won"] = battles_won
                run_context["nodes_cleared"] = nodes_cleared
                newly = check_achievements(player, run_context, unlocked_achievements)
                for name in newly:
                    typewriter(f"\n*** ACHIEVEMENT UNLOCKED: {name} ***")
                    time.sleep(0.5)
                save_achievements(unlocked_achievements)

                run_log.append(f"Node {nodes_cleared}: Defeated ELITE at Tier {current_tier}")
                time.sleep(1)

        elif next_node.node_type == "boss":
            from enemyPool import generate_random_enemy
            from combatSystem import boss_combat
            # Boss is always max tier, always elite
            boss_enemy = generate_random_enemy(tier=3, elite_chance=1.0)
            boss_enemy.hp = int(boss_enemy.hp * 2)       # double HP for boss feel
            boss_enemy.max_hp = boss_enemy.hp
            boss_enemy.atk = int(boss_enemy.atk * 1.5)   # stronger attacks
            result = boss_combat(player, boss_enemy, engine)

            if result == DEATH:
                typewriter("\n=== YOU WERE DEFEATED BY THE BOSS ===")
                game_over_screen()
                return
            else:
                battles_won += 1
                show_victory_narrative(player.name, battles_won, player.longest_streak)
                typewriter("\n*** BOSS DEFEATED — YOU WIN THE RUN! ***")
                player.gain_xp(200 + current_tier * 20)
                player.apply_gold(100 + current_tier * 20)
                time.sleep(2)

                run_log.append(f"Node {nodes_cleared}: Defeated the BOSS — run complete!")

                run_context["beat_boss"] = True

                break  # end the run after boss victory
        # Shop
        elif next_node.node_type == "shop":
            if player.gold == 0:
                run_context["visited_shop_broke"] = True
            shop(player)

            run_log.append(f"Node {nodes_cleared}: Visited shop (Gold: {player.gold})")

        # Maze / Quiz Trial
        elif next_node.node_type == "maze":
            quiz_trial(player, engine)

            run_log.append(f"Node {nodes_cleared}: Completed maze trial")

        # Rest
        elif next_node.node_type == "rest":
            heal_amount = int(player.max_hp * 0.3)
            player.hp = min(player.max_hp, player.hp + heal_amount)
            typewriter(f"You rest and recover {heal_amount} HP.")
            time.sleep(1)

            run_log.append(f"Node {nodes_cleared}: Rested (+HP)")

        elif next_node.node_type == "trial":
            typewriter("\nA Knowledge Trial appears — a chance to prove your mastery.")
            quiz_trial(player, engine)
            run_log.append(f"Node {nodes_cleared}: Completed Knowledge Trial")

        save_game(player, {
            "tier": current_tier,
            "battles_won": battles_won,
            "nodes_cleared": nodes_cleared,
        }, SAVE_PATH)

        # -------------------------
        # Between-node random event
        # -------------------------
        random_event(player)

        # -------------------------
        # Difficulty scaling & passive recovery
        # -------------------------
        if nodes_cleared % 5 == 0:
            current_tier = min(current_tier + 1, 3)
            typewriter(f"\n{'='*40}")
            typewriter(f"  TIER {current_tier} REACHED")
            typewriter(f"  Enemies grow stronger from here.")
            typewriter(f"{'='*40}")
            show_tier_narrative(current_tier)
            time.sleep(1.5)

        player.hp = min(player.max_hp, player.hp + int(player.max_hp * 0.05))
        typewriter(f"Current HP: {player.hp}/{player.max_hp}")
        typewriter(f"Gold: {player.gold} | EXP: {player.exp}")
        time.sleep(0.5)

    # -------------------------
    # Run Summary
    # -------------------------
    clear_screen()
    typewriter("\n=== RUN ENDED ===")
    typewriter(f"Battles Won: {battles_won}")
    typewriter(f"Nodes Cleared: {nodes_cleared}")
    typewriter(f"Final Gold: {player.gold}")
    typewriter(f"Highest Streak: {player.longest_streak}")
    session_stats = SessionStats()
    session_stats.print_summary()
    engine.print_review()

    engine.print_review()

    if run_log:
        time.sleep(1)
        typewriter("\n--- Run Journal ---")
        for entry in run_log:
            typewriter(f"  {entry}")
            time.sleep(0.05)

    try:
        with open(LAST_RUN_PATH, "w") as f:
            f.write(f"Battles Won: {battles_won}\n")
            f.write(f"Nodes Cleared: {nodes_cleared}\n")
            f.write(f"Highest Streak: {player.longest_streak}\n")
            f.write(f"Final Gold: {player.gold}\n")
            f.write(f"Final Level: {player.lvl}\n")
    except Exception:
        pass
            
    delete_save(SAVE_PATH)

    time.sleep(5)
    typewriter("\nReturning to main menu...")
    time.sleep(1)

def restore_player(pdata):
    """Reconstruct a MainCharacter from saved player data."""
    from items import (HealingPotion, MegaHealingPotion, AttackBoost,
                       DefenseBoost, SpeedBoost, PoisonBomb, FreezeScroll,
                       WeaknessCurse, HintPotion, DoubleGoldCharm, RevivalStone)

    name_to_class = {
        "Healing Potion": HealingPotion,
        "Mega Healing Potion": MegaHealingPotion,
        "Attack Boost": AttackBoost,
        "Defense Boost": DefenseBoost,
        "Speed Boost": SpeedBoost,
        "Poison Bomb": PoisonBomb,
        "Freeze Scroll": FreezeScroll,
        "Weakness Curse": WeaknessCurse,
        "Hint Potion": HintPotion,
        "Double Gold Charm": DoubleGoldCharm,
        "Revival Stone": RevivalStone,
    }

    player = MainCharacter(
        pdata["name"],
        pdata["max_hp"],
        pdata["atk"],
        pdata["defense"],
        pdata["spd"],
        pdata["wisdom"],
        pdata["crit_chance"],
        pdata["crit_multiplier"],
    )
    player.hp = pdata["hp"]
    player.lvl = pdata["lvl"]
    player.exp = pdata["exp"]
    player.xp_to_next = pdata["xp_to_next"]
    player.gold = pdata["gold"]
    player.streak = pdata["streak"]
    player.longest_streak = pdata["longest_streak"]
    player.focus = pdata["focus"]
    player.max_focus = pdata["max_focus"]
    player.mastery = pdata["mastery"]
    player.max_action_points = pdata["action_points"]
    player.inventory = [
        name_to_class[i["name"]]()
        for i in pdata["inventory"]
        if i["name"] in name_to_class
    ]
    player.class_name = pdata.get("class_name", "")
    player.class_passive = pdata.get("class_passive", "")
    player.run_modifier = pdata.get("run_modifier", "")
    player.skills = create_skill_pool()
    return player

RUN_MODIFIERS = [
    {
        "name": "Scholar's Burden",
        "description": "All questions are harder, but correct answers deal double damage.",
        "apply": lambda p: setattr(p, "run_modifier", "scholar")
    },
    {
        "name": "Cursed Knowledge",
        "description": "Wrong answers cost 10 HP in addition to streak penalty.",
        "apply": lambda p: setattr(p, "run_modifier", "cursed")
    },
    {
        "name": "Iron Will",
        "description": "You cannot escape any battle. Rewards are 50% higher.",
        "apply": lambda p: setattr(p, "run_modifier", "ironwill")
    },
    {
        "name": "Lucky Start",
        "description": "Begin with a random rare item and 20 extra gold.",
        "apply": lambda p: _apply_lucky_start(p)
    },
    {
        "name": "No modifier",
        "description": "Standard run.",
        "apply": lambda p: None
    },
]

def _apply_lucky_start(player):
    from learningEngine import random_item_pool
    bonus = random_item_pool(num_rewards=1)
    player.inventory.extend(bonus)
    player.gold += 20
    player.run_modifier = "lucky"

def choose_run_modifier(player):
    typewriter("\nBefore you begin — choose a run modifier:")
    time.sleep(0.5)
    for i, mod in enumerate(RUN_MODIFIERS, 1):
        typewriter(f"{i}. {mod['name']}")
        typewriter(f"   {mod['description']}")
    while True:
        choice = input("> ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(RUN_MODIFIERS):
            selected = RUN_MODIFIERS[int(choice) - 1]
            selected["apply"](player)
            typewriter(f"\nModifier selected: {selected['name']}")
            time.sleep(1)
            return
        typewriter("Invalid choice.")

if __name__ == "__main__":
    while True:
        action = title_screen(LAST_RUN_PATH)

        if action == "start":
            main_game()
            restart = game_over_screen()
            if not restart:
                break

        elif action == "practice":
            from learningEngine import practice_mode
            practice_mode(engine)

        elif action == "achievements":
            unlocked = load_achievements()
            print_achievements(unlocked)
            input("\nPress Enter to return to menu...")

        elif action == "reconfigure":
            from config import setup_wizard, CONFIG_FILE
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
            CONFIG = setup_wizard()
            NOTE_PATHS = get_notes_paths(CONFIG)
            SAVE_PATH = get_save_path(CONFIG)
            LAST_RUN_PATH = get_last_run_path(CONFIG)
            engine.questions.clear()
            engine.wrong_answers.clear()
            for qtype, path in NOTE_PATHS.items():
                validate_notes(path, qtype)
                engine.load_notes(path, qtype=qtype,
                                  difficulty=NOTE_DIFFICULTIES.get(qtype, 1))
            typewriter("Notes reloaded. Returning to menu...")
            time.sleep(1)

        elif action == "exit":
            break

