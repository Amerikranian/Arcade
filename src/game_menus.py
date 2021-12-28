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
                lambda x, y: x.screen_manager.add_screen(GameSelectedMenu(y)),
                game,
                should_include_self=True,
            )
        self.add_item_without_callback("Go back")
        self.set_intro_message("What would you like to play?")


class GameSelectedMenu(Menu):
    def __init__(self, game_name):
        super().__init__()
        self.game_name = game_name

    def on_create(self):
        # We inform the player what they are going to play
        # This will allow for updating game statistics and will get rid of redundant passage of game_name
        self.context.player.set_last_played_game(self.game_name)
        self.add_item(
            "Play",
            lambda x: self.screen_manager.add_screen(GameVariationMenu()),
        )
        self.add_item(
            "Instructions",
            lambda x: x.screen_manager.add_screen(GameHelpMenu()),
        )
        self.add_item_without_callback("Go back")
        self.set_intro_message(
            "%s menu" % self.context.gdm.fetch_game_display_name(self.game_name)
        )


class GameHelpMenu(Menu):
    def on_create(self):
        game_name = self.context.player.fetch_last_game_played()
        for i in self.context.gdm.fetch_game_doc(game_name).splitlines():
            self.add_item_without_callback(i)
        self.add_item_without_callback("Go back")
        self.set_intro_message("%s instructions menu" % game_name)


class GameVariationMenu(Menu):
    def on_create(self):
        game_name = self.context.player.fetch_last_game_played()
        variations = list(self.context.player.fetch_unlocked_game_variations(game_name))
        for v in variations:
            self.add_item(
                v,
                lambda x: self.screen_manager.add_screen(GameDifficultyMenu(v)),
                should_exit=True,
            )

        self.add_item_without_callback("Go back")
        self.set_intro_message("%s variation menu" % game_name)


class GameDifficultyMenu(Menu):
    def __init__(self, variation):
        super().__init__()
        self.variation = variation

    def on_create(self):
        game_name = self.context.player.fetch_last_game_played()
        diffs = self.context.player.fetch_unlocked_game_variation_difficulties(
            game_name, self.variation
        )
        for d in diffs:
            self.add_item(
                self.context.gdm.fetch_game_difficulty_label(game_name, d),
                lambda x: x.screen_manager.add_screen(
                    getattr(games, game_name)(self.variation, d)
                ),
                should_exit=True,
            )

        self.add_item_without_callback("Go back")
        self.set_intro_message("%s difficulty menu" % game_name)


class StatisticsMenu(Menu):
    def __init__(
        self, stat_items, variation, difficulty, s_intro="", include_statistics=True
    ):
        super().__init__()
        self.stat_items = stat_items
        self.variation = variation
        self.difficulty = difficulty
        self.s_intro = s_intro
        self.inc_stats = include_statistics

    def on_create(self):
        # Preliminaries
        game_name = self.context.player.fetch_last_game_played()
        game_stats = self.context.player.fetch_unlocked_game_stats(
            game_name, self.variation, self.difficulty
        )
        display_order = self.context.gdm.fetch_game_statistic_display_order(game_name)

        # Go through and try to update persistent stats
        for stat, stat_obj in game_stats.items():
            if stat in self.stat_items:
                stat_obj.update(self.stat_items[stat])

        for stat in [
            *display_order,
            *sorted(i for i in self.stat_items if i not in display_order),
        ]:
            if stat in game_stats:
                output_msg = (
                    self.context.gdm.fetch_game_statistic_display_msg(game_name, stat)
                    % game_stats[stat].eval()
                )
            else:
                output_msg = f"{stat}: {self.stat_items[stat]}"
            self.add_item_without_callback(output_msg)

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
            should_exit=True,
        )
        self.add_item_without_callback("No")
        self.set_intro_message("Are you sure you would like to quit?")
