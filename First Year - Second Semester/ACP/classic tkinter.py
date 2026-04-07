import tkinter as tk
from tkinter import ttk

def submit_data():
    name = entry.get()
    selected_names = listbox.curselection()

    items = [listbox.get(i) for i in selected_names]

    agree = check_var.get()
    intro.delete("1.0", tk.END) # clear the previous text in area

    intro.insert(tk.END, f"Name: {name}\n")
    intro.insert(tk.END, f"Selected Names: {items}\n")
    intro.insert(tk.END, f"Agreed: { 'Yes' if agree else 'No' }\n")

root = tk.Tk() # creates the application window
root.title("Hello World") # .title() sets te window title bar text
root.geometry("1000x1000") # .geometry() sets the window size

label = tk.Label(root, text="Welcome to the world!", font=("Papyrus", 50)) # insert text inside window
label.pack(pady=20) # adds widget to the window (layout)

# Input / Entry widget
entry = tk.Entry(root)
entry.pack(pady=20)

# Listbox widget
listbox = tk.Listbox(root, selectmode=tk.MULTIPLE) # allows for multiple selections
listbox.pack(pady=5)
items = ["Vermi", "Raylene", "Valentine", "Sirius"]
for item in items:
    listbox.insert(tk.END, item) # adds item to the end of the listbox

# Checkbutton
check_var = tk.IntVar() # variable to state if the checkbox is check or not
# Checkbox widget
check = tk.Checkbutton(root, text='I agree to submit my soul willingly.', variable=check_var)
check.pack(pady=5)

# Button widget
startButt = tk.Button(root, text='Submit', command=submit_data)
startButt.pack(pady=5)

# Multi-line text area widget
intro = tk.Text(root, height=5, width=100)
intro.pack(pady=5)

root.mainloop() # keeps the window open