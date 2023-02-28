from typing import TypeVar, List
import pygame

import settings

from src.PowerUp import PowerUp, Tile


class Bomb4(PowerUp):
    def take(self, board: TypeVar("Board")) -> List[Tile]:
        # Add self and neighbors to the play state matches
        tiles = board.tiles
        
        match = []

        if not self in match:
            match.append(self)

        if self.i > 0:
            match.append(tiles[self.i - 1][self.j])
        if self.i < settings.BOARD_HEIGHT - 1:
            match.append(tiles[self.i + 1][self.j])
        if self.j > 0:
            match.append(tiles[self.i][self.j - 1])
        if self.j < settings.BOARD_WIDTH - 1:
            match.append(tiles[self.i][self.j + 1])

        return match
       

    def render(self, surface: pygame.Surface, offset_x: int, offset_y: int) -> None:
        super().render(surface, offset_x, offset_y)
        my_font = pygame.font.SysFont('Comic Sans MS', 20)
        text_surface = my_font.render('4', False, (0, 0, 0))
        text_width, text_height = text_surface.get_size()
        surface.blit(
            text_surface, 
            (self.x + offset_x + settings.TILE_SIZE // 2 - text_width // 2, 
             self.y + offset_y + settings.TILE_SIZE // 2 - text_height // 2))
        