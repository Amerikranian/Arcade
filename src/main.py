import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import cytolk.tolk as tolk
import pygame
import games
from menu import Menu
from screen_manager import ScreenManager
from context import Context


def main():
    c = pygame.time.Clock()
    ctx = Context()
    ctx.load_resources()
    sm = ScreenManager()
    s = Menu(
        {
            "Start game": lambda x: None,
            "Quit": lambda x: x.exit(),
        }
    )
    sm.add_screen(s)
    while sm.has_screens():
        delta = c.tick(60) / 1000
        sm.update(delta)

    ctx.free_resources()


if __name__ == "__main__":
    pygame.init()
    w = pygame.display.set_mode((720, 480))
    pygame.display.set_caption("Testing Stuff")
    tolk.load()
    main()
    pygame.quit()
