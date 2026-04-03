# LEARNING ENGINE

import random, json
import time
from Spawns import MainCharacter, Enemy
from items import AllItems
from ui import typewriter

def validate_notes(filepath, qtype):
    """
    Check a notes file for formatting errors before loading.
    Prints warnings for any malformed lines.
    Returns True if file loaded cleanly, False if errors found.
    """
    errors = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        typewriter(f"[Validator] File not found: {filepath}")
        return False

    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue

        if qtype in ("TF", "AR"):
            if "=" not in line:
                errors.append(f"  Line {i}: missing '=' separator → {line!r}")
            else:
                parts = line.split("=", 1)
                if not parts[0].strip():
                    errors.append(f"  Line {i}: empty question → {line!r}")
                if not parts[1].strip():
                    errors.append(f"  Line {i}: empty answer → {line!r}")
                if qtype == "TF":
                    ans = parts[1].strip().lower()
                    if ans not in ("true", "false"):
                        errors.append(f"  Line {i}: TF answer must be 'True' or 'False' → {ans!r}")

        elif qtype == "MC":
            try:
                import json
                data = json.loads(line)
                for key in ("question", "options", "answer"):
                    if key not in data:
                        errors.append(f"  Line {i}: missing key '{key}'")
                if "options" in data and data.get("answer") not in data["options"]:
                    errors.append(f"  Line {i}: answer not in options list")
            except Exception:
                errors.append(f"  Line {i}: invalid JSON → {line!r}")

    if errors:
        typewriter(f"[Validator] Issues in {filepath}:")
        for err in errors:
            typewriter(err)
        return False

    typewriter(f"[Validator] {filepath} — OK ({len(lines)} lines)")
    return True

