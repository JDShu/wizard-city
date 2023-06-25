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
from pygame.locals import *
import random

from state import *
from tools import *
import mapmaker

BLOCK_SIZE = Screen_Settings.BLOCK_SIZE
PANEL = Screen_Settings.PANEL
WIDTH = Screen_Settings.WIDTH
HEIGHT = Screen_Settings.HEIGHT

class Spritesheet:
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert()

    def imgat(self, rect, size, colorkey = -1):
        rect = Rect(rect)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, RLEACCEL)
        image = pygame.transform.scale(image, size)
        return image

    def imgsat(self, x, y, size, colorkey = -1):
        imgs = []
        temp = self.calc_rects(x,y)
        for rect in temp:
            imgs.append(self.imgat(rect, size, colorkey))
        return imgs
    
    def calc_rects( self, x, y ):
        rects = []
        rect = self.sheet.get_rect()
        w_increment, h_increment = rect.w/x, rect.h/y
        for down in range(y):
            for across in range(x):
                rects.append((across * w_increment, down * h_increment, w_increment, h_increment))
        return rects

class Animated_Sprite( pygame.sprite.Sprite ):
    def __init__ ( self, filename, x_sprites, y_sprites, size, rate, x=0,y=0):
        pygame.sprite.Sprite.__init__( self )
        temp = Spritesheet(os.path.join("data", filename))
        self.current = temp.imgsat(x_sprites,y_sprites,(int(size[0]*BLOCK_SIZE), int(size[1]*BLOCK_SIZE)))
        self.image = self.current[0]
        self.frame = 0
        self.rate_max = rate
        self.rate = self.rate_max
        self.loop_length = x_sprites
        self.x, self.y = x,y
        x1,y1 = mapmaker.calc_coord(x,y,WIDTH,HEIGHT,BLOCK_SIZE*WIDTH,BLOCK_SIZE*HEIGHT)
        self.rect = Rect(x1,y1,size[0]*BLOCK_SIZE - 2, size[0]*BLOCK_SIZE - 2)

    def update ( self ):
        self.image = self.current[self.frame]
        if self.rate < 0:
            self.rate = self.rate_max
            self.frame += 1
            if self.frame > self.loop_length - 1:
                self.frame = 0
        else:
            self.rate -= 1
            
    def draw_rect( self, top, left ):
        self.rect.top -= top
        self.rect.left -= left

    def normal_rect( self, top, left ):
        self.rect.top += top
        self.rect.left += left
    
class Tile:
    def __init__ ( self, filename, colorkey = None ):
        self.image = pygame.image.load(os.path.join("data",filename)).convert()
        self.image = pygame.transform.scale(self.image, (BLOCK_SIZE , BLOCK_SIZE ))
        
    def rect( self, x, y ):
        return mapmaker.calc_coord(x,y,WIDTH,HEIGHT,BLOCK_SIZE*WIDTH,BLOCK_SIZE*HEIGHT)
    

class Barrier (pygame.sprite.Sprite):
    def __init__( self, filename, size, x, y, colorkey = 0):
        pygame.sprite.Sprite.__init__( self )
        self.image, self.rect = load_image( filename, colorkey )
        self.image = pygame.transform.scale(self.image, (size*BLOCK_SIZE - 1, size*BLOCK_SIZE - 1))
        self.rect = self.image.get_rect()
        self.rect.topleft = mapmaker.calc_coord(x,y,WIDTH,HEIGHT,BLOCK_SIZE*WIDTH,BLOCK_SIZE*HEIGHT)
        
class Wall( Barrier ):
    def __init__( self, gm, x = 0, y = 0 ):
        Barrier.__init__( self, "wall.bmp", 1,x,y)
        self.add(gm.allsprites, gm.wallgroup, gm.bumpers)
        
class Base( Barrier ):
    def __init__( self, gm, x = 0, y = 0 ):
        Barrier.__init__( self, "base.bmp", 2,x,y)
        self.add(gm.allsprites, gm.bases, gm.bumpers)
        
class Metal( Barrier ):
    def __init__( self, gm, x = 0, y = 0 ):
        Barrier.__init__( self, "metal.jpg", 1,x,y)
        self.add(gm.allsprites, gm.metal, gm.bumpers)
        
class Shield( pygame.sprite.Sprite ):
    def __init__(self, wizard):
        pygame.sprite.Sprite.__init__( self )
        self.image, self.rect = load_image("shield.bmp", -1)
        self.wizard = wizard
        
    def update( self ):
        self.rect.center = self.wizard.rect.center

