import os.path

import pygame.image

from user.inv_objects import InventoryObject, Gun
from world.map_objects import CollideType


class Player:
    VELOCITY = 1

    HEALTH = 10
    DAMAGE = pygame.USEREVENT + 1
    DAMAGE_EVENT = pygame.event.Event(DAMAGE)

    GRAVITY = 2

    PLAYER_WIDTH, PLAYER_HEIGHT = 32, 56
    SPAWN_X, SPAWN_Y = 0, 0

    PLAYER_STILL = pygame.image.load(os.path.join('assets', 'sprites', 'player', 'hero_still.png'))
    PLAYER_WALK_1 = pygame.image.load(os.path.join('assets', 'sprites', 'player', 'hero_walk_1.png'))
    PLAYER_WALK_2 = pygame.image.load(os.path.join('assets', 'sprites', 'player', 'hero_walk_2.png'))

    PLAYER_LEFT = pygame.transform.scale(PLAYER_STILL, (PLAYER_WIDTH, PLAYER_HEIGHT))
    PLAYER_LEFT_WALK_1 = pygame.transform.scale(PLAYER_WALK_1, (PLAYER_WIDTH, PLAYER_HEIGHT))
    PLAYER_LEFT_WALK_2 = pygame.transform.scale(PLAYER_WALK_2, (PLAYER_WIDTH, PLAYER_HEIGHT))

    PLAYER_RIGHT = pygame.transform.flip(PLAYER_LEFT, True, False)
    PLAYER_RIGHT_WALK_1 = pygame.transform.flip(PLAYER_LEFT_WALK_1, True, False)
    PLAYER_RIGHT_WALK_2 = pygame.transform.flip(PLAYER_LEFT_WALK_2, True, False)

    PLAYER_LEFT_WALKING = [PLAYER_LEFT_WALK_1, PLAYER_LEFT, PLAYER_LEFT_WALK_2, PLAYER_LEFT]
    PLAYER_RIGHT_WALKING = [PLAYER_RIGHT_WALK_1, PLAYER_RIGHT, PLAYER_RIGHT_WALK_2, PLAYER_RIGHT]

    HEART_WIDTH, HEART_HEIGHT = 36, 36

    FULL_HEART_IMG = pygame.image.load(os.path.join('assets', 'textures', 'player', 'full_heart.png'))
    EMPTY_HEART_IMG = pygame.image.load(os.path.join('assets', 'textures', 'player', 'empty_heart.png'))

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

    jump_height = 64
    jumping = False

    INVENTORY_SIZE = 2
    INVENTORY_SLOT_SIZE = INVENTORY_SLOT_WIDTH, INVENTORY_SLOT_HEIGHT = 72, 72
    INVENTORY_SLOT_IMG = pygame.image.load(os.path.join('assets', 'textures', 'player', 'inventory_slot.png'))
    INVENTORY_SLOT = pygame.transform.scale(INVENTORY_SLOT_IMG, INVENTORY_SLOT_SIZE)
    inventory: list[InventoryObject]
    inventory_selected_slot = 0

    def __init__(self, spawn_x=0, spawn_y=0):
        self.SPAWN_X = spawn_x
        self.SPAWN_Y = spawn_y
        self.rect = pygame.Rect(self.SPAWN_X, self.SPAWN_Y, self.PLAYER_WIDTH, self.PLAYER_HEIGHT)
        self.current_img = self.PLAYER_LEFT
        self.inventory = []

        self.inventory.append(Gun())

    def handle_movement(self, window, keys_pressed, level):
        self.prev_pos_x = self.rect.x
        self.prev_pos_y = self.rect.y
        x_change = 0
        y_change = 0
        if not self.jumping:
            if self.apply_gravity(level):
                y_change = self.GRAVITY
                self.direction = (self.direction[self.RIGHT], self.direction[self.LEFT], False, True)
            else:
                if keys_pressed[pygame.K_SPACE]:
                    self.jumping = True
        else:
            if self.jump_height >= -64:
                curve = (self.jump_height * abs(self.jump_height)) / 1024
                if not self.check_collision(level, (self.rect.x, self.rect.y - curve)):
                    self.direction = (self.direction[self.RIGHT], self.direction[self.LEFT], True, False)
                    y_change -= curve
                    self.jump_height -= 2
                else:
                    self.jumping = False
                    self.jump_height = 64
            else:
                self.jumping = False
                self.jump_height = 64

        if keys_pressed[pygame.K_a]:
            if not self.check_collision(level, (self.rect.x - self.VELOCITY, self.rect.y)):
                self.direction = (False, True, False, False)
                x_change -= self.VELOCITY
        if keys_pressed[pygame.K_d]:
            if not self.check_collision(level, (self.rect.x + self.VELOCITY, self.rect.y)):
                self.direction = (True, False, False, False)
                x_change += self.VELOCITY

        if x_change != 0:
            if self.rect.x + x_change > window.get_width() * 0.75 and self.direction[self.RIGHT]:
                level.scroll(-1, 0)
                x_change = 0
                self.prev_pos_x -= 1
            if self.rect.x + x_change < window.get_width() * 0.25 and self.direction[self.LEFT]:
                level.scroll(1, 0)
                x_change = 0
                self.prev_pos_x += 1
        if y_change != 0:
            if self.rect.y + y_change > window.get_height() * 0.75 and self.direction[self.DOWN]:
                level.scroll(0, -self.GRAVITY)
                y_change = 0
                self.prev_pos_y -= self.GRAVITY
            if self.rect.y + y_change < window.get_height() * 0.25 and self.direction[self.UP]:
                level.scroll(0, self.GRAVITY)
                y_change = 0
                self.prev_pos_y += self.GRAVITY

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

    def apply_gravity(self, level):
        if not self.check_collision(level, (self.rect.x, self.rect.y + self.GRAVITY)):
            return True
        return False

    def check_collision(self, level, change):
        potential_rect = pygame.Rect(change[0], change[1], self.PLAYER_WIDTH, self.PLAYER_HEIGHT)
        for map_object in level.map_objects:
            if isinstance(map_object, CollideType):
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
                if self.animation_frame_count < per_frame * len(frame_list):
                    if self.animation_frame_count < per_frame * (index + 1):
                        self.current_img = frame
                        break
                    continue
                self.animation_frame_count = 0
                break

    def add_to_inventory(self, item):
        self.inventory.append(item)

    def draw(self, surface: pygame.Surface):
        # Player Walking Animation
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
        surface.blit(self.current_img, (self.rect.x, self.rect.y))
        # Player Hearts
        last_heart = 5
        for heart in range(self.HEALTH):
            surface.blit(self.FULL_HEART, (last_heart, 5))
            last_heart += self.HEART_WIDTH + 5
        for heart in range(10 - self.HEALTH):
            if heart < 10:
                surface.blit(self.EMPTY_HEART, (last_heart, 5))
                last_heart += self.HEART_WIDTH + 5
        # Player Inventory
        last_slot = 15 + self.INVENTORY_SLOT.get_width()
        for slot in range(self.INVENTORY_SIZE):
            surface.blit(self.INVENTORY_SLOT, (surface.get_width() - last_slot,
                                               surface.get_height() - self.INVENTORY_SLOT.get_height() - 20))
            if len(self.inventory) >= slot + 1:
                self.inventory[slot].draw(surface, slot, (surface.get_width() - last_slot,
                                                          surface.get_height() - self.INVENTORY_SLOT.get_height() - 20))
            last_slot += self.INVENTORY_SLOT.get_width() + self.INVENTORY_SLOT.get_width() / 4
