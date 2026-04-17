"""GUI prototype for turn-based combat system.

This module provides a basic Tkinter-based GUI demonstrating a turn-based combat
interface with mock player and enemy entities, combat actions, and real-time UI updates.
"""

import tkinter as tk
from tkinter import ttk


class Entity:
    """Mock game entity with health, attack, defense, and speed stats.
    
    Attributes:
        name (str): Entity name
        max_hp (int): Maximum health points
        hp (int): Current health points
        atk (int): Attack damage value
        defense (int): Defense rating
        spd (int): Speed/initiative value
    """
    def __init__(self, name, hp, atk, defense, spd):
        """Initialize an entity with given stats.
        
        Args:
            name (str): Entity name
            hp (int): Health points
            atk (int): Attack damage
            defense (int): Defense rating
            spd (int): Speed value
        """
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.defense = defense
        self.spd = spd

    def take_dmg(self, dmg):
        """Reduce health by damage amount (minimum 0).
        
        Args:
            dmg (int): Damage to apply
        """
        self.hp = max(0, self.hp - dmg)

    def is_alive(self):
        """Check if entity is still alive.
        
        Returns:
            bool: True if hp > 0, False otherwise
        """
        return self.hp > 0


player = Entity("Player", 100, 15, 5, 5)
enemy = Entity("Enemy", 80, 12, 3, 4)


class GameGUI:
    """Tkinter-based GUI for turn-based combat demonstration.
    
    Provides a complete combat interface with player/enemy stats panels,
    combat log, action buttons, and real-time HP tracking.
    
    Attributes:
        root: Tkinter root window
        left: Left stat panel frame
        center: Center combat log frame
        button_frame: Action button container
    "
    def __init__(self, root):
        """Initialize the game GUI with root window.
        
        Args:
            root: Tkinter root window instance
        """
        self.root = root
        self.root.title("Game UI")
        self.root.geometry("1000x600")

        # ===== LEFT PANEL =====
        self.left = tk.Frame(root, bg="#1e1e1e", width=250)
        self.left.pack(side="left", fill="y")

        self.hp_label = tk.Label(self.left, text="", fg="white", bg="#1e1e1e")
        self.hp_label.pack(pady=10)

        self.hp_bar = ttk.Progressbar(self.left, length=200)
        self.hp_bar.pack()

        # ===== CENTER PANEL =====
        self.center = tk.Frame(root, bg="#121212")
        self.center.pack(side="left", fill="both", expand=True)

        self.text = tk.Text(self.center, bg="#121212", fg="white", wrap="word")
        self.text.pack(fill="both", expand=True)

        self.button_frame = tk.Frame(self.center)
        self.button_frame.pack(fill="x")

        self.update_stats()
        self.start_combat()

    def write(self, msg):
        """Add text message to combat log.
        
        Args:
            msg (str): Message to display
        """
        self.text.insert(tk.END, msg + "\n")
        self.text.see(tk.END)

    def clear_buttons(self):
        """Remove all action buttons from button frame."""
        for w in self.button_frame.winfo_children():
            w.destroy()

    def set_buttons(self, options):
        """Update action buttons with new options.
        
        Args:
            options (list): List of (button_text, callback) tuples
        """
        self.clear_buttons()
        for text, cmd in options:
            b = tk.Button(self.button_frame, text=text, command=cmd)
            b.pack(fill="x")

    def update_stats(self):
        """Update player HP display and progress bar."""
        self.hp_label.config(text=f"HP: {player.hp}/{player.max_hp}")
        self.hp_bar["maximum"] = player.max_hp
        self.hp_bar["value"] = player.hp

    def start_combat(self):
        """Initialize and start a combat sequence."""
        self.write("A battle begins!")
        self.player_turn()

    def player_turn(self):
        """Execute player's turn with action selection.
        
        Checks for win/loss conditions and presents available actions.
        """
        if not player.is_alive():
            self.write("You died.")
            return

        if not enemy.is_alive():
            self.write("Enemy defeated!")
            return

        self.write("\nYour turn:")
        self.set_buttons([
            ("Attack", self.attack_action),
            ("Ask", self.ask_action),
            ("Aid", self.aid_action),
            ("Abstain", self.abstain_action)
        ])

    def attack_action(self):
        """Execute basic attack against enemy.
        
        Damage calculation: player.atk - enemy.defense (minimum 1).
        """
        dmg = max(1, player.atk - enemy.defense)
        enemy.take_dmg(dmg)

        self.write(f"You dealt {dmg} damage!")
        self.after_player_action()

    def ask_action(self):
        """Execute question-based attack (placeholder for learning engine)."""
        self.write("You answered a question correctly!")
        dmg = 10
        enemy.take_dmg(dmg)
        self.write(f"Bonus damage: {dmg}")
        self.after_player_action()

    def aid_action(self):
        """Use an aid item to heal the player."""
        self.write("You used an aid (placeholder).")
        player.hp = min(player.max_hp, player.hp + 10)
        self.update_stats()
        self.after_player_action()

    def abstain_action(self):
        """Attempt to escape from combat (placeholder)."""
        self.write("You tried to escape...")
        self.root.after(1000, self.enemy_turn)

    def after_player_action(self):
        """Handle post-action state updates and check combat status."""
        self.update_stats()

        if enemy.hp <= 0:
            self.write("Enemy defeated!")
            self.clear_buttons()
            return

        self.root.after(1000, self.enemy_turn)

    def enemy_turn(self):
        """Execute enemy's automated turn with attack.
        
        Enemy attack damage: enemy.atk - player.defense (minimum 1).
        """
        if not enemy.is_alive():
            return

        self.write("\nEnemy turn...")

        dmg = max(1, enemy.atk - player.defense)
        player.take_dmg(dmg)

        self.write(f"Enemy dealt {dmg} damage!")
        self.update_stats()

        if player.hp <= 0:
            self.write("You were defeated...")
            self.clear_buttons()
            return

        self.root.after(1000, self.player_turn)


# Initialize and run the GUI
root = tk.Tk()
app = GameGUI(root)
root.mainloop()