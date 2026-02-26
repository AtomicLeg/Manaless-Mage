import sys
import pygame
import math
import random

from Scripts.utils import load_image, load_images, Animation

from Scripts.entities import PhysicsEntity, Player, DarkMage, Slime, Flamemite

from Scripts.tilemap import Tilemap
from Scripts.clouds import Clouds
from Scripts.particle import Particle

from Scripts.spark import Spark
from Scripts.hud import HUD

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Platformer Project Fall") #1. name of window 2. you can change the icon of the app too (look into it)
        self.screen = pygame.display.set_mode((640, 480))

        self.display = pygame.Surface((320,240))

        self.clock = pygame.time.Clock()
    
        self.movement = [False, False] 

        self.assets ={
            'Grass' : load_images('Tiles/Grass'),
            'Stone' : load_images('Tiles/Stone'),
            'Halfblock' : load_images('Tiles/Halfblock'),
            'Mana' : load_images('Tiles/Mana'),
            'Spawner' : load_images('Tiles/Spawner'),
            'Lava' : load_images('Tiles/Lava'),
            'Hazards' :load_images("Tiles/Hazards"),
            'DropDown' : load_images("Tiles/DropDown"),
            'Temp' :load_images('Tiles/Temp'),
            'Wall' :load_images('Tiles/Wall'),
            'Goal' : load_images('Tiles/Goal'),
            'Decor' : load_images('Tiles/Decor'),
            'Temp/Breaking' :Animation(load_images('Tiles/TempAnimations/Breaking'), img_dur=2, loop=False),
            'Temp/Shaking' :Animation(load_images('Tiles/TempAnimations/Shaking'),img_dur=5),
            'Temp/Broken' :load_image('Tiles/TempAnimations/Broken/000.png'),
            'Wall' :load_images('Tiles/Wall'),
            'EProjectile' : load_image('Enemies/DarkMage/EEnergy_Ball.png'),
            'EStaff' : load_image('Enemies/DarkMage/EStaff.png'),
            'FlameProjectile' : load_image('Enemies/Flame_mite/FlameProjectile.png'),
            'background' : load_image('background.png'),
            'castlebackground' : load_image('bgcastle.png'),
            'cavebackground': load_image('bgcave.png'),
            'clouds': load_images('clouds'),
            'player/idle' : Animation(load_images('Character/Idle'), img_dur=6),
            'player/run' : Animation(load_images('Character/Run'), img_dur=4),
            'player/Staffattack' : Animation(load_images('Character/Attack'),img_dur=6),
            'player/Failattack': Animation(load_images('Character/Failattack'), img_dur=4),
            'player/dash' : Animation(load_images('Character/Dash')),
            'player/jump' : Animation(load_images('Character/Jump')),
            'player/Wallslide' : Animation(load_images('Character/Wallslide')),
            'Flames' : Animation(load_images('particle/flames'), img_dur=20, loop=False),
            'ManaAmbience' : Animation(load_images('particle/ManaAmbience'),img_dur=20, loop=False),
            'Slime/idle' : Animation(load_images('Enemies/Slime/idle'), img_dur=6), #Nuke this folder if useless
            'Slime/walk' : Animation(load_images('Enemies/Slime/Walk'), img_dur=4),
            'Flamemite/idle' : Animation(load_images('Enemies/Flame_mite/idle'), img_dur=6), #Nuke this folder if useless
            'Flamemite/attack' : Animation(load_images('Enemies/Flame_mite/Attack')),
            'Flamemite/walk' : Animation(load_images('Enemies/Flame_mite/Walk'), img_dur=4),
            'DarkMage/EStaffattack' : Animation(load_images('Enemies/DarkMage/Attack'),img_dur=6),
            'DarkMage/walk' : Animation(load_images('Enemies/DarkMage/Walk'), img_dur=4),
            'DarkMage/idle' : Animation(load_images('Enemies/DarkMage/idle'), img_dur=4),
            'Projectile' : load_image('Character/Energy_Ball.png'),
            'Charged_Projectile' : load_image('Character/MAXENERGYBALL.png'),
        }

        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.player = Player(self, (50,50), (8,16))  #Check if it needs further updating!!!

        self.tilemap = Tilemap(self,tile_size= 16)  #16x16 pixel rendering

        self.current_level = 0
        self.load_level(0)

        self.hud = HUD(self)
        
        

    def load_level(self, map_id):
        self.tilemap.load('Maps/' + str(map_id) + '.json')

        self.current_level = map_id

        self.mana_pickups = []
        self.mana_respawn_data = {}

        for mana in self.tilemap.extract([('Mana', 0)]):
            mana_rect = pygame.Rect(mana['pos'][0], mana['pos'][1], 16, 16)
            self.mana_pickups.append(pygame.Rect(mana['pos'][0], mana['pos'][1], 16, 16))

            if self.current_level == 2:
                mana_key = f"{int(mana['pos'][0])};{int(mana['pos'][1])}"
                self.mana_respawn_data[mana_key] = {'rect' : mana_rect, 'collected' : False, 'respawn_timer' : 0}
        print(f"Level {self.current_level}: Created {len(self.mana_respawn_data)} mana respawn entries")
        print(f"Mana respawn data: {self.mana_respawn_data}")

        self.goal = []
        for goal in self.tilemap.extract([('Goal', 0)]):
            self.goal.append(pygame.Rect(goal['pos'][0], goal['pos'][1], 16, 16))

        self.temp_blocks = {}
        self.temp_blocks_animation = {}
        for loc, tile in list(self.tilemap.tilemap.items()):
            if tile['type'] == 'Temp':
                self.temp_blocks[loc] = {'state' : 'solid', 'timer' : 0, 'respawn_timer' : 0, 'original_variant' : tile['variant']}

                self.temp_blocks_animation[loc] = {'shaking': self.assets['Temp/Shaking'].copy(), 'breaking' : self.assets['Temp/Breaking'].copy(), 'broken' : self.assets['Temp/Broken'].copy()}

        self.enemies = []
        self.boss = None
        for spawner in self.tilemap.extract([('Spawner', 0),('Spawner',1),('Spawner',2), ('Spawner',3)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
            elif spawner['variant'] == 1:
                self.enemies.append(Slime(self, spawner['pos'], (16,12)))
            elif spawner['variant'] == 2:
                self.enemies.append(Flamemite(self, spawner['pos'], (16,13)))
            elif spawner['variant'] == 3:
                boss = DarkMage(self, spawner['pos'], (10,16))
                self.enemies.append(boss)
                self.boss = boss



        self.projectiles = []
        self.particles = []
        self.sparks = []
        
        
        self.scroll = [0, 0]
        self.current_level = map_id
        self.death_timer = 0

        self.player.hp = self.player.max_hp
        self.player.mana = 0
        self.player.dead = False
        self.player.invincibility = 0
        self.player.attacking = 0
        self.player.dashing = 0
        self.player.dash_cd = 0

    
    def run(self):
        
        while True:
            
            if self.current_level == 0:
                self.display.blit(self.assets['background'], (0,0))
            elif self.current_level == 1:
                self.display.blit(self.assets['cavebackground'], (0,0))
            elif self.current_level == 2:
                self.display.blit(self.assets['castlebackground'], (0,0))
            

            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30 
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            for loc in list(self.temp_blocks.keys()):  #Temp tiles management
                block = self.temp_blocks[loc]
                
                tile_pos = [int(s) for s in loc.split(';')]
                block_rect = pygame.Rect(tile_pos[0] * 16, tile_pos[1] * 16, 16, 16)

                if loc in self.temp_blocks_animation:
                    for key, anim in self.temp_blocks_animation[loc].items():
                        if key != 'broken':
                            anim.update()

                if block['state'] == 'broken':
                    block['respawn_timer'] += 1
                    if block['respawn_timer'] >= 300:
                        
                        block['state'] = 'solid'
                        block['timer'] = 0
                        block['respawn_timer'] = 0
                        self.tilemap.tilemap[loc] = {'type' : 'Temp', 'variant' : block['original_variant'], 'pos' : tile_pos}
                        self.temp_blocks_animation[loc]['shaking'] = self.assets['Temp/Shaking'].copy()
                        self.temp_blocks_animation[loc]['breaking'] = self.assets['Temp/Breaking'].copy()
                        self.temp_blocks_animation[loc]['broken'] = self.assets['Temp/Broken'].copy()
                
                elif block['state'] in ['solid', 'shaking']:
                    #to test if player is on the block
                    player_on_block = (self.player.rect().bottom <= block_rect.top + 4 and
                                        self.player.rect().bottom >= block_rect.top - 4 and
                                        self.player.rect().right > block_rect.left + 2 and
                                        self.player.rect().left < block_rect.right - 2 and
                                        self.player.velocity[1] >= 0
                                        ) and self.player.collisions['down'] 

                    if player_on_block:
                        #print(f"Block {loc}: state={block['state']}, timer={block['timer']}") 
                        
                        if block['state'] == 'solid':
                            #print(f"Changing block {loc} to SHAKING") 
                            block['state'] = 'shaking'
                            block['timer'] = 0
                            self.temp_blocks_animation[loc]['shaking'] = self.assets['Temp/Shaking'].copy()
                            
                        elif block['state'] == 'shaking':
                            block['timer'] += 1
                            if block['timer'] >= 35:
                                #print(f"Changing block {loc} to BREAKING") 
                                block['state'] = 'breaking'
                                block['timer'] = 0
                                self.temp_blocks_animation[loc]['breaking'] = self.assets['Temp/Breaking'].copy()
                        
                elif block['state'] == 'breaking':
                    anim = self.temp_blocks_animation[loc]['breaking']
                    anim.update()

                    if anim.done:
                        #print(f"Block {loc} BROKEN → deleting tile")
                                
                        if loc in self.tilemap.tilemap:
                            del self.tilemap.tilemap[loc]
                        block['state'] = 'broken'
                        block['respawn_timer'] = 0

            if self.current_level == 0:        
                self.clouds.update()
                self.clouds.render(self.display, offset=render_scroll)
            self.tilemap.render(self.display, offset=render_scroll)

            for loc in self.temp_blocks:
                block = self.temp_blocks[loc]
                tile_pos = [int(s) for s in loc.split(';')]
                x = tile_pos[0] * 16 - render_scroll[0]
                y = tile_pos[1] * 16 - render_scroll[1]

                if block['state'] == 'solid':
                    pass

                elif block['state'] == 'shaking':
                    anim = self.temp_blocks_animation[loc]['shaking']
                    img = anim.img()
                    self.display.blit(img, (x,y))

                elif block['state'] == 'breaking':
                    anim = self.temp_blocks_animation[loc]['breaking']
                    img = anim.img()
                    self.display.blit(img, (x,y))

                elif block['state'] == 'broken':
                    img = self.temp_blocks_animation[loc]['broken']
                    self.display.blit(img,(x,y))



            pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 0.3 + 0.7
            for mana_pickup in self.mana_pickups:
                mana_img = self.assets['Mana'][0].copy()
                mana_img.set_alpha(int(255 * pulse))
                self.display.blit(mana_img, (mana_pickup.x - render_scroll[0], mana_pickup.y - render_scroll[1]))

                if random.random() < 0.02:
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 0.5
                    self.particles.append(Particle(self, 'ManaAmbience', mana_pickup.center, velocity=[math.cos(angle) * speed, math.sin(angle) * speed], frame=random.randint(0,7)))

            for goal in self.goal:
                goal_img = self.assets['Goal'][0].copy()
                goal_img.set_alpha(int(255 * pulse))
                self.display.blit(goal_img, (goal.x - render_scroll[0], goal.y - render_scroll[1]))
            
            
            if self.player.dead:
                self.death_timer += 1
                if self.death_timer > 90:
                    self.load_level(self.current_level)
                    self.player.dead = False
                    self.death_timer = 0

            for enemy in self.enemies.copy():
                enemy.update(self.tilemap, movement = (0,0))
                enemy.render(self.display, offset =render_scroll)

            self.player.update(self.tilemap, (self.movement[1]- self.movement[0], 0))
            self.player.render(self.display, offset=render_scroll)

            
            player_tile_pos = (int(self.player.rect().centerx // 16), int(self.player.rect().centery // 16))
            tile_loc = str(player_tile_pos[0]) + ';' + str(player_tile_pos[1])
            if tile_loc in self.tilemap.tilemap:
                tile = self.tilemap.tilemap[tile_loc]
                if tile['type'] in ['Lava', 'Hazards'] :
                    self.player.hp = 0
                    self.player.die()

            for enemy in self.enemies:
                if self.player.rect().colliderect(enemy.rect()) and self.player.dashing == 0:
                    self.player.take_damage(10)

            for mana_pickup in self.mana_pickups.copy():
                if self.player.rect().colliderect(mana_pickup):
                    self.player.collect_mana(self.player.max_obtainable_mana)
                    
                    for i in range(10):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 2
                        self.particles.append(Particle(self, 'ManaAmbience', mana_pickup.center, velocity= [math.cos(angle) * speed, math.sin(angle) * speed], frame= random.randint(0,7)))

                    if self.current_level == 2:
                        mana_key = f"{int(mana_pickup.x)};{int(mana_pickup.y)}"  # respawn timer mechanic of mana in final stage
                        if mana_key in self.mana_respawn_data:
                            self.mana_respawn_data[mana_key]['collected'] = True
                            self.mana_respawn_data[mana_key]['respawn_timer'] = 0
                    self.mana_pickups.remove(mana_pickup)
            if self.current_level == 2:
                for mana_key, data in self.mana_respawn_data.items():
                    if data['collected']:
                        data['respawn_timer'] += 1

                        if data['respawn_timer'] % 60:
                            print(f"Mana {mana_key}: timer={data['respawn_timer']}/1200")
                        
                        if data['respawn_timer'] >= 1200:
                            print(f"RESPAWNING MANA at {mana_key}") 
                            data['collected'] = False
                            data['respawn_timer'] = 0

                            self.mana_pickups.append(data['rect'])

                            for i in range(15):
                                angle = random.random() * math.pi * 2
                                speed = random.random() * 1.5
                                self.particles.append(Particle(self, 'ManaAmbience', data['rect'].center,
                                    velocity=[math.cos(angle) * speed, math.sin(angle) * speed],
                                    frame=random.randint(0, 7)))


            for goal in self.goal:
                if self.player.rect().colliderect(goal):

                    for i in range(30):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 4
                        self.sparks.append(Spark(goal.center, angle, 3 + random.random()))
                    
                    try:
                        self.load_level(self.current_level + 1)
                    except FileNotFoundError:
                        print("You Win!")  #Subject to change
                    break


            #[[x,y], direction, timer]
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1

                projectile_type = projectile[4] if len(projectile) > 4 else 'player_basic'

                if projectile_type == 'player_strong':
                    img = self.assets['Charged_Projectile']
                elif projectile_type == 'darkmage':
                    img = self.assets['EProjectile']
                elif projectile_type == 'flamemite':
                    img = self.assets['FlameProjectile']
                else:
                    img = self.assets['Projectile']

                should_flip = projectile[1] < 0
                flipped_img = pygame.transform.flip(img, should_flip, False)


                self.display.blit(flipped_img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                            self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0) , 2 + random.random()))

                elif projectile[2] > 360 :
                    self.projectiles.remove(projectile)

                else: 
                    is_enemy_projectile = projectile_type in ['darkmage', 'flamemite']

                    proj_rect = pygame.Rect(projectile[0][0] - 4, projectile[0][1] - 4, 8, 8)

                    if is_enemy_projectile:
                        if self.player.rect().colliderect(proj_rect) and self.player.dashing == 0:
                            self.projectiles.remove(projectile)
                            damage = projectile[3] if len(projectile) > 3 else 15
                            self.player.take_damage(damage)

                            for i in range(10):
                                angle = random.random() * math.pi * 2
                                self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                    
                    else :
                        for enemy in self.enemies.copy():
                            if enemy.rect().colliderect(proj_rect):
                                damage = projectile[3] if len(projectile) > 3 else 25
                                enemy.health -= damage

                                self.projectiles.remove(projectile)

                                for i in range(8):
                                    angle = random.random() * math.pi * 2
                                    self.sparks.append(Spark(enemy.rect().center, angle, random.random()))

                                if enemy.health <= 0:
                                    enemy.die()
                                    self.enemies.remove(enemy)
                                    if enemy == self.boss:
                                        self.boss = None

                                    for i in range(20):
                                        angle = random.random() * math.pi * 2
                                        self.sparks.append(Spark(enemy.rect().center, angle, 2 + random.random()))
                                
                                break          

            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset = render_scroll)
                if kill:
                    self.sparks.remove(spark)

            
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset = render_scroll)
                if particle.type == 'flames':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)
            

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.player.jump()
                    if event.key == pygame.K_x:
                        if not self.player.basic_attack():
                            self.player.attack_fail()
                    if event.key == pygame.K_z:
                        if not self.player.strong_attack():
                            self.player.attack_fail()
                    if event.key == pygame.K_c:
                        self.player.dash()

                
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            if self.boss and self.boss in self.enemies:
                self.hud.render_boss_health(self.display, self.boss, "DARK MAGE")

            self.hud.render(self.display)

            self.hud.render_ability_indicators(self.display)

            if self.player.dead:
                self.hud.render_death_screen(self.display)

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60) # for keeping the game run at 60 fps
Game().run()






  

