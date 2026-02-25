import time, os, random
from Spawns import MainCharacter, Enemy, Spawn, MainCharacter
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
from learningEngine import LearningEngine

engine = LearningEngine()

engine = LearningEngine()
engine.load_notes("C:\\Users\\Larry Relativo\\OneDrive\\Desktop\\School\\Random Projects\\Project Proposal\\Core Game\\notes\\TorF.txt", qtype="TF")
engine.load_notes("C:\\Users\\Larry Relativo\\OneDrive\\Desktop\\School\\Random Projects\\Project Proposal\\Core Game\\notes\\MCQ.txt", qtype="MC")
engine.load_notes("C:\\Users\\Larry Relativo\\OneDrive\\Desktop\\School\\Random Projects\\Project Proposal\\Core Game\\notes\\Math.txt", qtype="AR")
engine.load_notes("C:\\Users\\Larry Relativo\\OneDrive\\Desktop\\School\\Random Projects\\Project Proposal\\Core Game\\notes\\Identify.txt", qtype="ID")


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
        return MainCharacter(name, 30, 25, 2, 10, 5, 0.3, 2.5) #berserker

    elif choice == "2":
        return MainCharacter(name, 50, 5, 10, 10, 5, 0.8, 2.5) #duelist

    elif choice == "3":
        return MainCharacter(name, 80, 5, 15, 5, 5, 0.3, 1.5) #sentinel
    
    elif choice == "4":
        return MainCharacter(name, 40, 8, 5, 7, 30, 1, 3.0) #arcanist
    
    elif choice == "5":
        return MainCharacter(name, random.randint(30, 100), random.randint(5, 40), random.randint(2, 15), random.randint(3, 20), random.randint(5, 25), random.randint(0, 1), random.uniform(0.5, 5)) #gambler

    elif choice == "6":
        return custom_build(name)

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

    while combat_active:
        display_entity_stats(player)
        display_entity_stats(enemy)

        # Player turn
        combat_active = player_turn(player, enemy, learning_engine)
        if not combat_active:
            return False  # player ran

        if enemy.hp <= 0:
            print(f"{enemy.name} defeated!")
            return True  # victory

        # Enemy turn
        enemy_turn(enemy, player)

        if player.hp <= 0:
            print("You were defeated...")
            return None  # player dead

def main_game():
    """Runs a full battle until someone dies or the player escapes."""
    player = create_character()

    enemy = generate_random_enemy(tier=1)

    typewriter("=" * 60)
    typewriter("\nWelcome to the Game-on Learning demo!")
    typewriter("In this battle, you'll face off against a fearsome enemy.")
    typewriter("But don't worry, with the power of knowledge, you will prevail!")
    time.sleep(1)
    typewriter("Let's get started!")
    time.sleep(1)
    typewriter("\nEntering combat...")
    typewriter("=" * 60)
    time.sleep(2)
    clear_screen()

    combat_active = True

    while combat_active:
        # -----------------------
        # PLAYER TURN
        # -----------------------
        display_entity_stats(player)
        display_entity_stats(enemy)

        battle_continues = player_turn(player, enemy, engine)  # True = continue, False = escape
        process_status_effects(player)
        process_status_effects(enemy)

        if not battle_continues:  # Player escaped
            typewriter("You successfully escaped the battle!")
            combat_active = False
            break

        if not enemy.is_alive():  # Enemy defeated
            typewriter(f"{enemy.name} has been defeated! {player.name} wins!")
            combat_active = False
            xp_reward = 25 + (enemy.max_hp // 5)
            player.exp += xp_reward
            break

        # -----------------------
        # ENEMY TURN
        # -----------------------
        display_entity_stats(player)
        display_entity_stats(enemy)

        if player.is_alive():  # Only attack if player still alive
            enemy_turn(enemy, player)
            process_status_effects(player)
            process_status_effects(enemy)

        if not player.is_alive():  # Player defeated
            typewriter(f"{player.name} has been defeated by {enemy.name}...")
            combat_active = False
            break

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