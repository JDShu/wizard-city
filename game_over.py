'''
 * This file is part of Wizard City
 * Copyright (C) 2010 Hans Lo
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
'''

import pygame
import objects
from state import *

BLOCK_SIZE = Screen_Settings.BLOCK_SIZE
PANEL = Screen_Settings.PANEL
WIDTH = Screen_Settings.WIDTH
HEIGHT = Screen_Settings.HEIGHT

class Game_Over:
    def __init__( self, screen, play_state, game_state ):
        self.game_state = game_state
        self.screen = screen
        self.play_state = play_state
        self.text = pygame.sprite.RenderPlain()
        self.text.add(objects.Game_Over(BLOCK_SIZE*WIDTH/2, 5*BLOCK_SIZE))

    def reset( self ):
        self.text.empty()
        self.text.add(objects.Game_Over(BLOCK_SIZE*WIDTH/2, 5*BLOCK_SIZE))
    
    def process( self ):
        mode = Mode.OVER
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return Mode.QUIT
            if event.type == pygame.USEREVENT+1:
                self.text.update()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_x and not pygame.mixer.get_busy():
                self.reset()
                self.game_state.high_score.start(True)
                if self.game_state.score > self.game_state.lowest_score:
                    mode = Mode.SCORES
                else:
                    pygame.mixer.music.play(-1)
                    mode = Mode.MENU
                self.play_state.clear()
                
        return mode
        
    def draw( self ):
        self.screen.fill((0,0,0))
        self.play_state.draw()
        self.text.draw(self.screen)
