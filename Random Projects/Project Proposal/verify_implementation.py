#!/usr/bin/env python3
"""Simple static verification of question type implementation."""

import sys
import os
import json
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Core Game'))

def verify_implementation():
    """Verify question type implementation without executing game code."""
    
    print("=" * 70)
    print("QUESTION TYPE IMPLEMENTATION VERIFICATION")
    print("=" * 70)
    
    results = {
        "config": False,
        "learning_engine": False,
        "combat_system": False,
        "spawns": False,
        "achievements": False,
        "polish": False,
        "all_questions_present": False
    }
    
    # 1. Check config.json
    print("\n[1] Checking config.json...")
    try:
        with open("Core Game/config.json", "r") as f:
            config = json.load(f)
        
        expected_types = {"TF", "MC", "AR", "ID", "FB", "OD"}
        actual_types = set(config.get("notes", {}).keys())
        
        print(f"    Configured types: {sorted(actual_types)}")
        
        if expected_types == actual_types:
            print("    ✓ All 6 question types configured")
            results["config"] = True
        else:
            missing = expected_types - actual_types
            print(f"    ✗ Missing: {missing}")
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    # 2. Check learningEngine.py
    print("\n[2] Checking learningEngine.py...")
    try:
        with open("Core Game/learningEngine.py", "r") as f:
            content = f.read()
        
        checks = [
            ('qtype in ("TF", "AR", "FB", "ID")', "validation"),
            ('qtype in ("TF", "AR", "FB", "ID")', "loading"),
            ('"FB": "Fill in the Blanks"', "category name"),
        ]
        
        all_ok = True
        for pattern, desc in checks:
            if pattern in content:
                print(f"    ✓ {desc} found")
            else:
                print(f"    ✗ {desc} not found")
                all_ok = False
        
        results["learning_engine"] = all_ok
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    # 3. Check combatSystem.py
    print("\n[3] Checking combatSystem.py...")
    try:
        with open("Core Game/combatSystem.py", "r") as f:
            content = f.read()
        
        checks = [
            ('"FB": "Fill in the Blanks"', "FB category name"),
            ('elif q_type == "FB":', "FB question handler"),
        ]
        
        all_ok = True
        for pattern, desc in checks:
            if pattern in content:
                print(f"    ✓ {desc} found")
            else:
                print(f"    ✗ {desc} not found")
                all_ok = False
        
        results["combat_system"] = all_ok
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    # 4. Check Spawns.py
    print("\n[4] Checking Spawns.py...")
    try:
        with open("Core Game/Spawns.py", "r") as f:
            content = f.read()
        
        if '"TF": 0, "MC": 0, "AR": 0, "ID": 0, "FB": 0, "OD": 0' in content:
            print("    ✓ Mastery dict includes FB and OD")
            results["spawns"] = True
        else:
            print("    ✗ Mastery dict missing FB or OD")
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    # 5. Check achievements.py
    print("\n[5] Checking achievements.py...")
    try:
        with open("Core Game/achievements.py", "r") as f:
            content = f.read()
        
        checks = [
            ('all 6 question types', "achievement description"),
            ('["TF","MC","AR","ID","FB","OD"]', "achievement check"),
        ]
        
        all_ok = True
        for pattern, desc in checks:
            if pattern in content:
                print(f"    ✓ {desc} found")
            else:
                print(f"    ✗ {desc} not found")
                all_ok = False
        
        results["achievements"] = all_ok
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    # 6. Check polish_features.py
    print("\n[6] Checking polish_features.py...")
    try:
        with open("Core Game/polish_features.py", "r") as f:
            content = f.read()
        
        if '["TF", "MC", "AR", "ID", "FB", "OD"]' in content:
            print("    ✓ Session stats includes FB and OD")
            results["polish"] = True
        else:
            print("    ✗ Session stats missing FB or OD")
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    # 7. Check question files exist
    print("\n[7] Checking question files...")
    try:
        from learningEngine import LearningEngine
        from config import load_config, get_notes_paths
        
        config = load_config()
        note_paths = get_notes_paths(config)
        
        expected_files = {"TF", "MC", "AR", "ID", "FB", "OD"}
        file_counts = {}
        
        for qtype, path in note_paths.items():
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    lines = [l.strip() for l in f if l.strip()]
                file_counts[qtype] = len(lines)
                print(f"    ✓ {qtype}: {len(lines)} entries")
            else:
                print(f"    ✗ {qtype}: File not found - {path}")
        
        results["all_questions_present"] = set(file_counts.keys()) == expected_files
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {check}")
    
    print(f"\nResult: {passed}/{total} checks passed")
    
    if passed == total:
        print("\nSUCCESS: All question types fully implemented!")
        return True
    else:
        print(f"\nFAILED: {total - passed} check(s) failed")
        return False

if __name__ == "__main__":
    success = verify_implementation()
    sys.exit(0 if success else 1)
