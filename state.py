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

import os
import pygame
import pickle

import objects
import mapmaker

class Screen_Settings:
    BLOCK_SIZE = 18
    PANEL = 5
    WIDTH = 32
    HEIGHT = 32


class Mode:
    MENU, PLAY, OVER, SCORES, CREDITS, QUIT = range(6)
    
class State:
    def __init__(self, campaign, screen):
        import menu
        import play
        import game_over
        import high_score
        import game_credits


        self.screen = screen
        
        self.mode = Mode.MENU
        self.level = 0
        F = open(campaign, "rb")
        self.campaign = pickle.load(F)
        self.new_session()

        self.play = play.Play(self.screen, self)
        self.menu = menu.Menu(self.screen, self)
        self.game_over = game_over.Game_Over(self.screen, self.play, self)
        self.high_score = high_score.High_Score(self.screen, self)
        self.credits = game_credits.Credits(self.screen, self)

        F = open(os.path.join("misc","highscore.scr"),"rb")
        self.highscore = pickle.load(F)
        self.highscore.sort()
        self.lowest_score = self.highscore[0][0]
        
    def load_wizmap( self, wizmap ):
        self.wizmap = wizmap
        self.enemy_reserves = wizmap.enemy_reserves
        
    def next_level( self ):
        self.level += 1
        if self.level >= len(self.campaign):
            self.level = 0
        self.current_map = os.path.join("maps", self.campaign[self.level])

    def new_session( self ):
        self.lives = 3
        self.score = 0
        self.level = 0
        self.current_map = os.path.join("maps", self.campaign[self.level])

class Group_Manager:
    def __init__( self ):
        self.allsprites = pygame.sprite.RenderPlain()
        self.allsprites2 = pygame.sprite.RenderPlain()
        self.active_group = pygame.sprite.RenderPlain()
        self.wallgroup = pygame.sprite.RenderPlain()
        self.projectiles = pygame.sprite.RenderPlain()
        self.own_projectiles = pygame.sprite.RenderPlain()
        self.enemy_projectiles = pygame.sprite.RenderPlain()
        self.enemies = pygame.sprite.RenderPlain()
        self.metal = pygame.sprite.RenderPlain()
        self.bumpers = pygame.sprite.RenderPlain()
        self.bases = pygame.sprite.RenderPlain()
        self.spawns = pygame.sprite.RenderPlain()

    def empty_all( self ):
        self.allsprites.empty()
        self.allsprites2.empty()
        self.wallgroup.empty()
        self.bumpers.empty()
        self.metal.empty()
        self.enemies.empty()
        self.bases.empty()
        self.spawns.empty()
        self.active_group.empty()
        self.enemy_projectiles.empty()
        self.projectiles.empty()
        self.own_projectiles.empty()
