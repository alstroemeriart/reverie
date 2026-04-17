#!/usr/bin/env python3
"""Comprehensive test to verify all question types work in game context."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Core Game'))

from learningEngine import LearningEngine
from config import load_config, get_notes_paths
from Spawns import MainCharacter

def test_comprehensive():
    """Comprehensive test of question type implementation."""
    
    print("=" * 70)
    print("COMPREHENSIVE QUESTION TYPE IMPLEMENTATION TEST")
    print("=" * 70)
    
    # Test 1: Load configuration
    print("\n[1] Loading configuration...")
    config = load_config()
    note_paths = get_notes_paths(config)
    print(f"    Configured note files: {list(note_paths.keys())}")
    
    # Test 2: Initialize learning engine
    print("\n[2] Initializing learning engine...")
    engine = LearningEngine()
    
    difficulties = {
        "TF": 1, "MC": 2, "AR": 2, "ID": 3,
        "FB": 2, "OD": 3,
    }
    
    questions_by_type = {}
    for qtype, path in note_paths.items():
        try:
            engine.load_notes(path, qtype=qtype, difficulty=difficulties.get(qtype, 1))
            count = sum(1 for q in engine.questions if q['type'] == qtype)
            questions_by_type[qtype] = count
            print(f"    ✓ {qtype}: {count} questions loaded")
        except Exception as e:
            print(f"    ✗ {qtype}: Error - {e}")
    
    # Test 3: Create player and verify mastery tracking
    print("\n[3] Testing player mastery tracking...")
    player = MainCharacter(
        name="TestPlayer",
        max_hp=100,
        atk=10,
        defense=5,
        spd=8,
        wisdom=7,
        crit_chance=0.15,
        crit_multiplier=1.5
    )
    
    # Check mastery dictionary includes all types
    expected_types = set(difficulties.keys())
    actual_types = set(player.mastery.keys())
    
    print(f"    Expected mastery types: {sorted(expected_types)}")
    print(f"    Actual mastery types:   {sorted(actual_types)}")
    
    if expected_types.issubset(actual_types):
        print("    ✓ All question types in mastery dictionary")
    else:
        missing = expected_types - actual_types
        print(f"    ✗ Missing types: {missing}")
    
    # Test 4: Verify difficulty mappings
    print("\n[4] Verifying difficulty assignments...")
    from main import NOTE_DIFFICULTIES
    
    print("    Question type → Difficulty level:")
    for qtype, difficulty in sorted(NOTE_DIFFICULTIES.items()):
        print(f"      {qtype}: {difficulty}")
    
    if set(NOTE_DIFFICULTIES.keys()) == expected_types:
        print("    ✓ All question types in difficulty mapping")
    else:
        print(f"    ✗ Mismatch in difficulty mapping")
    
    # Test 5: Verify question sampling
    print("\n[5] Testing random question sampling...")
    samples = {}
    for qtype in questions_by_type.keys():
        q = engine.get_random_question()
        if q and q['type'] in questions_by_type:
            samples[q['type']] = q
            print(f"    ✓ Sampled {q['type']}: {q['question'][:40]}...")
    
    # Test 6: Verify combat category names
    print("\n[6] Verifying combat category names...")
    from combatSystem import CATEGORY_NAMES
    
    print("    Question type → Display name:")
    for qtype in sorted(expected_types):
        name = CATEGORY_NAMES.get(qtype, "UNKNOWN")
        print(f"      {qtype}: {name}")
    
    if expected_types.issubset(set(CATEGORY_NAMES.keys())):
        print("    ✓ All question types have display names")
    else:
        print("    ✗ Missing display names")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    total_questions = sum(questions_by_type.values())
    print(f"Total questions loaded: {total_questions}")
    print(f"Question types available: {sorted(questions_by_type.keys())}")
    
    all_ok = (
        expected_types.issubset(actual_types) and
        expected_types.issubset(set(CATEGORY_NAMES.keys())) and
        expected_types == set(NOTE_DIFFICULTIES.keys())
    )
    
    if all_ok and total_questions > 0:
        print("\n✓ ALL TESTS PASSED - Question types fully integrated!")
        return True
    else:
        print("\n✗ Some tests failed - see details above")
        return False

if __name__ == "__main__":
    success = test_comprehensive()
    sys.exit(0 if success else 1)
