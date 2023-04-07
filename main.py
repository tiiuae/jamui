"""
Description:

Author: Willian T. Lunardi
Contact: wtlunar@gmail.com
License: MIT License (https://opensource.org/licenses/MIT)

Repository:
"""

from typing import List

import numpy as np
import pygame

from bar_plot import BarPlot
from node import Node
from options import Options
from util import Screen, Font, WHITE, quit_pygame


def main() -> None:
    args: Options = Options()

    # Initialize Pygame
    pygame.init()

    # Set up the screen
    screen: pygame.Surface = Screen.get_instance(args)
    font: pygame.font.Font = Font.get_instance(24)

    # Create mesh nodes and jammer
    mesh_nodes: List[Node] = [
        Node(f'Node {i + 1}', 2, 'node_green2.png', ((args.screen_size[0] // 2) - args.node_spacing + (i * args.node_spacing), (args.top_height // 4))) for i in range(3)]
    jammer: Node = Node('Jammer', 2, 'node_red.png', (args.screen_size[0] // 2, 3 * args.top_height // 4))

    # Create the bar plot
    channels: List[int] = [36, 40, 44, 48, 149, 153, 157, 161, 165]
    plot_width: int = args.screen_width
    plot_height: int = args.screen_height // 2
    bar_plot: BarPlot = BarPlot(
        x=args.screen_size[0] // 2 - plot_width // 2,
        y=args.screen_size[1] - plot_height,
        width=plot_width,
        height=plot_height,
        x_axis=channels,
        x_title='5GHz Channels',
        y_title='Estimated Channel Quality'
    )

    # Main loop
    done: bool = False
    while not done:
        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                r: float = np.random.random()
                for node in mesh_nodes:
                    node.change_channel(int(r * 10))

        # Clear the screen
        screen.fill(WHITE)

        # Add border around whole screen
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, args.screen_width, args.screen_height), 1)

        # Draw mesh nodes
        for node in mesh_nodes:
            node.draw(screen, font)

        # Draw jammer
        jammer.draw(screen, font)

        # Draw plot
        bar_plot.draw(screen, font)

        # Update the display
        pygame.display.flip()

    # Quit Pygame
    quit_pygame()


if __name__ == '__main__':
    main()
