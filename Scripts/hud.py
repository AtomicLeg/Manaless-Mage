import pygame
import math

class HUD:
    
    def __init__(self, game):
        self.game = game
        
        
        self.hp_bar_color = (220, 50, 50)  
        self.hp_bg_color = (80, 20, 20)    
        self.mana_bar_color = (100, 150, 255)  
        self.mana_bg_color = (30, 50, 100)     
        self.border_color = (255, 255, 255)    
        self.text_color = (255, 255, 255)      
        self.shadow_color = (0, 0, 0)          
        
        
        self.bar_width = 100
        self.bar_height = 8
        self.bar_border = 1
        self.bar_spacing = 4
        
        
        self.padding_x = 10
        self.padding_y = 10
        
        
        self.font_size = 14
        try:
            self.font = pygame.font.Font(None, self.font_size)
            self.large_font = pygame.font.Font(None, 18)
            self.huge_font = pygame.font.Font(None, 24) #For ability indicators
        except:
            self.font = pygame.font.SysFont('arial', self.font_size)
            self.large_font = pygame.font.SysFont('arial', 18)
            self.huge_font = pygame.font.SysFont('arial', 24)
    
    def draw_bar(self, surf, x, y, current, maximum, bar_color, bg_color, label=""):
        
        percentage = max(0, min(1, current / maximum)) if maximum > 0 else 0
        fill_width = int(self.bar_width * percentage)
        
        bg_rect = pygame.Rect(x, y, self.bar_width, self.bar_height)
        pygame.draw.rect(surf, bg_color, bg_rect)
        
        if fill_width > 0:
            fill_rect = pygame.Rect(x, y, fill_width, self.bar_height)
            pygame.draw.rect(surf, bar_color, fill_rect)
        
        pygame.draw.rect(surf, self.border_color, bg_rect, self.bar_border)
        
        if label:
            label_surf = self.font.render(label, False, self.text_color)
            label_x = x - label_surf.get_width() - 4
            label_y = y + (self.bar_height - label_surf.get_height()) // 2
            
            shadow_surf = self.font.render(label, False, self.shadow_color)
            surf.blit(shadow_surf, (label_x + 1, label_y + 1))
            surf.blit(label_surf, (label_x, label_y))
        
        value_text = f"{int(current)}/{int(maximum)}"
        value_surf = self.font.render(value_text, False, self.text_color)
        value_x = x + self.bar_width + 4
        value_y = y + (self.bar_height - value_surf.get_height()) // 2
        
        shadow_surf = self.font.render(value_text, False, self.shadow_color)
        surf.blit(shadow_surf, (value_x + 1, value_y + 1))
        surf.blit(value_surf, (value_x, value_y))
    
    def draw_text_with_shadow(self, surf, text, x, y, font=None, color=None):
        
        if font is None:
            font = self.font
        if color is None:
            color = self.text_color
        
        shadow_surf = font.render(str(text), False, self.shadow_color)
        surf.blit(shadow_surf, (x + 1, y + 1))
    
        text_surf = font.render(str(text), False, color)
        surf.blit(text_surf, (x, y))
    
    def render(self, surf):
        
        player = self.game.player
        
        
        x = self.padding_x + 20  # Leave space for labels
        y = self.padding_y
        
        
        self.draw_bar(surf, x, y, player.hp, player.max_hp, self.hp_bar_color, self.hp_bg_color, "HP")
        
        y += self.bar_height + self.bar_spacing
        self.draw_bar(surf, x, y, player.mana, player.max_mana, self.mana_bar_color, self.mana_bg_color, "MP")
        
        level_text = f"Level {self.game.current_level + 1}"
        level_x = surf.get_width() - self.padding_x
        level_y = self.padding_y
        
        level_surf = self.large_font.render(level_text, False, self.text_color)
        level_x -= level_surf.get_width()
        
        shadow_surf = self.large_font.render(level_text, False, self.shadow_color)
        surf.blit(shadow_surf, (level_x + 1, level_y + 1))
        surf.blit(level_surf, (level_x, level_y))
    
    def render_boss_health(self, surf, enemy, boss_name="Dark Mage"):
        
        boss_bar_width = 150
        boss_bar_height = 10
        
        x = (surf.get_width() - boss_bar_width) // 2
        y = 20
        
        name_surf = self.large_font.render(boss_name, False, self.text_color)
        name_x = x + (boss_bar_width - name_surf.get_width()) // 2
        name_y = y - 14
        
        shadow_surf = self.large_font.render(boss_name, False, self.shadow_color)
        surf.blit(shadow_surf, (name_x + 1, name_y + 1))
        surf.blit(name_surf, (name_x, name_y))
        
        max_health = 400  
        percentage = max(0, min(1, enemy.health / max_health))
        fill_width = int(boss_bar_width * percentage)
        
        bg_rect = pygame.Rect(x, y, boss_bar_width, boss_bar_height)
        pygame.draw.rect(surf, self.hp_bg_color, bg_rect)
        
        if fill_width > 0:
            fill_rect = pygame.Rect(x, y, fill_width, boss_bar_height)
            boss_color = (255, 100, 100)  
            pygame.draw.rect(surf, boss_color, fill_rect)
        
        pygame.draw.rect(surf, self.border_color, bg_rect, 2)
        
        health_text = f"{int(enemy.health)}/{max_health}"
        health_surf = self.font.render(health_text, False, self.text_color)
        health_x = x + (boss_bar_width - health_surf.get_width()) // 2
        health_y = y + boss_bar_height + 2
        
        shadow_surf = self.font.render(health_text, False, self.shadow_color)
        surf.blit(shadow_surf, (health_x + 1, health_y + 1))
        surf.blit(health_surf, (health_x, health_y))
    
    def render_ability_indicators(self, surf):
        
        player = self.game.player
        
        x = self.padding_x
        y = surf.get_height() - self.padding_y - 45
        
        dash_available = player.dash_cd <= 0
        dash_color = (100, 255, 100) if dash_available else (100, 100, 100)
        dash_text = "DASH" if dash_available else f"DASH {player.dash_cd // 60 + 1}s"
        
        self.draw_text_with_shadow(surf, dash_text, x, y, color=dash_color)
     
        y += 15
        basic_available = player.can_cast(player.b_attack_cost)
        basic_color = (150, 200, 255) if basic_available else (100, 100, 100)
        basic_text = f"ATK (X): {player.b_attack_cost}MP"
        
        self.draw_text_with_shadow(surf, basic_text, x, y, color=basic_color)
        
        y += 15
        strong_available = player.can_cast(player.C_attack_cost)
        strong_color = (255, 150, 255) if strong_available else (100, 100, 100)
        strong_text = f"STRONG (Z): {player.C_attack_cost}MP"
        
        self.draw_text_with_shadow(surf, strong_text, x, y, color=strong_color)
    
    def render_death_screen(self, surf):

        overlay = pygame.Surface(surf.get_size())
        overlay.set_alpha(180)
        overlay.fill((50, 0, 0))
        surf.blit(overlay, (0, 0))
        
        death_text = "YOU DIED"
        death_surf = self.huge_font.render(death_text, False, (255, 100, 100))
        death_x = (surf.get_width() - death_surf.get_width()) // 2
        death_y = (surf.get_height() - death_surf.get_height()) // 2 - 10
        
        shadow_surf = self.huge_font.render(death_text, False, self.shadow_color)
        surf.blit(shadow_surf, (death_x + 2, death_y + 2))
        surf.blit(death_surf, (death_x, death_y))
        
        respawn_text = "Respawning..."
        respawn_surf = self.large_font.render(respawn_text, False, self.text_color)
        respawn_x = (surf.get_width() - respawn_surf.get_width()) // 2
        respawn_y = death_y + 20
        
        self.draw_text_with_shadow(surf, respawn_text, respawn_x, respawn_y)
    
    def render_victory_screen(self, surf):
        
        overlay = pygame.Surface(surf.get_size())
        overlay.set_alpha(150)
        overlay.fill((0, 50, 0))
        surf.blit(overlay, (0, 0))
        
        victory_text = "LEVEL COMPLETE!"
        victory_surf = self.huge_font.render(victory_text, False, (100, 255, 100))
        victory_x = (surf.get_width() - victory_surf.get_width()) // 2
        victory_y = (surf.get_height() - victory_surf.get_height()) // 2
        
        shadow_surf = self.huge_font.render(victory_text, False, self.shadow_color)
        surf.blit(shadow_surf, (victory_x + 2, victory_y + 2))
        surf.blit(victory_surf, (victory_x, victory_y))
