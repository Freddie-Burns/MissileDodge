import pygame
import random


CLOUD_SPEED = 4
BALLOON_RISE_SPEED = 3

            
class Balloon(pygame.sprite.Sprite):
    def __init__(self):
        super(Balloon, self).__init__()
        self.surf = pygame.image.load("resources/balloon.png").convert()
        self.surf.set_colorkey((255, 255, 255), pygame.RLEACCEL)
        
        screen_width, screen_height = pygame.display.get_surface().get_size()          
        height = random.randint(screen_height/4, screen_height)
        self.rect: pygame.Rect = self.surf.get_rect(topleft=(screen_width, height))
    
    def update(self):
        self.rect.move_ip((-CLOUD_SPEED, -BALLOON_RISE_SPEED))
        if self.rect.bottom < 0:
            self.kill()   