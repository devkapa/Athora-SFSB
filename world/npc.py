import os

import pygame


class Bullet:

    BULLET_WIDTH, BULLET_HEIGHT = 10, 5
    BULLET_TEXTURE = pygame.image.load(os.path.join('assets', 'textures', 'bullet.png'))
    RIGHT, LEFT = 0, 1

    rect: pygame.Rect
    facing: int

    def __init__(self, x, y, facing):
        self.rect = pygame.Rect(x, y, self.BULLET_WIDTH, self.BULLET_HEIGHT)
        self.facing = facing

    def draw(self, surface):
        surface.blit(self.BULLET_TEXTURE, (self.rect.x, self.rect.y))


class NPC:

    HEALTH: int

    TEXTURE: pygame.Surface
    NPC_WIDTH, NPC_HEIGHT = 32, 56

    RIGHT, LEFT = 0, 1
    FACING = RIGHT

    rect: pygame.Rect

    RED = (255, 0, 0)

    def __init__(self, pos_x, pos_y, health, texture):
        self.TEXTURE_IMG = pygame.image.load(os.path.join('assets', 'sprites', 'npc', texture))
        self.TEXTURE_NORMAL = pygame.transform.scale(self.TEXTURE_IMG, (self.NPC_WIDTH, self.NPC_HEIGHT))
        self.TEXTURE_FLIPPED = pygame.transform.flip(self.TEXTURE_NORMAL, True, False)
        self.TEXTURE = self.TEXTURE_NORMAL
        self.rect = pygame.Rect(pos_x, pos_y, self.NPC_WIDTH, self.NPC_HEIGHT)
        self.HEALTH = health

    def draw(self, window):
        self.update(window)
        window.blit(self.TEXTURE, (self.rect.x, self.rect.y))

    def update(self, window):
        pass

    def change_health(self, amt):
        self.HEALTH += amt

    def facing(self):
        return self.FACING


class RobotEnemy(NPC):

    texture = 'robot-preview.png'
    health = 10

    alerted = False
    alerted_time = 0
    alerted_image = pygame.image.load(os.path.join('assets', 'textures', 'exclamation.png'))

    RADIUS_WIDTH, RADIUS_HEIGHT = 500, 150
    viewing_radius: pygame.Rect

    last_bullet = -1

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, self.health, self.texture)
        self.viewing_radius = pygame.Rect(self.rect.x - (self.RADIUS_WIDTH / 2 + self.NPC_WIDTH / 2),
                                          self.rect.y - (self.RADIUS_HEIGHT / 2 + self.NPC_HEIGHT / 2),
                                          self.RADIUS_WIDTH, self.RADIUS_HEIGHT)

    def update(self, window):
        self.viewing_radius.x = self.rect.x - self.RADIUS_WIDTH / 2 + self.NPC_WIDTH / 2
        self.viewing_radius.y = self.rect.y - self.RADIUS_HEIGHT / 2 + self.NPC_HEIGHT / 2

        if pygame.player.rect.colliderect(self.viewing_radius):
            self.alerted = True
            if pygame.player.rect.x + pygame.player.rect.width / 2 < self.viewing_radius.x + self.viewing_radius.width / 2:
                self.FACING = self.LEFT
                self.TEXTURE = self.TEXTURE_FLIPPED
            if pygame.player.rect.x + pygame.player.rect.width / 2 > self.viewing_radius.x + self.viewing_radius.width / 2:
                self.FACING = self.RIGHT
                self.TEXTURE = self.TEXTURE_NORMAL
        else:
            self.alerted = False
            self.alerted_time = 0

        if self.alerted_time > 0:
            window.blit(self.alerted_image, (self.rect.x + self.rect.width / 2 - self.alerted_image.get_width() / 2,
                                             self.rect.y - 20))
        if self.alerted_time > 1:
            x = 0
            y = self.rect.y + (self.rect.h / 2)
            if self.FACING == self.LEFT:
                x = self.rect.x
            if self.FACING == self.RIGHT:
                x = self.rect.x + self.rect.w

            if len(pygame.level.map_bullets) < 3:
                pygame.level.map_bullets.append(Bullet(x, y, self.FACING))
                self.alerted_time = 0
