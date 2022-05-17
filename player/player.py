import os.path
import pygame


class Player(pygame.sprite.Sprite):

    tiles = 3

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.movex = 0
        self.movey = 0
        self.frame = 0

        self.images = []

        texture = pygame.image.load(os.path.join('assets', 'sprites', 'hero.png')).convert()

        self.images.append(texture)
        self.image = pygame.transform.scale(self.images[0], (64, 64))

        self.rect = self.image.get_rect()

    def _move(self, x, y):
        self.movex += x
        self.movey += y

    def move(self, event, down):
        if event.key == ord('w') or event.key == pygame.K_UP:
            self._move(0, -self.tiles if down else self.tiles)
        if event.key == ord('a') or event.key == pygame.K_LEFT:
            self._move(-self.tiles if down else self.tiles, 0)
        if event.key == ord('s') or event.key == pygame.K_DOWN:
            self._move(0, self.tiles if down else -self.tiles)
        if event.key == ord('d') or event.key == pygame.K_RIGHT:
            self._move(self.tiles if down else -self.tiles, 0)

    def update(self):
        self.rect.x += self.movex
        self.rect.y += self.movey


