"""
Description:

Author: Willian T. Lunardi
Contact: wtlunar@gmail.com
License: MIT License (https://opensource.org/licenses/MIT)

Repository:
"""

import threading
import time
from enum import Enum
from typing import Union, Tuple, Optional

import numpy as np
import pygame
from scipy.ndimage.filters import gaussian_filter1d

from options import Options


class Colors(Enum):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)


class Vec2:
    def __init__(self, x: Union[Tuple[float, float], float], y: Optional[float] = None) -> None:
        if y is None:
            self.x, self.y = x
        else:
            self.x, self.y = x, y

    def __add__(self, other: 'Vec2') -> 'Vec2':
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vec2') -> 'Vec2':
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> 'Vec2':
        return Vec2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> 'Vec2':
        return Vec2(self.x / scalar, self.y / scalar)

    def __repr__(self) -> str:
        return f"Vec2({self.x}, {self.y})"


class BlinkController:
    def __init__(self, times: int = 5, blink_interval: float = 0.5):
        self.text_on: bool = True
        self.blinking: bool = False
        self.times: int = times
        self.blink_interval: float = blink_interval
        self.last_blink: float = 0

    def start(self) -> None:
        if self.blinking:
            return

        def run() -> None:
            counter: int = 0
            while counter < self.times * 2 + 1:
                self.blinking: bool = True
                self.text_on: bool = not self.text_on
                now: float = time.time()
                self.last_blink: float = now
                counter += 1
                time.sleep(self.blink_interval)
            self.stop()

        thread = threading.Thread(target=run)
        thread.start()

    def stop(self) -> None:
        self.text_on: bool = True
        self.blinking: bool = False


class Screen:
    __instance = None

    @staticmethod
    def get_instance(args: Options) -> pygame.Surface:
        """
        Returns a singleton instance of the Pygame screen.

        Args:
            args (Options): An instance of the Options class.

        Returns:
            pygame.Surface: The Pygame screen.
        """
        if Screen.__instance is None:
            if args.full_screen:
                info = pygame.display.Info()
                args.update_resolution(info.current_w, info.current_h)
                Screen.__instance = pygame.display.set_mode(args.screen_size, args.full_screen)
            else:
                Screen.__instance = pygame.display.set_mode(args.screen_size)
            pygame.display.set_caption("Mesh Network")
        return Screen.__instance

    @staticmethod
    def clear() -> None:
        """
        Clears the Pygame screen.
        """
        Screen.__instance.fill(WHITE)


class Font:
    __instance = None
    __size = None

    @staticmethod
    def get_instance(size: int) -> pygame.font.Font:
        """
        Returns a singleton instance of the Pygame font.

        Args:
            size (int): The font size.

        Returns:
            pygame.font.Font: The Pygame font.
        """
        if Font.__instance is None or Font.__size != size:
            Font.__size = size
            Font.__instance = pygame.font.SysFont(None, size)
        return Font.__instance


def quit_pygame() -> None:
    pygame.quit()


def generate_smooth_distribution(n_samples: int, index: int, noise: float = 0.05) -> np.ndarray:
    # Initialize an array with n_samples zeros
    distribution = np.zeros(n_samples)
    # Set the minimum value around the specified index
    distribution[index] = 0.1
    # Set the remaining values using a Gaussian kernel
    distribution = gaussian_filter1d(distribution, sigma=n_samples / 10)
    # Add some random noise to the distribution
    noise_array = noise * np.random.rand(n_samples)
    distribution += noise_array
    # Normalize the distribution so that its values sum up to one
    distribution /= np.sum(distribution)
    return normalize_array(distribution, lb=0.1, ub=1.0)


def normalize_array(arr: np.ndarray, lb: float = 0.0, ub: float = 1.0) -> np.ndarray:
    min_val = np.min(arr)
    max_val = np.max(arr)
    if max_val == min_val:
        return np.full_like(arr, lb)
    else:
        return (arr - min_val) / (max_val - min_val) * (ub - lb) + lb
