import datetime
import os.path
import sys

import pygame

from pygame.locals import *

flags = DOUBLEBUF

pygame.font.init()
pygame.display.init()
pygame.mixer.init()

WHITE = (255, 255, 255)
AQUA = (0, 255, 255)
PINK = (255, 225, 225)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (168, 168, 168)
BLACK = (0, 0, 0)
POTION = (111, 142, 109)

WIDTH, HEIGHT = 832, 640
WIN = pygame.display.set_mode((WIDTH, HEIGHT), flags, 8)
WIN.set_alpha(None)
pygame.display.set_caption("Athora: SpaceF Strikes Back")

ICON = pygame.image.load(os.path.join('assets', 'textures', 'tiles', 'wall.png'))
pygame.display.set_icon(ICON)

BACKGROUND = pygame.image.load(os.path.join('assets', 'textures', 'overlay', 'night_sky.png')).convert()
BACKGROUND_SURFACE = pygame.Surface((WIDTH, HEIGHT))
BACKGROUND_SURFACE.blit(BACKGROUND, (0, 0))

SIGNPOST_WIDTH, SIGNPOST_HEIGHT = 600, 120
SIGNPOST_IMG = pygame.image.load(os.path.join('assets', 'textures', 'overlay', 'signpost.png')).convert()
SIGNPOST = pygame.transform.scale(SIGNPOST_IMG, (SIGNPOST_WIDTH, SIGNPOST_HEIGHT))

FPS = 60
TITLE, PAUSED, CONTINUE, TRANSITION = -1, 0, 1, 2
DEDUCT, NONE, GAIN = -1, 0, 1
SIGN_OPEN, SIGN_OBJ = 0, 1
IS_INTERACTING, INTERACTING_WITH = 0, 1

AMBIENCE_CHANNEL = pygame.mixer.Channel(6)
AMBIENCE = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'ambience.wav'))


from user.inv_objects import Gun, Potion
from user.player import Player
from world.map import Map, Maps
from world.map_objects import InteractiveType, ExitDoor, CollideType, DroppedItem, Sign, Lava
from world.npc import RobotEnemy, NPC


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


def render_font(text, px, color=WHITE, alpha=None):
    font = pygame.font.Font(os.path.join('assets', 'fonts', 'pressstart.ttf'), px)
    text = font.render(text, True, color)
    text.set_alpha(alpha) if alpha is not None else None
    return text


def create_overlay_surface(colour, alpha=180):
    surface = pygame.Surface((WIDTH, HEIGHT))
    surface.set_alpha(alpha)
    surface.fill(colour)
    return surface


def draw_window(player, level, elapsed_time, state):
    WIN.fill(BLACK)
    WIN.blit(BACKGROUND_SURFACE, (0, 0))
    level.draw(WIN)
    if player.HEALTH > 0:
        if state == CONTINUE:
            draw_bullets(player, level)
        player.draw(WIN)
        title = render_font(level.title, 28)
        timer = render_font(str(datetime.timedelta(seconds=round(elapsed_time))), 20)
        WIN.blit(title, (WIDTH - 5 - title.get_width(), 10))
        WIN.blit(timer, (WIDTH - 5 - timer.get_width(), title.get_height() + title.get_height() / 2))


def draw_bullets(player, level):
    npc_collision = False
    bullets = level.map_bullets.copy()
    for bullet in bullets:
        for npc in level.map_npc:
            if bullet.rect.colliderect(npc.rect) and isinstance(bullet.origin(), Player):
                npc.change_health(-1)
                npc_collision = True
            if npc.HEALTH <= 0:
                level.map_npc.remove(npc)
        if bullet.facing == bullet.LEFT:
            bullet.rect.x -= bullet.SPEED
        if bullet.facing == bullet.RIGHT:
            bullet.rect.x += bullet.SPEED
        if bullet.rect.x < 0 or bullet.rect.x > WIDTH:
            level.map_bullets.remove(bullet)
        elif bullet.rect.colliderect(player.rect) and isinstance(bullet.origin(), NPC):
            player.change_hp(-1)
            level.map_bullets.remove(bullet)
        elif npc_collision:
            level.map_bullets.remove(bullet)
        elif any(wall.rect.colliderect(bullet.rect) and isinstance(wall, CollideType) for wall in level.map_objects):
            level.map_bullets.remove(bullet)
        else:
            bullet.draw(WIN)
        npc_collision = False


