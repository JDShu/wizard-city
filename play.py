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
import os

import objects
from tools import load_image
from wizmap import *
from objects import *
from state import *

from collections import defaultdict

BLOCK_SIZE = Screen_Settings.BLOCK_SIZE
PANEL = Screen_Settings.PANEL
WIDTH = Screen_Settings.WIDTH
HEIGHT = Screen_Settings.HEIGHT

class Play:
    def __init__( self, screen, game_state ):
        self.game_state = game_state
        self.screen = screen
        self.group_manager = Group_Manager()
        self.font = pygame.font.Font("data/free_sans.ttf", 18)
        self.already_playing = False
        self.lives_text = None
        self.background = pygame.Surface(self.screen.get_size())
        self.s = pygame.mixer.Sound(os.path.join("data","sounds","opening.ogg"))
                
    def clear( self ):
        self.lives_text = None
        self.group_manager.empty_all()

    def new_keybuffer( self ):
        self.keybuffer = defaultdict(lambda: False)
        
    def start( self ):
        pygame.mixer.music.stop()
        self.s.play()
        F = open(self.game_state.current_map, "rb")
        self.game_state.load_wizmap(pickle.load(F))
        self.new_keybuffer()
        background_tile = objects.Tile("grass.bmp")
        for x in range(WIDTH):
            for y in range(HEIGHT):
                if  self.game_state.wizmap.map[x][y] == 1:
                    objects.Wall(self.group_manager,x,y)
                elif self.game_state.wizmap.map[x][y] == 2:
                    objects.Grunt(self.group_manager,x,y)
                elif self.game_state.wizmap.map[x][y] == 3:
                    objects.Metal(self.group_manager,x,y)
                elif self.game_state.wizmap.map[x][y] == 4:
                    objects.Base(self.group_manager,x,y)
                elif self.game_state.wizmap.map[x][y] == 5:
                    self.wizard = objects.Wizard(self.group_manager, x,y)
                    self.spawn_point = x,y
                    #self.shield = objects.Shield(self.wizard)
                    #self.shield.add( self.group_manager.allsprites2 )
                elif self.game_state.wizmap.map[x][y] == 6:
                    objects.Spawn(self.group_manager, x,y)
                self.background.blit(background_tile.image, background_tile.rect(x,y))

        self.number_spawn_spots = len(self.group_manager.spawns.sprites())                    
        self.panel, self.panel_rect = load_image("panel.bmp")
        self.panel = pygame.transform.scale(self.panel, (WIDTH*BLOCK_SIZE , PANEL*BLOCK_SIZE ))
        self.no_enemies = len(self.group_manager.enemies.sprites())
        
    def process( self ):
        self.mode = Mode.PLAY
        if not self.already_playing:
            self.start()
            self.already_playing = True
        else:
            self.set_gameplay_rects()
                
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return Mode.QUIT
            elif event.type == pygame.KEYDOWN:
                self.keybuffer[ event.key ] = True
            elif event.type == pygame.KEYUP:
                self.keybuffer[ event.key ] = False
            if event.type == pygame.USEREVENT+1:
                self.update_all()
                self.test_base_destroyed()
                self.spawn_enemies()                                                                    
                self.destroy_destructable()
                self.hit_enemy()
                self.projectile_projectile_collision()
                self.projectile_metal_collision()
                self.enemy_bumping()
                self.wizard_hit()                
                #self.manage_shield()

        self.render_text()
                    
        if not self.group_manager.enemies.sprites() and self.game_state.enemy_reserves <= 0:
            self.game_state.next_level()
            self.clear()
            self.start()
        
        self.set_draw_rects()    
                    
        return self.mode

    def update_all( self ):
        self.wizard.update(self.keybuffer)
        self.group_manager.projectiles.update()
        #self.shield.update()
        self.group_manager.enemies.update()
        self.group_manager.spawns.update()
    
    def render_text( self ):
        self.lives_text = self.font.render('Lives: ' + str(self.game_state.lives), True, (255,255, 255))
        self.lives_rect = self.lives_text.get_rect()
        self.lives_rect.midleft = BLOCK_SIZE*(1*WIDTH/4 - 2), BLOCK_SIZE*(HEIGHT + 2)
        self.score_text = self.font.render('Score: ' + str(self.game_state.score), True, (255,255, 255))
        self.score_rect = self.score_text.get_rect()
        self.score_rect.midleft = BLOCK_SIZE*(2*WIDTH/4 - 2), BLOCK_SIZE*(HEIGHT + 2)
        self.level_text = self.font.render('Level: ' + str(self.game_state.level + 1), True, (255,255, 255))
        self.level_rect = self.score_text.get_rect()
        self.level_rect.midleft = BLOCK_SIZE*(3*WIDTH/4 - 2), BLOCK_SIZE*(HEIGHT + 2)
                
    def draw( self ):
        self.screen.fill((0,0,0))
        self.screen.blit(self.background, (0,0))
        self.group_manager.allsprites.draw(self.screen)
        self.group_manager.active_group.draw(self.screen)
        if self.lives_text:
            self.screen.blit(self.panel, (0, BLOCK_SIZE*HEIGHT))
            self.screen.blit(self.lives_text, self.lives_rect)
            self.screen.blit(self.score_text, self.score_rect)
            self.screen.blit(self.level_text, self.level_rect)

    def test_base_destroyed( self ):
        L = pygame.sprite.groupcollide(self.group_manager.projectiles, self.group_manager.bases, False, False)
        for p in L:
            for b in L[p]:
                if not p.destroyed:
                    p.destroy()
                    b.kill()
                    self.already_playing = False
                    self.s.play()
                    self.mode = Mode.OVER

    def spawn_enemies( self ):
        spawn_list = self.group_manager.spawns.sprites()
        rand_int = random.randint(0,self.number_spawn_spots - 1)
        current_spawn = spawn_list[rand_int]
        if not current_spawn.spawning and self.no_enemies < self.game_state.wizmap.max_enemies and self.game_state.enemy_reserves > 0 and not pygame.sprite.spritecollideany(current_spawn, self.group_manager.enemies):
            current_spawn.start_spawn()
            self.game_state.enemy_reserves -= 1
            self.no_enemies += 1
            
    def hit_enemy( self ):
        L = pygame.sprite.groupcollide(self.group_manager.own_projectiles, self.group_manager.enemies, False, False)
        for p in L:
            for enemy in L[p]:
                if not p.destroyed:
                    enemy.dying_sound.play()
                    self.game_state.score += enemy.value
                    self.no_enemies -= 1
                    enemy.kill()
            p.destroy()
            
    def destroy_destructable( self ):
        L = pygame.sprite.groupcollide(self.group_manager.projectiles, self.group_manager.wallgroup, False, False )
        for p in L:
            for w in L[p]:
                if not p.destroyed:
                    w.kill()
            p.destroy()

    def projectile_projectile_collision( self ):
        L = pygame.sprite.groupcollide(self.group_manager.enemy_projectiles, self.group_manager.own_projectiles, False, False)
        for e in L:
            for p in L[e]:
                p.destroy()
            e.destroy()

        
    def projectile_metal_collision( self ):
        for p in pygame.sprite.groupcollide(self.group_manager.projectiles, self.group_manager.metal, False, False):
            p.destroy()

    def enemy_bumping( self ):
        for enemy in self.group_manager.enemies.sprites():
            for spawn in pygame.sprite.spritecollide(enemy, self.group_manager.spawns, False):    
                if spawn.spawning:
                    enemy.change_direction()
            if pygame.sprite.spritecollideany(enemy, self.group_manager.metal):
                enemy.change_direction()
            elif pygame.sprite.spritecollideany(enemy, self.group_manager.wallgroup):
                enemy.change_direction()
            elif pygame.sprite.collide_rect(enemy, self.wizard):
                enemy.change_direction()
                                        
            else:
                temp_list = pygame.sprite.spritecollide(enemy, self.group_manager.enemies, False)
                for other in temp_list:
                    if enemy != other:
                        enemy.change_direction()
                        break

    def wizard_hit( self ):
        for p in pygame.sprite.spritecollide(self.wizard, self.group_manager.enemy_projectiles, True):
            if not p.destroyed:
                if self.wizard.shield < 0:
                    self.game_state.lives -= 1
                    if self.game_state.lives <= 0:
                        self.wizard.kill()
                        self.already_playing = False
                        self.s.play()
                        self.mode = Mode.OVER
                    else:
                        self.wizard.dying_sound.play()
                        self.wizard.respawn(*self.spawn_point)
                        #self.shield.update()
                        #self.shield.add(self.group_manager.allsprites2)

    def manage_shield( self ):
        if self.wizard.shield < 0:
            self.shield.remove(self.group_manager.allsprites2)

    def set_gameplay_rects( self ):
        self.wizard.normal_rect()
        for e in self.group_manager.enemies.sprites():
            e.normal_rect()
        for s in self.group_manager.spawns.sprites():
            s.normal_rect()

    def set_draw_rects( self ):
        self.wizard.draw_rect()
        for s in self.group_manager.spawns.sprites():
            s.draw_rect()
        for e in self.group_manager.enemies.sprites():
            e.draw_rect()
