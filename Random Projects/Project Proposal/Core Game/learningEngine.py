import random, json
import time
from Spawns import MainCharacter, Enemy
from items import HintPotion
from ui import typewriter

class LearningEngine:
    def __init__(self):
        self.questions = []

    def load_notes(self, filepath, qtype="TF"):
        """
        Load questions from a notes file.
        - TF: True/False format, each line "Statement = True/False"
        - MC: Multiple Choice, JSON format per line: {"question": "...", "options": ["A","B"], "answer": "B"}
        - AR: Arithmetic or ID, "Question = Answer"
        """
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                lines = file.readlines()

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if qtype == "TF" or qtype == "AR":
                    if "=" not in line:
                        continue
                    statement, answer = line.split("=")
                    self.questions.append({
                        "type": qtype,
                        "question": statement.strip(),
                        "answer": answer.strip()
                    })

                elif qtype == "MC":
                    # Expecting JSON string per line
                    try:
                        data = json.loads(line)
                        if "question" in data and "options" in data and "answer" in data:
                            data["type"] = "MC"
                            self.questions.append(data)
                    except json.JSONDecodeError:
                        continue

        except FileNotFoundError:
            typewriter(f"Notes file not found: {filepath}")

    def get_random_question(self):
        if not self.questions:
            return None
        return random.choice(self.questions)
    
