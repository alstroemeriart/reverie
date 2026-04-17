#!/usr/bin/env python3
"""
TreeMap visualization test script
Tests the TreeMap rendering with sample data
"""
import sys
import os
import tkinter as tk

# Add the Game On folder to path
game_folder = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, game_folder)

print("=" * 70)
print("TREE MAP TEST")
print("=" * 70)

try:
    print("\n1. Importing modules...")
    from gui import TreeMap
    print("   ✓ TreeMap imported")
    
    print("\n2. Creating test window...")
    root = tk.Tk()
    root.title("TreeMap Test")
    root.geometry("400x500")
    print("   ✓ Window created")
    
    print("\n3. Creating TreeMap canvas...")
    canvas = tk.Canvas(root, width=220, height=340, bg="#1c2128")
    canvas.pack(fill="both", expand=True)
    tree_map = TreeMap(canvas)
    print("   ✓ TreeMap created")
    
    print("\n4. Testing TreeMap.set_history()...")
    test_history = ["battle", "battle", "shop"]
    test_pending = ["rest", "elite"]
    tree_map.set_history(test_history, "shop", test_pending)
    print(f"   ✓ Set history: {test_history}")
    print(f"   ✓ Set pending: {test_pending}")
    
    print("\n5. Checking TreeMap state...")
    print(f"   - Nodes created: {len(tree_map._nodes)}")
    print(f"   - History: {tree_map._history}")
    print(f"   - Pending branches: {len(tree_map._pending_branches)}")
    
    print("\n6. Rendering TreeMap...")
    root.update()
    print(f"   ✓ Canvas width (actual): {canvas.winfo_width()}")
    print(f"   ✓ Canvas height (actual): {canvas.winfo_height()}")
    
    print("\n7. Testing TreeMap.advance()...")
    tree_map.advance("rest")
    print(f"   ✓ Advanced to 'rest'")
    print(f"   - Updated history: {tree_map._history}")
    
    print("\n✓ TreeMap test successful!")
    print("\nThe TreeMap should now display:")
    print("  - A vertical chain of visited nodes (battle → battle → shop → rest)")
    print("  - Future branches at the bottom")
    print("  - Colored nodes for different states")
    print("\nClose this window to continue.")
    
    root.after(10000, root.quit)  # Auto-close after 10 seconds
    root.mainloop()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
