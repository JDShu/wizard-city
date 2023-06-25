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
import sys
import pickle

def main():
    new = False
    dir_list = os.listdir("./campaign/")
    map_list = os.listdir("./maps/")
    if len(sys.argv) > 1:
        if sys.argv[1] in dir_list:
            campaign_name = sys.argv[1]
            F = open("./campaign/" + campaign_name, "r+b")
        else:
            print "Campaign does not exist"
    else:
        new = True
        campaign_name = raw_input("Campaign Name: ")
            
    if new:
        campaign = []
    else:
        campaign = pickle.load(F)
        
    while True:
        command = raw_input("Command: ").split()
        l = len(command)
        print command
        if l == 0:
            print "no command"
            pass
        elif command[0] == "add":
            if l == 1:
                print "No map specified"
            elif command[1] in map_list:
                if l == 2:
                    add_map(command[1],campaign)
                elif command[2].isdigit():
                    add_map(command[1],campaign,int(command[2]))
                else:
                    print "Position not an integer"
                print campaign
            else:
                print "Invalid map"
        elif command[0] == "remove":
            if l == 1:
                print "no map specified"
            elif command[1] in campaign:
                remove_map(command[1], campaign)
                print campaign
            else:
                print "Invalid map"
            
        elif command[0] == "print":
            print campaign
        elif command[0] == "quit":
            break
        
    F = open("./campaign/" + campaign_name, "wb")
    pickle.dump(campaign, F)
        
def add_map(game_map, campaign, i = -1):
    if i == -1:
        campaign.append( game_map )
    else:
        campaign.insert( i, game_map )

def remove_map(game_map, campaign):
    campaign.remove( game_map )

if __name__ == "__main__":
    main()
