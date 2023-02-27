from typing import TypeVar
from abc import ABC, abstractmethod
import pygame

from src.Tile import Tile

class PowerUp(ABC, Tile):
    @abstractmethod
    def take(self, play_state: TypeVar('PlayState')) -> None:
        """Method executed when the powerup is taken"""
        pass