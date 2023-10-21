# Import the packages needed for this code
import numpy as np
import pickle
import pygame
import random
import time

# Import other modules from this project
import balloon
import cooldown
import cloud
import enemy
import player

# Import commonly used objects from pygame
from pygame.locals import(
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_RETURN,
    K_p,
    K_r,
    K_f,
    K_d,
    K_SPACE,
    KEYDOWN,
    QUIT,
    )


# Initialise pygame modules
pygame.init()


# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Frame speed
FPS = 30

# Game clock
CLOCK = pygame.time.Clock()

# Speeds in pixels per frame
PLAYER_SPEED = 10
CLOUD_SPEED = 4
BALLOON_RISE_SPEED = 3

# Time between events in ms
BALLOON_PERIOD = 4e3
CLOUD_PERIOD = 3e2
MISSILE_PERIOD = 1e3
DIFFICULTY_PERIOD = 1e4

# Custom pygame events & timings
ADD_ENEMY = pygame.USEREVENT + 1
ADD_CLOUD = pygame.USEREVENT + 2
ADD_BALLOON = pygame.USEREVENT + 3
INCR_DIFF = pygame.USEREVENT + 4


def main():
    loop = GameLoop()
    while loop.quit is False:
        loop.check_events()
        if loop.pause is False:
            if loop.alive:
                loop.run_frame()
            else:
                loop.end_screen()
        CLOCK.tick(FPS)  


