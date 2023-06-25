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
from tools import load_image

import objects
from state import *
from tools import *

BLOCK_SIZE = Screen_Settings.BLOCK_SIZE
PANEL = Screen_Settings.PANEL
WIDTH = Screen_Settings.WIDTH
HEIGHT = Screen_Settings.HEIGHT

class Button(pygame.sprite.Sprite):
    def __init__( self, main, hover, button_type, x = 100, y = 100 ):
        pygame.sprite.Sprite.__init__( self )
        self.main, self.rect = load_image(main, 0)
        self.hover,z = load_image(hover, 0)
        self.rect.center = x, y
        self.image = self.main
        self.hovering = False
        self.type = button_type
        
    def update( self ):
        if self.rect.collidepoint( pygame.mouse.get_pos() ):
            self.image = self.hover
            self.hovering = True
        else:
            self.image = self.main
            self.hovering = False

    def clicked( self ):
        return self.returned

class Menu:
    def __init__( self, screen, game_state ):
        self.game_state = game_state
        self.screen = screen
        self.buttons = pygame.sprite.RenderPlain()
        self.allsprites = pygame.sprite.RenderPlain()
        self.new = Button( "new_game.jpg", "new_game_hover.jpg", "new", BLOCK_SIZE*WIDTH/6, BLOCK_SIZE*2/3*HEIGHT)
        self.high_score = Button( "high_score.jpg","score_hover.jpg","score", BLOCK_SIZE*WIDTH/6, BLOCK_SIZE*2/3*HEIGHT + 30)
        self.credits = Button( "b_credits.jpg", "b_h_credits.jpg", "credits", BLOCK_SIZE*WIDTH/6, BLOCK_SIZE*2/3*HEIGHT + 60)
        self.quit = Button( "quit.jpg", "quit_hover.jpg", "quit", BLOCK_SIZE*WIDTH/6, BLOCK_SIZE*2/3*HEIGHT + 90)
        self.buttons.add(self.new, self.quit, self.credits, self.high_score)
        self.allsprites.add(self.new, self.quit, self.credits, self.high_score)
        self.selected_button = None
        self.background, self.background_rect = load_image("wizard_menu.jpg", 0)
        self.background = pygame.transform.scale(self.background, screen.get_size())
        self.background_rect = self.background.get_rect()
        pygame.mixer.music.play(-1)
                
    def process( self ):
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return Mode.QUIT
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for b in self.buttons:
                    if b.hovering:
                        self.selected_button = b
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.selected_button and self.selected_button.hovering:
                    if self.selected_button.type == "new":
                        self.game_state.new_session()
                        return Mode.PLAY
                    elif self.selected_button.type == "quit":
                        return Mode.QUIT
                    elif self.selected_button.type == "score":
                        self.game_state.high_score.start()
                        return Mode.SCORES
                    elif self.selected_button.type == "credits":
                        return Mode.CREDITS
                else:
                    self.selected_button = None
                    
        self.buttons.update()
        return Mode.MENU
        
    def draw( self ):
        self.screen.blit(self.background, self.background_rect)
        self.allsprites.draw(self.screen)        
