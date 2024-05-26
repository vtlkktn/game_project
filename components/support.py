import os
import pygame

BASE_PATH = 'assets/images/'


def load_image(path):
    img = pygame.image.load(BASE_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img


def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images


class Animation:
    def __init__(self, images, img_dur=5, loop=True) -> None:
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0

    def copy_anim(self):
        return Animation(self.images, self.img_duration, self.loop)

    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True

    def img(self):
        return self.images[int(self.frame / self.img_duration)]


class Text:
    def __init__(self, display, text, font, pos) -> None:
        self.game = display
        self.text = text
        self.font = font
        self.pos = list(pos)

    def render(self):
        text = self.font.render(self.text, False, (255, 255, 255))
        self.game.blit(text, self.pos)


def scale_images(images, size):
    return [pygame.transform.scale(image, size) for image in images]
