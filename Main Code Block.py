""" 
Lazor Project

This program solves the Lazor Game by:
    Parsing board configuration files (.bff format)
    Simulating laser paths through different block types (reflect, opaque, and refract)
    Finding vaid block placements that makes lasers hit all the targets
    Outputting the solution to a file 

Uses object-oriented design with class structures. 
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
        direction: normalized direction vector (components are +_ 1)
    """


class Block: 
    """ 
    Base class for all the block types for the game. 
    Implemnts the common functionality for block operations. 
    """


class ReflectBlock (Block):
    """
    Block that reflects incoming lasers at 90 degrees.
    """
    def interact(self, laser: Laser):


class OpaqueBlock (Block):
    """
    Block that absorbs lasers and stops their propagation).
    """

class RefractBlock (Block):
    """
    Block that refracts, creating both reflected and transmitted beams.
    """

class Board:
    """
    Represents the game board with:
        Grid of blocks 
        Laser sources
        Target points 
        Available blocks to place 
    """