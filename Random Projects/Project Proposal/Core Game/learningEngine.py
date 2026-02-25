import random, json

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
            print(f"Notes file not found: {filepath}")

    def get_random_question(self):
        if not self.questions:
            return None
        return random.choice(self.questions)