"""
Description:

Author: Willian T. Lunardi
Contact: wtlunar@gmail.com
License: MIT License (https://opensource.org/licenses/MIT)

Repository:
"""

from util import *


class Text:
    def __init__(self, text: Union[str, int, float], position: Union[Vec2, Tuple[int, int]], font_size: int = 24, color: pygame.Color = pygame.Color("black"),
                 orientation: str = 'horizontal'):
        self.text: str = str(text)
        self.blinking_message: str = ''
        self.position: Vec2 = position if isinstance(position, Vec2) else Vec2(*position)
        self.blink_controller: BlinkController = BlinkController()
        self.font_size: int = font_size
        self.color: pygame.Color = color
        self.orientation: str = orientation

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        str_text: str = self.text if not self.blink_controller.blinking else self.blinking_message
        rendered_text: pygame.Surface = font.render(str_text, True, self.color)
        rotated_text: pygame.Surface = self._apply_orientation(rendered_text)
        text_pos: Vec2 = self.position - Vec2(rotated_text.get_width() // 2, rotated_text.get_height() // 2)

        if self.blink_controller.text_on:
            surface.blit(rotated_text, (text_pos.x, text_pos.y))

    def update_text(self, new_text: str, blinking_message: str) -> None:
        self.text: str = new_text
        self.blinking_message: str = blinking_message
        self.blink()

    def blink(self) -> None:
        self.blink_controller.start()

    def _apply_orientation(self, rendered_text: pygame.Surface) -> pygame.Surface:
        if self.orientation == 'horizontal':
            return rendered_text
        elif self.orientation == 'vertical':
            return pygame.transform.rotate(rendered_text, 90)
        else:
            raise ValueError(f"Invalid orientation '{self.orientation}'. Supported values are 'horizontal' and 'vertical'.")
