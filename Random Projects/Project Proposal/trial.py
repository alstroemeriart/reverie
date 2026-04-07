import tkinter as tk
from tkinter import ttk

# ===== MOCK PLAYER / ENEMY =====
class Entity:
    def __init__(self, name, hp, atk, defense, spd):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.defense = defense
        self.spd = spd

    def take_dmg(self, dmg):
        self.hp = max(0, self.hp - dmg)

    def is_alive(self):
        return self.hp > 0


player = Entity("Player", 100, 15, 5, 5)
enemy = Entity("Enemy", 80, 12, 3, 4)


# ===== MAIN GUI CLASS =====
class GameGUI:
    def __init__(self, root):
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

    # ===== UI HELPERS =====
    def write(self, msg):
        self.text.insert(tk.END, msg + "\n")
        self.text.see(tk.END)

    def clear_buttons(self):
        for w in self.button_frame.winfo_children():
            w.destroy()

    def set_buttons(self, options):
        self.clear_buttons()
        for text, cmd in options:
            b = tk.Button(self.button_frame, text=text, command=cmd)
            b.pack(fill="x")

    def update_stats(self):
        self.hp_label.config(text=f"HP: {player.hp}/{player.max_hp}")
        self.hp_bar["maximum"] = player.max_hp
        self.hp_bar["value"] = player.hp

    # ===== COMBAT FLOW =====
    def start_combat(self):
        self.write("A battle begins!")
        self.player_turn()

    def player_turn(self):
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

    # ===== PLAYER ACTIONS =====
    def attack_action(self):
        dmg = max(1, player.atk - enemy.defense)
        enemy.take_dmg(dmg)

        self.write(f"You dealt {dmg} damage!")
        self.after_player_action()

    def ask_action(self):
        # Placeholder for your learning engine
        self.write("You answered a question correctly!")
        dmg = 10
        enemy.take_dmg(dmg)
        self.write(f"Bonus damage: {dmg}")
        self.after_player_action()

    def aid_action(self):
        self.write("You used an aid (placeholder).")
        player.hp = min(player.max_hp, player.hp + 10)
        self.update_stats()
        self.after_player_action()

    def abstain_action(self):
        self.write("You tried to escape...")
        self.root.after(1000, self.enemy_turn)

    def after_player_action(self):
        self.update_stats()

        if enemy.hp <= 0:
            self.write("Enemy defeated!")
            self.clear_buttons()
            return

        self.root.after(1000, self.enemy_turn)

    # ===== ENEMY TURN =====
    def enemy_turn(self):
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


# ===== RUN =====
root = tk.Tk()
app = GameGUI(root)
root.mainloop()