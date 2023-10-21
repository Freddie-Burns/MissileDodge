import numpy as np
import pygame
import time

from pygame import(
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    )


# Players' speed in pixels per frame
PLAYER_SPEED = 10

# Plane rotation params
MAX_ROT = 15
FRAME_ROT = 1


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load("resources/plane.png").convert()
        self.surf.set_colorkey((255, 255, 255), pygame.RLEACCEL)
        
        
        self.screen_width, self.screen_height = pygame.display.get_surface().get_size()        
        self.rect: pygame.Rect = self.surf.get_rect(center=(-100, self.screen_height/2))
        
        # Upward, downward, or no rotation this frame
        self.rot = 0
        # Current rotation
        self.angle = 0
        
        self.flash_time = 0
        self.defend_time = 0
        self.direction = [0, 0]
        
        # Defend counter
        self.is_defending = 0
        self.defend_time = 0   
        self.defend_cooldown = 5
        
    def draw(self, screen):
        screen.blit(self.get_surf(), self.rect)
        if self.is_defending:
            surf = pygame.Surface((64, 64))
            surf.set_colorkey((0, 0, 0))
            surf.set_alpha(100)
            rect = surf.get_rect()
            rect.center = self.rect.center
            pygame.draw.circle(surf, (255, 200, 100), (32, 30), 32)        
            screen.blit(surf, self.rect)
    
    def defend(self, cool_down=5):
        if self.defend_cooldown_remaining():
            return False
        self.defend_time = time.time()
        self.is_defending = 5
        
    def defend_cooldown_remaining(self):
        remaining = 5 + self.defend_time - time.time()
        if remaining < 0:
            remaining = 0
        return remaining
        
    def flash(self, boost=20, cool_down=5):
        if time.time() - self.flash_time < cool_down:
            return False
        self.flash_time = time.time()
        speed = PLAYER_SPEED        
        if self.direction == [0, 0]:
            self.direction = [1, 0]
        elif self.direction[0] and self.direction[1]:
            speed = int(speed/np.sqrt(2))
        dx = self.direction[0] * speed * boost
        dy = self.direction[1] * speed * boost
        self.rect.move_ip(dx, dy)
        return True
    
    def get_surf(self):
        if self.angle:
            return self.rotate()
        else:
            return self.surf
        
    def rotate(self):
        return pygame.transform.rotate(self.surf, self.angle)        
    
    def update(self, pressed_keys):
        if self.is_defending:
            self.is_defending -= 1
        
        # Assume no rotation this frame
        self.rot = 0

        # Maintain movement speed in the diagonal
        keys = pressed_keys
        if (keys[K_UP] or keys[K_DOWN]) and (keys[K_LEFT] or keys[K_RIGHT]):
            speed = int(PLAYER_SPEED / np.sqrt(2))
        else: speed = PLAYER_SPEED
            
        self.direction = [0, 0]
        
        if pressed_keys[K_UP]:
            self.rot += FRAME_ROT
            self.rect.move_ip(0, -speed)
            self.direction[1] -= 1
        if pressed_keys[K_DOWN]:
            self.rot -= FRAME_ROT
            self.rect.move_ip(0, speed)
            self.direction[1] += 1
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-speed, 0)
            self.direction[0] -= 1
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(speed, 0)
            self.direction[0] += 1
        
        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.screen_width:
            self.rect.right = self.screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > self.screen_height:
            self.rect.bottom = self.screen_height
            
        # Adjust rotation ange
        if self.rot:
            if abs(self.angle) < MAX_ROT:
                # If plane angled incorrectly rotate faster by factor
                if np.sign(self.angle) == self.rot: factor = 1
                else: factor = 3
                self.angle += factor * self.rot
        else:
            if self.angle:
                # If no rotation go back to level flight 
                new_angle = abs(self.angle) - 2
                if new_angle < 0: new_angle = 0
                self.angle = np.sign(self.angle) * new_angle