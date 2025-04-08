""" 
Lazor Project

This program solves the Lazor Game by:
    Parsing board configuration files (.bff format)
    Simulating laser paths through different block types (reflect, opaque, and refract)
    Finding vaid block placements that makes lasers hit all the targets
    Outputting the solution to a file 

"""

import time 
import copy
import os
from dataclasses import dataclass
from typing import List, Set, Optional

@dataclass
class Point:
    '''
    2D point class to represent a point with integer coordinates. 
    It does the following using dataclass:
        Adding 2 points.
        Comparing 2 points.
        Hashing - so that it can be used in sets/dictionaries.
        String documentation - for debugging. 
    '''
    x: int
    y: int

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))

@dataclass
class Laser:
    """
    Represents a laser beam with: 
        orgin: starting point
        direction: normalized direction vector (components are +/- 1)
    """
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction


class Block: 
    """ 
    Base class for all the block types for the game. 
    Implemnts the common functionality for block operations. 
    """
    def __init__(self, pos, fixed=False):
        """
        Initializes a block at a given position. 
        Arguments:
            pos: The position of the block on the board
            fixed: whether the block is fixed or not (fixed meaning it can't move)
        """
        self.pos = pos
        self.fixed = fixed 
    
    def interact(self, laser):
        """ 
        Defines how the block interacts with an incoming laser
        Arguments:
            laser: incoming laser 
        Returns:
            list of outgoing lasers after the interaction
        """
        raise NotImplementedError
    

class ReflectBlock (Block):
    """
    Block that reflects incoming lasers at 90 degrees.
    """
    
    def interact(self, laser):
        """
        Reflects the incoming laser beam.
        
        Arguments:
            laser: incoming laser beam
            
        Returns:
            list containing one reflected laser beam
        """
        # reflect by reversing both x and y components
        def interact(self, laser):
            return [Laser(self.pos, Point(-laser.direction.x, -laser.direction.y))]


class OpaqueBlock (Block):
    """
    Block that absorbs lasers and stops their propagation).
    """

    def interact(self, laser):
        """
        Absorb the incoming laser beam.
        
        Arguments:
            laser: incoming laser beam
            
        Returns:
            empty list, since the laser stops here
        """
        return []


class RefractBlock (Block):
    """
    Block that refracts, creating both reflected and transmitted beams.
    """

    def interact(self, laser):
        """
        Refract the incoming laser beam into two beams.
        
        Arguments:
            laser: incoming laser beam
            
        Returns:
            list containing both refracted and reflected beams
        """
        return [
            Laser(self.pos, laser.direction),
            Laser(self.pos, Point(-laser.direction.x, -laser.direction.y))
        ]

