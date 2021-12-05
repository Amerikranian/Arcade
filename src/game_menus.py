"""Holds all generic menus
Any game-specific menus should be made in the respective game
This file should be updated with menus that either don't rely on any game or do not care what game is passed to them"""
import games
from menu import Menu


class MainMenu(Menu):
    def on_create(self):
        self.add_item(
            "Play games", lambda x: x.screen_manager.add_screen(GameListMenu())
        )
        self.add_item("Quit", lambda x: x.exit())
        self.set_intro_message("Welcome!")


class GameListMenu(Menu):
    def on_create(self):
        # We don't override the enter transition function because it would regenerate the menu every time we returned to this state
        # Since game unlocks are planned to occur in a shop of sorts, and the games themselves have no ability to unlock games, we can generate the items once because the shop can only be accessed in the main menu
        for game in self.context.player.fetch_unlocked_games():
            # Todo: Actually add the selected game to the screen_manager instance
            self.add_item(game, lambda x: None)
        self.add_item("Go back", lambda x: x.exit())
        self.set_intro_message("What would you like to play?")
