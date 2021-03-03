# Copyright 2014 Anonymous7 from Reddit, Julian Andrews
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

import cython
from xorshift_rand cimport randint
from evaluate cimport cy_evaluate
from cards cimport cards_to_mask
from cards import all_boards
from evaluate import evaluate


cdef extern from "stdlib.h":
    ctypedef unsigned long size_t
    void *malloc(size_t n_bytes)
    void free(void *ptr)


cdef unsigned long long card_masks_table[52]


cdef unsigned int load_card_masks():
    for i in range(52):
        card_masks_table[i] = 1 << i
    return 0


load_card_masks()


cdef unsigned int filter_options(unsigned long long *source, 
        unsigned long long *target, 
        unsigned int num_options, 
        unsigned long long dead):
    """
    Removes all options that share a dead card
    Returns total number of options kept
    """
    cdef unsigned long long options
    cdef unsigned int total = 0
    for 0 <= s < num_options:
        option = source[s]
        if option & dead == 0:
            target[total] = option
            total += 1
    return total


cdef unsigned long long deal_card(unsigned long long dead):
    cdef unsigned int cardex
    cdef unsigned long long card
    while True:
        cardex = randint(52)
        card = card_masks_table[cardex]
        if dead & card == 0:
            return card


cdef float hand_vs_range_monte_carlo(unsigned long long hand, 
        unsigned long long *options, 
        int num_options, 
        unsigned long long start_board, 
        int num_board, 
        int iterations):
    """
    Return equity of hand vs range.
    Note that only unweighted ranges are supported.
    Note that only heads-up evaluations are supported.
    
    hand is a two-card hand mask
    options is an array of num_options options for opponent's two-card hand
    board is a hand mask of the board; num_board says how many cards are in it
    """
    cdef unsigned int count = 0
    cdef unsigned int option_index = 0
    cdef unsigned long long option
    cdef unsigned long long dealt
    cdef unsigned int hero
    cdef unsigned int villain
    cdef unsigned long long board
    for 0 <= i < iterations:
        # choose an option for opponent's hand
        option = options[option_index]
        option_index += 1
        if option_index >= num_options:
            option_index = 0
        # deal the rest of the board
        dealt = hand | option
        board = start_board
        for j in range(5 - num_board):
            board |= deal_card(board | dealt)
        hero = cy_evaluate(board | hand, 7)
        villain = cy_evaluate(board | option, 7)
        if hero > villain:
            count += 2
        elif hero == villain:
            count += 1
    return 0.5 * <double>count / <double>iterations


def py_hand_vs_range_monte_carlo(py_hand, py_villain, py_board, 
        py_iterations):
    cdef unsigned long long hand = cards_to_mask(py_hand)
    cdef int num_options = len(py_villain)
    cdef unsigned long long *options = <unsigned long long*>malloc(
            sizeof(unsigned long long) * num_options)
    cdef unsigned long long start_board = cards_to_mask(py_board)
    cdef int num_board = len(py_board)
    cdef int iterations = py_iterations
    cdef float equity  # DuplicatedSignature
    cdef unsigned long long mask
    for index, option in enumerate(py_villain):
        options[index] = cards_to_mask(option[0])
        # This strips and ignores the weight.
    num_options = filter_options(options, options, num_options, 
            start_board | hand)
    equity = hand_vs_range_monte_carlo(hand, options, num_options, 
            start_board, num_board, iterations)
    free(options)
    return equity


cdef float hand_vs_range_exact(unsigned long long hand, 
        unsigned long long *options, 
        int num_options, 
        unsigned long long complete_board):
    # I think it might be okay (good) not to randomly sample options, but
    # instead to evenly sample them. (Still with a randomly sampled board, of
    # course.) This'll make the results converge faster. We can only do this
    # because we know that every option is equally likely (unlike, for example,
    # range vs. range equity calculation).
    cdef unsigned int wins = 0
    cdef unsigned int ties = 0
    cdef unsigned long long option  # @DuplicatedSignature
    cdef unsigned int hero = cy_evaluate(complete_board | hand, 7)
    cdef unsigned int villain  # @DuplicatedSignature
    for i in range(num_options):
        # choose an option for opponent's hand
        option = options[i]
        villain = cy_evaluate(complete_board | option, 7)
        if hero > villain:
            wins += 1
        elif hero == villain:
            ties += 1
    return (wins + 0.5 * ties) / <double>num_options


