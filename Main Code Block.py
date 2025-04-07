""" 
Lazor Project

This program solves the Lazor Game by:
    Parsing board configuration files (.bff format)
    Simulating laser paths through different block types (reflect, opaque, and refract)
    Finding vaid block placements that makes lasers hit all the targets
    Outputting the solution to a file 

"""

import time 
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
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"{self.__class__.__name__}(pos={self.pos}, fixed={self.fixed})"
    



class ReflectBlock (Block):
    """
    Block that reflects incoming lasers at 90 degrees.
    """
    
    def interact(self, laser: Laser):
        """
        Reflects the incoming laser beam.
        
        Arguments:
            laser: incoming laser beam
            
        Returns:
            list containing one reflected laser beam
        """
        # reflect by reversing both x and y components
        new_dir = Point(-laser.direction.x, -laser.direction.y)
        return [Laser(self.pos, new_dir)]


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
        return [
            Laser(self.pos, laser.direction),  # Transmitted beam (continues)
            Laser(self.pos, Point(-laser.direction.x, -laser.direction.y))  # Reflected beam
        ]

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
        self.grid = {}  # dictionary mapping positions to Block objects
        self.lasers = []  # list of Laser objects (starting points)
        self.targets = set()  # set of Point objects that must be intersected
        self.available_blocks = {'A': 0, 'B': 0, 'C': 0}  # available block counts

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
        norm_dx = 1 if dx > 0 else -1
        norm_dy = 1 if dy > 0 else -1
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
        return 0 <= pos.x <= self.width and 0 <= pos.y <= self.height
    
    def simulate_lasers(self) -> Set[Point]:
        """
        Simulate all laser paths through the current board configuration.
        
        Returns:
            set of all points that lasers pass through
        """
        visited = set()  # points visited by lasers
        active_lasers = [copy.deepcopy(laser) for laser in self.lasers]  # working copy

        while active_lasers:
            laser = active_lasers.pop()
            current = laser.origin
            direction = laser.direction

            while True:
                # move laser one step in its direction
                current += direction

                # check if laser went out of bounds
                if not self.is_valid_position(current):
                    break

                # record this point as visited by a laser
                visited.add(current)

                # check for block interaction
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
            true if all targets are hit by lasers, otherwise false 
        """
        laser_paths = self.simulate_lasers()
        return self.targets.issubset(laser_paths)