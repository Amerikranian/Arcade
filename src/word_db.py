import sqlite3


class WordDB:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def load(self, db_path):
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.close()
        self.connection = None
        self.cursor = None

    def word_in_db(self, word):
        return (
            self.cursor.execute(
                """SELECT EXISTS(SELECT 1 FROM words WHERE name=(? ))""",
                (word.lower(),),
            ).fetchone()[0]
            == 1
        )

    def fetch_random_words(self, lower_bound, upper_bound, limit, is_unique=False):
        """Fetches the desired amount of words without repetition, with the given bounds, and the desired unique constraint.
        I.e, if unique is `True`, the words will not contain repeating letters"""
        # sqlite wants integers instead of booleans. We're happy to oblige
        unique = int(is_unique)
        # sqlite returns a list of tuples
        # This is true even if we sample one value from the rows
        # So we unpack each tuple as it comes in
        return [
            n[0]
            for n in self.cursor.execute(
                """SELECT name from words WHERE length BETWEEN (?) AND (?) AND is_unique = (?) ORDER BY RANDOM() LIMIT (?)""",
                (lower_bound, upper_bound, unique, limit),
            )
        ]

    def fetch_random_word(self, lower_bound, upper_bound, is_unique=False):
        return self.fetch_random_words(lower_bound, upper_bound, 1, is_unique)[0]
