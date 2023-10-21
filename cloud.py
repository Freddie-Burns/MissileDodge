import numpy as np
import pygame
import random


CLOUD_SPEED = 4
MIN_R, MAX_R = 50, 100
WIDTH, HEIGHT = 500, 400
RADII = [50, 50, 60, 60, 70, 70, 90]    
COORDS = [
    (100, 200),
    (180, 200),
    (260, 200),
    (340, 200),
    (130, 130),
    (210, 130),
    (290, 130)]

            
class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        size = np.array([350, 200]) * random.randint(2, 10) / 10
        self.surf = generate_cloud()
        self.surf = pygame.transform.scale(self.surf, size)
        self.rect: pygame.Rect = self.surf.get_rect()
        
        screen_width, screen_height = pygame.display.get_surface().get_size()        
        x = screen_width
        y = random.randint(0, screen_height)    
        self.rect: pygame.Rect = self.surf.get_rect(topleft=(x, y))
        
        self.speed = CLOUD_SPEED

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()

           
def generate_cloud():
    surf = pygame.Surface((WIDTH, HEIGHT))
    surf.set_colorkey((0, 0, 0))
    random.shuffle(RADII)
    for i, coord in enumerate(COORDS):
        r = RADII[i]  
        w, h = coord
        pygame.draw.circle(surf, (255, 255, 255), (w, h), r)        
    return surf
