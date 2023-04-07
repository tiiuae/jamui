"""
options.py
Description: 

Author: Willian T. Lunardi
Contact: wtlunar@gmail.com
License: MIT License (https://opensource.org/licenses/MIT)

Repository:
"""

import argparse


class Options:
    def __init__(self):
        self.full_screen = True
        self.screen_width = 1250
        self.screen_height = 1000
        self.node_spacing = 0
        self.top_height = 0
        self.font_size = 0
        self.noise = 0.05
        self.screen_size = (self.screen_width, self.screen_height)
        self.parse_options()

    def parse_options(self):
        parser = argparse.ArgumentParser(description='Mesh Network Jamming Avoidance Demo UI')

        parser.add_argument('--full-screen', action='store_true', default=self.full_screen, help='Set full screen mode')
        parser.add_argument('--screen-width', type=int, default=self.screen_width, help='Screen width in pixels')
        parser.add_argument('--screen-height', type=int, default=self.screen_height, help='Screen height in pixels')
        parser.add_argument('--node-spacing', type=int, default=self.node_spacing, help='Spacing between nodes in pixels')
        parser.add_argument('--top-height', type=int, default=self.top_height, help='Height of the top section in pixels')
        parser.add_argument('--font-size', type=int, default=self.font_size, help='Font size in pixels')
        parser.add_argument('--noise', type=float, default=self.noise, help='Amount of noise to add to the distribution')

        args = parser.parse_args()

        self.full_screen = args.full_screen
        self.screen_width = args.screen_width
        self.screen_height = args.screen_height
        self.node_spacing = args.node_spacing
        self.top_height = args.top_height
        self.font_size = args.font_size
        self.noise = args.noise

        if self.node_spacing == 0 or self.top_height == 0 or self.font_size == 0:
            self.update_resolution(self.screen_width, self.screen_height)

        return self

    def update_resolution(self, width, height):
        self.screen_width, self.screen_height = width, height
        self.node_spacing = self.screen_width // 3
        self.top_height = self.screen_height // 2
        self.font_size = int(0.04 * self.screen_height)
        self.screen_size = (self.screen_width, self.screen_height)
