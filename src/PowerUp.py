from typing import TypeVar, List
from abc import ABC, abstractmethod
import pygame

from src.Tile import Tile

class PowerUp(ABC, Tile):
    @abstractmethod
    def take(self, board: TypeVar('Board')) -> List[Tile]:
        """Method executed when the powerup is taken"""
        pass