import random

class LearningEngine:
    def __init__(self):
        self.questions = []

    def load_notes(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                lines = file.readlines()

            for line in lines:
                if "=" in line:
                    statement, answer = line.strip().split("=")
                    self.questions.append({
                        "question": statement.strip(),
                        "answer": answer.strip()
                    })

        except FileNotFoundError:
            print("Notes file not found.")

    def get_random_question(self):
        if not self.questions:
            return None
        return random.choice(self.questions)