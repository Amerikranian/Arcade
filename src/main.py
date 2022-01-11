import os
import logging
import synthizer
import time

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame

import games

from file_manager import FileManager
from game_menus import MainMenu
from screen_manager import ScreenManager
from context import Context
from audio import BufferCache, SoundManager

LOGGER_DIR = "logs"
LOGGER_FMT = "%Y/%m/%d %H:%M:%S"


def init():
    if not os.path.isdir(LOGGER_DIR):
        os.mkdir(LOGGER_DIR)
    # Make valid filename stem
    PARTIAL_FILE_STEM = time.strftime(LOGGER_FMT).replace("/", "-").replace(":", "-")
    logging.basicConfig(
        filename=f"{LOGGER_DIR}/{PARTIAL_FILE_STEM}.log",
        encoding="utf-8",
        format="%(asctime)s %(levelname)s: %(module)s %(message)s",
        datefmt=LOGGER_FMT,
        level=logging.DEBUG,
    )

    pygame.init()
    w = pygame.display.set_mode((720, 480))
    pygame.display.set_caption("Testing Stuff")

    with synthizer.initialized():
        main()

    shutdown()


def shutdown():
    pygame.quit()


def main():
    c = pygame.time.Clock()
    fm = FileManager()
    synthizer_context = synthizer.Context(enable_events=True)
    s = SoundManager(synthizer_context, BufferCache(fm))
    ctx = Context(fm, s)
    ctx.load_resources()
    sm = ScreenManager(ctx)
    sm.add_screen(MainMenu())
    while sm.has_screens():
        delta = c.tick(60) / 1000
        sm.update(delta)
        s.update()

    ctx.export_resources()
    ctx.free_resources()


if __name__ == "__main__":
    init()
