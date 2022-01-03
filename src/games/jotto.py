import cytolk.tolk as tolk
from .text_game import TextGame, TextInputObserver


class Jotto(TextGame):
    def __init__(self, variation, difficulty):
        super().__init__(variation, difficulty)
        self.add_observer(JottoObs())


class JottoObs(TextInputObserver):
    def __init__(self):
        super().__init__("^[a-z]$", True)
        self.hidden_word = ""
        self.letter_cnt = 0

    def handle_start(self, game, *args, **kwargs):
        self.hidden_word = game.context.word_db.fetch_random_word(5, 5, True)

    def is_char_matching(self, char):
        return super().is_char_matching(char) and len(self.text) < len(self.hidden_word)

    def handle_text_submit(self, game, *args, **kwargs):
        res = False
        if len(self.text) < len(self.hidden_word):
            tolk.output("You must submit a word containing exactly five letters", True)
            res = True
        else:
            res = True
            if not game.context.word_db.word_in_db(self.text):
                tolk.output("No nonsense, please", True)
            else:
                self.letter_cnt = len([l for l in self.text if l in self.hidden_word])
                tolk.output(str(self.letter_cnt))

            self.clear_text()

        return res

    def has_won(self):
        return self.letter_cnt == len(self.hidden_word)

    def gather_statistics(self):
        base_stats = super().gather_statistics()
        base_stats["Hidden word"] = self.hidden_word
        return base_stats
