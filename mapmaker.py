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

import sys
import pygame
import pickle
import string
import os

import wizmap
import objects
from tools import display_box

BLOCK_SIZE = 16
HEIGHT = 32
WIDTH = 32

NUM_MODES = 7

reference = {}
reference[0] = "Erase"
reference[1] = "Wall"
reference[2] = "Grunt"
reference[3] = "Indestructable"
reference[4] = "Base"
reference[5] = "Wizard"
reference[6] = "Spawn"

def main():
    pygame.init()
    pygame.display.set_caption('Wizmap Maker')
    
    if len(sys.argv) == 1:
        level = wizmap.Wizmap()
    else:
        level = wizmap.Wizmap( sys.argv[1] ) #not implemented

    size = width, height = BLOCK_SIZE*WIDTH, BLOCK_SIZE*(HEIGHT+5)
    black = 0,0,0    
    screen =  pygame.display.set_mode(size)

    wizard_surface = scaled_surface("m_wizard.bmp", 2)
    wall_surface = scaled_surface("wall.bmp", 1)
    enemy_surface = scaled_surface("enemy.bmp", 2)
    metal_surface = scaled_surface("metal.jpg",1)
    base_surface = scaled_surface("base.bmp",2)
    spawn_surface = scaled_surface("m_spawn.bmp",2)

    mode = 0

    mouse_buffer = False
    map_name = ask(screen, "Map Name")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_state(level, os.path.join("maps", map_name + ".map"))
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_buffer = True
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_buffer = False 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    mode = cycle_mode( mode )
        if mouse_buffer:
            x, y = calc_square( pygame.mouse.get_pos(), WIDTH, HEIGHT, BLOCK_SIZE*WIDTH, BLOCK_SIZE*HEIGHT)
            level.place_item( x, y, mode )
            
        screen.fill(black)
        for x in range(WIDTH):
            for y in range(HEIGHT):
                if level.map[x][y] == 1:
                    screen.blit( wall_surface, calc_coord(x, y, WIDTH, HEIGHT, BLOCK_SIZE*WIDTH, BLOCK_SIZE*HEIGHT))
                elif level.map[x][y] == 2:
                    screen.blit( enemy_surface, calc_coord(x, y, WIDTH, HEIGHT,BLOCK_SIZE*WIDTH, BLOCK_SIZE*HEIGHT))
                elif level.map[x][y] == 3:
                    screen.blit( metal_surface, calc_coord(x, y, WIDTH, HEIGHT, BLOCK_SIZE*WIDTH, BLOCK_SIZE*HEIGHT))
                elif level.map[x][y] == 4:
                    screen.blit( base_surface, calc_coord(x, y, WIDTH, HEIGHT, BLOCK_SIZE*WIDTH, BLOCK_SIZE*HEIGHT))
                elif level.map[x][y] == 5:
                    screen.blit( wizard_surface, calc_coord(x, y, WIDTH, HEIGHT, BLOCK_SIZE*WIDTH, BLOCK_SIZE*HEIGHT))
                elif level.map[x][y] == 6:
                    screen.blit( spawn_surface, calc_coord(x, y, WIDTH, HEIGHT, BLOCK_SIZE*WIDTH, BLOCK_SIZE*HEIGHT))
        pygame.display.flip()

def cycle_mode( mode ):
    mode += 1
    if mode == NUM_MODES:
        mode = 0
    #print reference[mode]
    return mode
        
def calc_square( mouse_pos, width, height, res_x, res_y ):
    square_x = int(mouse_pos[0] * width / res_x)
    square_y = int(mouse_pos[1] * height / res_y)
    return square_x, square_y

def calc_coord( x, y, width, height, res_x, res_y ):
    coord_x = int(x*res_x/width)
    coord_y = int(y*res_y/height)
    return coord_x, coord_y

def save_state( level, filename ):
    F = open( filename, "wb" )
    pickle.dump( level, F )

def scaled_surface( filename, size ):
    
    surface = pygame.image.load( os.path.join("data", filename) )
    surface = pygame.transform.scale( surface, (size*BLOCK_SIZE - 1, size*BLOCK_SIZE - 1 ) )
    return surface

def get_key():
    while 1:
        event = pygame.event.poll()
        if event.type == pygame.KEYDOWN:
            return event.key
        else:
            pass


def ask(screen, question):
    "ask(screen, question) -> answer"
    pygame.font.init()
    current_string = []
    display_box(screen, question + ": " + string.join(current_string,""))
    while True:
        inkey = get_key()
        if inkey == pygame.K_BACKSPACE:
            current_string = current_string[0:-1]
        elif inkey == pygame.K_RETURN:
            break
        elif inkey == pygame.K_MINUS:
            current_string.append("_")
        elif inkey <= 127:
            current_string.append(chr(inkey))
        display_box(screen, question + ": " + string.join(current_string,""))
    return string.join(current_string,"")

if __name__ == "__main__":    
    main()
 
