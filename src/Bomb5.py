from typing import TypeVar, List
import pygame

import settings

from src.PowerUp import PowerUp, Tile


class Bomb5(PowerUp):
    def take(self, board: TypeVar("Board")) -> List[Tile]:
        # Add self and neighbors to the play state matches
        tiles = board.tiles
        
        color = self.color

        match = []

        for row in tiles:
            match += [tile for tile in row if tile.color == color]

        return match
       

    def render(self, surface: pygame.Surface, offset_x: int, offset_y: int) -> None:
        super().render(surface, offset_x, offset_y)
        my_font = pygame.font.SysFont('Comic Sans MS', 20)
        text_surface = my_font.render('5', False, (0, 0, 0))
        text_width, text_height = text_surface.get_size()
        surface.blit(
            text_surface, 
            (self.x + offset_x + settings.TILE_SIZE // 2 - text_width // 2, 
             self.y + offset_y + settings.TILE_SIZE // 2 - text_height // 2))
        