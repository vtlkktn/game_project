import pygame
from settings import *
from utils import import_folder


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)

        self.size = (50, 50)
        self.import_assets()
        self.status = 'up_idle'
        self.frame_index = 0

        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.z = LAYERS['main']

        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

    def import_assets(self):
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
        }

        for animation in self.animations.keys():
            full_path = '../assets/images/character/' + animation
            self.animations[animation] = self.load_and_scale_images(full_path)

    def load_and_scale_images(self, path):
        frames = import_folder(path)
        scaled_frames = [pygame.transform.scale(frame, self.size) for frame in frames]
        return scaled_frames

    def animate(self, dt):
        self.frame_index += 1 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        self.image = self.animations[self.status][int(self.frame_index)]

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.direction.y = -1
            self.status = 'up'
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
            self.status = 'down'
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.status = 'right'
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.status = 'left'
        else:
            self.direction.x = 0

    def get_status(self):
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'

    def move(self, dt):
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        new_pos = self.pos + self.direction * self.speed * dt

        map_width = 5000  
        map_height = 5000

    # Обмежуємо рух гравця в межах карті
        if 0 <= new_pos.x <= map_width:
            self.pos.x = new_pos.x

        if 0 <= new_pos.y <= map_height:
            self.pos.y = new_pos.y


        self.rect.center = self.pos


    def update(self, dt):
        self.input()
        self.get_status()

        self.move(dt)
        self.animate(dt)