#!/usr/bin/env python3
"""Test script to verify all question types load correctly."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Core Game'))

from learningEngine import LearningEngine, validate_notes
from config import load_config, get_notes_paths

def test_question_loading():
    """Test that all question types load successfully."""
    
    # Load configuration
    config = load_config()
    note_paths = get_notes_paths(config)
    
    print("=" * 60)
    print("Testing Question Type Loading")
    print("=" * 60)
    
    # Define difficulty for each type
    difficulties = {
        "TF": 1,
        "MC": 2,
        "AR": 2,
        "ID": 3,
        "FB": 2,
        "OD": 3,
    }
    
    # Test each question type
    engine = LearningEngine()
    total_questions = 0
    
    for qtype, path in note_paths.items():
        print(f"\n[{qtype}] {path}")
        
        # Validate the file
        is_valid = validate_notes(path, qtype)
        
        if is_valid:
            # Load the questions
            before_count = len(engine.questions)
            engine.load_notes(path, qtype=qtype, difficulty=difficulties.get(qtype, 1))
            after_count = len(engine.questions)
            loaded = after_count - before_count
            total_questions += loaded
            
            print(f"  ✓ Loaded {loaded} questions")
            
            # Show a sample question
            if loaded > 0:
                sample = engine.questions[-1]  # Get the last loaded question
                print(f"  Sample: {sample['question'][:50]}...")
        else:
            print(f"  ✗ Validation failed")
    
    print("\n" + "=" * 60)
    print(f"Total questions loaded: {total_questions}")
    print(f"Question types in engine: {len(engine.questions)} total")
    
    # Verify all types are represented
    types_loaded = {q['type'] for q in engine.questions}
    expected_types = set(note_paths.keys())
    
    print(f"\nExpected types: {sorted(expected_types)}")
    print(f"Loaded types:   {sorted(types_loaded)}")
    
    if types_loaded == expected_types:
        print("\n✓ All question types loaded successfully!")
        return True
    else:
        missing = expected_types - types_loaded
        print(f"\n✗ Missing types: {missing}")
        return False

if __name__ == "__main__":
    success = test_question_loading()
    sys.exit(0 if success else 1)
