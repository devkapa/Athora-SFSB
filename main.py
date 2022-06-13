import datetime
import os.path
import sys

import pygame

from pygame.locals import *

# Enable double buffer
flags = DOUBLEBUF

# Initialise pygame modules
pygame.font.init()
pygame.display.init()
pygame.mixer.init()

# RGB colour codes
WHITE = (255, 255, 255)
AQUA = (0, 255, 255)
PINK = (255, 225, 225)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (168, 168, 168)
BLACK = (0, 0, 0)
POTION = (111, 142, 109)
MAGENTA = (255, 0, 255)

# Create an opaque window surface with defined width and height, and set a title
WIDTH, HEIGHT = 832, 640
WIN = pygame.display.set_mode((WIDTH, HEIGHT), flags, 8)
WIN.set_alpha(None)
pygame.display.set_caption("Athora: SpaceF Strikes Back")

# Set the icon of the window
ICON = pygame.image.load(os.path.join('assets', 'textures', 'tiles', 'wall.png'))
pygame.display.set_icon(ICON)

# Load background image and blit to a surface for later use
BACKGROUND = pygame.image.load(os.path.join('assets', 'textures', 'overlay', 'night_sky.png')).convert()
BACKGROUND_SURFACE = pygame.Surface((WIDTH, HEIGHT))
BACKGROUND_SURFACE.blit(BACKGROUND, (0, 0))

# Load and scale image to be used for signposts
SIGNPOST_WIDTH, SIGNPOST_HEIGHT = 600, 120
SIGNPOST_IMG = pygame.image.load(os.path.join('assets', 'textures', 'overlay', 'signpost.png')).convert()
SIGNPOST = pygame.transform.scale(SIGNPOST_IMG, (SIGNPOST_WIDTH, SIGNPOST_HEIGHT))

# Constant for game's frames per second
FPS = 60

# Enum values to be used for readable code:
TITLE, PAUSED, CONTINUE, TRANSITION = -1, 0, 1, 2  # Game state
DEDUCT, NONE, GAIN = -1, 0, 1  # Damage indicator
SIGN_OPEN, SIGN_OBJ = 0, 1  # Sign tuple indexes
IS_INTERACTING, INTERACTING_WITH = 0, 1  # InteractiveType tuple indexes

# Set an audio channel to be used only for background music
AMBIENCE_CHANNEL = pygame.mixer.Channel(6)
AMBIENCE = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'misc', 'ambience.wav'))


# Import modules intentionally after pygame is initialised to allow for image conversion
from user.inv_objects import Gun, Potion
from user.player import Player
from world.level import Level, Levels
from world.level_objects import InteractiveType, ExitDoor, CollideType, DroppedItem, Sign, Lava
from world.npc import RobotEnemy, NPC


# Returns a list containing the contents of each level file in the game assets
def get_levels():
    levels = []
    levels_dir = os.path.join('assets', 'levels')
    level_files = [f for f in os.listdir(levels_dir)
                   if os.path.isfile(os.path.join(levels_dir, f)) and f.lower().endswith(".txt")]
    for level in sorted(level_files, key=level_sorter):
        with open(f'{os.path.join(levels_dir, level)}', 'r') as file:
            levels.append(file.read())
    return levels


# Sort the levels in ascending order
def level_sorter(x):
    return os.path.split(x)[-1]


# Returns a surface with text in the game font
def render_text(text, px, color=WHITE, alpha=None):
    font = pygame.font.Font(os.path.join('assets', 'fonts', 'pressstart.ttf'), px)
    text = font.render(text, True, color)
    text.set_alpha(alpha) if alpha is not None else None
    return text


# Returns a surface, the same size as the game window, with a translucent colour overlay
def create_overlay_surface(colour, alpha=180):
    surface = pygame.Surface((WIDTH, HEIGHT))
    surface.set_alpha(alpha)
    surface.fill(colour)
    return surface


