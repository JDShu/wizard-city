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

class Credits:
    def __init__( self, screen, game_state ):
        self.game_state = game_state
        self.screen = screen
        self.background, self.background_rect = load_image("credits.jpg", 0)
        self.background = pygame.transform.scale(self.background, screen.get_size())
        self.background_rect = self.background.get_rect()
                        
    def process( self ):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return Mode.QUIT
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONUP:
                return Mode.MENU
                
        return Mode.CREDITS

    def draw ( self ):
        self.screen.blit(self.background, self.background_rect)        
