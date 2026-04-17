"""
Polish features - end-of-run stats, keyboard shortcuts, confirmations
"""
from ui import typewriter
import time
import json


class RunStats:
    """Detailed statistics for a completed run."""
    
    def __init__(self, player, run_context, session_stats):
        self.player = player
        self.run_context = run_context
        self.session_stats = session_stats
        self.final_level = player.lvl
        self.final_gold = player.gold
        self.final_hp = player.hp
        self.final_streak = player.streak
        self.longest_streak = player.longest_streak
        self.inventory_count = len(player.inventory)
        self.battles_won = run_context.get("battles_won", 0)
        self.nodes_cleared = run_context.get("nodes_cleared", 0)
        self.beat_boss = run_context.get("beat_boss", False)
        self.xp_earned = player.exp  # This should be tracked separately
    
    def display_detailed_stats(self):
        """Display comprehensive end-of-run statistics."""
        typewriter("\n" + "=" * 60)
        typewriter("                ═══ RUN SUMMARY ═══")
        typewriter("=" * 60)
        
        # Character performance
        typewriter("\n┌─ CHARACTER PERFORMANCE ─────────────────────────────┐")
        typewriter(f"│ Final Level:        {self.final_level:>40} │")
        typewriter(f"│ Battles Won:        {self.battles_won:>40} │")
        typewriter(f"│ Nodes Cleared:      {self.nodes_cleared:>40} │")
        typewriter(f"│ Boss Defeated:      {'YES' if self.beat_boss else 'NO':>40} │")
        typewriter("└────────────────────────────────────────────────────┘")
        
        # Combat statistics
        typewriter("\n┌─ COMBAT STATISTICS ─────────────────────────────────┐")
        typewriter(f"│ Current HP:         {self.final_hp}/{self.player.max_hp:>37} │")
        typewriter(f"│ Final Streak:       {self.final_streak:>40} │")
        typewriter(f"│ Best Streak:        {self.longest_streak:>40} │")
        typewriter("└────────────────────────────────────────────────────┘")
        
        # Learning statistics
        accuracy = self.session_stats.accuracy()
        total_questions = (self.session_stats.correct + 
                          self.session_stats.wrong)
        typewriter("\n┌─ LEARNING STATISTICS ───────────────────────────────┐")
        typewriter(f"│ Questions Answered: {total_questions:>40} │")
        typewriter(f"│ Correct:            {self.session_stats.correct:>40} │")
        typewriter(f"│ Incorrect:          {self.session_stats.wrong:>40} │")
        typewriter(f"│ Accuracy:           {accuracy:>38}% │")
        typewriter("└────────────────────────────────────────────────────┘")
        
        # Rewards
        typewriter("\n┌─ REWARDS ───────────────────────────────────────────┐")
        typewriter(f"│ Gold Earned:        {self.final_gold:>40} │")
        typewriter(f"│ Items Found:        {self.inventory_count:>40} │")
        typewriter("└────────────────────────────────────────────────────┘")
        
        typewriter("\n" + "=" * 60)
        typewriter("\n(Press Enter to continue...)")
        time.sleep(1)


class SessionStats:
    """Tracks learning statistics for the current run."""
    def __init__(self):
        self.correct = 0
        self.wrong = 0
        self.by_type = {t: {"correct": 0, "wrong": 0} for t in ["TF", "MC", "AR", "ID", "FB", "OD"]}

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


KEYBOARD_SHORTCUTS = {
    "I": ("Inventory", "Show item count and list"),
    "Esc": ("Pause Menu", "Open pause menu (hint: you can't escape in combat!)"),
    "?": ("Help", "Show keyboard shortcuts"),
}


def print_keyboard_shortcuts():
    """Display available keyboard shortcuts."""
    typewriter("\n" + "=" * 50)
    typewriter("      KEYBOARD SHORTCUTS")
    typewriter("=" * 50)
    for key, (name, desc) in KEYBOARD_SHORTCUTS.items():
        typewriter(f"\n{key:>5} - {name}")
        typewriter(f"        {desc}")
    typewriter("\n" + "=" * 50)
    typewriter("\n(Press Enter to close...)")
