"""
Description:

Author: Willian T. Lunardi
Contact: wtlunar@gmail.com
License: MIT License (https://opensource.org/licenses/MIT)

Repository:
"""

from text import Text
from util import *


class Node:
    def __init__(self, name: str, channel: int, position: Tuple[int, int]):
        self.channel: int = channel
        if name == 'Jammer':
            self.sprite: pygame.Surface = pygame.image.load(f'sprites/node_red.png').convert_alpha()
        else:
            self.sprite: pygame.Surface = pygame.image.load(f'sprites/node_green2.png').convert_alpha()
        self.shadow: pygame.Surface = pygame.image.load(f'sprites/node_shadow.png').convert_alpha()
        self.rect: pygame.Rect = self.sprite.get_rect()
        self.position: Vec2 = position if isinstance(position, Vec2) else Vec2(*position)

        # Set text positions
        self.name: Text = Text(name, self.position + Vec2(0, self.rect.height // 2))
        self.channel_text: Text = Text(f'Channel: {channel}', self.position - Vec2(0, self.rect.height // 2)) if channel is not None else None

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        self.rect.center = (self.position.x, self.position.y)
        surface.blit(self.shadow, self.rect)
        surface.blit(self.sprite, self.rect)
        if self.channel_text is not None:
            self.channel_text.draw(surface, font)
        self.name.draw(surface, font)

    def change_channel(self, new_channel: int) -> None:
        self.channel_text.update_text(new_text=f'Channel: {new_channel}', blinking_message=f'Moving to {new_channel} (from {self.channel})')
        self.channel: int = new_channel