class GameLoop():
    def __init__(self):
        """Create the loop that runs the game."""
        # Loop flags
        self.quit = False
        self.pause = False
        self.alive = True
        
        # Reset event flags
        reset_events()
        
        # Create game screen
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Create player
        self.player = player.Player()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        
        # Non-player sprite groups
        self.balloons = pygame.sprite.Group()
        self.back_clouds = pygame.sprite.Group()
        self.front_clouds = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        
        # Player score
        self.score = 0           

        # Set difficulty level & time between missiles in ms
        self.level = 1
        self.missile_period = int(1e3)
        pygame.time.set_timer(ADD_ENEMY, self.missile_period)
        
        self.flash_cooldown = cooldown.FlashCoolDown()
        self.defend_cooldown = cooldown.DefendCoolDown()
        self.starting_animation()
        
    def check_events(self):
        """Respond to all events raised this frame."""
        for event in pygame.event.get():
            
            # Check valid key presses
            if event.type == KEYDOWN:
                    
                if event.key == K_SPACE or event.key == K_f:
                    if self.player.flash():
                        self.flash_cooldown.flash()
                        
                # Defend if d key
                if event.key == K_d:
                    if not self.player.defend_cooldown_remaining():
                        self.player.defend()
                        self.defend_cooldown.defend()
                
                # Quit if esc key
                elif event.key == K_ESCAPE:
                    self.quit = True
                
                # Reset if r key
                elif event.key == K_r:
                    self.__init__()
                    break
                
                # Pause if p key
                elif event.key == K_p:
                    if self.alive:
                        self.pause = not self.pause
                
                # Pause or reset if enter key
                elif event.key == K_RETURN:
                    if self.alive:
                        self.pause = not self.pause
                    else:
                        self.__init__()
                        break
            
            # Check for window closed        
            elif event.type == QUIT:
                self.quit = True
            
            # Create a new enemy and add to sprite groups            
            elif event.type == ADD_ENEMY:
                if not self.pause:
                    new_enemy = enemy.add_enemy(self.level, self.screen)
                    self.enemies.add(new_enemy)
                    self.all_sprites.add(new_enemy)
            
            # Create a new cloud and add to groups    
            elif event.type == ADD_CLOUD:
                if not self.pause:
                    new_cloud = cloud.Cloud()
                    self.all_sprites.add(new_cloud)
                    if random.random() < 0.5:
                        new_cloud.speed = int(0.5*new_cloud.speed)
                        self.back_clouds.add(new_cloud)
                    else:
                        new_cloud.surf.set_alpha(140)
                        self.front_clouds.add(new_cloud)
                
            # Create a new balloon and add to groups
            elif event.type == ADD_BALLOON:
                if not self.pause:
                    new_balloon = balloon.Balloon()
                    self.balloons.add(new_balloon)
                    self.all_sprites.add(new_balloon)
                
            # Increase difficulty by decreasing missile period
            elif event.type == INCR_DIFF:
                if not self.pause:
                    self.missile_period *= 0.8
                    pygame.time.set_timer(ADD_ENEMY, int(self.missile_period))     
                    self.level += 1
                
    def run_frame(self):
        """Run one frame of the game."""
        self.update_sprites()
        self.check_collisions()
        self.draw_screen()
        if not self.alive:
            self.end_screen()

    def check_collisions(self):
        """Check for collions with player."""
        # Check if any enemies have collided with player
        missile = pygame.sprite.spritecollideany(self.player, self.enemies)
        if missile:
            if self.player.is_defending:
                missile.kill()
                self.score += 5
            else:   
                self.player_loses(missile)
            
        # Check if any balloons have collided with player
        balloon = pygame.sprite.spritecollideany(self.player, self.balloons)
        if balloon:
            self.score += 10 + (self.level-1) * 2
            balloon.kill()

    def update_sprites(self):
        """Update all sprites."""
        # Get keys pressed by user at start of frame
        pressed_keys = pygame.key.get_pressed()
        self.player.update(pressed_keys)
        
        # Update positions of enemies, clouds
        self.enemies.update()
        self.back_clouds.update()
        self.front_clouds.update()
        self.balloons.update()       
        
        # Update cooldown bars
        self.flash_cooldown.update()
        self.defend_cooldown.update()

    def player_loses(self, missile):
        """Player hit by missile."""
        self.player.surf = pygame.image.load("resources/explosion.png").convert()
        self.player.surf.set_colorkey((255, 255, 255), RLEACCEL)  
        missile.kill()
        self.pause = True
        self.alive = False        
        
    def draw_screen(self):
        """Draw objects onto screen."""
        # Fill screen with sky blue
        self.screen.fill((135, 200, 245))    
        
        # Draw sprites, clouds last so they are on top
        for cloud in self.back_clouds:
            self.screen.blit(cloud.surf, cloud.rect)
        #self.screen.blit(self.player.get_surf(), self.player.rect)
        self.player.draw(self.screen)
        for balloon in self.balloons:
            self.screen.blit(balloon.surf, balloon.rect)
        for enemy in self.enemies:
            enemy.draw()
        for cloud in self.front_clouds:
            self.screen.blit(cloud.surf, cloud.rect)
            
        self.screen.blit(self.flash_cooldown.surface, (10, 5))
        self.screen.blit(self.defend_cooldown.surface, (10, 30))
            
        if self.level > 5:
            color_filter = strobe_color()
            self.screen.blit(color_filter, (0, 0))   
            
        # Draw flash and defend on cool down bars
        flash_surf = pygame.font.Font(None, 24).render("Flash", True, (0, 0, 0))
        defend_surf = pygame.font.Font(None, 24).render("Defend", True, (0, 0, 0))
        self.screen.blit(flash_surf, (12, 7))
        self.screen.blit(defend_surf, (12, 32))
            
        # Draw level and score
        score_txt = f"Score: {self.score}"
        level_txt = f"Level: {self.level}"
        score_surf = pygame.font.Font(None, 38).render(score_txt, True, (0, 0, 0))
        level_surf = pygame.font.Font(None, 38).render(level_txt, True, (0, 0, 0))
        self.screen.blit(score_surf, (10, 55))
        self.screen.blit(level_surf, (10, 80))
            
        # Update display
        pygame.display.flip()        
        
    def end_screen(self):      
        if not self.input_name():
            return None
        self.screen.fill((255, 200, 200))
        hs_text = "High Scores"
        height = 100
        pos = (SCREEN_WIDTH/2, height)
        score_font = pygame.font.Font(None, 60)
        score_surf = score_font.render(hs_text, True, (0, 0, 0)) 
        score_rect = score_surf.get_rect(center=(pos))
        self.screen.blit(score_surf, score_rect)
        
        with open("resources/high_scores.pkl", 'rb') as file:
            hs = pickle.load(file)
        hs.append([self.name, self.score])
        hs = sorted(hs, key=lambda x: x[1], reverse=True)[:5]
        for score in hs:
            height += 50
            pos = (SCREEN_WIDTH/2, height)               
            text = f"{score[0]}: {score[1]}"         
            score_surf = score_font.render(text, True, (0, 0, 0))
            score_rect = score_surf.get_rect(center=(pos))
            self.screen.blit(score_surf, score_rect)
            
        with open("resources/high_scores.pkl", 'wb') as file:
            pickle.dump(hs, file)
    
        pygame.display.flip()     
        
    def input_name(self):
        # basic font for user typed
        base_font = pygame.font.Font(None, 32)
        user_text = ''
        
        # Input box 
        input_rect = pygame.Rect(200, 200, 100, 40)
        
        # Colors for change when user clicks box
        color = (150, 150, 150)
        active = False
        continue_text_enter = True
        
        while continue_text_enter:
            for event in pygame.event.get():
                # if user types QUIT then the screen will close
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.quit = True
            
                if event.type == pygame.KEYDOWN:
                    # End text enter on return
                    if event.key == K_RETURN:
                        continue_text_enter = False
                    elif event.key == K_ESCAPE:
                        continue_text_enter = False
                        self.quit = False
                    # Check for backspace
                    elif event.key == pygame.K_BACKSPACE:
                        # Set text as all but last element
                        user_text = user_text[:-1]
                    else:
                        # Add the character to the string
                        user_text += event.unicode  
                        
            self.name = user_text
            
            # Set background color of screen
            back_surf = pygame.Surface((300, 300))
            back_surf.set_alpha(10)
            back_surf.fill((200, 200, 200))
            back_rect = back_surf.get_rect()
            back_rect.center = (50+SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
            self.screen.blit(back_surf, back_rect)
                
            # Draw a rectangle on the screen
            input_rect.center = (SCREEN_WIDTH/2, 300)
            pygame.draw.rect(self.screen, color, input_rect)

            # Create the surface objects for the text by rendering fonts
            score_surface = base_font.render(f"Score: {self.score}", True, (0, 0, 0))
            instruct_surface = base_font.render("Type name below", True, (0, 0, 0))
            text_surface = base_font.render(user_text, True, (255, 255, 255))
        
            # Blit the three surfaces containing text to the screen
            self.screen.blit(score_surface, (input_rect.x, input_rect.y-100))
            self.screen.blit(instruct_surface, (input_rect.x, input_rect.y-50))
            self.screen.blit(text_surface, (input_rect.x+5, input_rect.y+5))
        
            # Set width of textfield so that text cannot get outside of user's text input
            input_rect.w = max(100, text_surface.get_width()+10)
        
            # Flip will update the portion of the screen that has changed
            pygame.display.flip()
        
            # Ensure 30 fps
            CLOCK.tick(30)   
    
        # False return means no name was inputed and the highscores are not shown
        if user_text == "" or user_text is None or user_text == '\n':
            return False    
        else:
            return True
            
    def starting_animation(self):
        for i in range(30):
            new_cloud = cloud.Cloud()
            self.all_sprites.add(new_cloud)
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_WIDTH)
            new_cloud.rect.topleft = (x, y)
            if random.random() < 0.5:
                new_cloud.speed = int(0.5*new_cloud.speed)
                self.back_clouds.add(new_cloud)
            else:   
                new_cloud.surf.set_alpha(140)
                self.front_clouds.add(new_cloud)        
        while self.player.rect.left < 100:
            self.player.rect.move_ip(PLAYER_SPEED/2, 0)
            for back_cloud in self.back_clouds:
                back_cloud.update()
            for front_cloud in self.front_clouds:
                front_cloud.update()
            self.draw_screen()
            CLOCK.tick(FPS)        

        
def reset_events():
    """Setup custom events."""
    # Set timers for regular occurance of events.
    pygame.time.set_timer(ADD_CLOUD, int(CLOUD_PERIOD))
    pygame.time.set_timer(ADD_BALLOON, int(BALLOON_PERIOD)) 
    pygame.time.set_timer(INCR_DIFF, int(DIFFICULTY_PERIOD))  
            
            
def strobe_color():
    t = time.time() % (2*np.pi)
    red = 125 * (np.sin(t) + 1)
    blue = 125 * (np.sin(t + 2*np.pi/3) + 1)
    green = 125 * (np.sin(t + 4*np.pi/3) + 1)
    alpha = 60 * (np.sin(10 * t) + 1)
    color_filter = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    color_filter.set_alpha(alpha)    
    color_filter.fill((red, blue, green))
    return color_filter


def scale_rect(rect: pygame.Rect, factor):
    center = rect.center
    rect.w *= factor
    rect.h *= factor
    rect.center = center
    return rect
        
                  
            
if __name__ == "__main__":
    main()
