import datetime
import os.path

import pygame
import time

from world.map import Map, Maps
from player.player import Player
from world.map_objects import InteractiveType, ExitDoor

pygame.font.init()

WHITE = (255, 255, 255)
AQUA = (0, 255, 255)
PINK = (255, 225, 225)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (168, 168, 168)
BLACK = (0, 0, 0)

WIDTH, HEIGHT = 832, 640
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Athora: SpaceF Strikes Back")

ICON = pygame.image.load(os.path.join('assets', 'textures', 'wall.png'))
pygame.display.set_icon(ICON)

BACKGROUND = pygame.image.load(os.path.join('assets', 'textures', 'grass_bkg.png')).convert_alpha()

FPS = 144
PAUSED, CONTINUE = 0, 1
DEDUCT, NONE, GAIN = -1, 0, 1


def get_levels():
    levels = []
    maps_dir = os.path.join('assets', 'levels')
    level_files = [f for f in os.listdir(maps_dir)
                   if os.path.isfile(os.path.join(maps_dir, f)) and f.lower().endswith(".txt")]
    for level in sorted(level_files, key=level_sorter):
        with open(f'{os.path.join(maps_dir, level)}', 'r') as file:
            levels.append(file.read())
    return levels


def level_sorter(x):
    return os.path.split(x)[-1]


def render_font(text, px):
    font = pygame.font.Font(os.path.join('assets', 'fonts', 'pressstart.ttf'), px)
    return font.render(text, True, WHITE)


def create_overlay_surface(colour, alpha=180):
    surface = pygame.Surface((WIDTH, HEIGHT))
    surface.set_alpha(alpha)
    surface.fill(colour)
    return surface


def draw_window(player, global_map, formatted_elapsed_time):
    WIN.fill(BLACK)
    WIN.blit(BACKGROUND, (0, 0))
    global_map.draw(WIN)
    player.draw(WIN)
    title = render_font(global_map.title, 28)
    timer = render_font(str(formatted_elapsed_time), 20)
    WIN.blit(timer, (WIDTH - timer.get_width(), title.get_height() + 15))
    WIN.blit(title, (WIDTH - title.get_width(), 9))


def draw_overlay(colour, title, subheading):
    WIN.blit(create_overlay_surface(colour), (0, 0))
    title_text = render_font(title, 40)
    subheading_text = render_font(subheading, 30)
    WIN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - title_text.get_height() // 2))
    WIN.blit(subheading_text,
             (WIDTH // 2 - subheading_text.get_width() // 2, HEIGHT // 2 - subheading_text.get_height() // 2 + 45))


def draw_damage(damage, damage_frames):
    if damage > NONE:
        WIN.blit(create_overlay_surface(GREEN, alpha=180 - (damage_frames * 6)), (0, 0))
    if damage < NONE:
        WIN.blit(create_overlay_surface(RED, alpha=180 - (damage_frames * 6)), (0, 0))


def check_for_interactions(global_map, player):
    for map_object in global_map.map_objects:
        if isinstance(map_object, InteractiveType):
            if map_object.rect.colliderect(player.rect):
                draw_popup(map_object, player)
                return True, map_object
    return False, None


def draw_popup(interactive, player):
    popup_text = render_font(interactive.POPUP, 10)
    WIN.blit(popup_text, (player.rect.x + player.PLAYER_WIDTH / 2 - popup_text.get_width() / 2,
                          player.rect.y - player.PLAYER_HEIGHT / 2))


def main():
    clock = pygame.time.Clock()
    running = True
    start_time = time.time()

    state = CONTINUE

    player = Player()
    damage = NONE
    damage_frames = 0

    levels = []

    for index, level in enumerate(get_levels()):
        levels.append(Map(f'Level {index + 1}', level))

    levels = Maps(levels, player)

    hovering = (False, None)

    print(start_time)

    while running:

        clock.tick(FPS)
        current_level = levels.current
        time_elapsed = datetime.timedelta(seconds=round((time.time() - start_time)))

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
                pygame.quit()

            if state == PAUSED:

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_r and player.HEALTH < 1:
                        running = False

                    if event.key == pygame.K_p and player.HEALTH > 0:
                        state = CONTINUE
                        continue

            if state == CONTINUE:

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_p:
                        state = PAUSED
                        continue

                    if event.key == pygame.K_f and hovering[0]:
                        hovering[1].on_interact()

                if event.type == player.DAMAGE:
                    if event.hp > 0:
                        damage = GAIN
                    if event.hp < 0:
                        damage = DEDUCT

                if event.type == ExitDoor.ENTER:
                    levels + 1

                player.process_event(event)

        if state == CONTINUE:
            keys_pressed = pygame.key.get_pressed()
            player.handle_movement(WIN, keys_pressed, current_level)

        time_elapsed = datetime.timedelta(seconds=round((time.time() - start_time)))

        draw_window(player, current_level, time_elapsed)

        if damage != NONE:
            damage_frames += 1

        if damage_frames > 30:
            damage_frames = 0
            damage = NONE

        if damage_frames > 0:
            draw_damage(damage, damage_frames)

        interactions = check_for_interactions(current_level, player)

        if interactions[0]:
            hovering = (True, interactions[1])
        else:
            hovering = (False, None)

        if state == PAUSED and player.HEALTH > 0:
            draw_overlay(GRAY, "Game Paused", "Press P to unpause")

        if player.HEALTH <= 0:
            draw_overlay(RED, "You died!", "Press R to restart")
            state = PAUSED

        pygame.display.update()


if __name__ == '__main__':
    while True:
        main()
