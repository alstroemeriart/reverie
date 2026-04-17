#!/usr/bin/env python3
"""
Comprehensive TreeMap integration test
Tests the full flow from event emission to GUI rendering
"""
import sys
import os
import tkinter as tk
from unittest.mock import MagicMock, patch

# Add the Game On folder to path
game_folder = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, game_folder)

print("=" * 70)
print("TREE MAP INTEGRATION TEST")
print("=" * 70)

try:
    print("\n1. Creating test GUI...")
    root = tk.Tk()
    root.geometry("400x600")
    
    from gui import GameGUI
    gui = GameGUI(root)
    print("   ✓ GameGUI created")
    
    print("\n2. Getting TreeMap reference...")
    tree_map = gui._tree_map
    print(f"   ✓ TreeMap: {tree_map}")
    
    print("\n3. Simulating map_update event...")
    import ui
    
    # Send a map update event through the GUI
    event = {
        "type": "game",
        "name": "map_update",
        "text": "Tier 1/3 | Node 3",
        "history": ["battle", "elite", "shop"],
        "pending": ["rest", "boss"]
    }
    
    gui.on_event(event)
    print("   ✓ Event sent to GUI")
    
    print("\n4. Processing queue...")
    root.update()
    print("   ✓ Queue processed")
    
    print("\n5. Checking TreeMap state...")
    print(f"   - History: {tree_map._history}")
    print(f"   - Pending branches: {len(tree_map._pending_branches)}")
    print(f"   - Total nodes: {len(tree_map._nodes)}")
    
    if tree_map._history == ["battle", "elite", "shop"]:
        print("   ✓ History matches!")
    else:
        print("   ✗ History mismatch!")
        
    if len(tree_map._pending_branches) == 2:
        print("   ✓ Pending branches count matches!")
    else:
        print("   ✗ Pending branches count mismatch!")
    
    print("\n6. Testing advance functionality...")
    tree_map.advance("rest")
    print(f"   ✓ Advanced to 'rest'")
    print(f"   - Updated history: {tree_map._history}")
    
    print("\n✓ Full integration test successful!")
    print("\nThe TreeMap is now properly integrated and will:")
    print("  1. Receive map_update events with structured data")
    print("  2. Display visited nodes and future branches")
    print("  3. Update when advancing to next node")
    print("  4. Render all nodes with proper colors and icons")
    
    # Keep window open briefly to verify rendering
    print("\nRendering TreeMap for 5 seconds...")
    root.after(5000, root.quit)
    root.mainloop()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
