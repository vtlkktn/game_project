import pygame
from settings import *
from player import Player
from sprites import Generic
from core import Core
from arrow import Arrow


class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.all_sprites = CameraGroup()
        self.core = Core(max_health=1800)
        

        self.setup()
        self.setup_core()
        self.setup_bar()

        self.arrow = None

    def setup(self):
        self.player = Player((1500, 1250), self.all_sprites)
        Generic(
            pos=(0, 0),
            surf=pygame.image.load('ground.png').convert_alpha(),
            groups=self.all_sprites,
            z=LAYERS['ground'])

    def setup_core(self):
        core_pos = (1500, 1250)
        core_surface = pygame.image.load('core.png').convert_alpha()
        core_surface = pygame.transform.scale(core_surface, (90, 90))
        core_rect = core_surface.get_rect(topleft=core_pos)
        Generic(
            pos=core_pos,
            surf=core_surface,
            groups=self.all_sprites,
            z=LAYERS['core'])
        self.core_rect = core_rect
        core_center = self.core_rect.center
        self.arrow = Arrow(core_center)
        self.all_sprites.add(self.arrow)



    def setup_bar(self):
        self.bar_surface = pygame.Surface((90, 15))
        bar_pos = (1500, 1350)
        bar_length = (self.core.current_health / self.core.max_health) * 90
        self.bar_surface.fill((0, 0, 0))
        pygame.draw.rect(self.bar_surface, (255, 0, 0), (0, 0, bar_length, 15))
        font = pygame.font.Font(None, 24)
        text = font.render(f"{self.core.current_health}/{self.core.max_health}", True, (255, 255, 255))
        text_rect = text.get_rect(center=(45, 8))
        self.bar_surface.blit(text, text_rect)
        bar_rect = self.bar_surface.get_rect(topleft=bar_pos)
        bar_sprite = Generic(
            pos=bar_pos, 
            surf=self.bar_surface,
            groups=self.all_sprites, 
            z=LAYERS['bar'])
        self.bar_sprite = bar_sprite
        self.bar_rect = bar_rect
    
    def run(self, dt):
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt)

        if self.arrow is not None:
            player_rect = self.player.rect  # Замість числа встановлюємо гравця
            self.arrow.update(player_rect)




class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        player_center = pygame.math.Vector2(player.rect.center)
        self.offset = SCREEN_WIDTH / 2 - player_center.x, SCREEN_HEIGHT / 2 - player_center.y

        for layer in sorted(LAYERS.values()):
            for sprite in self.sprites():
                if sprite.z == layer:
                    offset_rect = sprite.rect.move(self.offset)
                    self.display_surface.blit(sprite.image, offset_rect)


