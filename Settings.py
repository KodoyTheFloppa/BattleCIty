import pygame

SCREEN_WIDTH = 780  # 60 * 13 = 780
SCREEN_HEIGHT = 585  # 45 * 13 = 585
FPS = 60

def upscale(image, scale_factor):
    """Функция для увеличения размера изображения."""
    width, height = image.get_size()
    return pygame.transform.scale(image, (width * scale_factor, height * scale_factor))