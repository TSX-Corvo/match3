from typing import TypeVar
import pygame

import settings

from src.PowerUp import PowerUp


class Bomb4(PowerUp):
    def take(self, play_state: TypeVar("PlayState")) -> None:
        print("Took Bomb4!")

    def render(self, surface: pygame.Surface, offset_x: int, offset_y: int) -> None:
        super().render(surface, offset_x, offset_y)
        my_font = pygame.font.SysFont('Comic Sans MS', 20)
        text_surface = my_font.render('4', False, (0, 0, 0))
        text_width, text_height = text_surface.get_size()
        surface.blit(
            text_surface, 
            (self.x + offset_x + settings.TILE_SIZE // 2 - text_width // 2, 
             self.y + offset_y + settings.TILE_SIZE // 2 - text_height // 2))
        