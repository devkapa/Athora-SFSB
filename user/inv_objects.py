import os.path

import pygame

from world.npc import Bullet

WHITE = (255, 255, 255)


def render_font(text, px):
    font = pygame.font.Font(os.path.join('assets', 'fonts', 'pressstart.ttf'), px)
    return font.render(text, True, WHITE)


class InventoryObject:

    NAME: str
    TEXTURE: pygame.Surface
    TEXTURE_WIDTH, TEXTURE_HEIGHT = 72, 72

    def __init__(self, name, texture):
        self.NAME = name
        self.TEXTURE_IMG = pygame.image.load(os.path.join('assets', 'textures', 'items', texture))
        self.TEXTURE = pygame.transform.scale(self.TEXTURE_IMG, (self.TEXTURE_WIDTH, self.TEXTURE_HEIGHT))

    def draw(self, surface, index, slot):
        surface.blit(self.TEXTURE, slot)
        if pygame.player.inventory_selected_slot == index:
            name = render_font(self.NAME, 15)
            surface.blit(name, (slot[0] + 74 / 2 - name.get_width() / 2, slot[1] - 20))

    def use(self):
        pass


class Gun(InventoryObject):

    NAME = 'Pistol'
    TEXTURE = 'gun.png'

    def __init__(self):
        super().__init__(self.NAME, self.TEXTURE)

    def use(self):
        x = 0
        y = pygame.player.rect.y + (pygame.player.rect.h / 2)
        bit = 1
        if pygame.player.direction[pygame.player.LEFT]:
            x = pygame.player.rect.x
        if pygame.player.direction[pygame.player.RIGHT]:
            x = pygame.player.rect.x + pygame.player.rect.w
            bit = 0
        own_bullets = 0
        for bullet in pygame.level.map_bullets:
            if bullet.origin() == pygame.player:
                own_bullets += 1
        if own_bullets < 3:
            pygame.level.map_bullets.append(Bullet(x, y, bit, pygame.player))
