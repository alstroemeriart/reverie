"""Bestiary system — tracks all enemies encountered with kill counts.

Persists encounter and kill data across all runs so players can see
a history of every enemy they have faced.
"""

import json
import os
from datetime import datetime

from config import BASE_DIR

# JSON file that stores all bestiary data between sessions
BESTIARY_FILE = os.path.join(BASE_DIR, "bestiary.json")


class Bestiary:
    """Tracks enemy encounters and kill counts across all runs.

    Data is stored in a dict keyed by enemy name:
        {
            "Goblin": {
                "kills": 4,
                "first_seen": "2024-01-01",
                "last_seen":  "2024-01-03"
            },
            ...
        }
    """

    def __init__(self) -> None:
        # entries: {enemy_name: {"kills": int, "first_seen": str, "last_seen": str}}
        self.entries: dict = {}
        self.load()

    # ── Persistence ─────────────────────────────────────────────────────────

    def load(self) -> None:
        """Load bestiary data from the JSON file.

        If the file doesn't exist or is corrupted, starts with an empty dict.
        """
        if os.path.exists(BESTIARY_FILE):
            try:
                with open(BESTIARY_FILE, "r", encoding="utf-8") as f:
                    self.entries = json.load(f)
            except Exception:
                # File corrupted or unreadable — start fresh
                self.entries = {}
        else:
            self.entries = {}

    def save(self) -> None:
        """Save bestiary data to the JSON file.

        Silently swallows errors so a save failure never crashes the game.
        """
        try:
            with open(BESTIARY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # Non-fatal

    # ── Recording ────────────────────────────────────────────────────────────

    def record_encounter(self, enemy_name: str) -> None:
        """Record that an enemy has been encountered (not necessarily killed).

        Creates a new entry for the enemy on first encounter; updates
        ``last_seen`` on subsequent ones.

        Args:
            enemy_name: The display name of the encountered enemy.
        """
        today = self._get_date()
        if enemy_name not in self.entries:
            # First time seeing this enemy — create the entry
            self.entries[enemy_name] = {
                "kills": 0,
                "first_seen": today,
                "last_seen": today,
            }
        else:
            # Already seen — just update the date
            self.entries[enemy_name]["last_seen"] = today

    def record_kill(self, enemy_name: str) -> None:
        """Record that an enemy was defeated and persist immediately.

        Calls record_encounter internally in case this enemy was never
        explicitly encountered before (defensive coding).

        Args:
            enemy_name: The display name of the defeated enemy.
        """
        # Ensure entry exists before incrementing
        if enemy_name not in self.entries:
            self.record_encounter(enemy_name)

        self.entries[enemy_name]["kills"] += 1
        self.entries[enemy_name]["last_seen"] = self._get_date()
        self.save()  # Persist after every kill so data isn't lost on crash

    # ── Statistics ───────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        """Return aggregate bestiary statistics.

        Returns:
            dict with keys:
                - ``total_entries`` (int): Unique enemy types encountered.
                - ``total_kills``   (int): Combined kills across all enemies.
                - ``entries``       (dict): Full raw entries dict.
        """
        total_kills = sum(e.get("kills", 0) for e in self.entries.values())
        return {
            "total_entries": len(self.entries),
            "total_kills": total_kills,
            "entries": self.entries,
        }

    def format_bestiary(self) -> str:
        """Build a formatted string representation of the bestiary for display.

        Enemies are sorted by kill count descending so the most-defeated
        enemies appear first.

        Returns:
            str: Multi-line formatted bestiary, or a short message if empty.
        """
        if not self.entries:
            return "No enemies encountered yet."

        lines = []
        lines.append("══════════════════════════════════════════════")
        lines.append("                  BESTIARY                    ")
        lines.append("══════════════════════════════════════════════\n")

        # Sort by kill count, highest first
        sorted_entries = sorted(
            self.entries.items(),
            key=lambda x: x[1].get("kills", 0),
            reverse=True,
        )

        for name, data in sorted_entries:
            kills = data.get("kills", 0)
            last  = data.get("last_seen", "Unknown")
            lines.append(f"{name:20} | Kills: {kills:3} | Last: {last}")

        lines.append("\n══════════════════════════════════════════════")
        stats = self.get_stats()
        lines.append(f"Total Unique Enemies : {stats['total_entries']}")
        lines.append(f"Total Kills          : {stats['total_kills']}")
        lines.append("══════════════════════════════════════════════")

        return "\n".join(lines)

    # ── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _get_date() -> str:
        """Return today's date as a YYYY-MM-DD string."""
        return datetime.now().strftime("%Y-%m-%d")


def get_bestiary() -> Bestiary:
    """Convenience factory: create and return a fresh Bestiary instance.

    Returns:
        Bestiary: A loaded Bestiary ready to use.
    """
    return Bestiary()