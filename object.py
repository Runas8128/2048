import pygame
import random

from util import makeText

class Object:
    def __init__(self):
        self.value = 0
        self.baseRect = None
        self.dirty = False
    
    async def draw(self, screen: pygame.Surface):
        if self.baseRect != None:
            pygame.draw.rect(screen, (0, 0, 0), self.baseRect, 3)
            if self.value != 0:
                screen.blit(
                    *makeText(str(self.value), 'nanumgothicbold', 50, self.baseRect.center)
                )
    
    def setRect(self, rect: pygame.Rect):
        self.baseRect = rect
    
    def make(self):
        self.value = 2 if random.random() < 0.9 else 4
    
    def remove(self):
        self.value = 0