def quiz_trial(player, engine):
    """
    Dynamic choice-driven trial puzzle with visual map and delays:
    - Player chooses paths (2-3 options each move)
    - Each move requires answering a question
    - Correct answer: base + optional rewards
    - Incorrect: streak penalty + other effects
    - Random chance of chest or trap
    - Visual ASCII map updates with each move
    """

    typewriter("\n=== Trial Exploration Challenge ===")
    time.sleep(1)
    typewriter("You enter a mysterious labyrinth. Choose your paths wisely!")
    time.sleep(1)

    base_rewards = {"exp": 10, "gold": 5}
    accumulated_rewards = {"exp": 0, "gold": 0, "items": []}
    moves = 0
    in_maze = True
    maze_map = []  # keeps track of paths taken for visual map

    while in_maze:
        moves += 1

        # Visual Map
        typewriter("\nMaze Map: " + " > ".join(maze_map) if maze_map else "Trial Map: Start")
        time.sleep(0.5)

        # Present 2-3 path options
        num_paths = random.choice([2, 3])
        paths = [chr(65 + i) for i in range(num_paths)]  # A, B, C
        typewriter(f"\nYou are at a crossroads! Choose your path: {', '.join(paths)}")
        choice = input("> ").strip().upper()

        if choice not in paths:
            typewriter("Invalid path! You hesitate and lose a turn.")
            time.sleep(1)
            continue

        # Update visual map
        maze_map.append(choice)
        typewriter(f"You chose path {choice}...")
        time.sleep(1)

        # Ask a random question for this move
        q_data = engine.get_random_question()
        if q_data is None:
            typewriter("No questions available! Skipping this move...")
            time.sleep(1)
            continue

        typewriter(f"\nQuestion: {q_data['question']}")
        player_answer = input("> ").strip().lower()
        correct_answer = q_data["answer"].strip().lower()
        time.sleep(0.5)

        # Reward / Punishment Logic
        if player_answer == correct_answer:
            typewriter("Correct! You proceed safely.")
            time.sleep(0.5)

            # Base reward + optional bonus
            accumulated_rewards["exp"] += base_rewards["exp"]
            accumulated_rewards["gold"] += base_rewards["gold"]

            # Optional bonus rewards
            bonus_options = ["gold", "exp", "item", "none"]
            bonus_choices = random.sample(bonus_options, random.choice([1, 2]))
            for bonus in bonus_choices:
                if bonus == "gold":
                    bonus_amount = random.randint(3, 10)
                    accumulated_rewards["gold"] += bonus_amount
                    typewriter(f"You found +{bonus_amount} gold!")
                    time.sleep(0.5)
                elif bonus == "exp":
                    bonus_amount = random.randint(5, 15)
                    accumulated_rewards["exp"] += bonus_amount
                    typewriter(f"You gained +{bonus_amount} experience!")
                    time.sleep(0.5)
                elif bonus == "item":
                    item = "Small Healing Potion"
                    accumulated_rewards["items"].append(item)
                    typewriter(f"You discovered an item: {item}!")
                    time.sleep(0.5)

        else:
            typewriter(f"Incorrect! The correct answer was: {q_data['answer']}")
            time.sleep(0.5)
            # Punish streak and chance for further penalties
            player.streak = max(0, player.streak - 1)
            typewriter("Your streak decreased!")
            time.sleep(0.5)
            penalty_chance = random.random()
            if penalty_chance < 0.3:
                lost_gold = min(accumulated_rewards["gold"], random.randint(2, 8))
                accumulated_rewards["gold"] -= lost_gold
                typewriter(f"You triggered a trap and lost {lost_gold} gold!")
                time.sleep(1)

        # Random chance: chest or trap
        special_event = random.random()
        if special_event < 0.2:
            chest_gold = random.randint(10, 25)
            chest_exp = random.randint(10, 25)
            accumulated_rewards["gold"] += chest_gold
            accumulated_rewards["exp"] += chest_exp
            typewriter(f"\nYou found a chest! +{chest_gold} gold, +{chest_exp} exp!")
            time.sleep(1)
            if random.random() < 0.2:
                player.max_hp += 5
                typewriter("Permanent HP boost! +5 Max HP")
                time.sleep(1)
        elif special_event < 0.25:
            typewriter("\nYou stumble into a trap! Answer correctly to escape.")
            time.sleep(0.5)
            trap_q = engine.get_random_question()
            trap_answer = input(f"{trap_q['question']} > ").strip().lower()
            if trap_answer != trap_q["answer"].strip().lower():
                typewriter("Wrong! You are ejected from the trial!")
                in_maze = False
                break
            else:
                typewriter("You escaped the trap safely!")
                time.sleep(0.5)

        # Chance to end trial early
        if moves >= 5 and random.random() < 0.2:
            typewriter("\nYou sense an exit nearby.")
            time.sleep(1)
            in_maze = False

        # Ask player if they want to continue
        if in_maze:
            cont_choice = input("Do you want to continue deeper into the trial? (y/n) > ").strip().lower()
            if cont_choice != "y":
                typewriter("You decide to exit the trial safely.")
                time.sleep(1)
                in_maze = False

    # Post-trial high-risk trial
    if moves >= 5:
        typewriter("\nYou found the final treasure chamber!")
        choice = input("Attempt High-Risk Trial for double rewards and permanent buffs? (y/n) > ").strip().lower()
        if choice == "y":
            typewriter("\nHigh-Risk Trial: Answer 3 questions correctly to double rewards.")
            time.sleep(1)
            trial_correct = 0
            for i in range(3):
                trial_q = engine.get_random_question()
                ans = input(f"{trial_q['question']} > ").strip().lower()
                if ans == trial_q["answer"].strip().lower():
                    trial_correct += 1
                    typewriter("Correct!")
                else:
                    typewriter(f"Wrong! The correct answer was: {trial_q['answer']}")
                time.sleep(0.5)

            if trial_correct == 3:
                typewriter("Perfect! Rewards doubled and permanent buffs granted!")
                accumulated_rewards["gold"] *= 2
                accumulated_rewards["exp"] *= 2
                player.max_hp += 10
                typewriter("Permanent +10 HP gained!")
                time.sleep(1)
            else:
                typewriter("You failed the trial. Rewards halved and streak penalized!")
                accumulated_rewards["gold"] //= 2
                accumulated_rewards["exp"] //= 2
                player.streak = max(0, player.streak - 2)
                time.sleep(1)

    # Apply accumulated rewards
    player.gold += accumulated_rewards["gold"]
    player.exp += accumulated_rewards["exp"]
    for item in accumulated_rewards["items"]:
        player.inventory.append(item)

    typewriter("\n=== Trial Exploration Complete ===")
    typewriter(f"Total Gold: {accumulated_rewards['gold']}, Total Exp: {accumulated_rewards['exp']}")
    if accumulated_rewards["items"]:
        typewriter(f"Items gained: {', '.join(accumulated_rewards['items'])}")
    typewriter(f"Final Streak: {player.streak}")
    time.sleep(6)