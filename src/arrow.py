import pygame
import math

class Arrow(pygame.sprite.Sprite):
    def __init__(self, core_center):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (255, 0, 0), ((15, 0), (0, 30), (30, 30)))
        self.rect = self.image.get_rect()
        self.core_center = core_center
        self.z = 0

    def update(self, player_rect):
        distance = math.hypot(self.core_center[0] - player_rect.centerx, self.core_center[1] - player_rect.centery)
        angle = math.atan2(self.core_center[1] - player_rect.centery, self.core_center[0] - player_rect.centerx)
        offset = 50
        self.rect.centerx = player_rect.centerx + int(math.cos(angle) * offset)
        self.rect.centery = player_rect.centery + int(math.sin(angle) * offset)
        self.image = pygame.transform.rotate(self.image, math.degrees(angle) - 90)
