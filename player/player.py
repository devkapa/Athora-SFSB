import os.path
import pygame


class Player(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.movex = 0
        self.movey = 0
        self.frame = 0

        self.images = []

        texture = pygame.image.load(os.path.join('assets', 'sprites', 'hero.png')).convert()
        self.images.append(texture)
        self.image = self.images[0]
        self.rect = self.image.get_rect()

    def move(self, x, y):
        self.movex += x
        self.movey += y

    def update(self):
        self.rect.x += self.movex
        self.rect.y += self.movey


