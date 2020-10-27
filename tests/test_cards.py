import unittest

import eval7
import itertools as it


class TestCards(unittest.TestCase):
    def test_all_boards(self):
        cases = (
            (("Ac", "Ah"), ("7d", "2c"), [], 1712304),
            (("Ac", "Ah"), ("7d", "2c"), ("7h", "5h", "2d"), 990)
        )
        for hand1, hand2, board_strs, expected_len in cases:
            hand1 = tuple(map(eval7.Card, hand1))

            hand2 = tuple(map(eval7.Card, hand2))
            board = tuple(map(eval7.Card, board_strs))

            res = list(eval7.cards.all_boards(list(it.chain(hand1, hand2)), board))
            self.assertEqual(len(res), expected_len)