def draw_overlay(colour, title, subheading):
    WIN.blit(create_overlay_surface(colour), (0, 0))
    title_text = render_font(title, 40)
    subheading_text = render_font(subheading, 30)
    WIN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - title_text.get_height() // 2))
    WIN.blit(subheading_text,
             (WIDTH // 2 - subheading_text.get_width() // 2, HEIGHT // 2 - subheading_text.get_height() // 2 + 45))


def draw_damage(damage, damage_frames):
    if damage > NONE:
        WIN.blit(create_overlay_surface(POTION, alpha=180 - (damage_frames * 6)), (0, 0))
    if damage < NONE:
        WIN.blit(create_overlay_surface(RED, alpha=180 - (damage_frames * 6)), (0, 0))


def draw_transition(transition_frames):
    WIN.blit(create_overlay_surface(BLACK, alpha=0 + transition_frames), (0, 0))


def check_for_interactions(global_map, player):
    for map_object in global_map.map_objects:
        if isinstance(map_object, InteractiveType):
            if map_object.rect.colliderect(player.rect):
                draw_popup(map_object.POPUP, player)
                return True, map_object
    return False, None


def draw_popup(text, player):
    popup_text = render_font(text, 12)
    WIN.blit(popup_text, (player.rect.x + player.PLAYER_WIDTH / 2 - popup_text.get_width() / 2,
                          player.rect.y - player.PLAYER_HEIGHT / 3))


def draw_sign(text):
    text = text.split("\n")
    exit_text = render_font("Enter >", 10)
    WIN.blit(SIGNPOST, (20, HEIGHT - SIGNPOST_HEIGHT))
    last_line = 0
    for line in text:
        sign_text = render_font(line, 20)
        WIN.blit(sign_text, (40, HEIGHT - SIGNPOST_HEIGHT + 20 + last_line))
        last_line += sign_text.get_height() + 10
    WIN.blit(exit_text, (SIGNPOST_WIDTH - exit_text.get_width(), HEIGHT - exit_text.get_height() - 10))


def draw_title_screen():
    WIN.blit(BACKGROUND, (0, 0))
    start_button = pygame.Rect(WIDTH / 2 - 100, HEIGHT / 2 + 50, 200, 75)
    quit_button = pygame.Rect(WIDTH / 2 - 100, HEIGHT / 2 + 150, 200, 75)
    logo = render_font("Athora", 60)
    sub_logo = render_font("SpaceF Strikes Back", 15)
    start_text = render_font("Play", 35 if start_button.collidepoint(pygame.mouse.get_pos()) else 30)
    quit_text = render_font("Quit", 35 if quit_button.collidepoint(pygame.mouse.get_pos()) else 30)
    WIN.blit(logo, (WIDTH / 2 - logo.get_width() / 2, HEIGHT / 2 - 150 + logo.get_height() / 2))
    WIN.blit(sub_logo, (WIDTH / 2 - sub_logo.get_width() / 2, HEIGHT / 2 - 50 + sub_logo.get_height() / 2))
    WIN.blit(start_text, (WIDTH / 2 - start_text.get_width() / 2, HEIGHT / 2 + 50 + start_text.get_height() / 2))
    WIN.blit(quit_text, (WIDTH / 2 - quit_text.get_width() / 2, HEIGHT / 2 + 150 + quit_text.get_height() / 2))
    return start_button, quit_button


def main():

    clock = pygame.time.Clock()
    running = True

    elapsed_time = 0

    state = TITLE

    player = Player()
    pygame.player = player
    gun_empty = False

    damage = NONE
    damage_frames = 0

    levels = []
    next_level_title = ""

    for index, level in enumerate(get_levels()):
        levels.append(Map(f'Level {index + 1}', level))

    levels = Maps(levels, player)

    hovering: (bool, InteractiveType) = (False, None)
    sign_status: (bool, Sign) = (False, None)

    changing_levels = False
    transition_frames = 0
    text_frames = 0

    while running:

        clock.tick(FPS)
        next_level = levels.next()

        if state == TITLE:

            start_button, quit_button = draw_title_screen()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if quit_button.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

                    if start_button.collidepoint(event.pos):
                        state = CONTINUE

            pygame.display.update()

            continue

        current_level = levels.current
        pygame.level = current_level

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

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

                    if event.key == pygame.K_m:
                        if player.inventory[player.inventory_selected_slot] is not None:
                            player.inventory[player.inventory_selected_slot].use()

                    if event.key == pygame.K_q:
                        player.remove_from_inventory()

                    if event.key == pygame.K_RETURN and sign_status[SIGN_OPEN]:
                        sign_status = (False, None)

                    if event.key == pygame.K_r:
                        if player.inventory[player.inventory_selected_slot] is not None:
                            selected = player.inventory[player.inventory_selected_slot]
                            if isinstance(selected, Gun):
                                selected.reload()
                                gun_empty = False

                    if event.key == pygame.K_1:
                        player.inventory_selected_slot = 1

                    if event.key == pygame.K_2:
                        player.inventory_selected_slot = 0

                    if event.key == pygame.K_f and hovering[IS_INTERACTING]:
                        hovering[INTERACTING_WITH].on_interact()

                if event.type == ExitDoor.ENTER:
                    if levels.next() is not None:
                        changing_levels = True
                        state = TRANSITION
                    else:
                        sign = Sign(0, 0, "This portal doesn't lead\nanywhere.")
                        sign_status = (True, sign)

                if event.type == Gun.EMPTY_GUN:
                    gun_empty = True

                if event.type == Potion.DRINK:
                    potion = event.potion
                    player.change_hp(potion.hp)
                    slot = player.inventory.index(potion)
                    player.inventory[slot] = None

                if event.type == DroppedItem.PICKUP:
                    item = event.item
                    player.add_to_inventory(item)

                if event.type == Sign.READ:
                    sign = event.sign
                    sign_status = (True, sign)

                if event.type == Lava.BURN and damage_frames == 0:
                    player.change_hp(-1)

                if event.type == player.DAMAGE:
                    if event.hp > 0:
                        damage = GAIN
                    if event.hp < 0:
                        if not player.DAMAGE_CHANNEL.get_busy() and player.HEALTH + event.hp > 0:
                            player.DAMAGE_CHANNEL.play(player.play_damage_sound())
                        damage = DEDUCT

                player.process_event(event)

        if state == CONTINUE:
            keys_pressed = pygame.key.get_pressed()
            player.handle_movement(WIN, keys_pressed, current_level)
            elapsed_time += 1 / FPS
            if not AMBIENCE_CHANNEL.get_busy():
                AMBIENCE_CHANNEL.play(AMBIENCE)

        if state != CONTINUE:
            if AMBIENCE_CHANNEL.get_busy():
                AMBIENCE_CHANNEL.stop()

        draw_window(player, current_level, elapsed_time, state)

        for enemy in levels.current.map_npc:
            if isinstance(enemy, RobotEnemy):
                if enemy.alerted:
                    enemy.alerted_time += 1 / FPS

        if gun_empty:
            draw_popup(Gun.RELOAD_TEXT, player)

        interactions = check_for_interactions(current_level, player)

        if interactions[IS_INTERACTING]:
            hovering = (True, interactions[INTERACTING_WITH])
        else:
            hovering = (False, None)

        if sign_status[SIGN_OPEN]:
            draw_sign(sign_status[SIGN_OBJ].CONTENTS)

        if damage != NONE:
            damage_frames += 1

        if damage_frames > 30:
            damage_frames = 0
            damage = NONE

        if damage_frames > 0:
            draw_damage(damage, damage_frames)

        if state == TRANSITION:

            if changing_levels:
                if transition_frames == 0:
                    next_level_title = next_level.title
                transition_frames += 2

            if not changing_levels:
                if transition_frames != 0:
                    transition_frames -= 2
                if text_frames != 0:
                    text_frames -= 4
                if transition_frames == 0 and text_frames == 0:
                    state = CONTINUE

            if transition_frames == 380:
                changing_levels = False
                levels + 1

            if transition_frames > 0:
                draw_transition(transition_frames)
                if transition_frames > 250:
                    text_frames += 4

            text = render_font(next_level_title, 30, alpha=text_frames)
            WIN.blit(text, (WIDTH/2 - text.get_width() / 2, HEIGHT/2 - text.get_height()/2))

        if state == PAUSED and player.HEALTH > 0:
            draw_overlay(GRAY, "Game Paused", "Press P to unpause")

        if player.HEALTH <= 0:
            draw_overlay(RED, "You died!", "Press R to restart")
            if state == CONTINUE:
                player.DEATH_NOISE.play()
            state = PAUSED

        pygame.display.update()


if __name__ == '__main__':
    while True:
        main()