class Wizard( pygame.sprite.Sprite ):
    def __init__( self, gm, x = 0, y = 0 ):
        pygame.sprite.Sprite.__init__( self )
        self.speed = 2
        self.direction = "up"
        self.shield = 50
        temp = Spritesheet(os.path.join("data", "wizard.bmp"))
        L = temp.imgsat(4,4,(36, 46))
        self.walk_down = L[0:4]
        self.walk_right = L[4:8]
        self.walk_left = L[8:12]
        self.walk_up = L[12:16]
        self.cooldown = 10
                
        self.current = self.walk_up
        self.frame = 0
        self.image = self.walk_up[0]
        x1,y1 = mapmaker.calc_coord(x,y,WIDTH,HEIGHT,BLOCK_SIZE*WIDTH,BLOCK_SIZE*HEIGHT)
        self.rect = Rect(x1,y1,2*BLOCK_SIZE - 2, 2*BLOCK_SIZE - 2)
        self.rate = 4
        self.gm = gm
        self.add(gm.active_group)
        self.offset_left = 0
        self.moving_direction = self.direction
        self.shot_sound = pygame.mixer.Sound(os.path.join("data","sounds","w_shot.ogg"))
        self.dying_sound = pygame.mixer.Sound(os.path.join("data","sounds","w_dying.ogg"))
        self.shot_sound.set_volume(0.1)
        self.dying_sound.set_volume(0.2)

        
    def update ( self, keybuffer ):
        self.shield -= 1

        if self.offset_left > 0:
            self.move(self.moving_direction)
            self.offset_left -= 1
            
        else:
            if keybuffer[pygame.K_UP]:
                self.moving_direction = "up"
                self.offset_left = BLOCK_SIZE/2
            elif keybuffer[pygame.K_DOWN]:            
                self.moving_direction = "down"
                self.offset_left = BLOCK_SIZE/2
            elif keybuffer[pygame.K_LEFT]:
                self.moving_direction = "left"
                self.offset_left = BLOCK_SIZE/2
            elif keybuffer[pygame.K_RIGHT]:
                self.moving_direction = "right"
                self.offset_left = BLOCK_SIZE/2
                        
        if self.cooldown < 1 and keybuffer[pygame.K_x] and len(self.gm.own_projectiles.sprites()) == 0:
            Projectile(self.gm, self.direction, self.rect.center ).add(self.gm.own_projectiles, self.gm.allsprites, self.gm.projectiles)
            self.shot_sound.play()
            self.cooldown = 10
        if self.cooldown >  0 and len(self.gm.own_projectiles.sprites()) == 0:
            self.cooldown -= 1
                                                                                    
    def draw_rect( self ):
        self.rect.top -= BLOCK_SIZE/3#BLOCK_SIZE + 12
                
    def normal_rect( self ):
        self.rect.top += BLOCK_SIZE/3#2*BLOCK_SIZE + 12
                
    def load_sprites( self, name ):
        sprites = []
        for i in range(4):
            image_name = "./data/wizard/%s_0%d.bmp" %(name,i)
            temp_image = pygame.image.load(image_name)
            temp_image = temp_image.convert()
            inv_color = temp_image.get_at((1, 1))
            temp_image.set_colorkey(inv_color)
            temp_image = pygame.transform.scale(temp_image, (36, 46))
            sprites.append(temp_image)

        return sprites

    def move( self, direction ):
        if direction == "up":
            self.current = self.walk_up
        elif direction == "down":
            self.current = self.walk_down
        elif direction == "left":
            self.current = self.walk_left
        elif direction == "right":
            self.current = self.walk_right
        self.direction = direction

        self.shift( direction,1 )
        if pygame.sprite.spritecollideany(self, self.gm.bumpers):
            self.shift( direction, -1 )
        self.image = self.current[self.frame]
        if self.rate < 0:
            self.rate = 4
            self.frame += 1
            if self.frame > 3:
                self.frame = 0
        else:
            self.rate -= 1
    def shift ( self, direction, sign ):
        if direction == "up":
            self.rect = self.rect.move(0, sign*-self.speed)
        elif direction == "down":
            self. rect = self.rect.move(0, sign*self.speed)
        elif direction == "left":
            self.rect = self.rect.move(sign*-self.speed, 0 )
        elif direction == "right":
            self.rect = self.rect.move( sign*self.speed, 0 )

    def respawn(self, x, y):
        self.rect.topleft = mapmaker.calc_coord(x,y,WIDTH,HEIGHT,BLOCK_SIZE*WIDTH,BLOCK_SIZE*HEIGHT)
        self.shield = 50
            
