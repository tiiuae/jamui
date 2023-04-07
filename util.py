import pygame
import numpy as np
from scipy.ndimage.filters import gaussian_filter1d

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


class Vec2:
    def __init__(self, x, y=None):
        if y is None:
            self.x, self.y = x
        else:
            self.x, self.y = x, y

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vec2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Vec2(self.x / scalar, self.y / scalar)

    def __repr__(self):
        return f"Vec2({self.x}, {self.y})"


class Screen:
    __instance = None

    @staticmethod
    def get_instance(args):
        if Screen.__instance is None:
            if args.full_screen:
                info = pygame.display.Info()
                args.update_resolution(info.current_w, info.current_h)
                Screen.__instance = pygame.display.set_mode(args.screen_size, args.full_screen)
            else:
                Screen.__instance = pygame.display.set_mode(args.screen_size)
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


def generate_smooth_distribution(n_samples, index, noise=0.05):
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


def normalize_array(arr, lb=0.0, ub=1.0):
    min_val = np.min(arr)
    max_val = np.max(arr)
    if max_val == min_val:
        return np.full_like(arr, lb)
    else:
        return (arr - min_val) / (max_val - min_val) * (ub - lb) + lb
