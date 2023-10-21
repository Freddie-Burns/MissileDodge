import numpy as np
import pygame
import random
import time


def add_enemy(level, screen):
    chance = random.random()
    if chance < (level / 20):
        return SineMissile(screen)
    elif chance < (2 * level / 20):
        return BoostMissile(screen)
    else:
        return Missile(screen)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, screen: pygame.Surface):
        super(Enemy, self).__init__()
        self.screen = screen
        self.screen_rect: pygame.Rect = screen.get_rect()
        self.height = random.randint(0, self.screen_rect.height) 
        
        # Declare surf attribute and type for draw & place methods
        self.surf: pygame.Surface = None 
        self.rect: pygame.Rect = None   
            
    def draw(self):
        self.screen.blit(self.surf, self.rect)
        
    def place(self):
        """Place surface just past right edge of screen at random height."""
        self.rect = self.surf.get_rect(topleft=(self.screen_rect.width, self.height)) 
    
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.centerx < (SCREEN_WIDTH*3/4):
            self.speed = 30
        if self.rect.right < 0:
            self.kill()                 
            

class Missile(Enemy):
    def __init__(self, screen):
        super(Missile, self).__init__(screen)
        self.surf = pygame.image.load("resources/missile.png").convert()
        self.surf.set_colorkey((255, 255, 255), pygame.RLEACCEL)        
        self.speed = random.randint(10, 25)
        self.place()
        
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()


class SineMissile(Enemy):
    def __init__(self, screen):
        super(SineMissile, self).__init__(screen)
        self.surf = pygame.image.load("resources/missile.png").convert()
        self.surf.set_colorkey((255, 255, 255), pygame.RLEACCEL)          
        self.speed = 10
        self.angle = 0
        self.offset = 2 * np.pi * np.random.random()   
        self.place()
        
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        t = time.time() % (2*np.pi)
        vy = np.sin(4*(t+self.offset))
        self.rect.move_ip(0, self.speed*vy)
        self.angle = np.arctan(vy) * 180 / np.pi        
        if self.rect.right < 0:
            self.kill()
            
    def draw(self):
        rotated_surf = pygame.transform.rotate(self.surf, self.angle)
        self.screen.blit(rotated_surf, self.rect)    
            
    
class BoostMissile(Enemy):
    def __init__(self, screen):
        super(BoostMissile, self).__init__(screen)
        self.surf = pygame.image.load("resources/missile.png").convert()
        self.surf.set_colorkey((255, 255, 255), pygame.RLEACCEL)             
        self.speed = 5
        self.boosted = False
        self.place()
        
    def update(self):
        if not self.boosted:
            if self.rect.left < (self.screen_rect.width * 3 / 4):
                self.speed = 30
        self.rect.move_ip(-self.speed, 0)
    