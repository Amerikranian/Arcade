"""Holds all generic menus
Any game-specific menus should be made in the respective game
This file should be updated with menus that either don't rely on any game or do not care what game is passed to them"""
import games
from menu import Menu

# Optionally added at the end of statistics prompt
STAT_INTRO = "statistics"


class MainMenu(Menu):
    def on_create(self):
        self.add_item(
            "Play games", lambda x: x.screen_manager.add_screen(GameListMenu())
        )
        self.add_item_without_callback("Quit")
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
        self.add_item_without_callback("Go back")
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
        self.add_item_without_callback("Go back")
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
        self.add_item_without_callback("Go back")
        self.set_intro_message(
            "%s instructions menu"
            % self.context.gdm.fetch_game_display_name(self.game_name)
        )


class GameVariationMenu(Menu):
    def __init__(self, game_name):
        super().__init__()
        self.game_name = game_name

    def on_create(self):
        variations = list(
            self.context.player.fetch_unlocked_game_variations(self.game_name)
        )
        for v in variations:
            self.add_item(
                v,
                lambda x: self.screen_manager.add_screen(
                    GameDifficultyMenu(self.game_name, v)
                ),
                True,
            )

        self.add_item_without_callback("Go back")
        self.set_intro_message(
            "%s variation menu"
            % self.context.gdm.fetch_game_display_name(self.game_name)
        )


class GameDifficultyMenu(Menu):
    def __init__(self, game_name, variation):
        super().__init__()
        self.game_name = game_name
        self.variation = variation

    def on_create(self):
        diffs = self.context.player.fetch_unlocked_game_variation_difficulties(
            self.game_name, self.variation
        )
        for d in diffs:
            self.add_item(
                self.context.gdm.fetch_game_difficulty_label(self.game_name, d),
                lambda x: x.screen_manager.add_screen(
                    getattr(games, self.game_name)(self.variation, d)
                ),
                True,
            )

        self.add_item_without_callback("Go back")
        self.set_intro_message("%s difficulty menu" % self.game_name)


class StatisticsMenu(Menu):
    def __init__(self, stat_items, s_intro="", include_statistics=True):
        super().__init__()
        self.stat_items = stat_items
        self.s_intro = s_intro
        self.inc_stats = include_statistics

    def on_create(self):
        for k, v in self.stat_items.items():
            self.add_item(k, v)
        if len(self.items) == 0:
            self.exit()
            return

        self.add_item_without_callback("Go back")
        self.set_intro_message(
            self.s_intro
            if not self.inc_stats or not self.s_intro
            else self.s_intro + STAT_INTRO
        )


class QuitMenu(Menu):
    """The classic "Are you sure" prompt.
    We assume that the next state in the stack, I.e, stack[-2], can send notifications.
    We inject `quit_flag` into the notification, but only if the user affirms that they would like to quit, otherwise we just pop.
    """

    def __init__(self, evt_type):
        super().__init__()
        self.evt_type = evt_type

    def on_create(self):
        self.add_item(
            "Yes",
            lambda x: x.screen_manager.fetch_screen_from_top(2).send_notification(
                self.evt_type, quit_flag=True
            ),
            True,
        )
        self.add_item_without_callback("No")
        self.set_intro_message("Are you sure you would like to quit?")
