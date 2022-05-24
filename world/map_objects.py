import os.path

import pygame


class ObjectType:

    OBJECT_WIDTH, OBJECT_HEIGHT = 32, 32

    TEXTURE: pygame.Surface

    rect: pygame.Rect

    def __init__(self, pos_x, pos_y, texture):
        self.TEXTURE_IMG = pygame.image.load(os.path.join('assets', 'textures', texture))
        self.TEXTURE = pygame.transform.scale(self.TEXTURE_IMG, (self.OBJECT_WIDTH, self.OBJECT_HEIGHT))
        self.rect = pygame.Rect(pos_x*self.OBJECT_WIDTH, pos_y*self.OBJECT_HEIGHT, self.OBJECT_WIDTH, self.OBJECT_HEIGHT)

    def draw(self, surface):
        surface.blit(self.TEXTURE, (self.rect.x, self.rect.y))


class Wall(ObjectType):

    texture = 'wall.png'

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, self.texture)


class Floor(ObjectType):

    texture = 'floor.png'

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, self.texture)

