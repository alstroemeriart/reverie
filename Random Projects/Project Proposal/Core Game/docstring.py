"""
Study RPG Dungeon Crawler
=========================

Project Goal
------------
To create a simple yet unique RPG dungeon crawler that transforms one's study notes
into an interactive learning experience. The game integrates quiz mechanics,
combat systems, stat allocation, procedural dungeon generation, and boss
battles into a cohesive educational game loop.

Core Concept
------------
The player progresses through a dungeon. Each room contains:
    - A combat encounter powered by study questions
    - Or a puzzle challenge (e.g., matching type questions)

Correct answers deal damage to enemies.
Incorrect answers cause the player to take damage.

Imported study notes serve as the content source for generating questions.

High-Level Architecture
-----------------------
The system must be modular and separated into layers:

1. Game Logic Layer (core mechanics, no UI dependency)
2. Question Engine (parses notes and generates questions)
3. Combat System (damage calculation, stat scaling)
4. Dungeon System (room structure + procedural generation)
5. Item & Potion System
6. Boss System
7. UI Layer (Tkinter or Pygame frontend)

Core Systems To Implement
-------------------------

1. Player System
    - Stats (HP, Attack, Defense, Intelligence, Speed, etc.)
    - Stat allocation system
    - Experience and leveling
    - Inventory (potions/items)

2. Question Engine
    - Load external notes file
    - Generate:
        * Multiple choice questions
        * Matching/puzzle questions
    - Track performance per topic

3. Combat System
    - Turn-based combat
    - Damage formula based on:
        * Player stats
        * Difficulty of question
        * Correct/incorrect answer
    - Mini-boss and boss phases

4. Potion System
    - Items that:
        * Remove incorrect choices
        * Extend timer
        * Increase damage multiplier
        * Reduce incoming damage
    - Limited usage per run

5. Dungeon System
    - Procedurally generated layout
    - Rooms classified as:
        * Combat
        * Puzzle
        * Mini-boss
        * Boss
    - Tracks cleared vs uncleared rooms

6. Boss System
    - Boss HP influenced by:
        * Player’s cumulative mistakes
        * Question accuracy
    - Phase-based combat mechanics
    - Final quick-attack finishing system

7. Progression System
    - Performance tracking
    - Reward stat points after clears
    - Scaling difficulty across floors

Design Constraints
------------------
- Keep logic modular (no giant while-loop structure)
- Avoid hardcoding questions directly into combat
- Ensure stat scaling remains mathematically balanced
- Make all systems extensible for future features

Minimum Viable Product (MVP)
----------------------------
Version 1 must include:
    - One player
    - Basic stat system
    - One combat encounter using questions
    - Simple damage formula
    - Basic GUI window (Tkinter or Pygame)
    - One small dungeon floor

Stretch Goals
-------------
- Advanced procedural generation
- Save/load system
- Multiple difficulty modes
- Visual animations
- Sound effects
- Adaptive difficulty scaling

Success Criteria 
----------------
The game should:
    - Load study notes
    - Generate questions dynamically
    - Allow player progression through a dungeon
    - Provide meaningful stat allocation choices
    - Reinforce learning through gameplay feedback

End Goal
--------
Deliver a functional educational RPG where studying feels like
progressing through a dungeon adventure.
"""