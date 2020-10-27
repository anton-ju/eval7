# Copyright 2014 Anonymous7 from Reddit, Julian Andrews
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

import unittest

import eval7


def str_to_cards(hand_str):
    cards = tuple(map(eval7.Card, hand_str.split()))
    return cards


def equities_2hands(hand1, hand2, start_board):
    all_cards = list(hand1) + list(hand2)
    all_boards = eval7.cards.all_boards(all_cards, start_board)
    win = 0
    tie = 0
    count = 0
    for board in all_boards:
        h1 = eval7.evaluate(hand1+start_board+board)
        h2 = eval7.evaluate(hand2+start_board+board)
        if h1 > h2:
            win += 1
        elif h1 == h2:
            tie += 1
        count += 1
    eq1 = (win + 0.5 * tie) / count
    return eq1, 1-eq1


def equities_3hands(hand1, hand2, hand3, start_board):
    all_cards = list(hand1) + list(hand2) + list(hand3)
    all_boards = eval7.cards.all_boards(all_cards, start_board)
    win1 = 0
    win2 = 0
    win3 = 0
    tie = 0
    count = 0
    for board in all_boards:
        h1 = eval7.evaluate(hand1+start_board+board)
        h2 = eval7.evaluate(hand2+start_board+board)
        h3 = eval7.evaluate(hand3+start_board+board)
        if h1 > h2 and h1 > h3:
            win1 += 1
        elif h1 == h2 and h1 == h3:
            tie += 1
        elif h2 > h1 and h2 > h3:
            win2 += 1
        else:
            win3 += 1
        count += 1
    tie = tie / 3
    eq1 = (win1 + tie) / count
    eq2 = (win2 + tie) / count
    eq3 = (win3 + tie) / count
    return eq1, eq2, eq3


def equities_4hands(hand1, hand2, hand3, hand4, start_board):
    all_cards = list(hand1) + list(hand2) + list(hand3) + list(hand4)
    all_boards = eval7.cards.all_boards(all_cards, start_board)
    win1 = 0
    win2 = 0
    win3 = 0
    win4 = 0
    tie = 0
    count = 0
    for board in all_boards:
        h1 = eval7.evaluate(hand1+start_board+board)
        h2 = eval7.evaluate(hand2+start_board+board)
        h3 = eval7.evaluate(hand3+start_board+board)
        h4 = eval7.evaluate(hand4+start_board+board)
        if h1 > h2 and h1 > h3 and h1 > h4:
            win1 += 1
        elif h1 == h2 and h1 == h3 and h1 == h4:
            tie += 1
        elif h2 > h1 and h2 > h3 and h2 > h4:
            win2 += 1
        elif h3 > h1 and h3 > h2 and h3 > h4:
            win3 += 1
        else:
            win4 += 1
        count += 1
    tie = tie / 4
    eq1 = (win1 + tie) / count
    eq2 = (win2 + tie) / count
    eq3 = (win3 + tie) / count
    eq4 = (win4 + tie) / count
    return eq1, eq2, eq3, eq4


def equities_5hands(hand1, hand2, hand3, hand4, hand5, start_board):
    all_cards = list(hand1) + list(hand2) + list(hand3) + list(hand4) + list(hand5)
    all_boards = eval7.cards.all_boards(all_cards, start_board)
    win1 = 0
    win2 = 0
    win3 = 0
    win4 = 0
    win5 = 0
    tie = 0
    count = 0
    for board in all_boards:
        h1 = eval7.evaluate(hand1+start_board+board)
        h2 = eval7.evaluate(hand2+start_board+board)
        h3 = eval7.evaluate(hand3+start_board+board)
        h4 = eval7.evaluate(hand4+start_board+board)
        h5 = eval7.evaluate(hand5+start_board+board)
        if h1 > h2 and h1 > h3 and h1 > h4 and h1 > h5:
            win1 += 1
        elif h1 == h2 and h1 == h3 and h1 == h4 and h1 == h5:
            tie += 1
        elif h2 > h1 and h2 > h3 and h2 > h4 and h2 > h5:
            win2 += 1
        elif h3 > h1 and h3 > h2 and h3 > h4 and h3 > h5:
            win3 += 1
        elif h4 > h1 and h4 > h2 and h4 > h3 and h4 > h5:
            win4 += 1
        else:
            win5 += 1
        count += 1
    tie = tie / 5
    eq1 = (win1 + tie) / count
    eq2 = (win2 + tie) / count
    eq3 = (win3 + tie) / count
    eq4 = (win4 + tie) / count
    eq5 = (win5 + tie) / count
    return eq1, eq2, eq3, eq4, eq5


