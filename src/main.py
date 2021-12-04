import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import cytolk.tolk as tolk
import pygame
import games
from menu import Menu
from screen_manager import ScreenManager
from game_data_manager import GameDataManager

GAME_INFO_PATH = "data/games/info.json"


def main():
    c = pygame.time.Clock()
    gdm = GameDataManager()
    gdm.load(GAME_INFO_PATH)
    print(gdm.generate_new_player_data())
    print(gdm.game_data)
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


if __name__ == "__main__":
    pygame.init()
    w = pygame.display.set_mode((720, 480))
    pygame.display.set_caption("Testing Stuff")
    tolk.load()
    main()
    pygame.quit()
