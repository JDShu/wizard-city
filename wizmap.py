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

import pickle

class Wizmap:
    def __init__(self, width = 11, height = 11 ):
        self.map = []
        for x in range(3*height):
            line = 3*width*[0]
            self.map.append( line )

        self.enemy_reserves = 15
        self.max_enemies = 5
        
    def print_wizmap( self ):
        for row in self.map:
            print(row)

    def place_item( self, x, y, item ):
        size = 1
        if item in (2, 4 ,5, 6 ):
            size = 2
        if item == 0:
            self.erase( x, y )
        elif self.possible_spot(x,y,size,item):
            self.place_large(x,y,size)
            self.map[x][y] = item
                        
    def erase( self, x, y ):
        if self.map[x][y] in (1,3):
            self.map[x][y] = 0
        elif self.map[x][y] in (2,4,5,6):
            for i in range(3):
                for j in range(2):
                    self.map[x + i][y + j] = 0
            
    def possible_spot( self, x, y, size, item):
        for i in range(size):
            for j in range(size):
                try:
                    if self.map[x + i][y + j] != 0:
                        return False
                except IndexError:
                    return False
        return True

    def place_large( self, x, y, size):
        for i in range(size):
            for j in range(size):
                self.map[x + i][y + j] = -1
                            
if __name__ == "__main__":
    W = Wizmap()
    W.print_wizmap()
