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
            # Since we are doing some black magic, we need to ensure that it will work off the bat
            if not hasattr(games, game):
                raise ValueError(
                    'The unlocked game, "%s", does not exist in games. Perhaps you forgot to import it?'
                    % game
                )
            self.add_item(
                self.context.gdm.fetch_game_display_name(game),
                lambda x: x.screen_manager.add_screen(GameSelectedMenu(game)),
            )
        self.add_item("Go back", lambda x: x.exit())
        self.set_intro_message("What would you like to play?")


class GameSelectedMenu(Menu):
    def __init__(self, game_name):
        super().__init__()
        self.game_name = game_name

    def on_create(self):
        self.add_item(
            "Play",
            lambda x: self.screen_manager.add_screen(GameVariationMenu(self.game_name)),
        )
        self.add_item(
            "Instructions",
            lambda x: x.screen_manager.add_screen(GameHelpMenu(self.game_name)),
        )
        self.add_item("Go back", lambda x: x.exit())
        self.set_intro_message(
            "%s menu" % self.context.gdm.fetch_game_display_name(self.game_name)
        )


class GameHelpMenu(Menu):
    def __init__(self, game_name):
        super().__init__()
        self.game_name = game_name

    def on_create(self):
        for i in self.context.gdm.fetch_game_doc(self.game_name).splitlines():
            self.add_item(i, lambda x: x.exit())
        self.add_item("Go back", lambda x: x.exit())
        self.set_intro_message(
            "%s instructions menu"
            % self.context.gdm.fetch_game_display_name(self.game_name)
        )


class GameVariationMenu(Menu):
    def __init__(self, game_name):
        super().__init__()
        self.game_name = game_name

    def on_create(self):
        # We only create the menu if the player has more than one variation unlocked
        variations = list(
            self.context.player.fetch_unlocked_game_variations(self.game_name)
        )
        if len(variations) > 1:
            for v in variations:
                self.add_item(
                    v,
                    lambda x: self.screen_manager.add_screen(
                        GameDifficultyMenu(self.game_name, v)
                    ),
                )
            self.add_item("Go back", lambda x: x.exit())
            self.set_intro_message(
                "%s variation menu"
                % self.context.gdm.fetch_game_display_name(self.game_name)
            )
        else:
            self.screen_manager.add_screen(
                GameDifficultyMenu(self.game_name, variations[0])
            )
            self.exit()

    def activate_item(self):
        # We override this so that we exit the menu and return the player back to the game play menu after statistics menu has been shown
        super().activate_item()
        self.exit()


class GameDifficultyMenu(Menu):
    def __init__(self, game_name, variation):
        super().__init__()
        self.game_name = game_name
        self.variation = variation

    def on_create(self):
        # Just like variations, we generate difficulty options when we actually have them
        # If we do this more we'll create a generic menu, but for now copypasting it is
        diffs = self.context.player.fetch_unlocked_game_variation_difficulties(
            self.game_name, self.variation
        )
        if len(diffs) > 1:
            for d in diffs:
                self.add_item(
                    self.context.gdm.fetch_game_difficulty_label(self.game_name, d),
                    lambda x: x.screen_manager.add_screen(
                        getattr(games, self.game_name)(self.variation, d)
                    ),
                )
            self.add_item("Go back", lambda x: x.exit())
        else:
            self.screen_manager.add_screen(
                getattr(games, self.game_name)(self.variation, diffs[0])
            )
            self.exit()

    def activate_item(self):
        super().activate_item()
        self.exit()
