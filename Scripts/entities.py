import pygame
import random
import math

from Scripts.particle import Particle
from Scripts.spark import Spark

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game= game
        self.type = e_type
        self.pos = list(pos)
        self.size= size 
        self.velocity = [0, 0]
        self.collisions = {"up" : False, "down": False, "right": False, "left": False}

        self.action =''
        self.anim_offset = (-2 , -2)
        self.flip= False
        self.set_action('idle')

        self.last_movement = [0, 0]


    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
           self.action = action
           self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def update(self, tilemap, movement = (0,0)):
        self.collisions = {"up" : False, "down": False, "right": False, "left": False}
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right 
                    self.collisions["left"] = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()

        is_dropping = hasattr(self, 'dropping_through') and self.dropping_through > 0
        if frame_movement[1] > 0 and not is_dropping:
            for rect in tilemap.dropdown_rects_around(self.pos):
                if entity_rect.colliderect(rect):
                    if entity_rect.bottom - frame_movement[1] <= rect.top + 2:
                        entity_rect.bottom = rect.top
                        self.collisions['down'] = True
                        self.pos[1] = entity_rect.y

        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions["down"] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions["up"] = True
                self.pos[1] = entity_rect.y
        
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.last_movement = movement
                
        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        if self.collisions["down"] or self.collisions["up"]: 
            self.velocity[1] = 0

        self.animation.update()

            
    def render(self, surf, offset=(0,0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
        

class Slime(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'Slime', pos, size)

        self.walking = 0
        self.health = 50

    def die(self):
        for i in range(15):
            angle = random.random() * math.pi * 2
            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))

    def update(self, tilemap, movement =(0,0)):
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7),self.pos[1] + 23)):
                if (self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
        elif random.random() < 0.01:
            self.walking = random.randint(30,120)
        

        super().update(tilemap, movement=movement) 

        if movement[0] != 0:
            self.set_action('walk')
        else:
            self.set_action('idle')

    

class Flamemite(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'Flamemite', pos, size)
        
        self.walking = 0
        self.health = 50
        self.attack_cooldown = 0

    def die(self):
        for i in range(25):
            angle = random.random() * math.pi * 2
            speed = 2 + random.random() * 3
            self.game.sparks.append(Spark(self.rect().center, angle, 3 + random.random()))

    def update(self, tilemap, movement =(0,0)):

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7),self.pos[1] + 23)):
                if (self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)

            if not self.walking and self.attack_cooldown <=0:
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if abs(dis[1]) < 48 and abs(dis[0]) < 100:
                    direction = -2.0 if self.flip else 2.0
                    self.game.projectiles.append([[self.rect().centerx + (-7 if self.flip else 7), self.rect().centery], direction, 0, 20, 'flamemite'])

                    for i in range(6):
                        self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + (math.pi if self.flip else 0), 2 + random.random()))
                        self.attack_cooldown = 90

        elif random.random() < 0.01:
            self.walking = random.randint(30,120)


        super().update(tilemap, movement=movement) 

        if movement[0] != 0:
            self.set_action('walk')
        else:
            self.set_action('idle')  


    
class DarkMage(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'DarkMage', pos, size)  

        self.walking = 0
        self.health = 400

    def die(self):
        for i in range(40):
            angle = random.random() * math.pi * 2
            self.game.sparks.append(Spark(self.rect().center, angle, 3 + random.random() * 2))
    
    def update(self, tilemap, movement =(0,0)):
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7),self.pos[1] + 23)):
                if (self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)

            if not self.walking:
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])    
                if (abs(dis[1])<48):   #48 pixels distance is taken  
                    if (self.flip and dis[0] < 0):
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0, 15, 'darkmage'])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))

                    if (not self.flip and dis[0] > 0):
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0, 15, 'darkmage'])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 , 2 + random.random()))

        elif random.random() < 0.01:
            self.walking = random.randint(30,120)


        super().update(tilemap, movement=movement) 

        if movement[0] != 0:
            self.set_action('walk')
        else:
            self.set_action('idle')   


