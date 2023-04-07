import threading
import time

from util import *


class BlinkController:
    def __init__(self, times: int = 5, blink_interval: float = 0.5):
        self.text_on = True
        self.blinking = False
        self.times = times
        self.blink_interval = blink_interval
        self.last_blink = 0

    def start(self):
        if self.blinking:
            return

        def run():
            counter = 0
            while counter < self.times * 2 + 1:
                self.blinking = True
                self.text_on = not self.text_on
                now = time.time()
                self.last_blink = now
                counter += 1
                time.sleep(self.blink_interval)
            self.stop()

        thread = threading.Thread(target=run)
        thread.start()

    def stop(self):
        self.text_on = True
        self.blinking = False


class Text:
    def __init__(self, text, position, font_size=24, color=pygame.Color("black"), orientation='horizontal'):
        self.text = text if isinstance(text, str) else str(text)
        self.blinking_message = ''
        self.position = position if isinstance(position, Vec2) else Vec2(*position)
        self.blink_controller = BlinkController()
        self.font_size = font_size
        self.color = color
        self.orientation = orientation

    def draw(self, surface, font):
        str_text = self.text if not self.blink_controller.blinking else self.blinking_message
        rendered_text = font.render(str_text, True, self.color)
        rotated_text = self._apply_orientation(rendered_text)
        text_pos = self.position - Vec2(rotated_text.get_width() // 2, rotated_text.get_height() // 2)

        if self.blink_controller.text_on:
            surface.blit(rotated_text, (text_pos.x, text_pos.y))

    def update_text(self, new_text: str, blinking_message):
        self.text = new_text
        self.blinking_message = blinking_message
        self.blink()

    def blink(self):
        self.blink_controller.start()

    def _apply_orientation(self, rendered_text):
        if self.orientation == 'horizontal':
            return rendered_text
        elif self.orientation == 'vertical':
            return pygame.transform.rotate(rendered_text, 90)
        else:
            raise ValueError(f"Invalid orientation '{self.orientation}'. Supported values are 'horizontal' and 'vertical'.")


class Node:
    def __init__(self, name, channel, sprite_name, position):
        self.channel = channel
        self.sprite_name = sprite_name
        self.sprite = pygame.image.load(f'sprites/{sprite_name}').convert_alpha()
        self.shadow = pygame.image.load(f'sprites/node_shadow.png').convert_alpha()
        self.rect = self.sprite.get_rect()
        self.position = position if isinstance(position, Vec2) else Vec2(*position)

        # Set text positions
        self.name = Text(name, self.position + Vec2(0, self.rect.height // 2))
        self.channel_text = Text(f'Channel: {channel}', self.position - Vec2(0, self.rect.height // 2))

    def draw(self, surface, font):
        self.rect.center = (self.position.x, self.position.y)
        surface.blit(self.shadow, self.rect)
        surface.blit(self.sprite, self.rect)
        self.channel_text.draw(surface, font)
        self.name.draw(surface, font)

    def change_channel(self, new_channel: int):
        self.channel_text.update_text(new_text=f'Channel: {new_channel}', blinking_message=f'Moving to {new_channel} (from {self.channel})')
        self.channel = new_channel

    def set_position(self, position):
        self.position = position if isinstance(position, Vec2) else Vec2(*position)
        self.channel_text.position = self.position - Vec2(0, self.rect.height // 2 + FONT_SIZE)
        self.name.position = self.position + Vec2(0, self.rect.height // 2 + FONT_SIZE)
