import os.path

import pygame.image

from world.map_objects import Wall


class Player:

    VELOCITY = 1

    HEALTH = 10
    DAMAGE = pygame.USEREVENT + 1
    DAMAGE_EVENT = pygame.event.Event(DAMAGE)

    PLAYER_WIDTH, PLAYER_HEIGHT = 32, 56
    SPAWN_X, SPAWN_Y = 0, 0

    PLAYER_LEFT_IMG = pygame.image.load(os.path.join('assets', 'sprites', 'hero_left_still.png'))
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

    def handle_movement(self, window, keys_pressed, level):
        x_change = 0
        y_change = 0
        if keys_pressed[pygame.K_w] and self.rect.y - self.VELOCITY > 0:
            if not self.check_collision(level, (self.rect.x, self.rect.y - self.VELOCITY)):
                y_change -= self.VELOCITY
            x_change = 0
        if keys_pressed[pygame.K_a] and self.rect.x - self.VELOCITY > 0:
            if not self.check_collision(level, (self.rect.x - self.VELOCITY, self.rect.y)):
                x_change -= self.VELOCITY
            y_change = 0
        if keys_pressed[pygame.K_s] and self.rect.y + self.VELOCITY < window.get_height() - self.PLAYER_WIDTH:
            if not self.check_collision(level, (self.rect.x, self.rect.y + self.VELOCITY)):
                y_change += self.VELOCITY
            x_change = 0
        if keys_pressed[pygame.K_d] and self.rect.x + self.VELOCITY < window.get_width() - self.PLAYER_WIDTH:
            if not self.check_collision(level, (self.rect.x + self.VELOCITY, self.rect.y)):
                x_change += self.VELOCITY
            y_change = 0
        self.rect.x += x_change
        self.rect.y += y_change

    def check_collision(self, level, change):
        potential_rect = pygame.Rect(change[0], change[1], self.PLAYER_WIDTH, self.PLAYER_HEIGHT)
        for map_object in level.map_objects:
            if isinstance(map_object, Wall):
                if map_object.rect.colliderect(potential_rect):
                    return True
        return False

    def process_event(self, event):
        if event.type == self.DAMAGE:
            if self.HEALTH + event.hp > 10:
                self.HEALTH = 10
                return
            self.HEALTH += event.hp

    def change_hp(self, amount):
        self.DAMAGE_EVENT.hp = amount
        pygame.event.post(self.DAMAGE_EVENT)

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