def py_hand_vs_range_exact(py_hand, py_villain, py_board):
    cdef unsigned long long hand = cards_to_mask(py_hand)  # @DuplicatedSignature
    cdef int num_options = len(py_villain)  # @DuplicatedSignature
    cdef unsigned long long *options = <unsigned long long*>malloc(
            sizeof(unsigned long long) * num_options)  # @DuplicatedSignature
    cdef unsigned long long complete_board = cards_to_mask(py_board)
    cdef float equity
    cdef unsigned long long mask  # @DuplicatedSignature
    cdef unsigned long long dead = complete_board | hand  
    for index, option in enumerate(py_villain):
        options[index] = cards_to_mask(option[0])
        # This strips and ignores the weight
    num_options = filter_options(options, options, num_options, 
            complete_board | hand)
    equity = hand_vs_range_exact(hand, options, num_options, complete_board)
    free(options)
    return equity


def py_equities_2hands(hand1, hand2, start_board):
    all_cards = list(hand1) + list(hand2)
    win = 0
    tie = 0
    count = 0
    for board in all_boards(all_cards, start_board):
        h1 = evaluate(hand1+start_board+board)
        h2 = evaluate(hand2+start_board+board)
        if h1 > h2:
            win += 1
        elif h1 == h2:
            tie += 1
        count += 1
    eq1 = (win + 0.5 * tie) / count
    return eq1, 1-eq1


def py_outcome_breakdown_3hands(hand1, hand2, hand3, start_board):
    all_cards = list(hand1) + list(hand2) + list(hand3)
    case111 = 0
    case113 = 0
    case131 = 0
    case122 = 0
    case123 = 0
    case132 = 0
    case212 = 0
    case221 = 0
    case213 = 0
    case231 = 0
    case311 = 0
    case312 = 0
    case321 = 0
    count = 0
    for board in all_boards(all_cards, start_board):
        h1 = evaluate(hand1+start_board+board)
        h2 = evaluate(hand2+start_board+board)
        h3 = evaluate(hand3+start_board+board)
        if h1 > h2 and h1 > h3 and h2 > h3:
            case123 += 1
        elif h1 > h2 and h1 > h3 and h3 > h2:
            case132 += 1
        elif h2 > h1 and h2 > h3 and h1 > h3:
            case213 += 1
        elif h3 > h1 and h3 > h2 and h1 > h2:
            case231 += 1
        elif h2 > h1 and h2 > h3 and h3 > h1:
            case312 += 1
        elif h3 > h1 and h3 > h2 and h2 > h1:
            case321 += 1
        elif h1 == h2 and h1 == h3 and h3 == h2:
            case111 += 1
        elif h1 == h2 and h1 > h3 and h2 > h3:
            case113 += 1
        elif h1 > h2 and h1 > h3 and h2 == h3:
            case122 += 1
        elif h2 > h1 and h2 > h3 and h1 == h3:
            case212 += 1
        elif h3 > h1 and h3 > h2 and h1 == h2:
            case221 += 1
        elif h2 > h1 and h3 > h1 and h2 == h3:
            case311 += 1
        elif h2 > h1 and h3 > h1 and h2 == h3:
            case311 += 1
        count += 1
    result = {
        '111': case111/count,
        '113': case113/count,
        '131': case131/count,
        '122': case122/count,
        '123': case123/count,
        '132': case132/count,
        '212': case212/count,
        '221': case221/count,
        '213': case213/count,
        '231': case231/count,
        '311': case311/count,
        '312': case312/count,
        '321': case321/count,
    }
    return result


def py_equities_3hands(hand1, hand2, hand3, start_board):
    all_cards = list(hand1) + list(hand2) + list(hand3)
    win1 = 0
    win2 = 0
    win3 = 0
    tie = 0
    count = 0
    for board in all_boards(all_cards, start_board):
        h1 = evaluate(hand1+start_board+board)
        h2 = evaluate(hand2+start_board+board)
        h3 = evaluate(hand3+start_board+board)
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


