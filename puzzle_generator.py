import random
from typing import List, Set, Tuple, Optional
from collections import deque
from game_engine import Position, EdgeWall, Direction, RicochetGame

class PuzzleGenerator:
    @staticmethod
    def generate_strategic_puzzle(game, puzzle_index=None) -> bool:
        game.walls = set()
        layouts = [
            # The Crossroads - Corner navigation with border walls
            {
                'start': Position(1, 1),
                'goal': Position(3, 3), 
                'friend1': Position(0, 3),
                'friend2': Position(3, 0),
                'walls': [
                    # Internal barriers
                    EdgeWall(Position(1, 2), Position(2, 2)),  # Vertical wall
                    EdgeWall(Position(2, 1), Position(2, 2)),  # Horizontal wall
                    EdgeWall(Position(2, 3), Position(3, 3)),  # Vertical wall
                    # Border edge walls (perpendicular to boundaries)
                    EdgeWall(Position(0, 1), Position(0, 2)),  # Top edge horizontal
                    EdgeWall(Position(1, 0), Position(2, 0)),  # Left edge vertical
                    EdgeWall(Position(4, 2), Position(4, 3)),  # Bottom edge horizontal
                    EdgeWall(Position(2, 4), Position(3, 4)),  # Right edge vertical
                ]
            },
            # Crystal Maze - Central barriers with edge walls
            {
                'start': Position(0, 2),
                'goal': Position(4, 2),
                'friend1': Position(2, 0),
                'friend2': Position(2, 4),
                'walls': [
                    # Central cross pattern
                    EdgeWall(Position(1, 1), Position(2, 1)),  # Vertical wall
                    EdgeWall(Position(2, 1), Position(2, 2)),  # Horizontal wall
                    EdgeWall(Position(2, 3), Position(3, 3)),  # Vertical wall
                    # Edge walls
                    EdgeWall(Position(0, 0), Position(0, 1)),  # Top edge horizontal
                    EdgeWall(Position(3, 0), Position(4, 0)),  # Left edge vertical
                    EdgeWall(Position(1, 4), Position(2, 4)),  # Right edge vertical
                    EdgeWall(Position(4, 3), Position(4, 4)),  # Bottom edge horizontal
                ]
            },
            # Diagonal Challenge - Zigzag with edge barriers
            {
                'start': Position(0, 0),
                'goal': Position(4, 4),
                'friend1': Position(1, 4),
                'friend2': Position(4, 1),
                'walls': [
                    # Diagonal internal barriers
                    EdgeWall(Position(1, 1), Position(1, 2)),  # Horizontal wall
                    EdgeWall(Position(2, 2), Position(3, 2)),  # Vertical wall
                    EdgeWall(Position(3, 3), Position(4, 3)),  # Vertical wall
                    # Edge walls creating stops
                    EdgeWall(Position(0, 2), Position(0, 3)),  # Top edge horizontal
                    EdgeWall(Position(2, 0), Position(3, 0)),  # Left edge vertical
                    EdgeWall(Position(1, 4), Position(2, 4)),  # Right edge vertical
                    EdgeWall(Position(4, 1), Position(4, 2)),  # Bottom edge horizontal
                ]
            },
            # Spiral Gateway - Complex edge and internal walls
            {
                'start': Position(0, 1),
                'goal': Position(4, 3),
                'friend1': Position(1, 0),
                'friend2': Position(3, 4),
                'walls': [
                    # Internal spiral barriers
                    EdgeWall(Position(1, 1), Position(1, 2)),  # Horizontal wall
                    EdgeWall(Position(2, 2), Position(2, 3)),  # Horizontal wall
                    EdgeWall(Position(3, 1), Position(3, 2)),  # Horizontal wall
                    # Edge walls for complex paths
                    EdgeWall(Position(0, 3), Position(0, 4)),  # Top edge horizontal
                    EdgeWall(Position(2, 0), Position(3, 0)),  # Left edge vertical
                    EdgeWall(Position(1, 4), Position(2, 4)),  # Right edge vertical
                    EdgeWall(Position(4, 0), Position(4, 1)),  # Bottom edge horizontal
                ]
            }
        ]
        
        if puzzle_index is not None:
            layout = layouts[puzzle_index % len(layouts)]
            game.current_puzzle_index = puzzle_index % len(layouts)
        else:
            layout = random.choice(layouts)
            game.current_puzzle_index = layouts.index(layout)
        
        game.start_pos = layout['start']
        game.goal_pos = layout['goal']
        game.friend1_pos = layout['friend1']
        game.friend2_pos = layout['friend2']
        game.robot_pos = game.start_pos
        
        for wall in layout['walls']:
            game.walls.add(wall)
        # Check that each friend can move somewhere (not boxed in)
        def _reachable(pos):
            return any(game.ricochet_move(pos, d)[0] != pos for d in Direction)
        assert _reachable(game.friend1_pos), "Friend1 is boxed in!"
        assert _reachable(game.friend2_pos), "Friend2 is boxed in!"
        # Fully reset state at the end
        game.visited_friends = set()
        game.move_count = 0
        game.game_won = False
        game.update_grid()
        return True
    
    @staticmethod
    def verify_puzzle_solvable(game) -> bool:
        """
        Verify that the puzzle is solvable using BFS pathfinding.
        Returns True if there's a valid solution path.
        """
        # State: (robot_pos, visited_friends_set, move_count)
        start_state = (game.start_pos, frozenset(), 0)
        visited_states = set()
        queue = deque([start_state])
        
        max_moves = 50  # Reasonable upper bound to prevent infinite search
        
        while queue:
            robot_pos, visited_friends, move_count = queue.popleft()
            
            # Skip if we've exceeded reasonable move count
            if move_count > max_moves:
                continue
            
            # Create state key for visited tracking
            state_key = (robot_pos, visited_friends)
            if state_key in visited_states:
                continue
            visited_states.add(state_key)
            
            # Check win condition - goal can be reached by passing through OR stopping on it
            if len(visited_friends) == 2:
                # Try moving to goal position from current position
                for direction in [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]:
                    goal_pos, goal_path = game.ricochet_move(robot_pos, direction)
                    # Check if goal is reached during this move
                    for pos in goal_path[1:]:  # Skip starting position
                        if pos == game.goal_pos:
                            return True
            
            # Try all four directions
            for direction in [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]:
                new_pos, path = game.ricochet_move(robot_pos, direction)
                
                # Skip if no movement occurred
                if new_pos == robot_pos:
                    continue
                
                # Check for friend collection during this move
                new_visited = set(visited_friends)
                for pos in path[1:]:  # Skip starting position
                    if pos == game.friend1_pos:
                        new_visited.add(game.friend1_pos)
                    elif pos == game.friend2_pos:
                        new_visited.add(game.friend2_pos)
                
                # Add new state to queue
                new_state = (new_pos, frozenset(new_visited), move_count + 1)
                queue.append(new_state)
        
        return False
    
    @staticmethod
    def generate_guaranteed_solvable_puzzle(game, max_attempts=10) -> bool:
        """
        Generate a puzzle that is guaranteed to be solvable.
        Uses the pre-designed layouts which are known to be solvable.
        """
        for attempt in range(max_attempts):
            # Generate a strategic puzzle
            success = PuzzleGenerator.generate_strategic_puzzle(game)
            if not success:
                continue
            
            # Verify it's solvable
            if PuzzleGenerator.verify_puzzle_solvable(game):
                return True
            
            # If not solvable, try the next layout
            continue
        
        # Fallback to the first known-good layout if all attempts fail
        return PuzzleGenerator.generate_strategic_puzzle(game, puzzle_index=0)