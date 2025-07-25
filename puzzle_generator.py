import random
from typing import List, Set, Tuple, Optional
from collections import deque
from game_engine import Position, EdgeWall, Direction, RicochetGame

class PuzzleGenerator:
    @staticmethod
    def _add_island_walls(game):
        game.walls = set()
        game.add_border_walls()
        # Define the four 2x2 islands (corners)
        islands = [
            [(0,0), (0,1), (1,0), (1,1)], # top-left
            [(0,3), (0,4), (1,3), (1,4)], # top-right
            [(3,0), (3,1), (4,0), (4,1)], # bottom-left
            [(3,3), (3,4), (4,3), (4,4)]  # bottom-right
        ]
        # For each island, randomly pick one of four L-shaped wall configs
        l_shapes = [
            [(0,0,0,1),(0,0,1,0)], # top-left corner
            [(0,1,0,0),(0,1,1,1)], # top-right corner
            [(1,0,0,0),(1,0,1,1)], # bottom-left corner
            [(1,1,0,1),(1,1,1,0)]  # bottom-right corner
        ]
        for idx, island in enumerate(islands):
            base = island[0]
            configs = [
                [(base[0], base[1], base[0], base[1]+1), (base[0], base[1], base[0]+1, base[1])], # L at top-left
                [(base[0], base[1]+1, base[0], base[1]), (base[0], base[1]+1, base[0]+1, base[1]+1)], # L at top-right
                [(base[0]+1, base[1], base[0], base[1]), (base[0]+1, base[1], base[0]+1, base[1]+1)], # L at bottom-left
                [(base[0]+1, base[1]+1, base[0]+1, base[1]), (base[0]+1, base[1]+1, base[0], base[1]+1)] # L at bottom-right
            ]
            l = random.choice(configs)
            for wall in l:
                game.walls.add(EdgeWall(Position(wall[0], wall[1]), Position(wall[2], wall[3])))
        # Add one wall centered on each board edge
        mid = game.grid_size // 2
        game.walls.add(EdgeWall(Position(0, mid-1), Position(0, mid))) # top
        game.walls.add(EdgeWall(Position(game.grid_size-1, mid-1), Position(game.grid_size-1, mid))) # bottom
        game.walls.add(EdgeWall(Position(mid-1, 0), Position(mid, 0))) # left
        game.walls.add(EdgeWall(Position(mid-1, game.grid_size-1), Position(mid, game.grid_size-1))) # right

    @staticmethod
    def _random_positions(game):
        all_cells = [(i, j) for i in range(game.grid_size) for j in range(game.grid_size)]
        random.shuffle(all_cells)
        pos = [Position(*all_cells.pop()) for _ in range(4)]
        return pos[0], pos[1], pos[2], pos[3] # start, goal, friend1, friend2

    @staticmethod
    def _compute_solution_length(game, max_moves=30):
        start = game.start_pos
        goal = game.goal_pos
        friend1 = game.friend1_pos
        friend2 = game.friend2_pos
        
        # State: (position, collected_items_set, moves)
        # collected_items can contain friend1, friend2, and goal
        queue = deque()
        queue.append((start, frozenset(), 0))
        visited = set()
        
        while queue:
            pos, collected, moves = queue.popleft()
            if moves > max_moves:
                continue
                
            state = (pos, collected)
            if state in visited:
                continue
            visited.add(state)
            
            # Win condition: goal is collected
            if goal in collected:
                return moves
            
            # Try all four directions
            for direction in Direction:
                new_pos, path = game.ricochet_move(pos, direction)
                if new_pos == pos:
                    continue
                
                new_collected = set(collected)
                
                # Check what we collect during this slide
                for cell in path[1:]:  # Skip starting position
                    if cell == friend1:
                        new_collected.add(friend1)
                    elif cell == friend2:
                        new_collected.add(friend2)
                    elif cell == goal:
                        # Only allow collecting goal if both friends are collected
                        if friend1 in new_collected and friend2 in new_collected:
                            new_collected.add(goal)
                
                queue.append((new_pos, frozenset(new_collected), moves + 1))
        
        return None

    @staticmethod
    def generate_strategic_puzzle(game, difficulty='Medium', max_attempts=30) -> bool:
        difficulty_ranges = {
            'Easy': (6, 10),
            'Medium': (10, 14),
            'Hard': (14, 20)
        }
        min_moves, max_moves = difficulty_ranges.get(difficulty, (10, 14))
        for attempt in range(max_attempts):
            # Reset state at the start of each attempt
            game.visited_friends = set()
            game.move_count = 0
            game.game_won = False
            PuzzleGenerator._add_island_walls(game)
            start, goal, friend1, friend2 = PuzzleGenerator._random_positions(game)
            game.start_pos = start
            game.goal_pos = goal
            game.friend1_pos = friend1
            game.friend2_pos = friend2
            game.robot_pos = start
            game.update_grid()
            moves = PuzzleGenerator._compute_solution_length(game, max_moves=max_moves+5)
            if moves is not None and min_moves <= moves <= max_moves:
                game.optimal_moves = moves
                return True
        # fallback to original layout
        return False

    @staticmethod
    def verify_puzzle_solvable(game) -> bool:
        """
        Verify that the puzzle is solvable using BFS pathfinding.
        Returns True if there's a valid solution path.
        """
        solution_length = PuzzleGenerator._compute_solution_length(game, max_moves=50)
        return solution_length is not None
    
    @staticmethod
    def generate_guaranteed_solvable_puzzle(game, difficulty='Medium', max_attempts=10) -> bool:
        # Keep trying procedural generation until we succeed - no fallbacks!
        attempt = 0
        while True:
            attempt += 1
            if PuzzleGenerator.generate_strategic_puzzle(game, difficulty):
                if attempt > max_attempts:
                    print(f"Note: Found solution after {attempt} attempts (target was {max_attempts})")
                return True
            
            # Optional: Print progress for very long searches (but keep trying!)
            if attempt % 50 == 0:
                print(f"Still searching... attempt {attempt} for {difficulty} difficulty")
        
        # This line should never be reached since we loop forever until success
    
    @staticmethod
    def generate_original_strategic_puzzle(game, puzzle_index=None, _retry_count=0) -> bool:
        """Original hand-designed puzzles as fallback"""
        # Prevent infinite recursion
        if _retry_count > 5:
            print("Warning: Too many retries, using layout 1 regardless")
            puzzle_index = 1
        
        game.walls = set()
        game.visited_friends = set()
        game.move_count = 0
        game.game_won = False
        
        game.add_border_walls()
        
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
            }
        ]
        
        if puzzle_index is not None:
            layout = layouts[puzzle_index % len(layouts)]
            game.current_puzzle_index = puzzle_index % len(layouts)
        else:
            layout = layouts[0]  # Default to first layout
            game.current_puzzle_index = 0
        
        game.start_pos = layout['start']
        game.goal_pos = layout['goal']
        game.friend1_pos = layout['friend1']
        game.friend2_pos = layout['friend2']
        game.robot_pos = game.start_pos
        
        for wall in layout['walls']:
            game.walls.add(wall)
        
        # Calculate optimal moves for the original layout
        game.optimal_moves = PuzzleGenerator._compute_solution_length(game)
        
        # If this layout has no solution, try the next one
        if game.optimal_moves is None:
            # Recursively try next layout
            next_index = (puzzle_index + 1) if puzzle_index is not None else 1
            if next_index < len(layouts) and _retry_count < 5:
                return PuzzleGenerator.generate_original_strategic_puzzle(game, next_index, _retry_count + 1)
            else:
                # If all layouts failed, try the first solvable one we know works
                return PuzzleGenerator.generate_original_strategic_puzzle(game, 1, _retry_count + 1)  # Layout 1 is known to be solvable
        
        game.update_grid()
        return True