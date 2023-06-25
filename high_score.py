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

from state import *
from tools import *

BLOCK_SIZE = Screen_Settings.BLOCK_SIZE
PANEL = Screen_Settings.PANEL
WIDTH = Screen_Settings.WIDTH
HEIGHT = Screen_Settings.HEIGHT

class High_Score:
    def __init__( self, screen, game_state ):
        self.game_state = game_state
        self.screen = screen
        self.font = pygame.font.Font("data/free_sans.ttf", 18)
        self.input_mode = False
        self.start()
        self.background, self.background_rect = load_image("highscore.jpg", 0)
        self.background = pygame.transform.scale(self.background, screen.get_size())
        self.background_rect = self.background.get_rect()
        
    def start( self, input_mode = False ):
        self.input_mode = input_mode
        self.player_score = self.game_state.score
        self.current_string = []
        self.screen.fill((0,0,0))
        F = open(os.path.join("misc","highscore.scr"),"rb")    
        self.highscore = pickle.load(F)

        self.keybuffer = []
        for i in range(320):
            self.keybuffer.append( False )
        
        if input_mode:
            self.highscore += [(self.player_score, None)]
            self.highscore.sort()
            self.highscore.reverse()
            self.highscore = self.highscore[0:-1]
        self.highscore.sort()
        self.highscore.reverse()
                        
    def process( self ):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return Mode.QUIT
            if self.input_mode and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.highscore[self.position] = (self.player_score, "".join(self.current_string))
                    self.highscore.sort()
                    F = open(os.path.join("misc","highscore.scr"),"wb")    
                    pickle.dump(self.highscore, F)
                    return Mode.MENU
                elif event.key == pygame.K_BACKSPACE:
                    self.current_string = self.current_string[0:-1]
                elif event.key <= 127 and len(self.current_string) < 10:
                    k = event.key
                    if event.mod and pygame.KMOD_SHIFT:
                        k -= 32
                    self.current_string.append(chr(k))
                    
            elif not self.input_mode and event.type == pygame.KEYDOWN:
                self.keybuffer[event.key] = True
                self.just_started = True
                return Mode.MENU
            elif not self.input_mode and event.type == pygame.MOUSEBUTTONUP:
                self.just_started = True
                return Mode.MENU
            elif event.type == pygame.KEYDOWN:
                self.keybuffer[event.key] = False
                
        return Mode.SCORES 

    def draw ( self ):
        
        self.screen.blit(self.background, self.background_rect)        
        y_position = BLOCK_SIZE*12
        for i, entry in enumerate(self.highscore):
            if entry[1] == None:
                entry = (entry[0], "".join(self.current_string))
                self.position = i
            score = self.font.render(str(entry[0]), True, (0,0,0))
            name = self.font.render(str(entry[1]), True, (0,0,0))
            score_rect = score.get_rect()
            name_rect = name.get_rect()
            score_rect.midright = 5*BLOCK_SIZE, y_position
            name_rect.midleft = 8*BLOCK_SIZE, y_position
            self.screen.blit(score, score_rect)
            self.screen.blit(name, name_rect)
            y_position += BLOCK_SIZE*2
