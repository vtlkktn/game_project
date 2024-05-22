import pygame
from settings import *
from player import Player
from sprites import Generic
from core import Core


class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.all_sprites = CameraGroup()
        self.core = Core(max_health=1800)

        self.setup()
        self.setup_core()

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

    def run(self, dt):
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)
        self.draw_core(self.core_rect)
        self.all_sprites.update(dt)

    def draw_core(self, core_rect):
        core_hp = self.core.current_health
        bar_width = 5  # Фіксована ширина риски
        bar_height = core_hp / self.core.max_health * core_rect.height
        bar_color = (0, 255, 0)  # Зелений колір для риски
        bar_rect = pygame.Rect(core_rect.right + 5, core_rect.top, bar_width, bar_height)  # Прямокутник для риски

        # Малювання риски
        pygame.draw.rect(self.display_surface, bar_color, bar_rect)

        # Опціонально можна намалювати контур риски для більшої видимості
        pygame.draw.rect(self.display_surface, (0, 0, 0), bar_rect, 1)

        # Додавання прямокутника як атрибуту для майбутнього використання
        self.core_rect = core_rect





class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        self.offset.x = SCREEN_WIDTH / 2 - player.rect.centerx
        self.offset.y = SCREEN_HEIGHT / 2 - player.rect.centery

        for layer in sorted(LAYERS.values()):
            for sprite in self.sprites():
                if sprite.z == layer:
                    if layer == LAYERS['core']:
                        offset_rect = sprite.rect.move(self.offset)
                        self.display_surface.blit(sprite.image, offset_rect)
                    else:
                        offset_rect = sprite.rect.move(self.offset)
                        self.display_surface.blit(sprite.image, offset_rect)
