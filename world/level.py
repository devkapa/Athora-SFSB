from user.inv_objects import Potion, Gun
from user.player import Player
from world.level_objects import ObjectType, Background, Wall, ExitDoor, Air, Barrier, Grass, Dirt, DroppedItem, Sign, \
    Lava, ExitHelicopter, StairLeft, StairRight, Printer, Board, Water, Glass, DirtBkg, Bush, Tree
from world.npc import RobotEnemy, NPC, Bullet, RobotBoss


class Level:

    # The string layout pulled from the level file
    layout: str

    # Objects, NPCs and Bullets within the level
    level_objects: list[ObjectType]
    level_npc: list[NPC]
    level_bullets: list[Bullet]

    # The point in the level where the player will spawn
    spawn_point: ObjectType

    # Name of the level
    title: str

    def __init__(self, title, layout):
        split_layout = layout.split("\n")

        self.title = title
        self.layout = layout
        self.level_objects = []
        self.level_npc = []
        self.level_bullets = []

        # Characters which correspond to different level objects
        # If the character is present, the object will be added to the level at that position
        for line_index, line in enumerate(split_layout):
            for char_index, char in enumerate(line):
                if char == "-":
                    self.level_objects.append(Background(char_index, line_index))
                if char == "~":
                    self.level_objects.append(Water(char_index, line_index))
                if char == "W":
                    self.level_objects.append(Wall(char_index, line_index))
                if char == "S":
                    spawn = Air(char_index, line_index)
                    self.spawn_point = spawn
                    self.level_objects.append(spawn)
                if char == "T":
                    self.level_objects.append(ExitDoor(char_index, line_index))
                if char == "H":
                    self.level_objects.append(DroppedItem(char_index, line_index, Potion(10)))
                if char == "P":
                    self.level_objects.append(DroppedItem(char_index, line_index, Gun()))
                if char == "B":
                    self.level_objects.append(Barrier(char_index, line_index))
                if char == "G":
                    self.level_objects.append(Grass(char_index, line_index))
                if char == "D":
                    self.level_objects.append(Dirt(char_index, line_index))
                if char == "s":
                    self.level_objects.append(DirtBkg(char_index, line_index))
                if char == "I":
                    self.level_objects.append(StairLeft(char_index, line_index))
                if char == ":":
                    self.level_objects.append(Background(char_index, line_index))
                    self.level_objects.append(StairLeft(char_index, line_index))
                if char == "J":
                    self.level_objects.append(StairRight(char_index, line_index))
                if char == "g":
                    self.level_objects.append(Glass(char_index, line_index))
                if char == "m":
                    self.level_objects.append(Bush(char_index, line_index))
                if char == "j":
                    self.level_objects.append(Tree(char_index, line_index))
                if char == ";":
                    self.level_objects.append(Background(char_index, line_index))
                    self.level_objects.append(StairRight(char_index, line_index))
                if char == "L":
                    self.level_objects.append(Lava(char_index, line_index))
                if char == "A":
                    self.level_objects.append(Board(char_index, line_index))
                if char == "E":
                    self.level_npc.append(RobotEnemy(char_index * 32, line_index * 32))
                if char == "l":
                    self.level_npc.append(RobotEnemy(char_index * 32, line_index * 32))
                    self.level_objects.append(Background(char_index, line_index))
                if char == "d":
                    self.level_npc.append(RobotEnemy(char_index * 32, line_index * 32))
                    self.level_objects.append(DirtBkg(char_index, line_index))
                if char == "R":
                    self.level_npc.append(RobotEnemy(char_index * 32, line_index * 32, health=3))
                if char == "n":
                    self.level_objects.append(Glass(char_index * 32, line_index * 32))
                    self.level_npc.append(RobotBoss(char_index * 32, line_index * 32, health=30))
                if char == "O":
                    self.level_objects.append(Background(char_index, line_index))
                    self.level_objects.append(Printer(char_index, line_index,
                                                 "Black: 0%  Yellow: 0%\nCyan: 0%  Magenta: 100%\nFewlett Packard"))
                if char == "!":
                    self.level_objects.append(Sign(char_index, line_index,
                                                 "Welcome to Athora!\nPress 'A' & 'D' or '←' & '→'\nto move!"))
                if char == "@":
                    self.level_objects.append(Sign(char_index, line_index,
                                                 "Excellent work! Try jumping\nover this wall by pressing\n'SPACE'!"))
                if char == "#":
                    self.level_objects.append(Sign(char_index, line_index,
                                                 "Nice! Here, take this gun.\nTry shooting this robot\nby pressing 'M'!"))
                if char == "$":
                    self.level_objects.append(Sign(char_index, line_index,
                                                 "Whew, that was close! This\npotion will heal you up.\nPress 'M' to use."))
                if char == "%":
                    self.level_objects.append(Sign(char_index, line_index,
                                                 "Use '1' and '2' to switch\nbetween your inventory\nslots!"))
                if char == "^":
                    self.level_objects.append(Sign(char_index, line_index,
                                                 "Good job finishing the\ntutorial. Enter this portal\nto begin your journey!"))
                if char == "&":
                    self.level_objects.append(Sign(char_index, line_index,
                                                 "Welcome back.\nYour conscience has been \nbothering you for a while."))
                if char == "*":
                    self.level_objects.append(Sign(char_index, line_index,
                                                 "Figure out what's\ngoing on here.\nGood luck"))
                if char == "(":
                    self.level_objects.append(Sign(char_index, line_index,
                                                 "Look out\nthere are guards ahead."))
                if char == ")":
                    self.level_objects.append(Sign(char_index,line_index,
                                                   "Self flying helicopter\nPre-production unit\nAuthorised personnel only"))
                if char == "o":
                    self.level_objects.append(Background(char_index, line_index))
                    self.level_objects.append(Sign(char_index,line_index,
                                                   "Welcome to SpaceF\nleading in innovation\nas the only company."))
                if char == "C":
                    self.level_objects.append(ExitHelicopter(char_index, line_index))
                if char == "p":
                    self.level_objects.append(DirtBkg(char_index, line_index))
                    self.level_objects.append(Sign(char_index, line_index,
                                                 "You dare use the\nsecret tunnel\nMeant for Felon himself?"))

    # Call the draw function of every object and NPC within the map, given it is currently visible in the game's viewport
    def draw(self, surface):
        for obj in self.level_objects:
            if 0 - obj.OBJECT_WIDTH < obj.rect.x < surface.get_width() and 0 - obj.OBJECT_HEIGHT < obj.rect.y < surface.get_height():
                obj.draw(surface)
        for npc in self.level_npc:
            if 0 - npc.NPC_WIDTH < npc.rect.x < surface.get_width() and 0 - npc.NPC_HEIGHT < npc.rect.y < surface.get_height():
                npc.draw(surface)

    # Alter the position of objects, NPCs and bullets in the map to
    # create the effect that the player is moving across the map
    def scroll(self, vel_x, vel_y):
        for obj in self.level_objects:
            obj.rect.x += vel_x
            obj.rect.y += vel_y
        for npc in self.level_npc:
            npc.rect.x += vel_x
            npc.rect.y += vel_y
        for bullet in self.level_bullets:
            bullet.rect.x += vel_x
            bullet.rect.y += vel_y

    def get_spawn_point(self):
        return self.spawn_point


# A structure containing a list of levels, the current level and methods to get the next level in line
class Levels:

    levels: list = []
    current: Level
    player: Player

    def __init__(self, levels, player):
        self.levels = levels
        self.current = self.levels[0]
        self.player = player
        self.spawn_player()

    def __add__(self, other):
        if isinstance(other, int):
            if self.levels[self.levels.index(self.current) + other] is not None:
                self.current = self.levels[self.levels.index(self.current) + other]
                self.spawn_player()

    def spawn_player(self):
        self.player.rect.x = self.current.spawn_point.rect.x
        self.player.rect.y = self.current.spawn_point.rect.y - self.player.PLAYER_WIDTH / 2

    def next(self):
        if 0 < self.levels.index(self.current) + 1 < len(self.levels):
            return self.levels[self.levels.index(self.current) + 1]
        return None
