import random, json
import time
from Spawns import MainCharacter, Enemy
from aid import AllItems
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
    
def random_item_pool(num_rewards=1):
    """Select a random reward from the aid pool with rarity weighting"""
    rewards = []

    for _ in range(num_rewards):
        drop = random.randint(0, 100)
        rarity = "common"  # default value
        if drop < 30:
            rarity = "common"
        elif drop < 60:
            rarity = "uncommon"
        elif drop < 95:
            rarity = "rare"
        else:
            rarity = "legendary"

        possibilities = [i for i in AllItems if i["rarity"] == rarity]
        if possibilities:
            item_data = random.choice(possibilities)
            rewards.append(item_data["class"]())

    return rewards

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
    typewriter("\nYou enter a mysterious labyrinth. Choose your paths wisely!")
    time.sleep(1)

    base_rewards = {"exp": 10, "gold": 5}
    accumulated_rewards = {"exp": 0, "gold": 0, "aid": []}
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

            # Base reward
            accumulated_rewards["exp"] += base_rewards["exp"]
            accumulated_rewards["gold"] += base_rewards["gold"]

            # Optional bonus rewards
            bonus_options = ["gold", "exp", "aid", "none"]
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
                elif bonus == "aid":
                    aid = random_item_pool(num_rewards=1)
                    accumulated_rewards["aid"].extend(aid)
                    for aid in aid:
                        typewriter(f"You discovered an aid: {aid.name}!")
                        time.sleep(0.5)

        else:
            typewriter(f"Incorrect! The correct answer was: {q_data['answer']}")
            time.sleep(0.5)
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
            if random.random() < 0.2:  # 20% chance for permabuff
                from statusEffects import DoubleGold
                player.status_effects.append(DoubleGold(duration=5))
                typewriter("Lucky bonus! You received Double Gold buff for 5 turns!")
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
                typewriter("Correct! You escape the trap safely.")
                time.sleep(0.5)

        # Exit after 5 moves or randomly continue
        if moves >= 5 and random.random() < 0.3:
            typewriter("\nYou find the exit of the maze. Trial completed!")
            in_maze = False
            break

    # Apply accumulated rewards
    player.gold += accumulated_rewards["gold"]
    player.exp += accumulated_rewards["exp"]
    for aid in accumulated_rewards["aid"]:
        player.inventory.append(aid)

    typewriter(f"\nTrial Rewards Summary:")
    typewriter(f"- Gold: {accumulated_rewards['gold']}")
    typewriter(f"- Exp: {accumulated_rewards['exp']}")
    if accumulated_rewards["aid"]:
        typewriter("- Aid:")
        for aid in accumulated_rewards["aid"]:
            typewriter(f"  - {aid.name}")

    time.sleep(1)