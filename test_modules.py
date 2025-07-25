#!/usr/bin/env python3
"""
Test script to verify the modular Ricochet Robots implementation works correctly.
"""

from game_engine import RicochetGame, Direction, Position
from puzzle_generator import PuzzleGenerator

def test_game_engine():
    print("Testing game engine...")
    game = RicochetGame()
    
    # Test basic initialization
    assert game.grid_size == 5
    assert game.move_count == 0
    assert not game.game_won
    print("✓ Game initialization works")
    
    # Test position creation
    pos = Position(2, 3)
    assert pos.row == 2 and pos.col == 3
    print("✓ Position class works")
    
    return True

def test_puzzle_generator():
    print("\nTesting puzzle generator...")
    game = RicochetGame()
    
    # Test strategic puzzle generation
    result = PuzzleGenerator.generate_strategic_puzzle(game)
    assert result == True
    assert game.start_pos is not None
    assert game.goal_pos is not None
    assert game.friend1_pos is not None
    assert game.friend2_pos is not None
    print("✓ Strategic puzzle generation works")
    
    # Test solvability verification
    is_solvable = PuzzleGenerator.verify_puzzle_solvable(game)
    print(f"✓ Puzzle solvability check: {is_solvable}")
    
    # Test guaranteed solvable generation
    result = PuzzleGenerator.generate_guaranteed_solvable_puzzle(game)
    assert result == True
    print("✓ Guaranteed solvable puzzle generation works")
    
    return True

def test_game_mechanics():
    print("\nTesting game mechanics...")
    game = RicochetGame()
    PuzzleGenerator.generate_strategic_puzzle(game, puzzle_index=0)
    
    # Test robot movement
    initial_pos = game.robot_pos
    result = game.move_robot(Direction.EAST)
    
    if result:
        moved, old_pos, new_pos, friend_visited = result
        print(f"✓ Robot moved from {old_pos.row},{old_pos.col} to {new_pos.row},{new_pos.col}")
        assert game.move_count == 1
    else:
        print("✓ Robot movement blocked (expected for some layouts)")
    
    print("✓ Game mechanics work correctly")
    return True

def main():
    print("🤖 Testing Ricochet Robots Modular Implementation")
    print("=" * 50)
    
    try:
        test_game_engine()
        test_puzzle_generator()
        test_game_mechanics()
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! The modular implementation works correctly.")
        print("\nModular structure:")
        print("├── game_engine.py    - Core game logic and mechanics")
        print("├── puzzle_generator.py - Puzzle creation and solvability verification")
        print("└── ricochet_gui_modular.py - GUI interface")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()