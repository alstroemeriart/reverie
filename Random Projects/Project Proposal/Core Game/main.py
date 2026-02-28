# Main game loop and character creation
import time, os, random
from Spawns import MainCharacter, Enemy, Spawn
from items import HealingPotion, AttackBoost, HintPotion
from combatSystem import (
    player_turn,
    enemy_turn,
    process_status_effects,
    display_entity_stats
)
from ui import title_screen, game_over_screen, typewriter, clear_screen
from combatCalc import calculate_damage, check_dodge, check_critical
from enemyPool import generate_random_enemy
from learningEngine import LearningEngine, quiz_trial
from shop import shop

engine = LearningEngine()

engine = LearningEngine()
engine.load_notes(r"C:\Users\Larry Relativo\OneDrive\Desktop\School\Random Projects\Project Proposal\Core Game\notes\TorF.txt", qtype="TF")
engine.load_notes(r"C:\Users\Larry Relativo\OneDrive\Desktop\School\Random Projects\Project Proposal\Core Game\notes\MCQ.txt", qtype="MC")
engine.load_notes(r"C:\Users\Larry Relativo\OneDrive\Desktop\School\Random Projects\Project Proposal\Core Game\notes\Math.txt", qtype="AR")
engine.load_notes(r"C:\Users\Larry Relativo\OneDrive\Desktop\School\Random Projects\Project Proposal\Core Game\notes\Identify", qtype="ID")

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
            "battle": "A hostile presence lurks ahead...",
            "elite": "A powerful elite enemy blocks your path.",
            "shop": "A wandering merchant appears.",
            "maze": "A mysterious maze entrance glows faintly.",
            "rest": "A quiet sanctuary for recovery."
        }
        return descriptions.get(self.node_type, "An unknown path.")

def generate_next_nodes(current_tier):
    node_count = random.choice([2, 3])

    nodes = []

    for _ in range(node_count):
        node_type = random.choices(
            ["battle", "elite", "shop", "maze", "rest"],
            weights=[50, 10, 15, 15, 10],
            k=1
        )[0]

        tier = current_tier

        if node_type == "elite":
            tier += 1

        nodes.append(PathNode(node_type, tier=tier))

    return nodes

def choose_next_path(current_tier):
    nodes = generate_next_nodes(current_tier)

    typewriter("\nChoose your next destination:")
    time.sleep(0.5)

    for i, node in enumerate(nodes, 1):
        typewriter(f"{i}. {node.describe()} ({node.node_type.upper()})")
        time.sleep(0.3)

    while True:
        choice = input("> ").strip()
        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(nodes):
                return nodes[choice - 1]

        typewriter("Invalid choice. Select a valid number.")

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
        return MainCharacter(name, 30, 15, 5, 10, 5, 0.3, 2.5) #berserker

    elif choice == "2":
        return MainCharacter(name, 50, 5, 10, 10, 5, 0.8, 2.5) #duelist

    elif choice == "3":
        return MainCharacter(name, 80, 5, 15, 5, 5, 0.3, 1.5) #sentinel
    
    elif choice == "4":
        return MainCharacter(name, 40, 5, 5, 7, 30, 1, 3.0) #arcanist
    
    elif choice == "5":
        return MainCharacter(name, random.randint(30, 100), random.randint(5, 40), random.randint(2, 15), random.randint(3, 20), random.randint(5, 25), random.randint(0, 1), random.uniform(0.5, 5)) #gambler

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

def start_combat(player, learning_engine, tier):
    enemy = generate_random_enemy(tier=tier)
    print(f"\nA wild {enemy.name} appears!")
    combat_active = True

    def apply_status(entity, effect):
        effect.on_apply(entity)
        entity.status_effects.append(effect)

    def process_turn_start(entity):
        entity.is_stunned = False  # reset each turn
        for effect in entity.status_effects:
            effect.on_turn_start(entity)


    def process_turn_end(entity):
        expired = []
        for effect in entity.status_effects:
            effect.on_turn_end(entity)
            if effect.is_expired():
                effect.on_expire(entity)
                expired.append(effect)

        for e in expired:
            entity.status_effects.remove(e)

    while combat_active:
        display_entity_stats(player)
        display_entity_stats(enemy)

        # Player turn
        result = player_turn(player, enemy, learning_engine)

        if result == "Escaped":
            return "Escaped"  # escape ends combat

        # Check if enemy defeated
        if enemy.hp <= 0:
            print(f"{enemy.name} defeated!")
            return True  # victory

        # Check if player defeated after player turn (e.g., enemy punishment in choice_ask)
        if player.hp <= 0:
            print("You were defeated...")
            return None  # player dead

        # Enemy turn
        enemy_turn(enemy, player)

        # Check if player defeated after enemy turn
        if player.hp <= 0:
            print("You were defeated...")
            return None  # player dead