class Projectile( Animated_Sprite ):
    def __init__( self, gm, direction, position ):
        Animated_Sprite.__init__(self, "projectile2.bmp", 4, 2, (1.5,1.5),1,*position)
        self.loop_length = 4
        self.normal = self.current[0:4]
        self.explosion = self.current[4:8]
        for i, e in enumerate(self.explosion):
            self.explosion[i] = pygame.transform.scale(e,(3*BLOCK_SIZE, 3*BLOCK_SIZE) )
        self.current = self.normal
        self.add(gm.active_group)
        self.speed = 4
        self.rect.center = position
        self.direction = direction
        self.destroyed = False
        
    def update( self ):
        if self.rect.top < -20 or self.rect.top > BLOCK_SIZE*HEIGHT + 20:
            self.kill()
        if self.rect.right < -20 or self.rect.left > BLOCK_SIZE*HEIGHT + 20:
            self.kill()
        if self.direction == "up":
            self.rect = self.rect.move(0, -self.speed)
        elif self.direction == "down":
            self. rect = self.rect.move(0, self.speed)
        elif self.direction == "left":
            self.rect = self.rect.move(-self.speed, 0 )
        elif self.direction == "right":
            self.rect = self.rect.move( self.speed, 0 )

        Animated_Sprite.update( self )
        if self.destroyed and self.frame == self.loop_length - 1:
            self.kill()

    def destroy( self ):
        #self.rect = self.explosion[0].get_rect()
        if self.current != self.explosion:
            self.destroyed = True
            self.current = self.explosion
            self.image = self.current[0]
            self.frame = 0
            self.speed = 0
            self.rate = 2
            self.rect = self.image.get_rect(center = self.rect.center)
        
        
class Enemy_Projectile( Animated_Sprite ):
    def __init__( self, gm, own_projectiles ,direction, position ):
        Animated_Sprite.__init__(self, "enemy_projectile.bmp",4,2,(1.5,1.5),2,*position)
        self.normal = self.current[0:4]
        self.explosion = self.current[4:8]
        for i, e in enumerate(self.explosion):
            self.explosion[i] = pygame.transform.scale(e,(3*BLOCK_SIZE, 3*BLOCK_SIZE) )
        self.current = self.normal
        self.add( gm.allsprites, gm.enemy_projectiles,  gm.projectiles, own_projectiles )
        self.speed = 4
        self.rect.center = position
        self.direction = direction
        self.destroyed = False
        
    def update( self ):
        if self.rect.top < -20 or self.rect.top > BLOCK_SIZE*HEIGHT + 20:
            self.kill()
        if self.rect.right < -20 or self.rect.left > BLOCK_SIZE*HEIGHT + 20:
            self.kill()
        if self.direction == "up":
            self.rect = self.rect.move(0, -self.speed)
        elif self.direction == "down":
            self. rect = self.rect.move(0, self.speed)
        elif self.direction == "left":
            self.rect = self.rect.move(-self.speed, 0 )
        elif self.direction == "right":
            self.rect = self.rect.move( self.speed, 0 )

        Animated_Sprite.update( self )

        if self.destroyed and self.frame == self.loop_length - 1:
            self.kill()
        
    def destroy( self ):
        #self.rect = self.explosion[0].get_rect()
        if not self.destroyed:
            self.destroyed = True
            self.current = self.explosion
            self.image = self.current[0]
            self.frame = 0
            self.speed = 0
            self.rate = 2
            self.rect = self.image.get_rect(center = self.rect.center)
            
