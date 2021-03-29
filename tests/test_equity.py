# Copyright 2014 Anonymous7 from Reddit, Julian Andrews
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

import unittest

import eval7


def str_to_cards(hand_str):
    cards = tuple(map(eval7.Card, hand_str.split()))
    return cards

NO_BOARD = str_to_cards('')


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

    def test_outcome_breakdown_3hands(self):

        cases = (
            ("3h Ah", "Qh Jc", "Kc Js", "", [0.5038, 0.1037, 0.1822]),
            ("Ac Ah", "7d 2c", "Kd Kh", "", [0.7141, 0.1037, 0.1822]),
            ("Ac Ah", "7d 2c", "Kd Kh", "7c 5h 2h", [0.3023, 0.6102, 0.0875])
        )
        for hand1, hand2, hand3, board_strs, expected_equity in cases:
            breakdown = eval7.py_outcome_breakdown(
                str_to_cards(board_strs),
                str_to_cards(hand1),
                str_to_cards(hand2),
                str_to_cards(hand3),
            )
            total = sum(list(breakdown.values()))

            self.assertEqual(total, 1)

            eq1 = breakdown['123'] + breakdown['132'] + breakdown['122'] \
                + breakdown['111'] / 3 + (breakdown['113'] + breakdown['131']) / 2
            self.assertAlmostEqual(eq1, expected_equity[0], places=4)

    def test_outcome_breakdown_2hands(self):

        cases = (
            ("3h Ah", "Qh Jc", "", 0.5795, 0.4152, 0.0054),
            ("Ac Ah", "7d 2c", "", 0.8799, 0.1161, 0.004),
            ("Kh Js", "Kd 9h", "", 0.6961, 0.2275, 0.0764),
            ("Ac Ah", "Kd Kh", "7c 5h 2h", 0.9162, 0.0838, 0.0)
        )
        for hand1, hand2, board_strs, h1, h2, t in cases:
            breakdown = eval7.py_outcome_breakdown(
                str_to_cards(board_strs),
                str_to_cards(hand1),
                str_to_cards(hand2),
            )
            total = sum(list(breakdown.values()))

            self.assertEqual(total, 1)

            self.assertAlmostEqual(breakdown['12'], h1, places=3)
            self.assertAlmostEqual(breakdown['21'], h2, places=3)
            self.assertAlmostEqual(breakdown['11'], t, places=3)