def main_game():
    """Runs a full RPG loop until player dies or escapes."""
    player = create_character()
    current_tier = 1
    battles_won = 0
    nodes_cleared = 0

    # Starting gold for shop
    player.gold = 50
    player.exp = 0
    player.streak = 0  

    typewriter("=" * 60)
    typewriter("\nWelcome to the Game-on Learning demo!")
    typewriter("Use knowledge and strategy to defeat enemies and gain rewards.")
    typewriter("Gold earned can be used in the shop to buy items.")
    typewriter("=" * 60)
    time.sleep(6)
    clear_screen()

    time.sleep(2)
    typewriter("=== ROGUELITE RUN STARTED ===")
    time.sleep(1)

    while player.is_alive():

        nodes_cleared += 1

        # =========================================
        # CONTROLLED EARLY GAME STRUCTURE
        # =========================================
        if nodes_cleared == 1:
            # Always start with battle
            next_node = PathNode("battle", tier=current_tier)

        elif nodes_cleared == 2:
            # Only battle or rest
            node_type = random.choice(["battle", "rest"])
            next_node = PathNode(node_type, tier=current_tier)

        else:
            # Fully randomized after node 2
            next_node = choose_next_path(current_tier)

        typewriter(f"\nYou proceed toward: {next_node.node_type.upper()}")
        time.sleep(1)

        # =========================
        # BATTLE NODE
        # =========================
        if next_node.node_type == "battle":

            result = start_combat(player, engine, next_node.tier)

            if result is None:
                break

            if result != "Escaped":
                battles_won += 1

                xp_reward = 20 + (current_tier * 5)
                gold_reward = 15 + (current_tier * 5)

                player.exp += xp_reward
                player.gold += gold_reward

                typewriter(f"You gained {xp_reward} EXP and {gold_reward} Gold!")
                time.sleep(1)

        # =========================
        # ELITE NODE
        # =========================
        elif next_node.node_type == "elite":

            typewriter("This enemy feels dangerous...")
            time.sleep(1)

            result = start_combat(player, engine, next_node.tier + 1)

            if result is None:
                break

            if result != "Escaped":
                xp_reward = 50 + (current_tier * 10)
                gold_reward = 40 + (current_tier * 10)

                player.exp += xp_reward
                player.gold += gold_reward

                player.max_hp += 5

                typewriter("Elite defeated!")
                typewriter(f"+{xp_reward} EXP, +{gold_reward} Gold")
                typewriter("Permanent +5 Max HP!")
                time.sleep(1)

        # =========================
        # SHOP NODE
        # =========================
        elif next_node.node_type == "shop":
            shop(player)

        # =========================
        # MAZE NODE
        # =========================
        elif next_node.node_type == "maze":
            quiz_trial(player, engine)

        # =========================
        # REST NODE
        # =========================
        elif next_node.node_type == "rest":
            heal_amount = int(player.max_hp * 0.3)
            player.hp = min(player.max_hp, player.hp + heal_amount)
            typewriter(f"You rest and recover {heal_amount} HP.")
            time.sleep(1)

        # =========================
        # DIFFICULTY SCALING
        # =========================
        if nodes_cleared % 5 == 0:
            current_tier = min(current_tier + 1, 5)
            typewriter("The world grows more dangerous...")
            time.sleep(1)

        # Small passive recovery after each node
        player.hp = min(player.max_hp, player.hp + int(player.max_hp * 0.05))

        typewriter(f"Current HP: {player.hp}/{player.max_hp}")
        typewriter(f"Gold: {player.gold} | EXP: {player.exp}")
        time.sleep(1)

    # =========================
    # RUN ENDS
    # =========================
    time.sleep(2)

    # Clear for next round
    clear_screen()

    # End summary
    typewriter("\n=== RUN ENDED ===")
    typewriter(f"Battles Won: {battles_won}")
    typewriter(f"Nodes Cleared: {nodes_cleared}")
    typewriter(f"Final Gold: {player.gold}")
    time.sleep(2)
    typewriter("\nBattle concluded. Returning to main menu...")
    time.sleep(2)


if __name__ == "__main__":
    while True:
        start = title_screen()
        if start:
            main_game()  # run combat
            restart = game_over_screen()
            if not restart:
                break
        else:
            break  # exit cleanly