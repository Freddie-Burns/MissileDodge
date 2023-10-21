import pygame as pg


# Time between events in ms
BALLOON_PERIOD = 4e3
CLOUD_PERIOD = 3e2
MISSILE_PERIOD = 1e3
DIFFICULTY_PERIOD = 1e4

# Custom pg events & timings
ADD_ENEMY = pg.USEREVENT + 1
ADD_CLOUD = pg.USEREVENT + 2
ADD_BALLOON = pg.USEREVENT + 3
INCR_DIFF = pg.USEREVENT + 4


class EventChecker():
    def __init__(self, game_loop):
        self.loop = game_loop
        
    def check_events(self):
        """Respond to all events raised this frame."""        
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:       
                self.key_down()         
            elif event.type == ADD_CLOUD:
                self.add_cloud()                                
            elif event.type == ADD_ENEMY:
                self.add_enemy()              
            elif event.type == ADD_BALLOON:
                self.add_balloon()                
            elif event.type == INCR_DIFF:
                self.increase_difficulty()                   
            elif event.type == pg.QUIT:
                self.loop.quit = True    
                    
    def add_balloon(self):
        if not self.loop.pause:
            new_balloon = balloon.Balloon()
            self.loop.balloons.add(new_balloon)
            self.loop.all_sprites.add(new_balloon)        
                    
    def add_cloud(self):
        if not self.loop.pause:
            new_cloud = cloud.Cloud()
            self.loop.all_sprites.add(new_cloud)
            if random.random() < 0.5:
                new_cloud.speed = int(0.5*new_cloud.speed)
                self.loop.back_clouds.add(new_cloud)
            else:
                new_cloud.surf.set_alpha(140)
                self.loop.front_clouds.add(new_cloud)        
                    
    def add_enemy(self):
        if not self.loop.pause:
            new_enemy = enemy.add_enemy(self.loop.level, self.loop.screen)
            self.loop.enemies.add(new_enemy)
            self.loop.all_sprites.add(new_enemy)        
        
    def increase_difficulty(self):
        if not self.loop.pause:
            self.loop.missile_period *= 0.8
            pg.time.set_timer(ADD_ENEMY, int(self.loop.missile_period))     
            self.loop.level += 1        
        
    def key_down(self):
        """Respond to user key presses."""
        # Flash if F pressed
        if event.key == pg.K_f:
            if self.loop.player.flash():
                self.loop.player.flash()
                self.loop.flash_cooldown.flash()    
                
        # Defend if D pressed
        elif event.key == pg.K_d:
            # Only call defend function if cooldown is zero
            if not self.loop.player.defend_cooldown_remaining():
                self.loop.player.defend()
                self.loop.defend_cooldown.defend()    
                
        # Quit if Esc pressed
        elif event.key == pg.K_ESCAPE:
            self.loop.quit = True    
            
        # Reset game if R pressed
        elif event.key == pg.K_r:
            self.loop.__init__()   
        
        # Pause if P pressed
        elif event.key == pg.K_p:
            if self.loop.alive:
                self.loop.pause = not self.loop.pause  
                
        # If player is alive then pause, otherwise reset
        elif event.key == pg.K_RETURN:
            if self.loop.alive:
                self.loop.pause = not self.loop.pause     
            else:
                self.loop.__init__()
            
              
def reset_events():
    """Setup custom events."""
    # Set timers for regular occurance of events.
    pg.time.set_timer(ADD_CLOUD, int(CLOUD_PERIOD))
    pg.time.set_timer(ADD_BALLOON, int(BALLOON_PERIOD)) 
    pg.time.set_timer(INCR_DIFF, int(DIFFICULTY_PERIOD))              