import pygame
import time


class FlashCoolDown():
    def __init__(self):
        self.surface = pygame.Surface((100, 20))
        self.surface.fill((100, 255, 100))
        self.rect = self.surface.get_rect()    
        self.prev_flash = 0
        self.length = self.max_length = 100
        self.cool_down = 5
    
    def update(self):
        delay = (time.time()-self.prev_flash)
        self.length = self.max_length * (1 - delay / self.cool_down)
        if self.length < 0:
            self.length = 0
        self.rect.width = self.length
        self.surface.fill((100, 255, 100))
        pygame.draw.rect(self.surface, (255, 0, 0), self.rect)       
        
    def flash(self):
        self.prev_flash = time.time()
        
        
class DefendCoolDown():
    def __init__(self):
        self.surface = pygame.Surface((100, 20))
        self.surface.fill((100, 255, 100))
        self.rect = self.surface.get_rect()    
        self.prev_defend = 0
        self.length = self.max_length = 100
        self.cool_down = 5
    
    def update(self):
        delay = (time.time()-self.prev_defend)
        self.length = self.max_length * (1 - delay / self.cool_down)
        if self.length < 0:
            self.length = 0
        self.rect.width = self.length
        self.surface.fill((100, 255, 100))
        pygame.draw.rect(self.surface, (255, 0, 0), self.rect)       
        
    def defend(self):
        self.prev_defend = time.time()
        