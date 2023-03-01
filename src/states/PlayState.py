"""
ISPPJ1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState.
"""
from typing import Dict, Any, List, Tuple

import pygame

from gale.input_handler import InputHandler, InputData
from gale.state_machine import BaseState
from gale.text import render_text
from gale.timer import Timer

import settings

from src.PowerUp import PowerUp
from src.Bomb4 import Bomb4
from src.Bomb5 import Bomb5


class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.level = enter_params["level"]
        self.board = enter_params["board"]
        self.score = enter_params["score"]

        # Position in the grid which we are highlighting
        self.board_highlight_i1 = -1
        self.board_highlight_j1 = -1
        self.board_highlight_i2 = -1
        self.board_highlight_j2 = -1

        self.highlighted_tile = False

        self.active = True

        self.timer = settings.LEVEL_TIME

        self.goal_score = self.level * 1.25 * 1000

        # A surface that supports alpha to highlight a selected tile
        self.tile_alpha_surface = pygame.Surface(
            (settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA
        )
        pygame.draw.rect(
            self.tile_alpha_surface,
            (255, 255, 255, 96),
            pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE),
            border_radius=7,
        )

        # A surface that supports alpha to draw behind the text.
        self.text_alpha_surface = pygame.Surface((212, 136), pygame.SRCALPHA)
        pygame.draw.rect(
            self.text_alpha_surface, (56, 56, 56, 234), pygame.Rect(0, 0, 212, 136)
        )

        def decrement_timer():
            self.timer -= 1

            # Play warning sound on timer if we get low
            if self.timer <= 5:
                settings.SOUNDS["clock"].play()

        Timer.every(1, decrement_timer)

        InputHandler.register_listener(self)

        # Avoid deadlocked board on start
        while self.__check_deadlock():
            self.board.initialize_tiles()

    def exit(self) -> None:
        InputHandler.unregister_listener(self)

    def update(self, _: float) -> None:
        if self.timer <= 0:
            Timer.clear()
            settings.SOUNDS["game-over"].play()
            self.state_machine.change("game-over", score=self.score)

        if self.score >= self.goal_score:
            Timer.clear()
            settings.SOUNDS["next-level"].play()
            self.state_machine.change("begin", level=self.level + 1, score=self.score)
        
        if self.highlighted_tile:
            tile = self.board.tiles[self.highlighted_i1][self.highlighted_j1]
            tile.update()


    def render(self, surface: pygame.Surface) -> None:
        self.board.render(surface)

        if self.highlighted_tile:
            # x = self.highlighted_j1 * settings.TILE_SIZE + self.board.x
            # y = self.highlighted_i1 * settings.TILE_SIZE + self.board.y

            x = self.board.tiles[self.highlighted_i1][self.highlighted_j1].x + self.board.x
            y = self.board.tiles[self.highlighted_i1][self.highlighted_j1].y + self.board.y
            surface.blit(self.tile_alpha_surface, (x, y))

        surface.blit(self.text_alpha_surface, (16, 16))
        render_text(
            surface,
            f"Level: {self.level}",
            settings.FONTS["medium"],
            30,
            24,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["medium"],
            30,
            52,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Goal: {self.goal_score}",
            settings.FONTS["medium"],
            30,
            80,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Timer: {self.timer}",
            settings.FONTS["medium"],
            30,
            108,
            (99, 155, 255),
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not self.active:
            return

        if input_id == "click" and input_data.pressed:
            pos_x, pos_y = input_data.position
            pos_x = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
            pos_y = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
            i = (pos_y - self.board.y) // settings.TILE_SIZE
            j = (pos_x - self.board.x) // settings.TILE_SIZE

            if 0 <= i < settings.BOARD_HEIGHT and 0 <= j <= settings.BOARD_WIDTH:
                # if we click a Powerup...
                if isinstance(self.board.tiles[i][j], PowerUp):
                    settings.SOUNDS["match"].stop()
                    settings.SOUNDS["match"].play()

                    # Let the powerup add the matches it needs
                    p_matches = self.board.tiles[i][j].take(self.board)

                    self.board.matches.append(p_matches)

                    # Add relevant score
                    self.score += len(p_matches) * 50

                     # Delete them like a regular match
                    self.board.remove_matches()

                    falling_tiles = self.board.get_falling_tiles()

                    def resolve_deadlock():
                        self.__calculate_matches(
                            [item[0] for item in falling_tiles])
                        self.active = False
                        while self.__check_deadlock():
                            self.board.initialize_tiles()
                        self.active = True

                    Timer.tween(
                        0.25,
                        falling_tiles,
                        on_finish=resolve_deadlock,
                    )

                    return


                if not self.highlighted_tile:
                    self.highlighted_i1 = i
                    self.highlighted_j1 = j
                    self.highlighted_tile = True
                    tile = self.board.tiles[self.highlighted_i1][self.highlighted_j1]
                    tile.is_dragged = True

        if input_id == "click" and self.highlighted_tile and input_data.released:
            pos_x, pos_y = input_data.position
            pos_x = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
            pos_y = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
            i = (pos_y - self.board.y) // settings.TILE_SIZE
            j = (pos_x - self.board.x) // settings.TILE_SIZE

            #return the dragged tile to its former position before the swap
            dragged_tile = self.board.tiles[self.highlighted_i1][self.highlighted_j1]
            dragged_tile.is_dragged = False
            dragged_tile.restore_position()

            # Trigger the swapping
            self.highlighted_i2 = i
            self.highlighted_j2 = j
            self.highlighted_tile = False
            self.__swap_highlighted_tiles()



    def __check_deadlock(self) -> bool:
        for row in range(settings.BOARD_HEIGHT - 1):
            # As we are traversing from top to down, left to right, it's only necessary to check the
            # tile to the right and the tile below the current one 

            for col in range(settings.BOARD_WIDTH - 1):
               
                # Check right    
                tile1 = self.board.tiles[row][col]
                tile2 = self.board.tiles[row][col + 1]
                self.__swap_tiles(tile1, tile2)
                matches = self.board.calculate_matches_for([tile1, tile2])
                self.__swap_tiles(tile1, tile2)

                if matches:
                    self.board.matches = []
                    # print(f"({tile1.i+1};{tile1.j+1}) ({tile2.i+1};{tile2.j+1})")
                    return False

                # Check down
                tile1 = self.board.tiles[row][col]
                tile2 = self.board.tiles[row + 1][col]
                self.__swap_tiles(tile1, tile2)
                matches = self.board.calculate_matches_for([tile1, tile2])
                self.__swap_tiles(tile1, tile2)

                if matches:
                    self.board.matches = []
                    # print(f"({tile1.i+1};{tile1.j+1}) ({tile2.i+1};{tile2.j+1})")
                    return False
        return True


    def __swap_tiles(self, tile1, tile2) -> None:
        (
            self.board.tiles[tile1.i][tile1.j],
            self.board.tiles[tile2.i][tile2.j],
        ) = (
            self.board.tiles[tile2.i][tile2.j],
            self.board.tiles[tile1.i][tile1.j],
        )
        tile1.i, tile1.j, tile2.i, tile2.j = (
            tile2.i,
            tile2.j,
            tile1.i,
            tile1.j,
        )

    def __swap_highlighted_tiles(self) -> None:
        di = abs(self.highlighted_i2 - self.highlighted_i1)
        dj = abs(self.highlighted_j2 - self.highlighted_j1)

        if di <= 1 and dj <= 1 and di != dj:
            self.active = False
            tile1 = self.board.tiles[self.highlighted_i1][
                self.highlighted_j1
            ]
            tile2 = self.board.tiles[self.highlighted_i2][
                self.highlighted_j2
            ]
        
            # Check beforehand if match will be generated
            self.__swap_tiles(tile1, tile2)
            mms = self.board.calculate_matches_for([tile1, tile2])
            self.board.matches = []

            # Restore the positions after the calculation
            self.__swap_tiles(tile1, tile2)

            # Only moves that create matches are allowed
            if mms is None:
                self.active = True
                return

            def arrive():
                tile1 = self.board.tiles[self.highlighted_i1][
                    self.highlighted_j1
                ]
                tile2 = self.board.tiles[self.highlighted_i2][
                    self.highlighted_j2
                ]
                self.__swap_tiles(tile1, tile2)
                self.__calculate_matches([tile1, tile2])
                # Check for deadlock after the move
                def resolve_deadlock():
                    self.active = False
                    while self.__check_deadlock():
                        self.board.initialize_tiles()
                    self.active = True

                Timer.after(1, resolve_deadlock)

            # Swap tiles
            Timer.tween(
                0.25,
                [
                    (tile1, {"x": tile2.x, "y": tile2.y}),
                    (tile2, {"x": tile1.x, "y": tile1.y}),
                ],
                on_finish=arrive,
            )

    def __calculate_matches(self, tiles: List) -> None:
        matches = self.board.calculate_matches_for(tiles)

        if matches is None:
            self.active = True
            return

        settings.SOUNDS["match"].stop()
        settings.SOUNDS["match"].play()

        powerups: List[PowerUp] = []

        for match in matches:
            # verify matches to see which ones generate powerups
            generated_by = match[-1]
            if len(match) >=5:
                #generate Bomb5
                p = Bomb5(generated_by.i, generated_by.j, generated_by.color, generated_by.variety)
                powerups.append(p)
            elif len(match) >= 4:
                p = Bomb4(generated_by.i, generated_by.j, generated_by.color, generated_by.variety)
                powerups.append(p)

            self.score += len(match) * 50

        self.board.remove_matches()       

        falling_tiles = self.board.get_falling_tiles()

        def after_fall():
            self.__calculate_matches(
                [item[0] for item in falling_tiles]
            )
            for p in powerups:
                self.board.tiles[p.i][p.j] = p

        Timer.tween(
            0.25,
            falling_tiles,
            on_finish=after_fall,
        )