class Board:
    """Game board with optimized laser simulation"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = {}
        self.lasers = []
        self.targets = set()
        self.available_blocks = {'A': 0, 'B': 0, 'C': 0}
    
    def add_block(self, block):
        """Add block with collision check"""
        if block.pos in self.grid:
            raise ValueError(f"Position {block.pos} occupied")
        self.grid[block.pos] = block
    
    def add_laser(self, x, y, dx, dy):
        """Add normalized laser source"""
        self.lasers.append(Laser(
            Point(x, y),
            Point(1 if dx > 0 else -1, 1 if dy > 0 else -1)
        ))
    
    def simulate_lasers(self) -> Set[Point]:
        """Optimized laser path tracing with early termination"""
        visited = set()
        active_lasers = copy.deepcopy(self.lasers)
        
        while active_lasers:
            laser = active_lasers.pop()
            current = laser.origin
            direction = laser.direction
            
            while True:
                current += direction
                
                # Early termination if all targets hit
                if self.targets.issubset(visited):
                    return visited
                
                if not (0 <= current.x <= self.width and 0 <= current.y <= self.height):
                    break
                
                visited.add(current)
                
                if current in self.grid:
                    new_lasers = self.grid[current].interact(Laser(current, direction))
                    active_lasers.extend(new_lasers)
                    break
        
        return visited
    
    def is_solved(self):
        """Check solution with early exit"""
        return self.targets.issubset(self.simulate_lasers())

def solve_lazor(board: Board, timeout: int = 60) -> Optional[Board]:
    """
    Optimized solver with:
    - Laser-guided placement heuristic
    - Early partial solution checks
    - Block type deduplication
    """
    start_time = time.time()
    empty_positions = [
        Point(x, y)
        for y in range(0, board.height + 1, 2)
        for x in range(0, board.width + 1, 2)
        if Point(x, y) not in board.grid
    ]
    
    # Create block inventory
    blocks = []
    for block_type, count in board.available_blocks.items():
        blocks.extend([block_type] * count)
    
    # Laser path cache for heuristics
    laser_paths = board.simulate_lasers()
    
    def get_next_position(placed: set) -> Optional[Point]:
        """Position prioritization heuristic"""
        # 1. Try positions along current laser paths
        for pos in empty_positions:
            if pos not in placed and pos in laser_paths:
                return pos
        # 2. Fall back to any available position
        return next((p for p in empty_positions if p not in placed), None)
    
    def backtrack(remaining: List[str], placed: Dict[Point, str]) -> bool:
        if time.time() - start_time > timeout:
            return False
            
        if not remaining:
            return board.is_solved()
        
        pos = get_next_position(placed)
        if not pos:
            return False
        
        # Try each unique remaining block type
        for block_type in set(remaining):
            # Place block
            if block_type == 'A':
                block = ReflectBlock(pos)
            elif block_type == 'B':
                block = OpaqueBlock(pos)
            else:
                block = RefractBlock(pos)
                
            board.add_block(block)
            placed[pos] = block_type
            
            # Early check if this helps
            new_paths = board.simulate_lasers()
            hits_targets = any(t in new_paths for t in board.targets)
            
            if hits_targets and backtrack(
                [b for b in remaining if b != block_type],
                placed
            ):
                return True
            
            # Backtrack
            del board.grid[pos]
            del placed[pos]
        
        return False
    
    if backtrack(blocks, {}):
        return board
    return None
def parse_bff(filename: str) -> Board:
    """
    Parse a .bff file and create a Board object.
    
    Args:
        filename: Path to the .bff file
        
    Returns:
        Initialized Board object
        
    Raises:
        ValueError: If file format is invalid
    """
    with open(filename, 'r') as f:
        # Read non-comment, non-empty lines
        lines = [line.strip() for line in f if not line.startswith('#') and line.strip()]

    board = None
    grid_mode = False
    grid_lines = []

    for line in lines:
        if line == 'GRID START':
            grid_mode = True
        elif line == 'GRID STOP':
            grid_mode = False
            # Process grid data
            height = len(grid_lines)
            width = len(grid_lines[0].split()) * 2  # Each cell covers 2 units
            board = Board(width, height)

            for y, row in enumerate(grid_lines):
                cells = row.split()
                for x, cell in enumerate(cells):
                    pos = Point(x * 2, y * 2)
                    if cell == 'A':
                        board.add_block(ReflectBlock(pos, fixed=True))
                    elif cell == 'B':
                        board.add_block(OpaqueBlock(pos, fixed=True))
                    elif cell == 'C':
                        board.add_block(RefractBlock(pos, fixed=True))
        elif grid_mode:
            grid_lines.append(line)
        elif line.startswith(('A ', 'B ', 'C ')):
            # Block counts (format: "A 2" means 2 reflect blocks)
            parts = line.split()
            block_type = parts[0]
            count = int(parts[1])
            board.available_blocks[block_type] = count
        elif line.startswith('L '):
            # Laser definition (format: "L x y dx dy")
            parts = line.split()
            x, y, dx, dy = map(int, parts[1:])
            board.add_laser(x, y, dx, dy)
        elif line.startswith('P '):
            # Target point (format: "P x y")
            parts = line.split()
            x, y = map(int, parts[1:])
            board.add_target(x, y)

    if board is None:
        raise ValueError("Invalid .bff file - no grid definition found")

    return board

def save_solution(board: Board, filename: str) -> None:
    """
    Save the solution to a text file.
    
    Args:
        board: Solved board configuration
        filename: Path to output file
    """
    with open(filename, 'w') as f:
        # Create grid representation
        grid = [['.' for _ in range(board.width // 2 + 1)] 
               for _ in range(board.height // 2 + 1)]

        # Mark blocks on grid
        for pos, block in board.grid.items():
            x, y = pos.x // 2, pos.y // 2
            if isinstance(block, ReflectBlock):
                grid[y][x] = 'A' if block.fixed else 'R'
            elif isinstance(block, OpaqueBlock):
                grid[y][x] = 'B' if block.fixed else 'O'
            elif isinstance(block, RefractBlock):
                grid[y][x] = 'C' if block.fixed else 'F'

        # Write grid to file
        f.write("Solution Grid:\n")
        for row in grid:
            f.write(' '.join(row) + '\n')

        # Write laser paths
        f.write("\nLaser Paths (* = laser passes through):\n")
        laser_points = board.simulate_lasers()
        for y in range(board.height + 1):
            for x in range(board.width + 1):
                f.write('*' if Point(x, y) in laser_points else '.')
            f.write('\n')

        # Write target points
        f.write("\nTarget Points:\n")
        for target in sorted(board.targets, key=lambda p: (p.y, p.x)):
            f.write(f"({target.x}, {target.y})\n")

if __name__ == "__main__":
    input_file = "mad_1.bff"  # Same directory as script
    output_file = "solution.txt"
    
    try:
        print(f"Solving {input_file}...")
        board = parse_bff(input_file)
        solution = solve_lazor(board)
        
        if solution:
            save_solution(solution, output_file)
            print(f"Solution saved to {output_file}")
        else:
            print("No solution found")
    except FileNotFoundError:
        print(f"Error: Could not find file '{input_file}'")
        print("Make sure:")
        print("1. The file exists")
        print("2. You're running from the right directory")
        print("Current directory contents:")
        import os
        print(os.listdir('.'))