import sys
import pygame
import random
import math
import os

from components.support import load_image, load_images, Animation, Text, scale_images
from components.entities import PhysicsEntity, Player, Enemy, Gem
from components.tilemap import Tilemap
from components.clouds import Clouds
from components.particle import Particle
from components.button import Button


class AdventureGame:
    def __init__(self) -> None:
        pygame.init()

        WIDTH, HEIGHT = 1024, 768

        pygame.display.set_caption('Осінні Пригоди Кота')

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.display = pygame.Surface((WIDTH / 2, HEIGHT / 2), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((WIDTH / 2, HEIGHT / 2))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        player_sprite = load_image('entities/player.png')

        self.assets = {
            'decor': load_images('tiles/decor'),
            'large_decor': load_images('tiles/large_decor'),
            'grass': load_images('tiles/grass'),
            'clouds': load_images('clouds'),
            'back_trees': load_image('trees.png'),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=30),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=8),
            'player': pygame.transform.scale(player_sprite, (21, 21)),
            'player/idle': Animation(scale_images(load_images('entities/player/idle'), (21, 21)), img_dur=45),
            'player/run': Animation(scale_images(load_images('entities/player/run'), (21, 21)), img_dur=4),
            'player/jump': Animation(scale_images(load_images('entities/player/jump'), (21, 21)), img_dur=4),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'menu_trees': load_image('menu_screen/0.png'),
            'menu_water': load_image('menu_screen/1.png'),
            'menu_grass': load_image('menu_screen/2.png'),
            'gem/idle': Animation(load_images('entities/gem/idle'), img_dur=25),
        }

        self.trees_width = self.assets['back_trees'].get_width()

        self.sfx = {
            'jump': pygame.mixer.Sound('assets/sfx/jump.mp3'),
            'explosion': pygame.mixer.Sound('assets/sfx/explosion.mp3'),
            'ambience': pygame.mixer.Sound('assets/sfx/ambience.wav'),
            'gem': pygame.mixer.Sound('assets/sfx/gem.mp3'),
        }

        self.vol_music = 0.008
        self.vol_ambience = 0.6
        self.vol_explosion = 0.8
        self.vol_jump = 0.7
        self.vol_gem = 0.9

        self.sfx['ambience'].set_volume(self.vol_ambience)
        self.sfx['explosion'].set_volume(self.vol_explosion)
        self.sfx['jump'].set_volume(self.vol_jump)
        self.sfx['gem'].set_volume(self.vol_gem)

        pygame.mixer.music.load('assets/music.mp3')
        pygame.mixer.music.set_volume(self.vol_music)
        pygame.mixer.music.play(-1)

        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.player = Player(self, (50, 50), (11, 16))

        self.tilemap = Tilemap(self, tile_size=16)

        self.level = 0
        self.load_level(self.level)

        self.screenshake = 0

        self.last_state = 'menu'

    def get_font(self, size):
        return pygame.font.Font('assets/font.ttf', size)

    def load_level(self, lvl_id):
        self.tilemap.load('assets/maps/' + str(lvl_id) + '.json')

        self.enemies = []
        self.gems = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1), ('spawners', 2)]):
            if spawner['variant'] == 0:
                self.player.rect_pos.x = spawner['pos'][0]
                self.player.rect_pos.y = spawner['pos'][1]
                self.player.air_time = 0
            elif spawner['variant'] == 2:
                self.gems.append(Gem(self, spawner['pos'], (16, 16)))
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (11, 16)))

        self.dead = 0
        self.particles = []
        self.collided = 0
        self.transition = -30
        self.level_ended = False
        self.wait_time = 0
        self.scroll = [0, 0]
        self.score = 0
        self.max_score = len(self.gems)

    def run(self):

        self.sfx['ambience'].play(-1)

        while True:
            self.display.fill((0, 0, 0, 0))
            self.display_2.fill((59, 107, 156))

            self.scroll[0] += (self.player.rect_pos.centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect_pos.centery - self.display.get_height() / 2 - self.scroll[1]) / 90
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            if int(self.scroll[1]) >= 18:
                self.scroll[1] = 18

            if int(self.scroll[0]) <= -100:
                self.scroll[0] = -100

            speed = 0.3
            for x in range(-10, 200):
                self.display_2.blit(self.assets['back_trees'],
                                    ((x * self.trees_width) - render_scroll[0] * speed, 270 - render_scroll[1] * speed))
                self.display_2.blit(self.assets['back_trees'],
                                    ((x * self.trees_width) - render_scroll[0] * speed, 220 - render_scroll[1] * speed))

            self.clouds.update()
            self.clouds.render(self.display_2, offset=render_scroll)

            self.screenshake = max(0, self.screenshake - 1)

            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.transition = min(30, self.transition + 1)
                if self.dead > 50:
                    self.load_level(self.level)

            self.tilemap.render(self.display, offset=render_scroll)

            if (self.score == self.max_score) and self.player.rect_pos.colliderect(self.tilemap.end_tile()):
                self.level_ended = True

            if self.level_ended:
                self.wait_time += 1

            if self.wait_time > 40:
                self.transition += 1
                if self.transition > 30:
                    self.level = min(self.level + 1, len(os.listdir('assets/maps')) - 1)
                    self.load_level(self.level)

            if self.transition < 0:
                self.transition += 1

            for gem in self.gems.copy():
                kill = gem.update(self.tilemap)
                gem.render(self.display, offset=render_scroll)
                if kill:
                    self.score += 1
                    self.gems.remove(gem)

            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.display_2.blit(display_sillhouette, offset)

            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if kill:
                    self.particles.remove(particle)

            for enemy in self.enemies.copy():
                enemy.update(self.tilemap)
                enemy.render(self.display, offset=render_scroll)

                if self.player.rect_pos.colliderect(enemy.rect_pos):
                    self.collided += 1

            if self.collided == 1:
                self.sfx['explosion'].play()
                self.dead += 1
                self.screenshake = max(25, self.screenshake)
                for num in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 3
                    self.particles.append(Particle(self, 'particle', self.player.rect_pos.center,
                                                   velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                             math.sin(angle + math.pi) * speed * 0.5],
                                                   frame=random.randint(0, 7)))
                self.collided += 1

            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)

            Text(self.display, f'Рахунок:{self.score}/{self.max_score}', self.get_font(8), (10, 10)).render()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and not self.level_ended:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        if self.player.jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        if self.player.jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_ESCAPE:
                        self.pause_menu()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False

            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255),
                                   (self.display.get_width() // 2, self.display.get_height() // 2),
                                   (30 - abs(self.transition)) * 10)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))

            self.display_2.blit(self.display, (0, 0))

            screenshake_offset = (
                random.random() * self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)
            pygame.display.update()
            self.clock.tick(60)

    def menu(self):

        self.sfx['ambience'].stop()

        self.load_level(self.level)

        self.transition = 0
        switch = 1

        if self.level == 0:
            play_button_text = 'Грати'
        else:
            play_button_text = 'Продовжити'

        button_width, button_height = 100, 40
        screen_center_x = self.display.get_width() / 2

        play_button = Button(
            self.display,
            self.get_font(11),
            play_button_text,
            button_width,
            button_height,
            (screen_center_x - button_width // 2 - 110, 320),
            6
        )
        option_button = Button(self.display, self.get_font(11), 'Опції', button_width, button_height,
                               (screen_center_x - button_width // 2, 320), 6)
        quit_button = Button(self.display, self.get_font(11), 'Вийти', button_width, button_height,
                             (screen_center_x - button_width // 2 + 110, 320), 6)

        while True:
            self.display.fill((0, 0, 0, 0))
            self.display_2.fill((59, 107, 156))
            self.display_2.blit(self.assets['menu_trees'], (0, 0))
            self.display_2.blit(self.assets['menu_water'], (0, 0))
            self.display.blit(self.assets['menu_grass'], (screen_center_x / 2, 0))

            if not switch:
                self.transition += 1
                if self.transition > 30:
                    self.transition = - 30
                    self.run()
            if self.transition < 0:
                self.transition += 1

            Text(self.display, 'Осінні Пригоди Котеняти', self.get_font(15), (screen_center_x - 160, 50)).render()

            play_button.render()
            if play_button.done == True:
                switch = 0

            option_button.render()
            if option_button.done == True:
                self.last_state = 'menu'
                self.option_menu()
                option_button.done = False

            quit_button.render()
            if quit_button.done == True:
                pygame.quit()
                sys.exit()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            for offset in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                self.display_2.blit(display_sillhouette, offset)

            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255),
                                   (self.display.get_width() // 2, self.display.get_height() // 2),
                                   (30 - abs(self.transition)) * 10)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))

            self.display_2.blit(self.display, (0, 0))

            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

    def pause_menu(self):

        self.movement = [False, False]

        self.sfx['ambience'].stop()

        self.transition = 0
        switch = 1

        play_button = Button(self.display, self.get_font(11), 'Назад', 100, 40, (205, 150), 6)
        option_button = Button(self.display, self.get_font(11), 'Опції', 100, 40, (205, 225), 6)
        quit_button = Button(self.display, self.get_font(11), 'Меню', 100, 40, (205, 300), 6)

        while True:
            self.display.fill((0, 0, 0, 0))
            self.display_2.fill((59, 107, 156))

            if not switch:
                self.transition += 1
                if self.transition > 30:
                    self.transition = - 30
                    self.run()
            if self.transition < 0:
                self.transition += 1

            Text(self.display, 'Пауза', self.get_font(22), (192, 50)).render()

            play_button.render()
            if play_button.done == True:
                switch = 0

            option_button.render()
            if option_button.done == True:
                self.last_state = 'pause'
                self.option_menu()
                option_button.done = False

            quit_button.render()
            if quit_button.done == True:
                self.menu()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            for offset in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                self.display_2.blit(display_sillhouette, offset)

            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255),
                                   (self.display.get_width() // 2, self.display.get_height() // 2),
                                   (30 - abs(self.transition)) * 10)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))

            self.display_2.blit(self.display, (0, 0))

            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

    def option_menu(self):

        self.movement = [False, False]

        self.sfx['ambience'].stop()

        self.transition = 0
        switch = 1

        back_button = Button(self.display, self.get_font(11), 'Назад', 100, 40, (205, 300), 6)
        sound_button_l = Button(self.display, self.get_font(16), '<', 30, 25, (200, 125), 6)
        sound_button_r = Button(self.display, self.get_font(16), '>', 30, 25, (415, 125), 6)
        volume_buttom_l = Button(self.display, self.get_font(16), '<', 30, 25, (200, 215), 6)
        volume_buttom_r = Button(self.display, self.get_font(16), '>', 30, 25, (415, 215), 6)

        sounds = list(self.sfx.copy())
        sounds.append('music')
        sound = 1

        sound_translations = {
            'jump': 'Стрибок',
            'explosion': 'Зіткнення',
            'ambience': 'Фон',
            'gem': 'Рибка',
            'music': 'Музика'
        }

        while True:
            self.display.fill((0, 0, 0, 0))
            self.display_2.fill((59, 107, 156))

            if not switch:
                self.transition += 1
                if self.transition > 30:
                    self.transition = - 30
                    self.run()
            if self.transition < 0:
                self.transition += 1

            Text(self.display, 'Опції', self.get_font(22), (180, 50)).render()

            Text(self.display, 'Звук:', self.get_font(16), (50, 125)).render()
            Text(self.display, 'Гучність:', self.get_font(16), (50, 215)).render()

            sound_name = sounds[sound]
            translated_sound_name = sound_translations.get(sound_name, sound_name)
            Text(self.display, translated_sound_name, self.get_font(16), (250, 125)).render()

            sound_button_l.render()
            if sound_button_l.done == True:
                sound = (sound - 1) % len(sounds)
                sound_button_l.done = False
            sound_button_r.render()
            if sound_button_r.done == True:
                sound = (sound + 1) % len(sounds)
                sound_button_r.done = False

            volume_buttom_l.render()
            volume_buttom_r.render()
            if sounds[sound] in self.sfx or sounds[sound] == 'music':
                current_vol = getattr(self, f'vol_{sounds[sound]}', None)
                if current_vol is not None:
                    Text(self.display, f'{round(current_vol * 100)}', self.get_font(16), (300, 215)).render()
                    if volume_buttom_l.done == True:
                        current_vol -= 0.1
                        if current_vol < 0:
                            current_vol = 0.0
                        setattr(self, f'vol_{sounds[sound]}', round(current_vol, 2))
                        if sounds[sound] == 'music':
                            pygame.mixer.music.set_volume(current_vol)
                        else:
                            self.sfx[sounds[sound]].set_volume(current_vol)
                        volume_buttom_l.done = False

                    if volume_buttom_r.done == True:
                        current_vol += 0.1
                        if current_vol > 1:
                            current_vol = 1.0
                        setattr(self, f'vol_{sounds[sound]}', round(current_vol, 2))
                        if sounds[sound] == 'music':
                            pygame.mixer.music.set_volume(current_vol)
                        else:
                            self.sfx[sounds[sound]].set_volume(current_vol)
                        volume_buttom_r.done = False

            back_button.render()
            if back_button.done == True:
                if self.last_state == 'menu':
                    self.menu()
                elif self.last_state == 'pause':
                    self.pause_menu()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            for offset in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                self.display_2.blit(display_sillhouette, offset)

            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255),
                                   (self.display.get_width() // 2, self.display.get_height() // 2),
                                   (30 - abs(self.transition)) * 10)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))

            self.display_2.blit(self.display, (0, 0))

            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)


AdventureGame().menu()
