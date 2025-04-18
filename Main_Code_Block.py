""" 
Lazor Project
Clara Kim and Nithya Parthasarathi 

This program solves the Lazor Game by:
    Parsing board configuration files (.bff format)
    Simulating laser paths through different block types (reflect, opaque, and refract)
    Finding vaid block placements that makes lasers hit all the targets
    Outputting the solution to a file in txt format

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

    def __add__(self, other: 'Point') -> 'Point':
        """ Add two points component-wise."""
        return Point(self.x + other.x, self.y + other.y)
    
    def __eq__ (self, other: object) -> bool:
        """Checks to see if the two points have the same coordinates."""
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y 
    
    def __hash__(self) -> int:
        """ Make Point hashable for use in sets/dictionaries."""
        return hash((self.x, self.y))
    
    def __repr__(self) -> str:
        """ String for debugging."""
        return f"Point({self.x}, {self.y})"

@dataclass
class Laser:
    """
    Represents a laser beam with: 
        orgin: starting point
        direction: normalized direction vector (components are +/- 1)
    """
    origin: Point
    direction: Point 


class Block: 
    """ 
    Base class for all the block types for the game. 
    Implemnts the common functionality for block operations. 
    """
    def __init__(self, pos: Point, fixed: bool = False) -> None:
        """
        Initializes a block at a given position. 
        Arguments:
            pos: The position of the block on the board
            fixed: whether the block is fixed or not (fixed meaning it can't move)
        """
        self.pos = pos
        self.fixed = fixed 
    
    def interact(self, laser: Laser) -> List[Laser]:
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
    
    def interact(self, laser: Laser) -> List[Laser]:
        """
        Reflects the incoming laser beam.
        
        Arguments:
            laser: incoming laser beam
            
        Returns:
            list containing reflected laser beam
        """
         # Where the laser came from
        prev_pos = laser.origin
        block_pos = self.pos

        dx = laser.direction.x
        dy = laser.direction.y

        # Determine which side was hit: horizontal or vertical
        if prev_pos.x == block_pos.x and prev_pos.y != block_pos.y:
            # Hit from top or bottom → flip y
            new_dir = Point(dx, -dy)
        elif prev_pos.y == block_pos.y and prev_pos.x != block_pos.x:
            # Hit from left or right → flip x
            new_dir = Point(-dx, dy)
        else:
            raise ValueError("Unexpected laser entry point — not adjacent to block.")

        return [Laser(block_pos, new_dir)]


class OpaqueBlock (Block):
    """
    Block that absorbs lasers and stops their propagation).
    """

    def interact(self, laser: Laser) -> List[Laser]:
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

    def interact(self, laser: Laser) -> List[Laser]:
        """
        Refract the incoming laser beam into two beams.
        
        Arguments:
            laser: incoming laser beam
            
        Returns:
            list containing both refracted and reflected beams
        """
        prev_pos = laser.origin
        block_pos = self.pos
        dx, dy = laser.direction.x, laser.direction.y

        # Transmitted beam (goes through unchanged)
        transmitted = Laser(block_pos, Point(dx, dy))

        # Reflected beam (one axis flipped based on entry side)
        if prev_pos.x == block_pos.x and prev_pos.y != block_pos.y:
            # Hit from top or bottom → flip y
            reflected = Laser(block_pos, Point(dx, -dy))
        elif prev_pos.y == block_pos.y and prev_pos.x != block_pos.x:
            # Hit from left or right → flip x
            reflected = Laser(block_pos, Point(-dx, dy))
        else:
            raise ValueError(f"Laser hit refract block from unexpected position. prev: {prev_pos}, block: {block_pos}")
        
        return [transmitted, reflected]

class Board:
    """
    Represents the game board with:
        Grid of blocks 
        Laser sources
        Target points 
        Available blocks to place 
    """
    def __init__(self, width: int, height: int) -> None:
        """
        Initialize an empty game board.
        
        Arguments
            width: maximum x-coordinate 
            height: maximum y-coordinate 
        """
        self.width = width
        self.height = height
        # self.grid = {}  # dictionary mapping positions to Block objects
        self.grid: dict[Point, Block] = {}
        # self.lasers = []  # list of Laser objects (starting points)
        self.lasers: List[Laser] = []
        self.targets: Set[Point] = set()  # set of Point objects that must be intersected
        self.available_blocks = {'A': 0, 'B': 0, 'C': 0}  # available block counts
        self.empty_positions: List[Point] = []

    def add_block(self, block: Block) -> None:
        """
        Add a block to the board.
        
        Arguments
            block: block to add
            
        Raises:
            ValueError: raises error if position is already occupied
        """
        if block.pos in self.grid:
            raise ValueError(f"Position {block.pos} already occupied")
        self.grid[block.pos] = block

    def add_laser(self, x: int, y: int, dx: int, dy: int) -> None:
        """
        Add a laser source to the board.
        
        Arguments:
            x: starting x-coordinate
            y: starting y-coordinate
            dx: initial x-direction component
            dy: initial y-direction component
        """
        # Nnrmalize direction to (+/- 1, +/-1)
        norm_dx = 1 if dx > 0 else -1 if dx < 0 else 0
        norm_dy = 1 if dy > 0 else -1 if dy < 0 else 0
        # norm_dx = 1 if dx > 0 else -1
        # norm_dy = 1 if dy > 0 else -1
        self.lasers.append(Laser(Point(x, y), Point(norm_dx, norm_dy)))

    def add_target(self, x: int, y: int) -> None:
        """
        Add a target point that must be intersected by lasers.
        
        Arguments:
            x: target x-coordinate
            y: target y-coordinate
        """
        self.targets.add(Point(x, y))

    def is_valid_position(self, pos: Point) -> bool:
        """
        Check if a position is within board bounds.
        
        Arguments:
            pos: position to check
            
        Returns:
            true if position is valid, otherwise false 
        """
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height
    
    def simulate_lasers(self) -> Set[Point]:
        """
        Simulate all laser paths through the current board configuration.
        
        Returns:
            set of all points that lasers pass through
        """
        visited = set()  # points visited by lasers
        visited_laser_origins = set()  # keep track of laser origins to avoid infinite loops
        active_lasers = [copy.deepcopy(laser) for laser in self.lasers]  # working copy

        while active_lasers:
            laser = active_lasers.pop()
            current = laser.origin
            direction = laser.direction

            # Add a unique identifier for this laser to prevent loops
            laser_id = (current, direction)
            if laser_id in visited_laser_origins:
                continue
            visited_laser_origins.add(laser_id)

            while True:
                # Move laser one step in its direction
                previous = current
                current = current + direction

                # Check if laser went out of bounds
                if not self.is_valid_position(current):
                    break

                # Record this point as visited by a laser
                visited.add(current)

                # Check for block interaction
                if current in self.grid:
                    block = self.grid[current]
                    new_lasers = block.interact(Laser(previous, direction))
                    active_lasers.extend(new_lasers)
                    break

        return visited
    
    def is_solved(self) -> bool:
        """
        Check if the current board configuration solves the puzzle.
        
        Returns:
            true if all targets are hit by lasers, otherwise false 
        """
        laser_paths = self.simulate_lasers()
        return self.targets.issubset(laser_paths)
    


# def parse_bff(filename):
def parse_bff(filename: str) -> tuple[List[List[str]], Board]:
    '''
    Parse a .bff file to create a Board object.

    Arguments:
        filename: path to the .bff file

    Returns:
        Board object initialised with the parsed data.
    '''
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines()]

    lines = [line for line in lines if line and not line.startswith('#')]  # remove comments and empty lines

    grid = []
    available_blocks = {'A': 0, 'B': 0, 'C': 0}
    lasers = []
    targets = []
    read_grid = False

    # Iterate through lines to parse the grid and other elements
    for line in lines:
        if line == 'GRID START':
            read_grid = True
            continue
        elif line == 'GRID STOP':
            read_grid = False
            continue

        if read_grid:
            grid.append(line.split())  # process grid lines
        else:
            parts = line.split()  # process other lines
            if not parts:
                continue

            instruction = parts[0]
            if instruction in ('A', 'B', 'C'):
                available_blocks[instruction] = int(parts[1])

            elif instruction == 'L':  # Laser in format L x y dx dy
                x, y, norm_dx, norm_dy = map(int, parts[1:5])
                lasers.append((x, y, norm_dx, norm_dy))

            elif instruction == 'P':  # Target in format P x y
                x, y = map(int, parts[1:3])
                targets.append((x, y))
    

    print(f"Grid demensions: {len(grid)}x{len(grid[0])}")
    print(f"Available blocks: {available_blocks}")
    print(f"Laser count: {len(lasers)}")
    print(f"Target count: {len(targets)}")

    # Evaulate the board dimensions
    height = len(grid)
    # width = len(grid[0])
    width = len(grid[0]) if height > 0 else 0
    
    # Create the board
    board = Board(width * 2, height *2)  # Muliply by 2 to account for the fine grid

    # Add fixed blocks to the board
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            pos = Point(x * 2, y * 2)
            if cell == 'o':  # Empty position where blocks can be placed
                board.empty_positions.append(pos)
            elif cell == 'A':
                board.add_block(ReflectBlock(pos, fixed=True))
            elif cell == 'B':
                board.add_block(OpaqueBlock(pos, fixed=True))
            elif cell == 'C':
                board.add_block(RefractBlock(pos, fixed=True))

    
    # Add available blocks to the board
    board.available_blocks = available_blocks

    # Add lasers to the board
    for x, y, norm_dx, norm_dy in lasers:
        board.add_laser(x, y, norm_dx, norm_dy)

    # Add targets to the board
    for x, y in targets:
        board.add_target(x, y)
    
    print(f"Empty positions: {board.empty_positions}")
    print(f"Fixed blocks: {len(board.grid)}")

    return grid, board


# def solver(board):
def solver(board: Board) -> Optional[List[Block]]:
    """
    Solve the Lazor game by finding a valid block placement.
    
    Arguments:
        board: Board object to solve
        
    Returns:
        List of blocks that make the board solvable, or None if no solution is found.
    """
    
    # Get all positions marked with 'o' (empty blocks)
    # empty_blocks = board.empty_positions.copy()
    #for pos in board.grid:
    #    if board.grid[pos] is None:
    #        empty_blocks.append(pos)

    # Get the available blocks to place on the board
    # Converte 'A', 2 into 'A', 'A' etc.
    blocks_placable = []
    for block_type, count in board.available_blocks.items():
        blocks_placable.extend([block_type] * count)

    solution = []  # List to store the solution blocks

    # Backtracking function to check all combinations of blocks
    def try_place(index):
        """
        Recursive function for block placements.

        Arguments:
            index: current index in the blocks list

        Returns:
            True if a soludtion is found, otherwise False.
        """
        if index >= len(blocks_placable):
            # Check if the board is solved with the current configuration
            return board.is_solved()
        
        # Try each empty position for the current block
        for pos in board.empty_positions:
            # Skip if the position is already occupied
            if pos in board.grid:
                continue

            current_type = blocks_placable[index]  # Get the current block type
            if current_type == 'A':
                block = ReflectBlock(pos)  # Create a ReflectBlock
            elif current_type == 'B':
                block = OpaqueBlock(pos)  # Create an OpaqueBlock
            elif current_type == 'C':
                block = RefractBlock(pos)  # Create a RefractBlock
            

            # Add the block to the board
            board.add_block(block)
            solution.append(block)


            # Check if the board is valid with the current block placement
            if try_place(index + 1):
                return True

            # Remove the block if no solution
            del board.grid[pos]
            solution.pop()

        return False

    if try_place(0):
        return solution  # Return the solution blocks if found
    return None


def save_solution(board: Board, grid: List[List[str]], filename: str) -> None:
    """
    Save the solution into a file with the original grid format.
    'o' is replaced with the block type used in the solution.

    Arguments:
        board: Board object with the solution
        grid: original grid layout in bff file
        filename: path to save the solution file as {original}_solution.bff
    """
    with open(filename, 'w') as f:
        f.write("GRID START\n")

        # Start going through each row of the grid
        for y, row in enumerate(grid):
            solution_row = []  # To store the row of the solution

            # Go through each cell in the row
            for x, cell in enumerate(row):
                pos = Point(x * 2, y * 2)  # Get the position in the fine grid


                if cell == 'x':
                    solution_row.append('x')
                elif cell == 'o':
                    if pos in board.grid:
                        block = board.grid[pos]  # Get the block at the position
                        
                        # Start placing the block type in the solution row
                        if isinstance(block, ReflectBlock):
                            solution_row.append('A')
                        elif isinstance(block, OpaqueBlock):
                            solution_row.append('B')
                        elif isinstance(block, RefractBlock):
                            solution_row.append('C')
                        
                    else:
                        solution_row.append('o')  # If no functional block is placed, keep it as 'o'
                else:
                    solution_row.append(cell)  #  Keep the original block type if no change occured
            
            #Write the solution row to the file with space between each cell
            f.write(' '.join(solution_row) + '\n')

        # Finish the file with GRID STOP
        f.write("GRID STOP\n")


if __name__ == '__main__':
    input_file = 'mad_4.bff'
    output_file = 'mad_4_solution.txt'

    time_start = time.time()  # Start timer

    grid, board = parse_bff(input_file)
    solution = solver(board)
    
    # Debug information
    print(f"Board dimensions: {board.width}x{board.height}")
    print(f"Number of empty positions: {len(board.empty_positions)}")
    print(f"Available blocks: {board.available_blocks}")
    print(f"Number of lasers: {len(board.lasers)}")
    print(f"Number of targets: {len(board.targets)}")

    time_final = time.time()  # End timer
    time_taken = time_final - time_start

    if solution:
        save_solution(board, grid, output_file)
        print(f"Solution is saved to {output_file}.")
    else:
        print("No solution.")

    print(f"{time_taken:.3f} seconds to solve.")