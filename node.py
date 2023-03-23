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
                time.sleep((self.last_blink + self.blink_interval) - now)

            self.stop()

        thread = threading.Thread(target=run)
        thread.start()

    def stop(self):
        self.text_on = True
        self.blinking = False


class Text:
    def __init__(self, text):
        self.text = text
        self.blinking_message = ''

        self.blink_controller = BlinkController()

    def draw(self, radius, center, font_size=24, position='center'):
        if not self.blink_controller.blinking:
            str_text = self.text
        else:
            str_text = self.blinking_message

        rendered_text = Font.get_instance(font_size).render(str_text, True, BLACK)
        if position == 'top':
            text_pos = (center[0] - rendered_text.get_width() // 2, center[1] - radius - rendered_text.get_height())
        elif position == 'bottom':
            text_pos = (center[0] - rendered_text.get_width() // 2, center[1] + radius + (rendered_text.get_height() // 4))
        elif position == 'center':
            text_pos = (center[0] - rendered_text.get_width() // 2, center[1] - rendered_text.get_height() // 2)

        if self.blink_controller.text_on:
            Screen.get_instance().blit(rendered_text, text_pos)

    def update_text(self, new_text: str, blinking_message):
        self.text = new_text
        self.blinking_message = blinking_message
        self.blink()

    def blink(self):
        self.blink_controller.start()


class Node:
    def __init__(self, radius, center, color, name, channel):
        self.radius = radius
        self.center = center
        self.color = color
        self.channel = channel
        self.name = Text(name)
        self.channel_text = Text(f'Channel: {self.channel}')

    def draw(self):
        pygame.draw.circle(Screen.get_instance(), self.color, self.center, self.radius)
        self.name.draw(self.radius, self.center, font_size=FONT_SIZE, position='bottom')
        self.channel_text.draw(self.radius, self.center, font_size=FONT_SIZE, position='top')

    def change_channel(self, new_channel: int):
        self.channel_text.update_text(new_text=f'Channel: {new_channel}', blinking_message=f'Moving to {new_channel} (from {self.channel})')
        self.channel = new_channel
