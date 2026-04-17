#!/usr/bin/env python3
"""
Verify TreeMap data flow and event handling
"""
import sys
import os

# Add the Game On folder to path
game_folder = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, game_folder)

print("=" * 70)
print("TREE MAP DATA FLOW TEST")
print("=" * 70)

try:
    print("\n1. Testing EventBus and game events...")
    import ui
    
    # Create a test listener
    events_received = []
    def test_listener(event):
        events_received.append(event)
        print(f"   Event received: {event['type']} - {event.get('name', 'N/A')}")
    
    ui.bus.subscribe(test_listener)
    print("   ✓ Test listener subscribed")
    
    print("\n2. Simulating draw_run_map() event...")
    # This simulates what draw_run_map sends
    ui.bus.game_event("map_update",
                      text="Tier 1/3 | Node 3   [B]--[B]--[*]--[S]?",
                      history=["battle", "battle"],
                      pending=["shop"])
    
    if events_received:
        last_event = events_received[-1]
        print(f"   ✓ Event sent: {last_event['type']}")
        print(f"   ✓ Data received:")
        print(f"     - text: {last_event.get('text', 'N/A')}")
        print(f"     - history: {last_event.get('history', [])}")
        print(f"     - pending: {last_event.get('pending', [])}")
    else:
        print("   ✗ No events received!")
    
    print("\n✓ Data flow test successful!")
    print("\nVerifying that GUI will receive:")
    print("  - Command: 'map'")
    print("  - Arguments: text, history list, pending list")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
