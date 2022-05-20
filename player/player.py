import os.path

import pygame.image


class Player:

    VELOCITY = 2

    HEALTH = 10
    DAMAGE = pygame.USEREVENT + 1

    PLAYER_WIDTH, PLAYER_HEIGHT = 64, 64
    SPAWN_X, SPAWN_Y = 0, 0

    PLAYER_LEFT_IMG = pygame.image.load(os.path.join('assets', 'sprites', 'hero.png'))
    PLAYER_LEFT = pygame.transform.scale(PLAYER_LEFT_IMG, (PLAYER_WIDTH, PLAYER_HEIGHT))

    HEART_WIDTH, HEART_HEIGHT = 36, 36

    FULL_HEART_IMG = pygame.image.load(os.path.join('assets', 'textures', 'full_heart.png'))
    EMPTY_HEART_IMG = pygame.image.load(os.path.join('assets', 'textures', 'empty_heart.png'))

    FULL_HEART = pygame.transform.scale(FULL_HEART_IMG, (HEART_WIDTH, HEART_HEIGHT))
    EMPTY_HEART = pygame.transform.scale(EMPTY_HEART_IMG, (HEART_WIDTH, HEART_HEIGHT))

    rect: pygame.Rect

    def __init__(self, spawn_x=0, spawn_y=0):
        self.SPAWN_X = spawn_x
        self.SPAWN_Y = spawn_y
        self.rect = pygame.Rect(self.SPAWN_X, self.SPAWN_Y, self.PLAYER_WIDTH, self.PLAYER_HEIGHT)

    def handle_movement(self, keys_pressed):
        if keys_pressed[pygame.K_a]:
            self.rect.x -= self.VELOCITY
        if keys_pressed[pygame.K_d]:
            self.rect.x += self.VELOCITY
        if keys_pressed[pygame.K_w]:
            self.rect.y -= self.VELOCITY
        if keys_pressed[pygame.K_s]:
            self.rect.y += self.VELOCITY

    def process_event(self, event):
        if event.type == self.DAMAGE:
            self.HEALTH -= 1

    def draw(self, surface):
        surface.blit(self.PLAYER_LEFT, (self.rect.x, self.rect.y))
        last_heart = 5
        for heart in range(self.HEALTH):
            surface.blit(self.FULL_HEART, (last_heart, 5))
            last_heart += self.HEART_WIDTH + 5
        for heart in range(10 - self.HEALTH):
            if heart < 10:
                surface.blit(self.EMPTY_HEART, (last_heart, 5))
                last_heart += self.HEART_WIDTH + 5
