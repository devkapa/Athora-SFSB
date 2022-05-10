import pygame
import pygame_gui


def main():
    pygame.init()

    pygame.display.set_caption("Athora: SpaceF Strikes Back")
    window_surface = pygame.display.set_mode((800, 600))

    background = pygame.Surface((800, 600))
    background.fill(pygame.Color('#00FFFF'))

    manager = pygame_gui.UIManager((800, 600))

    play = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)), text='Play!', manager=manager)

    clock = pygame.time.Clock()

    running = True

    while running:
        tick = clock.tick(60)/1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == play:
                    print("Play")

            manager.process_events(event)

        manager.update(tick)

        window_surface.blit(background, (0, 0))
        manager.draw_ui(window_surface)

        pygame.display.update()


if __name__ == '__main__':
    main()
