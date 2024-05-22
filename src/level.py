import pygame
from settings import *
from player import Player
from sprites import Generic


class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.all_sprites = CameraGroup()

        self.setup()

    def setup(self):
        self.player = Player((640, 360), self.all_sprites)
        Generic(
            pos = (0, 0),
            surf = pygame.image.load('ground.png').convert_alpha(),
            groups = self.all_sprites, 
            z = LAYERS['ground'])

    def run(self, dt):
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt)


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
                    offset_rect = sprite.rect.move(self.offset)
                    self.display_surface.blit(sprite.image, offset_rect)
