import numpy as np

from node import Node
from util import *

# Initialize Pygame
pygame.init()

# Set up the screen
screen = Screen.get_instance()
font = Font.get_instance(24)

# Define the nodes
node1 = Node(radius=RADIUS, center=(SCREEN_SIZE[0] // 4, SCREEN_SIZE[1] // 4), color=GREEN, name='N1', channel=2)
node2 = Node(radius=RADIUS, center=((SCREEN_SIZE[0] // 4) * 3, SCREEN_SIZE[1] // 4), color=GREEN, name=' N2', channel=2)
jammer = Node(radius=RADIUS, center=((SCREEN_SIZE[0] // 2), (SCREEN_SIZE[1] // 4) * 3), color=RED, name='Jammer', channel=2)
jammer.channel_text.update_text(new_text=f'Jamming Channel 2', blinking_message=f'Jamming Channel 2')
nodes = [node1, node2, jammer]

# Main loop
done = False
while not done:
    # Check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            r = np.random.random()
            node1.change_channel(int(r * 10))
            node2.change_channel(int(r * 10))

    # Clear the screen
    screen.fill(WHITE)

    # Draw the nodes
    for node in nodes:
        node.draw()

    # Update the display
    pygame.display.flip()

# Quit Pygame
quit_pygame()