# Draw the background, current level, player, timer and bullets on the window surface
def draw_window(player, level, elapsed_time, state):
    WIN.blit(BACKGROUND_SURFACE, (0, 0))
    level.draw(WIN)
    if player.HEALTH > 0:
        if state == CONTINUE:
            draw_bullets(player, level)
        player.draw(WIN)
        title = render_text(level.title, 28)
        score_text = render_text("Score: " + str(player.get_score()), 20)
        timer = render_text(str(datetime.timedelta(seconds=round(elapsed_time))), 20)
        WIN.blit(title, (WIDTH - 5 - title.get_width(), 10))
        WIN.blit(timer, (WIDTH - 5 - timer.get_width(), title.get_height() + title.get_height() / 2))
        WIN.blit(score_text, (WIDTH - 5 - score_text.get_width(), title.get_height() + title.get_height() / 2 + timer.get_height() + timer.get_height() / 3))


# Calculate and draw the position of all bullets on the screen
# Update bullets if they collide with an entity or an object
def draw_bullets(player, level):
    npc_collision = False
    bullets = level.level_bullets.copy()
    for bullet in bullets:
        for npc in level.level_npc:
            if bullet.rect.colliderect(npc.rect) and isinstance(bullet.origin(), Player):
                npc.change_health(-1)
                npc_collision = True
            if npc.HEALTH <= 0:
                player.add_score(10)
                level.level_npc.remove(npc)
        if bullet.facing == bullet.LEFT:
            bullet.rect.x -= bullet.SPEED
        if bullet.facing == bullet.RIGHT:
            bullet.rect.x += bullet.SPEED
        if bullet.rect.x < 0 or bullet.rect.x > WIDTH:
            level.level_bullets.remove(bullet)
        elif bullet.rect.colliderect(player.rect) and isinstance(bullet.origin(), NPC):
            player.change_hp(-1)
            level.level_bullets.remove(bullet)
        elif npc_collision:
            level.level_bullets.remove(bullet)
        elif any(wall.rect.colliderect(bullet.rect) and isinstance(wall, CollideType) for wall in level.level_objects):
            level.level_bullets.remove(bullet)
        else:
            bullet.draw(WIN)
        npc_collision = False


