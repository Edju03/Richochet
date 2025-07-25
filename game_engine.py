from typing import Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

class CellType(Enum):
    EMPTY = '.'
    START = 'S'
    GOAL = 'G'
    FRIEND1 = '1'
    FRIEND2 = '2'
    ROBOT = 'R'

class Direction(Enum):
    NORTH = (-1, 0)
    SOUTH = (1, 0)
    EAST = (0, 1)
    WEST = (0, -1)

@dataclass
class Position:
    row: int
    col: int
    
    def __hash__(self):
        return hash((self.row, self.col))
    
    def __eq__(self, other):
        return self.row == other.row and self.col == other.col
    
    def __lt__(self, other):
        return (self.row, self.col) < (other.row, other.col)
    
    def __add__(self, direction: Direction):
        dr, dc = direction.value
        return Position(self.row + dr, self.col + dc)

@dataclass
class EdgeWall:
    from_pos: Position
    to_pos: Position
    
    def __hash__(self):
        pos1, pos2 = sorted([self.from_pos, self.to_pos], key=lambda p: (p.row, p.col))
        return hash((pos1, pos2))
    
    def __eq__(self, other):
        pos1, pos2 = sorted([self.from_pos, self.to_pos], key=lambda p: (p.row, p.col))
        other_pos1, other_pos2 = sorted([other.from_pos, other.to_pos], key=lambda p: (p.row, p.col))
        return pos1 == other_pos1 and pos2 == other_pos2

class RicochetGame:
    def __init__(self, grid_size: int = 5):
        self.grid_size = grid_size
        self.grid = [[CellType.EMPTY for _ in range(grid_size)] for _ in range(grid_size)]
        self.walls = set()
        self.start_pos = None
        self.goal_pos = None
        self.friend1_pos = None
        self.friend2_pos = None
        self.robot_pos = None
        self.visited_friends = set()
        self.move_count = 0
        self.game_won = False
        self.puzzle_names = [
            "The Crossroads",
            "Crystal Maze", 
            "Diagonal Challenge",
            "Spiral Gateway"
        ]
        self.current_puzzle_index = 0
        self.path_positions: List[Position] = []
        self.optimal_moves: Optional[int] = None
        
    def add_border_walls(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                pos = Position(i, j)
                
                if i == 0:
                    outside_pos = Position(i - 1, j)
                    self.walls.add(EdgeWall(pos, outside_pos))
                if i == self.grid_size - 1:
                    outside_pos = Position(i + 1, j)
                    self.walls.add(EdgeWall(pos, outside_pos))
                if j == 0:
                    outside_pos = Position(i, j - 1)
                    self.walls.add(EdgeWall(pos, outside_pos))
                if j == self.grid_size - 1:
                    outside_pos = Position(i, j + 1)
                    self.walls.add(EdgeWall(pos, outside_pos))
    
    def is_wall_between(self, from_pos: Position, to_pos: Position) -> bool:
        wall = EdgeWall(from_pos, to_pos)
        return wall in self.walls
    
    def is_valid_position(self, pos: Position) -> bool:
        return 0 <= pos.row < self.grid_size and 0 <= pos.col < self.grid_size
    
    def ricochet_move(self, start_pos: Position, direction: Direction) -> Tuple[Optional[Position], List[Position]]:
        """Returns (final_position, path_taken)"""
        current_pos = start_pos
        path = [start_pos]
        
        while True:
            next_pos = current_pos + direction
            
            if not self.is_valid_position(next_pos):
                return current_pos, path
            
            if self.is_wall_between(current_pos, next_pos):
                return current_pos, path
            
            current_pos = next_pos
            path.append(current_pos)
    
    def move_robot(self, direction: Direction) -> bool:
        if self.game_won:
            return False
            
        new_pos, path = self.ricochet_move(self.robot_pos, direction)
        
        if new_pos == self.robot_pos:
            return False
        
        old_pos = self.robot_pos
        self.robot_pos = new_pos
        self.move_count += 1
        
        # Check if robot passed through any friends during the slide
        friend_visited = False
        for pos in path[1:]:  # Skip starting position
            if pos == self.friend1_pos and self.friend1_pos not in self.visited_friends:
                self.visited_friends.add(self.friend1_pos)
                friend_visited = True
            elif pos == self.friend2_pos and self.friend2_pos not in self.visited_friends:
                self.visited_friends.add(self.friend2_pos)
                friend_visited = True
        
        # Check win condition - goal can be reached by passing through OR stopping on it
        for pos in path[1:]:  # Skip starting position
            if pos == self.goal_pos and len(self.visited_friends) == 2:
                self.game_won = True
                break
        
        self.update_grid()
        return True, old_pos, new_pos, friend_visited
    
    def get_current_puzzle_name(self):
        return self.puzzle_names[self.current_puzzle_index]
    
    def update_grid(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                self.grid[i][j] = CellType.EMPTY
        if self.start_pos and self.move_count == 0:
            self.grid[self.start_pos.row][self.start_pos.col] = CellType.START
        if self.goal_pos:
            self.grid[self.goal_pos.row][self.goal_pos.col] = CellType.GOAL
        if self.friend1_pos:
            self.grid[self.friend1_pos.row][self.friend1_pos.col] = CellType.FRIEND1
        if self.friend2_pos:
            self.grid[self.friend2_pos.row][self.friend2_pos.col] = CellType.FRIEND2
        if self.robot_pos:
            self.grid[self.robot_pos.row][self.robot_pos.col] = CellType.ROBOT