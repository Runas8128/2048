from typing import Tuple
from enum import Enum, auto

import pygame

def makeText(text: str, font: str, size: int, center: Tuple[int]):
    font = pygame.font.SysFont(font, size)
    textObj = font.render(text, True, (0, 0, 0))
    textRect = textObj.get_rect()
    textRect.center = center
    return textObj, textRect