# Draw a window sized overlay above the game window with a title and subheading
def draw_overlay(colour, title, subheading):
    WIN.blit(create_overlay_surface(colour), (0, 0))
    title_text = render_text(title, 40)
    subheading_text = render_text(subheading, 30)
    WIN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - title_text.get_height() // 2))
    WIN.blit(subheading_text,
             (WIDTH // 2 - subheading_text.get_width() // 2, HEIGHT // 2 - subheading_text.get_height() // 2 + 45))


# Draw a window sized overlay above the game window and slowly fade out over time
# Change the colour of the overlay depending on if the player is taking damage or healing
def draw_damage(damage, damage_frames):
    if damage > NONE:
        WIN.blit(create_overlay_surface(POTION, alpha=180 - (damage_frames * 6)), (0, 0))
    if damage < NONE:
        WIN.blit(create_overlay_surface(RED, alpha=180 - (damage_frames * 6)), (0, 0))


# Draw a black window sized overlay above the game window and slowly fade in and out over time
def draw_transition(transition_frames):
    WIN.blit(create_overlay_surface(BLACK, alpha=0 + transition_frames), (0, 0))


# For every physical object in the current level, check if the player is colliding with it
# If the object is an InteractiveType, display a popup prompting the player to interact
def check_for_interactions(level, player):
    for level_object in level.level_objects:
        if isinstance(level_object, InteractiveType):
            if level_object.rect.colliderect(player.rect):
                draw_popup(level_object.POPUP, player)
                return True, level_object
    return False, None


# Draw a small text popup above the player's head
def draw_popup(text, player):
    popup_text = render_text(text, 12)
    WIN.blit(popup_text, (player.rect.x + player.PLAYER_WIDTH / 2 - popup_text.get_width() / 2,
                          player.rect.y - player.PLAYER_HEIGHT / 3))


# Draw a large signpost texture with a multi-line text popup at the bottom of the screen
def draw_sign(text):
    text = text.split("\n")
    exit_text = render_text("Enter >", 10, MAGENTA)
    WIN.blit(SIGNPOST, (20, HEIGHT - SIGNPOST_HEIGHT))
    last_line = 0
    for line in text:
        sign_text = render_text(line, 20, MAGENTA)
        WIN.blit(sign_text, (40, HEIGHT - SIGNPOST_HEIGHT + 20 + last_line))
        last_line += sign_text.get_height() + 10
    WIN.blit(exit_text, (SIGNPOST_WIDTH - exit_text.get_width(), HEIGHT - exit_text.get_height() - 10))


# Draw window sized screen with a title and interactive buttons that enlarge when hovered over
# Return the start and quit button rectangles to pass to the event checker
def draw_title_screen():
    WIN.blit(BACKGROUND, (0, 0))
    start_button = pygame.Rect(WIDTH / 2 - 100, HEIGHT / 2 + 50, 200, 75)
    quit_button = pygame.Rect(WIDTH / 2 - 100, HEIGHT / 2 + 150, 200, 75)
    logo = render_text("Athora", 60)
    sub_logo = render_text("SpaceF Strikes Back", 15)
    start_text = render_text("Play", 35 if start_button.collidepoint(pygame.mouse.get_pos()) else 30)
    quit_text = render_text("Quit", 35 if quit_button.collidepoint(pygame.mouse.get_pos()) else 30)
    WIN.blit(logo, (WIDTH / 2 - logo.get_width() / 2, HEIGHT / 2 - 150 + logo.get_height() / 2))
    WIN.blit(sub_logo, (WIDTH / 2 - sub_logo.get_width() / 2, HEIGHT / 2 - 50 + sub_logo.get_height() / 2))
    WIN.blit(start_text, (WIDTH / 2 - start_text.get_width() / 2, HEIGHT / 2 + 50 + start_text.get_height() / 2))
    WIN.blit(quit_text, (WIDTH / 2 - quit_text.get_width() / 2, HEIGHT / 2 + 150 + quit_text.get_height() / 2))
    return start_button, quit_button


def main():

    # Initialise pygame's clock and start the game loop
    clock = pygame.time.Clock()
    running = True

    # Initialise variable to keep track of elapsed time in seconds
    elapsed_time = 0

    # Set the initial state to the title screen
    state = TITLE

    # Create a player and set a pygame constant
    player = Player()
    pygame.player = player

    # Variables to hold damage state and elapsed frames
    damage = NONE
    damage_frames = 0

    # Empty list and string to hold levels
    levels = []
    next_level_title = ""

    # Serialize each level file into a Level object and append to a list
    for index, level in enumerate(get_levels()):
        levels.append(Level(f'Level {index + 1}', level))

    # Turn the list into an object which holds series of levels
    levels = Levels(levels, player)

    # Variables to hold interaction and sign state
    hovering: (bool, InteractiveType) = (False, None)
    sign_status: (bool, Sign) = (False, None)

    # Variables to hold level change state and elapsed frames
    changing_levels = False
    transition_frames = 0
    text_frames = 0

    while running:

        # Limit the loop to run only 60 times per second
        clock.tick(FPS)

        # Store the next level
        next_level = levels.next()

        # Check if the game is in the TITLE SCREEN state
        if state == TITLE:

            start_button, quit_button = draw_title_screen()

            # Iterate through pygame events
            for event in pygame.event.get():

                # Exit the program if the user quit
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Check if the user clicked the mouse
                if event.type == pygame.MOUSEBUTTONDOWN:

                    # Exit the program if the user pressed the "Quit" text
                    if quit_button.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

                    # Set the game state to CONTINUE if the user pressed the "Start" text
                    if start_button.collidepoint(event.pos):
                        state = CONTINUE

            pygame.display.update()

            continue

        # Get the current level
        current_level = levels.current
        pygame.level = current_level

        # Iterate through pygame events
        for event in pygame.event.get():

            # Exit the program if the user quit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Check if the game is in the PAUSED state
            if state == PAUSED:

                # Check if the user pressed a keyboard key
                if event.type == pygame.KEYDOWN:

                    # If the game is paused and the player is dead, end the game if 'R' is pressed
                    if event.key == pygame.K_r and player.HEALTH < 1:
                        running = False

                    # If the game is paused and the player is not dead, unpause the game if 'P' is pressed
                    if event.key == pygame.K_p and player.HEALTH > 0:
                        state = CONTINUE
                        continue

            # Check if the game is in the CONTINUE state
            if state == CONTINUE:

                # Check if the user pressed a keyboard key
                if event.type == pygame.KEYDOWN:

                    # Set the game state to PAUSED if 'P' is pressed
                    if event.key == pygame.K_p:
                        state = PAUSED
                        continue

                    # Use the selected item in the player's inventory if 'M' is pressed
                    if event.key == pygame.K_m:
                        if player.inventory[player.inventory_selected_slot] is not None:
                            player.inventory[player.inventory_selected_slot].use()

                    # Drop the selected item in the player's inventory if 'Q' is pressed
                    if event.key == pygame.K_q:
                        player.remove_from_inventory()

                    # Close a sign if one is currently open and 'ENTER' is pressed
                    if event.key == pygame.K_RETURN and sign_status[SIGN_OPEN]:
                        sign_status = (False, None)

                    # If the selected item in the player's inventory is a gun, reload it when 'R' is pressed
                    if event.key == pygame.K_r:
                        if player.inventory[player.inventory_selected_slot] is not None:
                            selected = player.inventory[player.inventory_selected_slot]
                            if isinstance(selected, Gun):
                                selected.reload()
                                Gun.EMPTY = False

                    # Switch inventory slots
                    if event.key == pygame.K_1:
                        player.inventory_selected_slot = 1

                    if event.key == pygame.K_2:
                        player.inventory_selected_slot = 0

                    # Interact with an InteractiveType object if 'F' is pressed
                    if event.key == pygame.K_f and hovering[IS_INTERACTING]:
                        hovering[INTERACTING_WITH].on_interact()

                # Advance to the next level if a portal is entered
                # If there is no next level, display a sign message
                if event.type == ExitDoor.ENTER:
                    if levels.next() is not None:
                        changing_levels = True
                        door = event.door
                        door.PORTAL_SOUND.play()
                        state = TRANSITION
                    else:
                        if sign_status[SIGN_OBJ] != ExitDoor.NO_LEVEL:
                            ExitDoor.NO_LEVEL.READ_SOUND.play()
                            sign_status = (True, ExitDoor.NO_LEVEL)

                # Add health to the player if a potion was consumed
                if event.type == Potion.DRINK:
                    potion = event.potion
                    player.change_hp(potion.hp)
                    slot = player.inventory.index(potion)
                    player.inventory[slot] = None

                # Add an item to the player's inventory if a dropped item was picked up
                if event.type == DroppedItem.PICKUP:
                    item = event.item
                    player.add_to_inventory(item)

                # Display a sign message if a sign was interacted with
                if event.type == Sign.READ:
                    sign = event.sign
                    if sign_status[SIGN_OBJ] != sign:
                        sign.READ_SOUND.play()
                        sign_status = (True, sign)

                # Burn the player if they are submerged in lava
                if event.type == Lava.BURN and damage_frames == 0:
                    player.change_hp(-1)

                # Alter the damage status if the player took damage
                if event.type == player.DAMAGE:
                    if event.hp > 0:
                        damage = GAIN
                    if event.hp < 0:
                        if not player.DAMAGE_CHANNEL.get_busy() and player.HEALTH + event.hp > 0:
                            player.DAMAGE_CHANNEL.play(player.play_damage_sound())
                        damage = DEDUCT

                # Pass events to the player to handle player damage
                player.process_event(event)

        # Check if the game state is set to CONTINUE
        if state == CONTINUE:

            # Handle player movement
            keys_pressed = pygame.key.get_pressed()
            player.handle_movement(WIN, keys_pressed, current_level)

            # Increment elapsed time by 1 every 60 frames
            elapsed_time += 1 / FPS

            # Play background music if it isn't playing already
            if not AMBIENCE_CHANNEL.get_busy():
                AMBIENCE_CHANNEL.play(AMBIENCE)

        # If the music is playing outside the CONTINUE state, stop it
        if state != CONTINUE:
            if AMBIENCE_CHANNEL.get_busy():
                AMBIENCE_CHANNEL.stop()

        draw_window(player, current_level, elapsed_time, state)

        # Increment an enemy's alert timer if they are alerted
        for enemy in levels.current.level_npc:
            if isinstance(enemy, RobotEnemy):
                if enemy.alerted:
                    enemy.alerted_time += 1 / FPS

        # If a Gun in the player's inventory is empty, prompt them to reload
        for item in player.inventory:
            if isinstance(item, Gun):
                if item.EMPTY and player.inventory[player.inventory_selected_slot] == item:
                    draw_popup(Gun.RELOAD_TEXT, player)

        # Check if the player is hovering over an InteractiveType object
        interactions = check_for_interactions(current_level, player)

        # If they are hovering over an InteractiveType, save it to a variable
        if interactions[IS_INTERACTING]:
            hovering = (True, interactions[INTERACTING_WITH])
        else:
            hovering = (False, None)

        # If a sign is read by a player, draw it
        if sign_status[SIGN_OPEN]:
            draw_sign(sign_status[SIGN_OBJ].CONTENTS)

        # Increment the damage frame counter if the player's health is changing
        if damage != NONE:
            damage_frames += 1

        # Reset the damage frame counter and damage status if it goes over 30
        if damage_frames > 30:
            damage_frames = 0
            damage = NONE

        # If the damage frame counter is incrementing, draw the damage animation
        if damage_frames > 0:
            draw_damage(damage, damage_frames)

        # Check if the game state is set to TRANSITIONING
        if state == TRANSITION:

            # If the animation is increasing, increment the transition frame counter
            if changing_levels:
                if transition_frames == 0:
                    next_level_title = next_level.title
                transition_frames += 2

            # If the animation is decreasing, decrement the transition and text frame counter
            # Once both counters are reset, set the game state back to CONTINUE
            if not changing_levels:
                if transition_frames != 0:
                    transition_frames -= 2
                if text_frames != 0:
                    text_frames -= 4
                if transition_frames == 0 and text_frames == 0:
                    state = CONTINUE

            # If the transition is finished increasing, start decreasing it
            # This also sets the current level to the next level
            if transition_frames == 380:
                changing_levels = False
                levels + 1

            # If the transition frame counter is increasing or decreasing, draw the animation
            if transition_frames > 0:
                draw_transition(transition_frames)
                # If the transition is almost opaque (alpha is ~250), start incrementing the text frame counter
                if transition_frames > 250:
                    text_frames += 4

            # Render text displaying the name of the next level at the opacity of the text frame counter
            text = render_text(next_level_title, 30, alpha=text_frames)
            WIN.blit(text, (WIDTH/2 - text.get_width() / 2, HEIGHT/2 - text.get_height()/2))

        # If the game state is set to PAUSED and the player is alive, render the PAUSE overlay
        if state == PAUSED and player.HEALTH > 0:
            draw_overlay(GRAY, "Game Paused", "Press P to unpause")

        # If the player is dead, render the death overlay and set the game state to PAUSED
        if player.HEALTH <= 0:
            draw_overlay(RED, "You died!", "Press R to restart")
            if state == CONTINUE:
                player.DEATH_NOISE.play()
            state = PAUSED

        pygame.display.update()


if __name__ == '__main__':
    while True:
        main()
