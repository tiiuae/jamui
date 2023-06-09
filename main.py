"""
Description:
Author: Willian T. Lunardi
Contact: wtlunar@gmail.com
License: MIT License (https://opensource.org/licenses/MIT)
Repository:
"""

import logging
import sqlite3
from typing import List

import pygame

from bar_plot import BarPlot
from node import Node
from options import Options
from util import Screen, Font, Colors, quit_pygame

logging.basicConfig(level=logging.INFO)


def main() -> None:
    args: Options = Options()

    # Initialize Pygame
    pygame.init()

    # Set up the screen
    screen: pygame.Surface = Screen.get_instance(args)
    font: pygame.font.Font = Font.get_instance(24)

    # Create mesh nodes and jammer
    mesh_nodes: List[Node] = [Node(f'Node {i + 1}', -1, ((args.screen_size[0] // 2) - args.node_spacing + (i * args.node_spacing), (args.top_height // 4))) for i in range(3)]
    jammer: Node = Node('Jammer', None, (args.screen_size[0] // 2, 3 * args.top_height // 4))

    # Create the bar plot
    channels: List[int] = [36, 40, 44, 48, 52, 56, 60, 64, 149, 153, 157, 161, 165]
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

    # Connect to the database
    conn = sqlite3.connect('server/demo.db')
    c = conn.cursor()
    current_channel = -1

    # Main loop
    done: bool = False
    while not done:
        # Check for latest wireless scanner channel on database
        latest_channel = None
        try:
            c.execute("SELECT * FROM node_channels")
            results = c.fetchall()
            if results is not None:
                latest_channel = int(results[0][1])
        except Exception as e:
            logging.error("Database connection error", exc_info=True)

        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            # elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            #     r: float = np.random.random()
            #     for node in mesh_nodes:
            #         node.change_channel(int(r * 10))

        # Check if latest channel is different from current, if yes, update text with animation
        if latest_channel is not None and latest_channel != current_channel:
            current_channel = latest_channel
            for node in mesh_nodes:
                node.change_channel(latest_channel)

        # Clear the screen
        screen.fill(Colors.WHITE.value)

        # Add border around whole screen
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, args.screen_width, args.screen_height), 1)

        # Draw mesh nodes
        for node in mesh_nodes:
            node.draw(screen, font)

        # Draw jammer
        jammer.draw(screen, font)

        # Draw plot by loading quality estimation values from database
        try:
            c.execute("SELECT * FROM channel_quality")
            results = c.fetchall()
            if results is not None:
                values = [None] * len(channels)
                for row in results:
                    if row[0] in channels:
                        values[channels.index(row[0])] = row[1]
                bar_plot.draw(screen, font, values, current_channel)
        except Exception as e:
            logging.error("Database connection error", exc_info=True)

        # Update the display
        pygame.display.flip()

    # Quit Pygame
    quit_pygame()


if __name__ == '__main__':
    main()
