import os

import pygame

from world.map_objects import CollideType


class Bullet:

    BULLET_WIDTH, BULLET_HEIGHT = 10, 5
    BULLET_TEXTURE = pygame.image.load(os.path.join('assets', 'textures', 'npc', 'bullet.png'))
    RIGHT, LEFT = 0, 1

    ORIGIN = None

    rect: pygame.Rect
    facing: int

    def __init__(self, x, y, facing, origin):
        self.rect = pygame.Rect(x, y, self.BULLET_WIDTH, self.BULLET_HEIGHT)
        self.facing = facing
        self.ORIGIN = origin

    def draw(self, surface):
        surface.blit(self.BULLET_TEXTURE, (self.rect.x, self.rect.y))

    def origin(self):
        return self.ORIGIN


class NPC:

    HEALTH: int
    MAX_HEALTH: int

    HEALTH_BAR = pygame.image.load(os.path.join('assets', 'textures', 'npc', 'health_bkg.png'))
    HEALTH_OVERLAY = 34

    GRAVITY = 2

    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    RED = (255, 0, 0)

    TEXTURE: pygame.Surface
    NPC_WIDTH, NPC_HEIGHT = 32, 56

    RIGHT, LEFT = 0, 1
    FACING = RIGHT

    rect: pygame.Rect

    def __init__(self, pos_x, pos_y, health, texture):
        self.TEXTURE_IMG = pygame.image.load(os.path.join('assets', 'sprites', 'npc', texture))
        self.TEXTURE_NORMAL = pygame.transform.scale(self.TEXTURE_IMG, (self.NPC_WIDTH, self.NPC_HEIGHT))
        self.TEXTURE_FLIPPED = pygame.transform.flip(self.TEXTURE_NORMAL, True, False)
        self.TEXTURE = self.TEXTURE_NORMAL
        self.rect = pygame.Rect(pos_x, pos_y, self.NPC_WIDTH, self.NPC_HEIGHT)
        self.HEALTH = health
        self.MAX_HEALTH = health

    def draw(self, window):
        self.update(window)
        window.blit(self.TEXTURE, (self.rect.x, self.rect.y))
        if self.HEALTH < self.MAX_HEALTH:
            window.blit(self.HEALTH_BAR, (self.rect.x + self.rect.width / 2 - self.HEALTH_BAR.get_width() / 2,
                                          self.rect.y + self.rect.height))
            percent = self.HEALTH / self.MAX_HEALTH
            ovl_width = self.HEALTH_OVERLAY
            new_width = round(ovl_width*percent)
            ovl = pygame.Rect(self.rect.x + self.rect.width / 2 - self.HEALTH_OVERLAY / 2,
                              self.rect.y + self.rect.height, new_width, 4)
            if percent < 0.35:
                pygame.draw.rect(window, self.RED, ovl)
            elif percent < 0.65:
                pygame.draw.rect(window, self.YELLOW, ovl)
            elif percent < 1:
                pygame.draw.rect(window, self.GREEN, ovl)

    def apply_gravity(self, level):
        if not self.check_collision(level, (self.rect.x, self.rect.y + self.GRAVITY)):
            return True
        return False

    def check_collision(self, level, change):
        potential_rect = pygame.Rect(change[0], change[1], self.NPC_WIDTH, self.NPC_HEIGHT)
        for map_object in level.map_objects:
            if isinstance(map_object, CollideType):
                if map_object.rect.colliderect(potential_rect):
                    return True
        return False

    def handle_movement(self, level):
        x_change = 0
        y_change = 0
        if self.apply_gravity(level):
            y_change = self.GRAVITY
        self.rect.x += x_change
        self.rect.y += y_change

    def update(self, window):
        self.handle_movement(pygame.level)

    def change_health(self, amt):
        self.HEALTH += amt

    def facing(self):
        return self.FACING


class RobotEnemy(NPC):

    texture = 'robot-preview.png'
    health = 10

    alerted = False
    alerted_time = 0
    alerted_image = pygame.image.load(os.path.join('assets', 'textures', 'npc', 'exclamation.png'))

    RADIUS_WIDTH, RADIUS_HEIGHT = 500, 150
    viewing_radius: pygame.Rect

    last_bullet = -1

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, self.health, self.texture)
        self.viewing_radius = pygame.Rect(self.rect.x - (self.RADIUS_WIDTH / 2 + self.NPC_WIDTH / 2),
                                          self.rect.y - (self.RADIUS_HEIGHT / 2 + self.NPC_HEIGHT / 2),
                                          self.RADIUS_WIDTH, self.RADIUS_HEIGHT)

    def update(self, window):
        super().update(window)
        self.viewing_radius.x = self.rect.x - self.RADIUS_WIDTH / 2 + self.NPC_WIDTH / 2
        self.viewing_radius.y = self.rect.y - self.RADIUS_HEIGHT / 2 + self.NPC_HEIGHT / 2

        if pygame.player.rect.colliderect(self.viewing_radius):
            self.alerted = True
            if pygame.player.rect.x + pygame.player.rect.width / 2 < self.viewing_radius.x + self.viewing_radius.width / 2:
                self.FACING = self.LEFT
                self.TEXTURE = self.TEXTURE_NORMAL
            if pygame.player.rect.x + pygame.player.rect.width / 2 > self.viewing_radius.x + self.viewing_radius.width / 2:
                self.FACING = self.RIGHT
                self.TEXTURE = self.TEXTURE_FLIPPED
        else:
            self.alerted = False
            self.alerted_time = 0

        if self.alerted_time > 0:
            window.blit(self.alerted_image, (self.rect.x + self.rect.width / 2 - self.alerted_image.get_width() / 2,
                                             self.rect.y - self.alerted_image.get_height()))
        if self.alerted_time > 1:
            x = 0
            y = self.rect.y + (self.rect.h / 2)
            if self.FACING == self.LEFT:
                x = self.rect.x
            if self.FACING == self.RIGHT:
                x = self.rect.x + self.rect.w

            own_bullets = 0
            for bullet in pygame.level.map_bullets:
                if bullet.origin() == self:
                    own_bullets += 1
            if own_bullets < 3:
                pygame.level.map_bullets.append(Bullet(x, y, self.FACING, self))
                self.alerted_time = 0
