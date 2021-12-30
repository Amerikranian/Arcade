import os
import logging
import time

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import cytolk.tolk as tolk
import pygame

import games

from file_manager import FileManager
from game_menus import MainMenu
from screen_manager import ScreenManager
from context import Context

LOGGER_DIR = "logs"
LOGGER_FMT = "%Y/%m/%d %H:%M:%S"


def main():
    c = pygame.time.Clock()
    fm = FileManager()
    ctx = Context(fm)
    ctx.load_resources()
    sm = ScreenManager(ctx)
    sm.add_screen(MainMenu())
    while sm.has_screens():
        delta = c.tick(60) / 1000
        sm.update(delta)
        ctx.sounds.update()

    ctx.export_resources()
    ctx.free_resources()


if __name__ == "__main__":
    if not os.path.isdir(LOGGER_DIR):
        os.mkdir(LOGGER_DIR)
    # Make valid filename stem
    partial_file_stem = time.strftime(LOGGER_FMT).replace("/", "-").replace(":", "-")
    logging.basicConfig(
        filename=f"{LOGGER_DIR}/{partial_file_stem}.log",
        encoding="utf-8",
        format="%(asctime)s %(message)s",
        datefmt=LOGGER_FMT,
        level=logging.DEBUG,
    )
    pygame.init()
    w = pygame.display.set_mode((720, 480))
    pygame.display.set_caption("Testing Stuff")
    tolk.load()
    main()
    pygame.quit()
