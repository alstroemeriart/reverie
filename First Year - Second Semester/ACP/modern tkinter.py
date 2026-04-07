import tkinter as tk
from tkinter import ttk

# Main window
root = tk.Tk()
root.title("TTK Modern Edition")
root.geometry("1500x1000")

# Notebook (tabs)
# Create tabs container
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, pady=10, padx=10)
# Fill makes widget stretch in BOTH directions
# Allows widget to expand when window resizes

# Create tabs
# Create two pages tabs
Avery = ttk.Frame(notebook)
Derek = ttk.Frame(notebook)

# Add tabs with titles
notebook.add(Avery, text="Avery", padding=10)
notebook.add(Derek, text="Derek", padding=10)

# Avery's tab content
ttk.Label(Avery, text="Whatever you do, at the crossroads, don't turn..?").pack()


root.mainloop()