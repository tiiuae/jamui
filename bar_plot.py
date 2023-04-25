"""
Description:

Author: Willian T. Lunardi
Contact: wtlunar@gmail.com
License: MIT License (https://opensource.org/licenses/MIT)

Repository:
"""

import random
import threading
import time
from typing import List

import numpy as np
import pygame

from text import Text


class Bar:
    def __init__(self, x: int, y: int, ch: int) -> None:
        self.x: int = x
        self.y: int = y
        self.ch = ch
        self.red_sprite: pygame.Surface = pygame.image.load(f'sprites/bar_red.png').convert_alpha()
        self.green_sprite: pygame.Surface = pygame.image.load(f'sprites/bar_green.png').convert_alpha()
        self.current_ch_sprite: pygame.Surface = pygame.image.load(f'sprites/bar_green_active.png').convert_alpha()
        self.shadow: pygame.Surface = pygame.image.load(f'sprites/bar_shadow2.png').convert_alpha()
        self.sprite: pygame.Surface = self.green_sprite
        self.rect: pygame.Rect = self.sprite.get_rect()
        self.ch_numb: Text = Text(ch, (x + self.rect.width // 2, self.y - 12), orientation='horizontal')
        self.value: float = 0.0
        self.target_value: float = 0.0

    def draw(self, surface: pygame.Surface, current_channel: int) -> None:
        if self.ch == current_channel:
            self.sprite = self.current_ch_sprite
        else:
            self.sprite = self.red_sprite if self.value < 0.5 else self.green_sprite
        self.rect = self.sprite.get_rect()

        # pygame.draw.circle(surface, (0, 255, 0), (self.x, self.y), 10)
        self.rect.bottomleft = (self.x, self.y + (self.rect.height * (1 - self.value)))
        surface.blit(self.sprite, self.rect)
        self.rect.bottomleft = (self.x + self.rect.width, self.y + (self.rect.height * (1 - self.value)))
        surface.blit(self.shadow, self.rect)

    def draw_ch_numb(self, surface: pygame.Surface, font: pygame.font.Font, ticks: bool = True) -> None:
        self.ch_numb.draw(surface, font)

        if ticks:
            pygame.draw.line(surface, (0, 0, 0), (self.x + self.rect.width // 2, self.y - 2), (self.x + self.rect.width // 2, self.y + 2))  # y line

    def transition_to_target_value(self, duration: float) -> None:
        if self.value == self.target_value:
            return

        start_value: float = self.value
        start_time: float = time.time()
        end_time: float = start_time + duration

        def run() -> None:
            while time.time() < end_time:
                t: float = (time.time() - start_time) / duration
                self.value = start_value + t * (self.target_value - start_value)
                time.sleep(0.01)

            self.value = self.target_value

        thread: threading.Thread = threading.Thread(target=run)
        thread.start()


class BarPlot:
    def __init__(self, x: int, y: int, width: int, height: int, x_axis: List[int], bar_width: int = 62, bottom_spacing: int = 50, side_spacing: int = 50, x_title: str = '',
                 y_title: str = '') -> None:
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height
        self.num_bars: int = len(x_axis)
        self.bar_width: int = bar_width
        self.bar_spacing: int = (width - side_spacing - bar_width * self.num_bars) // self.num_bars
        self.bottom_spacing: int = bottom_spacing
        self.side_spacing: int = side_spacing
        self.bars: List[Bar] = []

        self.x_text: Text = Text(x_title, (x + self.width // 2, self.y + self.height - (self.bottom_spacing // 2)), orientation='horizontal')
        self.y_text: Text = Text(y_title, (x + self.side_spacing // 2, y + self.height // 2), orientation='vertical')

        pad: int = self.bar_spacing // 2
        for i in range(self.num_bars):
            bar_x: int = self.x + pad + self.side_spacing + i * (self.bar_spacing + bar_width)
            bar_y: int = self.y + height - self.bottom_spacing
            bar: Bar = Bar(bar_x, bar_y, ch=x_axis[i])
            self.bars.append(bar)

        # Temporary
        self.last_update: float = time.time()
        self.update_bar_values(np.linspace(0.0, 1, self.num_bars))

    def update_bar_values(self, values: np.ndarray, transition_duration: float = 1.0) -> None:
        min_value, max_value = 0.1, 1.0
        value_range = max_value - min_value
        for i, bar in enumerate(self.bars):
            if values[i] is not None:
                bar.target_value = min_value + (values[i] * value_range)
                bar.transition_to_target_value(transition_duration)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, values: np.ndarray, current_channel: int) -> None:
        new_values_interval_sec: int = 2
        if time.time() - new_values_interval_sec > self.last_update:
            index: int = random.randint(0, self.num_bars - 1)
            # values: np.ndarray = generate_smooth_distribution(self.num_bars, index)
            self.update_bar_values(values)
            self.last_update: float = time.time()

        for i, bar in enumerate(self.bars):
            bar.draw(surface, current_channel)

        # Draw bottom and side rectangle
        pygame.draw.rect(surface, (255, 255, 255), (self.x, self.y + self.height - self.bottom_spacing, self.width, self.bottom_spacing), 0)  # x axis
        pygame.draw.line(surface, (0, 0, 0), (self.x, self.y + self.height - self.bottom_spacing), (self.x + self.width, self.y + self.height - self.bottom_spacing))  # x line

        for i, bar in enumerate(self.bars):
            bar.draw_ch_numb(surface, font)

        # pygame.draw.rect(surface, (255, 255, 255), (self.x, self.y, self.side_spacing, self.height), 0)  # y axis
        pygame.draw.line(surface, (0, 0, 0), (self.x + self.side_spacing, self.y), (self.x + self.side_spacing, self.y + self.height - self.bottom_spacing))  # y line

        self.x_text.draw(surface, font)
        self.y_text.draw(surface, font)

        # pygame.draw.circle(surface, (255, 0, 0), (self.x, self.y), 10)
        pygame.draw.rect(surface, (0, 0, 0), (self.x, self.y, self.width, self.height), 1)