def py_equities_4hands(hand1, hand2, hand3, hand4, start_board):
    all_cards = list(hand1) + list(hand2) + list(hand3) + list(hand4)
    win1 = 0
    win2 = 0
    win3 = 0
    win4 = 0
    tie = 0
    count = 0
    for board in all_boards(all_cards, start_board):
        h1 = evaluate(hand1+start_board+board)
        h2 = evaluate(hand2+start_board+board)
        h3 = evaluate(hand3+start_board+board)
        h4 = evaluate(hand4+start_board+board)
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


def py_equities_5hands(hand1, hand2, hand3, hand4, hand5, start_board):
    all_cards = list(hand1) + list(hand2) + list(hand3) + list(hand4) + list(hand5)
    win1 = 0
    win2 = 0
    win3 = 0
    win4 = 0
    win5 = 0
    tie = 0
    count = 0
    for board in all_boards(all_cards, start_board):
        h1 = evaluate(hand1+start_board+board)
        h2 = evaluate(hand2+start_board+board)
        h3 = evaluate(hand3+start_board+board)
        h4 = evaluate(hand4+start_board+board)
        h5 = evaluate(hand5+start_board+board)
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


cdef void all_hands_vs_range(unsigned long long *hands, 
        unsigned int num_hands,
        unsigned long long *all_options, 
        unsigned int num_options,
        unsigned long long board, 
        unsigned int num_board,
        long iterations, 
        float *result):
    """
    Return equity of each hand, versus range.
    Note that only unweighted ranges are supported.
    Note that only heads-up evaluations are supported.
    
    hands are two-card hand mask; num_hands is how many
    options is an array of num_options options for opponent's two-card hand
    board is a hand mask of the board; num_board says how many cards are in it
    iterations is iterations to perform
    result is a preallocated array in which to put results (order corresponds
        to order of hands)
    """
    cdef float equity  # @DuplicatedSignature
    cdef unsigned long long hand
    cdef unsigned int current_num_options
    cdef unsigned long long *options = <unsigned long long *>malloc(
            sizeof(unsigned long long) * num_options)
    for 0 <= i < num_hands:
        hand = hands[i]
        # Have to do card removal effects at this point - on a hand by hand basis.
        current_num_options = filter_options(all_options, options, 
                num_options, board | hand)
        if current_num_options == 0:
            result[i] = -1  # Villain's range makes this hand impossible for hero.
            continue
        if num_board == 5 and current_num_options <= iterations:
            equity = hand_vs_range_exact(hand, options, current_num_options, 
                    board)
        else:
            equity = hand_vs_range_monte_carlo(hand, options, 
                    current_num_options, board, num_board, iterations)
        result[i] = equity
    free(options)
        

def py_all_hands_vs_range(py_hero, py_villain, py_board, py_iterations):
    """
    Return dict mapping hero's hand to equity against villain's range on this board.
    
    hero and villain are ranges.
    board is a list of cards.
    
    TODO: consider randomising the order of opponent's hands at this point
    so that the evenly distributed sampling in hand_vs_range is unbiased.

    Board pre-filtering has been disabled. This is inefficient, and will 
    be addressed by a planned refactoring.
    """
    cdef unsigned long long *hands = <unsigned long long *>malloc(
            sizeof(unsigned long long) * len(py_hero))
    cdef unsigned int num_hands
    cdef unsigned long long *options = <unsigned long long *>malloc(
            sizeof(unsigned long long) * len(py_villain))
    cdef unsigned int num_options
    cdef unsigned long long board  # @DuplicatedSignature
    cdef unsigned int num_board
    cdef long iterations = <long>py_iterations
    cdef float *result = <float *>malloc(
            sizeof(float) * len(py_hero))
   
    num_hands = 0
    for hand, weight in py_hero:
        hands[num_hands] = cards_to_mask(hand)
        num_hands += 1
        
    num_options = 0
    for option, weight in py_villain:
        options[num_options] = cards_to_mask(option)
        num_options += 1
        
    board = cards_to_mask(py_board)
    num_board = len(py_board)

    all_hands_vs_range(hands, num_hands, options, num_options, board, 
            num_board, iterations, result)
    
    py_result = {}
    for i, (hand, weight) in enumerate(py_hero):
        if result[i] != -1:
            py_result[hand] = result[i]
    free(hands)
    free(options)
    free(result)
    
    return py_result
