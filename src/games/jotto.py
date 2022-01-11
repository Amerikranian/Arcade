from .text_game import TextGame, TextInputObserver


class Jotto(TextGame):
    def __init__(self, variation, difficulty):
        super().__init__(variation, difficulty)
        self.add_observer(JottoObs())


class JottoObs(TextInputObserver):
    def __init__(self):
        super().__init__("^[a-z]$", True)
        self.hidden_word = ""

    def handle_start(self, game, *args, **kwargs):
        super().handle_start(game, *args, **kwargs)
        self.hidden_word = game.context.word_db.fetch_random_word(5, 5, True)

    def is_char_matching(self, char):
        return super().is_char_matching(char) and len(self.text) < len(self.hidden_word)

    def handle_text_submit(self, game, *args, **kwargs):
        res = False
        if len(self.text) < len(self.hidden_word):
            game.context.spm.output(
                "You must submit a word containing exactly five letters", True
            )
        else:
            if not game.context.word_db.word_in_db(self.text):
                game.context.spm.output("No nonsense, please", True)
            else:
                letter_cnt = len([l for l in self.text if l in self.hidden_word])
                if letter_cnt == len(self.hidden_word):
                    self.set_win_state()
                else:
                    game.context.spm.output(str(letter_cnt))

            self.clear_text()

        return res

    def gather_statistics(self):
        base_stats = super().gather_statistics()
        base_stats["Hidden word"] = self.hidden_word
        return base_stats
