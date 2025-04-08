"""
Lazors Puzzle Solver

This program solves the Lazors puzzle game by:
1. Parsing board configuration files (.bff format)
2. Simulating laser paths through various block types
3. Finding valid block placements that make lasers hit all targets
4. Outputting the solution to a file

The implementation uses object-oriented design with proper class structures,
follows PEP8 style guidelines, and includes comprehensive comments.
"""

import time
from dataclasses import dataclass
from typing import List, Set, Optional


@dataclass
class Point:
    """
    Represents a 2D point with integer coordinates.
    Uses dataclass for automatic __init__, __repr__, etc.
    """
    x: int
    y: int

    def __add__(self, other: 'Point') -> 'Point':
        """Add two points component-wise."""
        return Point(self.x + other.x, self.y + other.y)

    def __eq__(self, other: object) -> bool:
        """Check if two points have the same coordinates."""
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        """Make Point hashable for use in sets/dictionaries."""
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"Point({self.x}, {self.y})"


@dataclass
class Laser:
    """
    Represents a laser beam with:
    - origin: Starting point
    - direction: Normalized direction vector (components are ±1)
    """
    origin: Point
    direction: Point


class Block:
    """
    Base class for all block types in the Lazors game.
    Implements common functionality for block operations.
    """

    def __init__(self, pos: Point, fixed: bool = False) -> None:
        """
        Initialize a block at given position.
        
        Args:
            pos: The position of the block on the board
            fixed: Whether the block is fixed (can't be moved)
        """
        self.pos = pos
        self.fixed = fixed

    def interact(self, laser: Laser) -> List[Laser]:
        """
        Define how the block interacts with an incoming laser.
        To be implemented by subclasses.
        
        Args:
            laser: The incoming laser beam
            
        Returns:
            List of outgoing lasers after interaction
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"{self.__class__.__name__}(pos={self.pos}, fixed={self.fixed})"


class ReflectBlock(Block):
    """Block that reflects incoming lasers at 90 degrees."""

    def interact(self, laser: Laser) -> List[Laser]:
        """
        Reflect the incoming laser beam.
        
        Args:
            laser: The incoming laser beam
            
        Returns:
            List containing one reflected laser beam
        """
        # Reflect by reversing both x and y components
        new_dir = Point(-laser.direction.x, -laser.direction.y)
        return [Laser(self.pos, new_dir)]


class OpaqueBlock(Block):
    """Block that absorbs lasers (stops their propagation)."""

    def interact(self, laser: Laser) -> List[Laser]:
        """
        Absorb the incoming laser beam.
        
        Args:
            laser: The incoming laser beam
            
        Returns:
            Empty list (laser stops here)
        """
        return []


class RefractBlock(Block):
    """Block that refracts lasers, creating both reflected and transmitted beams."""

    def interact(self, laser: Laser) -> List[Laser]:
        """
        Refract the incoming laser beam into two beams.
        
        Args:
            laser: The incoming laser beam
            
        Returns:
            List containing both refracted and reflected beams
        """
        return [
            Laser(self.pos, laser.direction),  # Transmitted beam (continues)
            Laser(self.pos, Point(-laser.direction.x, -laser.direction.y))  # Reflected beam
        ]


class Board:
    """
    Represents the game board with:
    - Grid of blocks
    - Laser sources
    - Target points
    - Available blocks to place
    """

    def __init__(self, width: int, height: int) -> None:
        """
        Initialize an empty game board.
        
        Args:
            width: Maximum x-coordinate (inclusive)
            height: Maximum y-coordinate (inclusive)
        """
        self.width = width
        self.height = height
        self.grid = {}  # Dictionary mapping positions to Block objects
        self.lasers = []  # List of Laser objects (starting points)
        self.targets = set()  # Set of Point objects that must be intersected
        self.available_blocks = {'A': 0, 'B': 0, 'C': 0}  # Available block counts

    def add_block(self, block: Block) -> None:
        """
        Add a block to the board.
        
        Args:
            block: The block to add
            
        Raises:
            ValueError: If position is already occupied
        """
        if block.pos in self.grid:
            raise ValueError(f"Position {block.pos} already occupied")
        self.grid[block.pos] = block

    def add_laser(self, x: int, y: int, dx: int, dy: int) -> None:
        """
        Add a laser source to the board.
        
        Args:
            x: Starting x-coordinate
            y: Starting y-coordinate
            dx: Initial x-direction component
            dy: Initial y-direction component
        """
        # Normalize direction to (±1, ±1)
        norm_dx = 1 if dx > 0 else -1
        norm_dy = 1 if dy > 0 else -1
        self.lasers.append(Laser(Point(x, y), Point(norm_dx, norm_dy)))

    def add_target(self, x: int, y: int) -> None:
        """
        Add a target point that must be intersected by lasers.
        
        Args:
            x: Target x-coordinate
            y: Target y-coordinate
        """
        self.targets.add(Point(x, y))

    def is_valid_position(self, pos: Point) -> bool:
        """
        Check if a position is within board bounds.
        
        Args:
            pos: Position to check
            
        Returns:
            True if position is valid, False otherwise
        """
        return 0 <= pos.x <= self.width and 0 <= pos.y <= self.height

    def simulate_lasers(self) -> Set[Point]:
        """
        Simulate all laser paths through the current board configuration.
        
        Returns:
            Set of all points that lasers pass through
        """
        visited = set()  # Points visited by lasers
        active_lasers = [copy.deepcopy(laser) for laser in self.lasers]  # Working copy

        while active_lasers:
            laser = active_lasers.pop()
            current = laser.origin
            direction = laser.direction

            while True:
                # Move laser one step in its direction
                current += direction

                # Check if laser went out of bounds
                if not self.is_valid_position(current):
                    break

                # Record this point as visited by a laser
                visited.add(current)

                # Check for block interaction
                if current in self.grid:
                    block = self.grid[current]
                    new_lasers = block.interact(Laser(current, direction))
                    active_lasers.extend(new_lasers)
                    break

        return visited

    def is_solved(self) -> bool:
        """
        Check if the current board configuration solves the puzzle.
        
        Returns:
            True if all targets are hit by lasers, False otherwise
        """
        laser_paths = self.simulate_lasers()
        return self.targets.issubset(laser_paths)


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


def solve_lazor(board: Board, timeout: int = 120) -> Optional[Board]:
    """
    Solve the Lazors puzzle using backtracking algorithm.
    
    Args:
        board: Initial board configuration
        timeout: Maximum time to spend solving (seconds)
        
    Returns:
        Solved Board if solution found, None otherwise
    """
    start_time = time.time()

    # Find all empty positions where blocks can be placed
    empty_positions = []
    for y in range(0, board.height + 1, 2):  # Step by 2 (block positions)
        for x in range(0, board.width + 1, 2):
            pos = Point(x, y)
            if pos not in board.grid:  # Only empty positions
                empty_positions.append(pos)

    # Create list of blocks to place from available counts
    blocks_to_place = []
    for block_type, count in board.available_blocks.items():
        for _ in range(count):
            if block_type == 'A':
                blocks_to_place.append(ReflectBlock(Point(0, 0)))
            elif block_type == 'B':
                blocks_to_place.append(OpaqueBlock(Point(0, 0)))
            elif block_type == 'C':
                blocks_to_place.append(RefractBlock(Point(0, 0)))

    def backtrack(index: int, used_positions: List[Point]) -> bool:
        """
        Recursive backtracking helper function.
        
        Args:
            index: Current block index to place
            used_positions: List of positions already occupied
            
        Returns:
            True if solution found from this state, False otherwise
        """
        # Check timeout
        if time.time() - start_time > timeout:
            return False

        # Base case: all blocks placed
        if index == len(blocks_to_place):
            return board.is_solved()

        # Try placing current block in all available positions
        for pos in empty_positions:
            if pos in used_positions:
                continue  # Position already used

            # Place the block
            block = blocks_to_place[index]
            block.pos = pos
            board.add_block(block)
            used_positions.append(pos)

            # Recurse to place next block
            if backtrack(index + 1, used_positions):
                return True

            # Backtrack - remove the block
            del board.grid[pos]
            used_positions.pop()

        return False

    # Start the backtracking process
    if backtrack(0, []):
        return board
    return None


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


def main() -> None:
    """Main function to execute the solver."""
    print("Lazors Puzzle Solver")
    print("-------------------\n")
    
    # Get input file
    input_file = input("Enter path to .bff file: ").strip()
    output_file = input("Enter output file path: ").strip()

    try:
        # Parse and solve
        print("\nParsing board configuration...")
        board = parse_bff(input_file)
        
        print("Solving puzzle (timeout after 2 minutes)...")
        solution = solve_lazor(board)
        
        # Output results
        if solution:
            print("\nSolution found! Saving to file...")
            save_solution(solution, output_file)
            print(f"Solution saved to {output_file}")
        else:
            print("\nNo solution found within time limit.")
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except ValueError as e:
        print(f"Error parsing file: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()