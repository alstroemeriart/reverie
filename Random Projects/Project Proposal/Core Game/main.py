# main.py
import time, os
from Spawns import MainCharacter, Enemy
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

    if name.upper() == "Rynier143":
        typewriter("⚡ DEBUG MODE ACTIVATED ⚡")

    typewriter("\nChoose a class:")
    typewriter("1. Warrior (High HP, High ATK)")
    typewriter("2. Tank (Very High HP, High DEF)")
    typewriter("3. Rogue (High SPD, Balanced ATK)")
    typewriter("4. Custom Build")

    choice = input("> ").strip()

    if choice == "1":
        return MainCharacter(name, 70, 20, 5, 4)

    elif choice == "2":
        return MainCharacter(name, 90, 7, 10, 3)

    elif choice == "3":
        return MainCharacter(name, 55, 10, 4, 8)

    elif choice == "4":
        return custom_build(name)

    else:
        typewriter("Invalid choice. Defaulting to Warrior.")
        return MainCharacter(name, 70, 12, 5, 4)
    
def custom_build(name):
    typewriter("\nYou have 40 stat points to distribute.")
    points = 40

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

    max_hp = 40 + allocate("HP")
    atk = 5 + allocate("ATK")
    defense = 5 + allocate("DEF")
    spd = 5 + allocate("SPD")

    return MainCharacter(name, max_hp, atk, defense, spd)

def main_game():
    """Runs a full battle until someone dies or the player escapes."""
    player = create_character()

    enemy = generate_random_enemy()

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