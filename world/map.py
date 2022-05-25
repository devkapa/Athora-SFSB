import pygame

from player.player import Player
from world.map_objects import ObjectType, Floor, Wall, ExitDoor


class Map:

    layout: str

    map_objects: list[ObjectType]
    center_point: ObjectType

    rect: pygame.Rect
    title: str

    def __init__(self, title, layout):
        split_layout = layout.split("\n")

        self.rect = pygame.Rect((0, 0), (832, 640))
        self.title = title
        self.layout = layout
        self.map_objects = []

        for line_index, line in enumerate(split_layout):
            for char_index, char in enumerate(line):
                if char == "W":
                    self.map_objects.append(Wall(char_index, line_index))
                if char == " ":
                    self.map_objects.append(Floor(char_index, line_index))
                if char == "C":
                    center = Floor(char_index, line_index)
                    self.center_point = center
                    self.map_objects.append(center)
                if char == "I":
                    self.map_objects.append(ExitDoor(char_index, line_index))

    def draw(self, surface):
        for obj in self.map_objects:
            obj.draw(surface)

    def get_center_point(self):
        return self.center_point


class Maps:

    maps: list = []
    current: Map
    player: Player

    def __init__(self, maps, player):
        self.maps = maps
        self.current = self.maps[0]
        self.player = player
        self.spawn_player()

    def __add__(self, other):
        if isinstance(other, int):
            self.current = self.maps[self.maps.index(self.current) + other]
            self.spawn_player()

    def spawn_player(self):
        self.player.rect.x = self.current.center_point.rect.x
        self.player.rect.y = self.current.center_point.rect.y - self.player.PLAYER_WIDTH / 2
