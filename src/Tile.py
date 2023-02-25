"""
ISPPJ1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Tile.
"""
import pygame

import settings


class Tile:
    def __init__(self, i: int, j: int, color: int, variety: int) -> None:
        self.i = i
        self.j = j
        self.x = self.j * settings.TILE_SIZE
        self.y = self.i * settings.TILE_SIZE
        self.color = color
        self.variety = variety
        self.alpha_surface = pygame.Surface(
            (settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA
        )
        self.is_dragged = False

    def update(self):
        if not self.is_dragged:
            return
        
        board_x = settings.VIRTUAL_WIDTH - 272
        board_y = 16

        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_x = mouse_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH - board_x
        mouse_y = mouse_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT - board_y

        if 0 <= mouse_x - settings.TILE_SIZE / 2 < 256 - settings.TILE_SIZE:
            self.x = mouse_x - settings.TILE_SIZE / 2
    
        if 0 <= mouse_y - settings.TILE_SIZE / 2 < 256 - settings.TILE_SIZE:
            self.y = mouse_y - settings.TILE_SIZE / 2


    def render(self, surface: pygame.Surface, offset_x: int, offset_y: int) -> None:
        self.alpha_surface.blit(
            settings.TEXTURES["tiles"],
            (0, 0),
            settings.FRAMES["tiles"][self.color][self.variety],
        )
        pygame.draw.rect(
            self.alpha_surface,
            (34, 32, 52, 200),
            pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE),
            border_radius=7,
        )
        surface.blit(self.alpha_surface, (self.x + 2 + offset_x, self.y + 2 + offset_y))
        surface.blit(
            settings.TEXTURES["tiles"],
            (self.x + offset_x, self.y + offset_y),
            settings.FRAMES["tiles"][self.color][self.variety],
        )

    def restore_position(self):
        self.x = self.j * settings.TILE_SIZE
        self.y = self.i * settings.TILE_SIZE