class LearningEngine:
    def __init__(self):
        self.questions = []
        self.wrong_answers = []

    def record_wrong(self, question_data):
        """Store a question the player got wrong for end-of-run review."""
        self.wrong_answers.append({
            "question": question_data["question"],
            "correct_answer": question_data["answer"],
            "type": question_data["type"],
        })

    def get_weak_areas(self):
        """Return which question types the player struggled with most."""
        from collections import Counter
        counts = Counter(q["type"] for q in self.wrong_answers)
        return counts.most_common()

    def print_review(self):
        """Print a summary of missed questions at end of run."""
        if not self.wrong_answers:
            typewriter("\nYou answered every question correctly. Excellent!")
            return

        typewriter(f"\n--- Review: {len(self.wrong_answers)} missed questions ---")
        for entry in self.wrong_answers[-10:]:   # show last 10 max
            typewriter(f"  Q: {entry['question']}")
            typewriter(f"  A: {entry['correct_answer']}")
            typewriter("")

        typewriter("Weak areas this run:")
        for qtype, count in self.get_weak_areas():
            category = {"TF": "True/False", "MC": "Multiple Choice",
                        "AR": "Arithmetic", "ID": "Identification"}.get(qtype, qtype)
            typewriter(f"  {category}: {count} wrong")

    def load_notes(self, filepath, qtype="TF", difficulty=1):
        """
        Load questions from a notes file.
        - TF: True/False format, each line "Statement = True/False"
        - MC: Multiple Choice, JSON format per line: {"question": "...", "options": ["A","B"], "answer": "B"}
        - AR: Arithmetic or ID, "Question = Answer"
        - OD: Ordering, each line: {"type":"OD","question":"Order these from smallest to largest", "items":["Atom","Molecule","Cell","Organ"],"answer":"1,2,3,4"}
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
                    statement, answer = line.split("=", 1)
                    self.questions.append({
                        "type": qtype,
                        "question": statement.strip(),
                        "answer": answer.strip(),
                        "difficulty" : difficulty
                    })

                elif qtype == "MC":
                    # Expecting JSON string per line
                    try:
                        data = json.loads(line)
                        if "question" in data and "options" in data and "answer" in data:
                            data["type"] = "MC"
                            data["difficulty"] = difficulty
                            self.questions.append(data)
                    except json.JSONDecodeError:
                        continue

                elif qtype == "OD":
                    try:
                        data = json.loads(line)
                        if "question" in data and "items" in data and "answer" in data:
                            data["type"] = "OD"
                            data["difficulty"] = difficulty
                            self.questions.append(data)
                    except json.JSONDecodeError:
                        continue

        except FileNotFoundError:
            typewriter(f"Notes file not found: {filepath}")

    def get_question(self, difficulty=None):
        """Get a random question, optionally filtered by difficulty (1, 2, or 3)."""
        if not self.questions:
            return None
        
        pool = self.questions
        if difficulty is not None:
            filtered = [q for q in self.questions if q.get("difficulty") == difficulty]
            if filtered:
                pool = filtered

        # Build weights — questions answered wrong recently get higher weight
        wrong_questions = {q["question"] for q in self.wrong_answers}
        weights = []
        for q in pool:
            if q["question"] in wrong_questions:
                weights.append(3)   # 3x more likely to appear again
            else:
                weights.append(1)

        return random.choices(pool, weights=weights, k=1)[0]

    # Keep get_random_question as an alias so existing code doesn't break
    def get_random_question(self):
        return self.get_question()
    
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

def combat_item_drop(tier=1):
    """
    Chance to drop an item after combat.
    Higher tier = better drop chance and rarity.
    """
    drop_chance = 0.3 + (tier * 0.1)   # 40% at tier 1, 60% at tier 3
    if random.random() > drop_chance:
        return None

    # Tier influences rarity weights
    if tier == 1:
        weights = [60, 30, 10, 0]     # common, uncommon, rare, legendary
    elif tier == 2:
        weights = [30, 40, 25, 5]
    else:
        weights = [10, 30, 45, 15]

    rarities = ["common", "uncommon", "rare", "legendary"]
    rarity = random.choices(rarities, weights=weights, k=1)[0]

    possibilities = [i for i in AllItems if i["rarity"] == rarity]
    if not possibilities:
        return None

    return random.choice(possibilities)["class"]()

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
        maze_difficulty = 1 if moves <= 2 else (2 if moves <= 4 else 3)
        q_data = engine.get_question(difficulty=maze_difficulty)
        if q_data is None:
            q_data = engine.get_question()
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
    player.apply_gold(accumulated_rewards["gold"])
    player.gain_xp(accumulated_rewards["exp"])
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


def practice_mode(engine):
    """
    Standalone question drill outside of combat.
    No penalties — just questions and answers with tracking.
    """
    from ui import typewriter, clear_screen
    clear_screen()
    typewriter("\n=== Practice Mode ===")
    typewriter("Answer questions to review your material.")
    typewriter("Type 'quit' at any time to return to the menu.\n")

    correct = 0
    total = 0
    wrong_log = []

    while True:
        q = engine.get_question()
        if q is None:
            typewriter("No questions loaded.")
            break

        q_type = q["type"]
        answer = q["answer"]
        category = {"TF": "True/False", "MC": "Multiple Choice",
                    "AR": "Arithmetic", "ID": "Identification"}.get(q_type, q_type)

        typewriter(f"\n[{category}] {q['question']}")

        if q_type == "TF":
            raw = input("(True/False) > ").strip()
        elif q_type == "MC":
            options = q.get("options", [])
            for i, opt in enumerate(options, 1):
                typewriter(f"  {i}. {opt}")
            raw = input("> ").strip()
            try:
                raw = options[int(raw) - 1]
            except (ValueError, IndexError):
                raw = ""
        else:
            raw = input("> ").strip()

        if raw.lower() == "quit":
            break

        if raw.lower() == answer.lower():
            typewriter("Correct!")
            correct += 1
        else:
            typewriter(f"Wrong. The answer was: {answer}")
            wrong_log.append(q)

        total += 1

        typewriter(f"Score: {correct}/{total}")
        time.sleep(0.5)

    typewriter(f"\nPractice complete. Final score: {correct}/{total}")
    if wrong_log:
        typewriter("\nYou missed these:")
        for q in wrong_log:
            typewriter(f"  Q: {q['question']}")
            typewriter(f"  A: {q['answer']}")
    time.sleep(1)

