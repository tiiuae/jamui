import pygame

SCREEN_SIZE = (1000, 1000)
RADIUS = SCREEN_SIZE[0] // 25
FONT_SIZE = int(0.04 * SCREEN_SIZE[0])
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


class Screen:
    __instance = None

    @staticmethod
    def get_instance():
        if Screen.__instance is None:
            Screen.__instance = pygame.display.set_mode(SCREEN_SIZE)
            pygame.display.set_caption("Mesh Network")
        return Screen.__instance


class Font:
    __instance = None
    __size = None

    @staticmethod
    def get_instance(size):
        if Font.__instance is None or Font.__size != size:
            Font.__size = size
            Font.__instance = pygame.font.SysFont(None, size)
        return Font.__instance


def quit_pygame():
    pygame.quit()
