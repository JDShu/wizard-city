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
import pickle

import objects
import mapmaker
import menu
import play
import game_over
import high_score
from objects import *
from wizmap import *
from state import *


BLOCK_SIZE = Screen_Settings.BLOCK_SIZE
PANEL = Screen_Settings.PANEL
WIDTH = Screen_Settings.WIDTH
HEIGHT = Screen_Settings.HEIGHT

class Main_Loop:
    def __init__( self ):
        pygame.init()
        pygame.display.set_caption('Wizard City')
        I = pygame.image.load(os.path.join("data","metal.bmp"))
        pygame.display.set_icon(I)
        pygame.mixer.init()
        pygame.mixer.music.load(os.path.join("data","sounds","mage_garden.ogg"))
        self.size = width, height = BLOCK_SIZE*WIDTH, BLOCK_SIZE*(HEIGHT + PANEL)
        self.WIDTH, self.HEIGHT = WIDTH, HEIGHT
        self.black = 0,0,0
        self.screen =  pygame.display.set_mode((width, height))
        pygame.time.set_timer(pygame.USEREVENT+1, 20)
        self.game_state = State("./campaign/test.cpn", self.screen)        
        
    def process_game( self ):
        if self.game_state.mode == Mode.QUIT:
            return False
        elif self.game_state.mode == Mode.PLAY:
            self.game_state.mode = self.game_state.play.process()
        elif self.game_state.mode == Mode.SCORES:
            self.game_state.mode = self.game_state.high_score.process()
        elif self.game_state.mode == Mode.MENU:
            self.game_state.mode = self.game_state.menu.process()
        elif self.game_state.mode == Mode.CREDITS:
            self.game_state.mode = self.game_state.credits.process()
        else:
            self.game_state.mode = self.game_state.game_over.process()
        return True
    
    def draw( self ):
        if self.game_state.mode == Mode.PLAY:
            self.game_state.play.draw()
        elif self.game_state.mode == Mode.MENU:
            self.game_state.menu.draw()
        elif self.game_state.mode == Mode.SCORES:
            self.game_state.high_score.draw()
        elif self.game_state.mode == Mode.CREDITS:
            self.game_state.credits.draw()
        elif self.game_state.mode == Mode.OVER:
            self.game_state.game_over.draw()
        pygame.display.flip()
