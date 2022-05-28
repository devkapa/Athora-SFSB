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

    PLAYER_STILL = pygame.image.load(os.path.join('assets', 'sprites', 'hero_still.png'))
    PLAYER_WALK_1 = pygame.image.load(os.path.join('assets', 'sprites', 'hero_walk_1.png'))
    PLAYER_WALK_2 = pygame.image.load(os.path.join('assets', 'sprites', 'hero_walk_2.png'))

    PLAYER_LEFT = pygame.transform.scale(PLAYER_STILL, (PLAYER_WIDTH, PLAYER_HEIGHT))
    PLAYER_LEFT_WALK_1 = pygame.transform.scale(PLAYER_WALK_1, (PLAYER_WIDTH, PLAYER_HEIGHT))
    PLAYER_LEFT_WALK_2 = pygame.transform.scale(PLAYER_WALK_2, (PLAYER_WIDTH, PLAYER_HEIGHT))

    PLAYER_RIGHT = pygame.transform.flip(PLAYER_LEFT, True, False)
    PLAYER_RIGHT_WALK_1 = pygame.transform.flip(PLAYER_LEFT_WALK_1, True, False)
    PLAYER_RIGHT_WALK_2 = pygame.transform.flip(PLAYER_LEFT_WALK_2, True, False)

    PLAYER_LEFT_WALKING = [PLAYER_LEFT_WALK_1, PLAYER_LEFT, PLAYER_LEFT_WALK_2, PLAYER_LEFT]
    PLAYER_RIGHT_WALKING = [PLAYER_RIGHT_WALK_1, PLAYER_RIGHT, PLAYER_RIGHT_WALK_2, PLAYER_RIGHT]

    HEART_WIDTH, HEART_HEIGHT = 36, 36

    FULL_HEART_IMG = pygame.image.load(os.path.join('assets', 'textures', 'full_heart.png'))
    EMPTY_HEART_IMG = pygame.image.load(os.path.join('assets', 'textures', 'empty_heart.png'))

    FULL_HEART = pygame.transform.scale(FULL_HEART_IMG, (HEART_WIDTH, HEART_HEIGHT))
    EMPTY_HEART = pygame.transform.scale(EMPTY_HEART_IMG, (HEART_WIDTH, HEART_HEIGHT))

    RIGHT, LEFT, UP, DOWN = 0, 1, 2, 3
    ANIMATION_SPEED = 30

    rect: pygame.Rect
    current_img: pygame.Surface

    prev_pos_x: int
    prev_pos_y: int

    direction = (False, True, False, False)
    animation_frame_count = 0

    def __init__(self, spawn_x=0, spawn_y=0):
        self.SPAWN_X = spawn_x
        self.SPAWN_Y = spawn_y
        self.rect = pygame.Rect(self.SPAWN_X, self.SPAWN_Y, self.PLAYER_WIDTH, self.PLAYER_HEIGHT)
        self.current_img = self.PLAYER_LEFT

    def handle_movement(self, window, keys_pressed, level):
        self.prev_pos_x = self.rect.x
        self.prev_pos_y = self.rect.y
        x_change = 0
        y_change = 0
        if keys_pressed[pygame.K_w] and self.rect.y - self.VELOCITY > 0:
            if not self.check_collision(level, (self.rect.x, self.rect.y - self.VELOCITY)):
                self.direction = (False, False, True, False)
                y_change -= self.VELOCITY
                x_change = 0
        if keys_pressed[pygame.K_a] and self.rect.x - self.VELOCITY > 0:
            if not self.check_collision(level, (self.rect.x - self.VELOCITY, self.rect.y)):
                self.direction = (False, True, False, False)
                x_change -= self.VELOCITY
                y_change = 0
        if keys_pressed[pygame.K_s] and self.rect.y + self.VELOCITY < window.get_height() - self.PLAYER_WIDTH:
            if not self.check_collision(level, (self.rect.x, self.rect.y + self.VELOCITY)):
                self.direction = (False, False, False, True)
                y_change += self.VELOCITY
                x_change = 0
        if keys_pressed[pygame.K_d] and self.rect.x + self.VELOCITY < window.get_width() - self.PLAYER_WIDTH:
            if not self.check_collision(level, (self.rect.x + self.VELOCITY, self.rect.y)):
                self.direction = (True, False, False, False)
                x_change += self.VELOCITY
                y_change = 0
        self.rect.x += x_change
        self.rect.y += y_change

    def moving(self):
        if self.prev_pos_x - self.rect.x != 0:
            if self.prev_pos_x - self.rect.x < 0:
                return True, self.RIGHT
            else:
                return True, self.LEFT
        if self.prev_pos_y - self.rect.y != 0:
            if self.prev_pos_y - self.rect.y < 0:
                return True, self.UP
            else:
                return True, self.DOWN
        return False, None

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

    def walking_animation(self, direction, frame_list):
        per_frame = self.ANIMATION_SPEED
        if self.moving()[1] == direction:
            for index, frame in enumerate(frame_list):
                if self.animation_frame_count < per_frame*len(frame_list):
                    if self.animation_frame_count < per_frame*(index+1):
                        self.current_img = frame
                        break
                    continue
                self.animation_frame_count = 0
                break

    def draw(self, surface):
        if self.moving()[0]:
            self.walking_animation(self.RIGHT, self.PLAYER_RIGHT_WALKING)
            self.walking_animation(self.LEFT, self.PLAYER_LEFT_WALKING)
            self.animation_frame_count += 1
        else:
            self.animation_frame_count = 0
            if self.direction[self.RIGHT]:
                self.current_img = self.PLAYER_RIGHT
            if self.direction[self.LEFT]:
                self.current_img = self.PLAYER_LEFT
            if self.direction[self.UP]:
                self.current_img = self.PLAYER_RIGHT
            if self.direction[self.DOWN]:
                self.current_img = self.PLAYER_LEFT
        surface.blit(self.current_img, (self.rect.x, self.rect.y))
        last_heart = 5
        for heart in range(self.HEALTH):
            surface.blit(self.FULL_HEART, (last_heart, 5))
            last_heart += self.HEART_WIDTH + 5
        for heart in range(10 - self.HEALTH):
            if heart < 10:
                surface.blit(self.EMPTY_HEART, (last_heart, 5))
                last_heart += self.HEART_WIDTH + 5
