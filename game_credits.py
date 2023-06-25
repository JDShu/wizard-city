import pygame

from tools import *
from state import *

class Credits:
    def __init__( self, screen, game_state ):
        self.game_state = game_state
        self.screen = screen
        self.background, self.background_rect = load_image("credits.jpg")
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
