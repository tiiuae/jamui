# jamui

This repository contains a Pygame UI for displaying jamming detection and avoidance. The UI features a mesh network consisting of three nodes: two regular nodes and a jammer node. The regular nodes are represented by circles with green color, while the jammer node is represented by a circle with red color. The nodes are initialized with a set radius, center, color, name, and channel.

The UI allows the user to switch the channel of the regular nodes by pressing the 'w' key. The channel information for each node is displayed using a Text class that shows the node name and the current channel number.

The Text class also provides a blinking function that can display a user-defined message in place of the node information. The blinking function is triggered when the channel of a node is changed and displays the message for a specified number of times and intervals.

The main loop of the UI continuously draws the nodes on the screen and updates the display. The user can close the UI by clicking the close button.

Overall, this Pygame UI provides a visual representation of jamming detection and avoidance in a mesh network.