class Player(PhysicsEntity):

    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.jumps = 2
        self.wall_slide = False
        self.attacking = 0

        self.mana = 0
        self.max_mana = 200
        self.max_obtainable_mana = 20

        self.hp = 120
        self.max_hp = 120
        self.invincibility = 0  # 1.5s immunity
        self.dead = False

        self.b_attack_cost = 20
        self.C_attack_cost = 100
        self.b_attack_dmg = 50
        self.C_attack_dmg = 200 

        self.dashing = 0
        self.dash_cd = 0

        self.dropping_through = 0

    def take_damage(self, amount):
        if self.invincibility > 0 or self.dead:
            return False
        self.hp -= amount
        self.invincibility = 60

        for i in range(15):
            angle = random.random() * math.pi * 2
            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))

        if self.hp <= 0:
            self.hp = 0
            self.die()
            return True
        return False
    

    def die(self):

        self.dead = True

        for i in range(40):
            angle = random.random() * math.pi * 2
            self.game.sparks.append(Spark(self.rect().center, angle, 3 + random.random()))

    def collect_mana(self, amount):
        self.mana = min(self.mana + amount, self.max_mana)
        return self.mana >= self.max_mana

    def use_mana(self, amount):
        if self.mana >= amount:
            self.mana -= amount
            return True
        return False
    
    def can_cast(self, mana_cost):
        return self.mana >= mana_cost
    
    def dash(self):
        
        if self.dash_cd <= 0 and self.dashing == 0:
            if self.flip:
                self.dashing = -45
            else :
                self.dashing = 45

            self.dash_cd = 120

            self.set_action('dash')

            return True
        return False

    def jump(self):

        if self.attacking > 0:
            return False
        

        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -5.0
                self.air_time = 5
                self.jumps = max(0, self.jumps -1)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -5.0
                self.air_time = 5
                self.jumps = max(0, self.jumps -1)
                return True

        elif self.jumps:
            self.velocity[1] = -4
            self.jumps -= 1
            self.air_time = 5
            return True
        
    def basic_attack(self):
        if self.attacking <= 0 and self.can_cast(self.b_attack_cost):
            self.use_mana(self.b_attack_cost)
            
            self.set_action('Staffattack')

            if self.flip == False:
                direction = 1.5 
            else: 
                direction = -1.5

            projectile_pos = [self.rect().centerx + (-7 if self.flip else 7), self.rect().centery]

            self.game.projectiles.append([projectile_pos, direction, 0, self.b_attack_dmg, 'player_basic'])

            for i in range(4):
                self.game.sparks.append(Spark(projectile_pos, random.random() - 0.5 + (math.pi if self.flip else 0), 2 + random.random()))

            self.attacking = 36 # Lock player for 6 frames * 6 img_dur
            return True
        return False
    
    def strong_attack(self):
        if self.attacking <= 0 and self.can_cast(self.C_attack_cost):
            self.use_mana(self.C_attack_cost)

            self.set_action('Staffattack')

            if self.flip == False:
                direction = 2.5
            else:
                direction = -2.5
            
            projectile_pos = [self.rect().centerx + (-7 if self.flip else 7), self.rect().centery]

            self.game.projectiles.append([projectile_pos, direction, 0, self.C_attack_dmg, 'player_strong'])

            for i in range(12):
                self.game.sparks.append(Spark(projectile_pos, random.random() - 0.5 + (math.pi if self.flip else 0), 3 + random.random()))
            
            self.attacking = 36
            return True
        return False
    
    def attack_fail(self):
        if self.attacking <= 0:
            self.set_action('Failattack')

            staff_pos = [self.rect().centerx + (-7 if self.flip else 7), self.rect().centery]
            for i in range(3):
                self.game.sparks.append(Spark(staff_pos, random.random() * math.pi * 2, 0.5 + random.random() * 0.5))
            
            self.attacking = 24 #penalty for not noticing
    
    def update(self, tilemap, movement = (0,0)):

        if self.dash_cd > 0:
            self.dash_cd -= 1

        if self.dashing != 0:
            movement= (0,0)
            dash_speed = 0.8 if self.dashing > 0 else -0.8
            self.velocity[0] = dash_speed * abs(self.dashing) / 15

            if self.dashing > 0:
                self.dashing = max(0, self.dashing - 1)
            else:
                self.dashing = min(0, self.dashing + 1)
            
        if self.dropping_through > 0:
            self.dropping_through -= 1    

        if self.game.movement[2] and self.collisions['down'] and self.dropping_through == 0:
            on_dropdown = False
            player_bottom_rect = pygame.Rect(self.rect().x, self.rect().bottom, self.rect().width, 4)

            for rect in self.game.tilemap.dropdown_rects_around(self.pos):
                if player_bottom_rect.colliderect(rect):
                    on_dropdown = True
                    break
            if on_dropdown and self.collisions['down']:
                self.dropping_through = 10
                self.pos[1] += 8
                self.velocity[1] = 1
                
            
        if self.attacking > 0:
            movement = (0,0)

        super().update(tilemap, movement=movement)

        if self.invincibility > 0:
            self.invincibility -= 1
        
        if self.attacking > 0:
            self.attacking -= 1

            if self.attacking == 0:
                if self.air_time > 4:
                    self.set_action('jump')
                elif movement[0] != 0:
                    self.set_action('run')
                else:
                    self.set_action('idle')

        self.air_time += 1  
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 2

        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            
            if self.attacking <= 0:            
                self.set_action('Wallslide')

        if self.attacking <= 0 and self.dashing == 0:
            if not self.wall_slide:
                if self.air_time > 4:
                    self.set_action('jump')
                elif movement[0] != 0:
                    self.set_action('run')
                else:
                    self.set_action('idle')


        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

    def render(self, surf, offset=(0, 0)):

        if self.invincibility > 0 and self.invincibility % 4 < 2 and self.dashing == 0: #For flickering effect
            return

        super().render(surf, offset = offset)

        


            








    
    