class Grunt( pygame.sprite.Sprite ):
    def __init__( self, gm,x,y, direction = "up" ):
        pygame.sprite.Sprite.__init__( self )
        self.rect = Rect(x,y,2*BLOCK_SIZE - 2, 2*BLOCK_SIZE - 2)
        self.direction = direction
        self.value = 0
        self.add(gm.active_group, gm.enemies, gm.bumpers)
        self.gm = gm
        self.speed = 2
        self.change_direction()
        self.own_projectiles = pygame.sprite.RenderPlain()
        self.value = 100
        self.cooldown = 15
        
        temp = Spritesheet(os.path.join("data","grunt.bmp"))
        L = temp.imgsat(3,4,(36, 46))
        self.walk_up = L[0:3]
        self.walk_down = L[3:6]
        self.walk_left = L[6:9]
        self.walk_right = L[9:12]
        self.current = self.walk_up
        self.frame = 0
        self.image = self.walk_up[0]
        x1,y1 = mapmaker.calc_coord(x,y,WIDTH,HEIGHT,BLOCK_SIZE*WIDTH,BLOCK_SIZE*HEIGHT)
        self.rect = Rect(x1,y1,2*BLOCK_SIZE - 2, 2*BLOCK_SIZE - 5)
        self.rate = 12
        self.offset_left = BLOCK_SIZE/4
        self.moving_direction = direction
        self.shot_sound = pygame.mixer.Sound(os.path.join("data","sounds","g_shot.ogg"))
        self.dying_sound = pygame.mixer.Sound(os.path.join("data","sounds","g_dying.ogg"))
        self.shot_sound.set_volume(0.1)
        self.dying_sound.set_volume(0.1)
        
    def draw_rect( self ):
        self.rect.top -= BLOCK_SIZE
    def normal_rect( self ):
        self.rect.top += BLOCK_SIZE
        
    def update( self ):
        if self.offset_left > 0:
            if self.direction == "up":
                self.current = self.walk_up
                self.rect = self.rect.move(0, -self.speed)
            elif self.direction == "down":
                self.current = self.walk_down
                self. rect = self.rect.move(0, self.speed)
            elif self.direction == "left":
                self.current = self.walk_left
                self.rect = self.rect.move(-self.speed, 0 )
            elif self.direction == "right":
                self.current = self.walk_right
                self.rect = self.rect.move( self.speed, 0 )
            self.offset_left -= 1
        else:
           self.offset_left = BLOCK_SIZE/2 
        
        if self.cooldown > 0 and len(self.own_projectiles.sprites()) < 1:
            self.cooldown -= 1
            
        if self.cooldown == 0:
            self.frame = -2
            Enemy_Projectile(self.gm, self.own_projectiles, self.direction, self.rect.center)
            self.shot_sound.play()
            
            self.cooldown = 15
            
        self.image = self.current[self.frame]
        if self.rate < 0:
            self.rate = 12
            self.frame += 1
            if self.frame > 1:
                self.frame = 0
        else:
            self.rate -= 1    
            
    def change_direction( self ):
        if self.direction == "up":
            self.rect = self.rect.move(0, self.speed)
        elif self.direction == "down":
            self. rect = self.rect.move(0, -self.speed)
        elif self.direction == "left":
            self.rect = self.rect.move( self.speed, 0 )
        elif self.direction == "right":
            self.rect = self.rect.move( -self.speed, 0 )
        
        while True:
            temp = random.randint(0,3)
            if temp == 0:
                temp = "up"
            elif temp == 1:
                temp = "down"
            elif temp == 2:
                temp = "left"
            elif temp == 3:
                temp = "right"
            if temp != self.direction:
                self.direction = temp
                break

            
class Static_Image( pygame.sprite.Sprite ):
    def __init__( self, image, x = 0, y = 0 ):
        pygame.sprite.Sprite.__init__( self )
        self.image, self.rect = load_image( image, -1 )
        self.rect.center = x, y
        
class Game_Over( Static_Image ):
    def __init__( self, x = 0, y = 0 ):
        Static_Image.__init__( self, "game_over.bmp", x, y + 400 )
        self.top = y
        self.speed = 10
        
    def update( self ):
        if self.rect.top > self.top:
            self.rect = self.rect.move(0,-self.speed)

class Spawn( Animated_Sprite ):
    def __init__( self,gm, x=0, y=0 ):
        Animated_Sprite.__init__( self, "spawn.bmp",12,1,(2,4),1,x,y )
        self.time_left = 50
        self.spawning = False
        self.gm = gm
        self.frame = 0
        self.rate = 1
        self.add(gm.spawns)
        self.wait = 10
        
    def start_spawn( self ):
        self.spawning = True
        self.add(self.gm.active_group, self.gm.bumpers)
                    
    def update ( self ):
        if self.spawning:
            Animated_Sprite.update( self )            
            self.time_left -= 1
            if self.time_left < 0:
                Grunt(self.gm, self.x,self.y)
                self.reset()
                
    def reset ( self ):
        self.time_left = 50
        self.spawning = False
        self.remove(self.gm.active_group,self.gm.bumpers)

    def draw_rect( self ):
        Animated_Sprite.draw_rect(self, 30,5)
        
    def normal_rect( self ):
        Animated_Sprite.normal_rect(self, 30,5)
