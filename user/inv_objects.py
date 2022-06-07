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
            surface.blit(name, (slot[0] + 72 / 2 - name.get_width() / 2, slot[1] - 20))

    def use(self):
        pass


class Gun(InventoryObject):

    NAME = 'Pistol'
    TEXTURE = 'gun.png'

    RELOAD_TEXT = "'R' to reload"
    EMPTY_GUN = pygame.USEREVENT + 4
    EMPTY_GUN_EVENT = pygame.event.Event(EMPTY_GUN)
    chamber = 3

    def __init__(self):
        super().__init__(self.NAME, self.TEXTURE)

    def draw(self, surface, index, slot):
        super().draw(surface, index, slot)
        bullets = render_font(str(self.chamber), 10)
        surface.blit(bullets, (slot[0] + 60 - bullets.get_width(), slot[1] + 60 - bullets.get_height()))
        if self.chamber == 0:
            pygame.event.post(self.EMPTY_GUN_EVENT)

    def use(self):
        if self.chamber == 0:
            return
        x = 0
        y = pygame.player.rect.y + (pygame.player.rect.h / 2)
        bit = 1
        if pygame.player.direction[pygame.player.LEFT]:
            x = pygame.player.rect.x
        if pygame.player.direction[pygame.player.RIGHT]:
            x = pygame.player.rect.x + pygame.player.rect.w
            bit = 0
        pygame.level.map_bullets.append(Bullet(x, y, bit, pygame.player))
        self.chamber -= 1

    def reload(self):
        self.chamber = 3