class TestEquity(unittest.TestCase):
    def test_hand_vs_range_exact(self):
        cases = (
            (("Ac", "Ah"), "AA", ("Kh", "Jd", "8c", "5d", "2s"), 0.5),
            (("Ac", "Ah"), "AsAd", ("Kh", "Jd", "8c", "5d", "2s"), 0.5),
            (("As", "Ad"), "AA, A3o, 32s", ("Kh", "Jd", "8c", "5d", "2s"), 0.95),
        )
        for hand_strs, range_str, board_strs, expected_equity in cases:
            hand = tuple(map(eval7.Card, hand_strs))
            villain = eval7.HandRange(range_str)
            board = tuple(map(eval7.Card, board_strs))
            equity = eval7.py_hand_vs_range_exact(hand, villain, board)
            self.assertAlmostEqual(equity, expected_equity, places=7)

    def test_hand_vs_range_monte_carlo(self):
        hand = map(eval7.Card, ("As", "Ad"))
        villain = eval7.HandRange("AA, A3o, 32s")
        board = []
        equity = eval7.py_hand_vs_range_monte_carlo(
            hand, villain, board, 10000000
        )
        self.assertAlmostEqual(equity, 0.85337, delta=0.002)

    def test_all_hands_vs_range(self):
        hero = eval7.HandRange("AsAd, 3h2c")
        villain = eval7.HandRange("AA, A3o, 32s")
        board = []
        equity_map = eval7.py_all_hands_vs_range(hero, villain, board, 10000000)
        self.assertEqual(len(equity_map), 2)
        hand1 = tuple(map(eval7.Card, ("As", "Ad")))
        hand2 = tuple(map(eval7.Card, ("3h", "2c")))
        self.assertAlmostEqual(equity_map[hand1], 0.85337, delta=0.002)
        self.assertAlmostEqual(equity_map[hand2], 0.22865, delta=0.002)

        # Hero has an impossible hand in his range.
        hero = eval7.HandRange("JsJc,QsJs")
        villain = eval7.HandRange("JJ")
        board = tuple(map(eval7.Card, ("Kh", "Jd", "8c")))
        equity_map = eval7.py_all_hands_vs_range(hero, villain, board, 10000000)
        hand = tuple(map(eval7.Card, ("Qs", "Js")))
        self.assertAlmostEqual(equity_map[hand], 0.03687, delta=0.0002)
        self.assertEqual(len(equity_map), 1)

    def test_equities_2hands(self):
        cases = (
            ("Ac Ah", "7d 2c", "", [0.8819, 0.1181]),
            ("Ac Ah", "7d 2c", "7c 5h 2h", [0.3061, 0.6939])
        )
        for hand1, hand2, board_strs, expected_equity in cases:
            equities = eval7.equity.py_equities_2hands(
                str_to_cards(hand1),
                str_to_cards(hand2),
                str_to_cards(board_strs)
            )
            self.assertAlmostEqual(equities[0], expected_equity[0], places=4)
            self.assertAlmostEqual(equities[1], expected_equity[1], places=4)

    def test_equities_3hands(self):
        cases = (
            ("Ac Ah", "7d 2c", "Kd Kh", "", [0.7141, 0.1037, 0.1822]),
            ("Ac Ah", "7d 2c", "Kd Kh", "7c 5h 2h", [0.3023, 0.6102, 0.0875])
        )
        for hand1, hand2, hand3, board_strs, expected_equity in cases:
            equities = eval7.equity.py_equities_3hands(
                str_to_cards(hand1),
                str_to_cards(hand2),
                str_to_cards(hand3),
                str_to_cards(board_strs)
            )
            self.assertAlmostEqual(equities[0], expected_equity[0], places=4)
            self.assertAlmostEqual(equities[1], expected_equity[1], places=4)
            self.assertAlmostEqual(equities[2], expected_equity[2], places=4)

    def test_equities_4hands(self):
        cases = (
            ("Ac Ah", "7d 2c", "Kd Kh", "6h 4h", "", [0.5524, 0.0892, 0.1792, 0.1791]),
            ("Ac Ah", "7d 2c", "Kd Kh", "6h 4h", "7c 5h 2h", [0.1634, 0.3268, 0.0622, 0.4476])
        )
        for hand1, hand2, hand3, hand4, board_strs, expected_equity in cases:
            equities = eval7.equity.py_equities_4hands(
                str_to_cards(hand1),
                str_to_cards(hand2),
                str_to_cards(hand3),
                str_to_cards(hand4),
                str_to_cards(board_strs)
            )
            self.assertAlmostEqual(equities[0], expected_equity[0], places=4)
            self.assertAlmostEqual(equities[1], expected_equity[1], places=4)
            self.assertAlmostEqual(equities[2], expected_equity[2], places=4)
            self.assertAlmostEqual(equities[3], expected_equity[3], places=4)

    def test_equities_5hands(self):
        cases = (
            ("Ac Ah", "7d 2c", "Kd Kh", "6h 4h", "5s 5c","", [0.4652, 0.0817, 0.1837, 0.1334, 0.1361]),
            ("Ac Ah", "7d 2c", "Kd Kh", "6h 4h", "5s 5c", "7c 5h 2h", [0.0796, 0.0850, 0.0607, 0.4116, 0.3630])
        )
        for hand1, hand2, hand3, hand4, hand5, board_strs, expected_equity in cases:
            equities = eval7.equity.py_equities_5hands(
                str_to_cards(hand1),
                str_to_cards(hand2),
                str_to_cards(hand3),
                str_to_cards(hand4),
                str_to_cards(hand5),
                str_to_cards(board_strs)
            )
            self.assertAlmostEqual(equities[0], expected_equity[0], places=4)
            self.assertAlmostEqual(equities[1], expected_equity[1], places=4)
            self.assertAlmostEqual(equities[2], expected_equity[2], places=4)
            self.assertAlmostEqual(equities[3], expected_equity[3], places=4)
            self.assertAlmostEqual(equities[4], expected_equity[4], places=4)
