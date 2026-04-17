"""Bestiary system - tracks all enemies encountered with kill counts."""

import json
import os

from config import BASE_DIR

BESTIARY_FILE = os.path.join(BASE_DIR, "bestiary.json")


class Bestiary:
    """Tracks enemy encounters and kill counts across all runs."""
    
    def __init__(self):
        self.entries = {}  # {enemy_name: {"kills": int, "first_seen": str, "last_seen": str}}
        self.load()
    
    def load(self):
        """Load bestiary from file."""
        if os.path.exists(BESTIARY_FILE):
            try:
                with open(BESTIARY_FILE, "r", encoding="utf-8") as f:
                    self.entries = json.load(f)
            except Exception:
                self.entries = {}
        else:
            self.entries = {}
    
    def save(self):
        """Save bestiary to file."""
        try:
            with open(BESTIARY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    
    def record_encounter(self, enemy_name: str):
        """Record that an enemy was encountered."""
        if enemy_name not in self.entries:
            self.entries[enemy_name] = {
                "kills": 0,
                "first_seen": self._get_date(),
                "last_seen": self._get_date()
            }
        else:
            self.entries[enemy_name]["last_seen"] = self._get_date()
    
    def record_kill(self, enemy_name: str):
        """Record that an enemy was defeated."""
        if enemy_name not in self.entries:
            self.record_encounter(enemy_name)
        self.entries[enemy_name]["kills"] += 1
        self.entries[enemy_name]["last_seen"] = self._get_date()
        self.save()
    
    def get_stats(self):
        """Get bestiary statistics."""
        total_entries = len(self.entries)
        total_kills = sum(e.get("kills", 0) for e in self.entries.values())
        return {
            "total_entries": total_entries,
            "total_kills": total_kills,
            "entries": self.entries
        }
    
    def format_bestiary(self) -> str:
        """Format bestiary for display."""
        if not self.entries:
            return "No enemies encountered yet."
        
        text = "══════════════════════════════════════════════\n"
        text += "                  BESTIARY                     \n"
        text += "═════════════════════════════════════════════\n\n"
        
        sorted_entries = sorted(
            self.entries.items(),
            key=lambda x: x[1].get("kills", 0),
            reverse=True
        )
        
        for name, data in sorted_entries:
            kills = data.get("kills", 0)
            first = data.get("first_seen", "Unknown")
            last = data.get("last_seen", "Unknown")
            text += f"{name:20} | Kills: {kills:3} | Last: {last}\n"
        
        text += "\n═════════════════════════════════════════════\n"
        stats = self.get_stats()
        text += f"Total Unique Enemies: {stats['total_entries']}\n"
        text += f"Total Kills: {stats['total_kills']}\n"
        text += "═════════════════════════════════════════════\n"
        
        return text
    
    @staticmethod
    def _get_date():
        """Get current date as string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")


def get_bestiary():
    """Get or create bestiary instance."""
    return Bestiary()
