# Lazor Project Main Code 

import time 
from dataclasses import dataclass
from typing import List, Set, Optional

class Point:
    '''
    Represents a 2D point wit integer coordinates.
    Uses dataclass for automatic __init__, __repr__, etc.
    '''
    x: int
    y: int

    def __add__(self, other: 'Point') -> 'Point':


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