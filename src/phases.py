from src.enums import Color, PhasesEnum
from abc import ABC, abstractmethod, abstractproperty
from src.game_components import Deck, NumberCard, JokerCard
from dataclasses import dataclass


class Phase(ABC):
    """Protocol of a Phase"""
    def __init__(self, deck: Deck, discard_pile: Deck):
        self.phase: PhasesEnum
        self.deck: Deck
        self.discard_pile: Deck
        self.draw_from_discard_pile: bool = False

    @abstractmethod
    def evaluate_hand(self, hand):
        ...


def get_phase(phase: PhasesEnum, deck: Deck, discard_pile: Deck) -> Phase:
    """Return the phase class based on the phase enum"""
    if phase == PhasesEnum.DOUBLETS_4:
        return Phase1Doublets4(deck=deck, discard_pile=discard_pile)
    elif phase == PhasesEnum.SAME_COLOR_6:
        return Phase2SameColor6(deck=deck)
    elif phase == PhasesEnum.SEQUENCE_4_AND_QUADRUPLET:
        return Phase3Sequence4AndQuadruplet(deck=deck)
    elif phase == PhasesEnum.SEQUENCE_8:
        return Phase4Sequence8(deck=deck)
    elif phase == PhasesEnum.SAME_COLOR_7:
        return Phase5SameColor7(deck=deck)
    elif phase == PhasesEnum.SEQUENCE_9:
        return Phase6Sequence9(deck=deck)
    elif phase == PhasesEnum.QUADRUPLETS_2:
        return Phase7Quadruplets2(deck=deck)
    elif phase == PhasesEnum.SAME_COLOR_SEQUENCE_4_AND_TRIPLET:
        return Phase8SameColorSequence4AndTriplet(deck=deck)
    elif phase == PhasesEnum.SEQUENCE_5_AND_TRIPLET:
        return Phase9Sequence5AndTriplet(deck=deck)
    elif phase == PhasesEnum.SEQUENCE_5_AND_SAME_COLOR_SEQUENCE_3:
        return Phase10Sequence5AndSameColorSequence3(deck=deck)
    else:
        raise ValueError("Phase not found")

@dataclass
class Phase1Doublets4(Phase):
    """Phase 1: 4 pairs with the same number"""
    deck: Deck
    discard_pile: Deck
    phase = PhasesEnum.DOUBLETS_4
    draw_from_discard_pile: bool = False
    player_action: str = ""

    def evaluate_hand(self, hand: Deck):
        solutions = self.check_solutions(hand)
        finished_phase = self.finished_phase(solutions)
        probs = None
        if not finished_phase:
            probs = self.calculate_card_probabilities(hand, solutions)
            # discard the card with the lowest probability of being useful in the future
            # if there are multiple cards with the same probability, discard any of them

            # index of min probability
            min_prob_index = probs.index(min(probs))
            return hand.get_card(min_prob_index), probs
        else:
            return finished_phase, probs

    def check_solutions(
            self,
            hand: Deck,
            solutions: list[dict[list]] = None) -> list[dict[list]]:
        """
        Create a solution options list for the phase.

        3 steps:
            1. Use the number cards to create pairs.
            2. Check if the discard pile card can improve the solution.
            3. Add jokers to the solutions.
        """
        solutions = [] if solutions is None else solutions
        hand.sort_deck()

        for i, card in enumerate(hand.number_cards):
            added = False
            for solution in solutions:
                if card.number in solution:
                    if len(solution[card.number]) < 2:
                        solution[card.number].append(card)
                        added = True
                        break
            if not added:
                solutions.append({card.number: [card]})

        # if there are draw options then check if any of them improve the solutions. Only one can be drawn.
        draw_option = self.discard_pile.get_card()  # top card on the discard pile
        if draw_option:
            for solution in solutions:
                key = list(solution.keys())[0]
                if len(solution[key]) < 2:
                    if isinstance(draw_option, NumberCard):
                        if key == draw_option.number:
                            solution[key].append(draw_option)
                            self.player_action = f"Draw {draw_option} from the discard pile"
                            self.draw_from_discard_pile = True
                            break
                    elif isinstance(draw_option, JokerCard):
                        if key in draw_option.numbers:
                            solution[key].append(draw_option)
                            self.player_action = f"Draw {draw_option} from the discard pile"
                            self.draw_from_discard_pile = True
                            break

        # add jokers to the solutions
        for joker in hand.jokers:
            added = False
            for solution in solutions:
                key = list(solution.keys())[0]
                if len(solution[key]) < 2:
                    if key in joker.numbers:
                        solution[key].append(joker)
                        added = True
                        break

            if not added:
                for number in joker.numbers:
                    solutions.append({number: [joker]})

        return solutions

    def calculate_card_probabilities(self, hand: Deck, solutions: list[dict[list]]):
        """
        Calculate the probability of each card to be part of the phase solution.

        All cards that are already part of a pair have a probability of 1.
        """
        # Note: This assumes perfect memory of the discard pile, since we only account for the cards that are left in
        # the deck and implicitly the first discard pile card, if useful.
        a_posteriori = self.deck.number_value_counts(percentage=True, include_jokers=True)

        # set the probability of the pairs to 1
        # all other cards get their a_posteriori probability
        def _eval_card(card):
            if isinstance(card, NumberCard):
                return a_posteriori[card.number]
            elif isinstance(card, JokerCard):
                # if the joker is not already part of the solution then all the numbers are an option
                return sum([a_posteriori[number] for number in card.numbers])
            else:
                raise ValueError("Card type not found")

        probs = [0 for _ in hand.cards]
        for solution in solutions:
            key = list(solution.keys())[0]
            if len(solution[key]) == 2:
                for cards in solution.values():
                    for card in cards:
                        probs[card.idx] = 1
            else:  # if only solution option
                for cards in solution[key]:
                    if isinstance(cards, list):
                        for card in cards:
                            probs[card.idx] = _eval_card(card)
                    else:
                        probs[cards.idx] = _eval_card(cards)
        return probs

    @staticmethod
    def finished_phase(solutions: list[dict[list]]) -> bool:
        """
        Check if the hand has 4 pairs with the same number.
        :param hand: assume that the hand is sorted
        :return:
        """
        # check if 4 pairs are found
        num_pairs = 0
        for solution in solutions:
            key = list(solution.keys())[0]
            if len(solution[key]) >= 2:
                num_pairs += 1
        return num_pairs >= 4




class Phase2SameColor6(Phase):
    """Phase 2: 6 cards of the same color"""
    deck: Deck
    phase = PhasesEnum.SAME_COLOR_6

    def evaluate_hand(self, hand: Deck):
        # check if the hand has 6 cards of the same color
        colors = hand.get_colors()
        return max(colors.values()) >= 6

    def calculate_card_probabilities(self, deck: Deck, hand: Deck):
        """
        Calculate the probability of each card to be part of the phase solution.

        All cards that are already part of the solution have a probability of 1.
        """
        pass

class Phase3Sequence4AndQuadruplet(Phase):
    """Phase 3: 1 sequence of 4 & 1 quadruplet"""
    deck: Deck
    phase = PhasesEnum.SEQUENCE_4_AND_QUADRUPLET

    def evaluate_hand(self, hand: Deck):
        # check if the hand has a sequence of 4 and a quadruplet
        numbers = hand.get_numbers()
        value_counts = {}
        for number in numbers:
            value_counts[number] = value_counts.get(number, 0) + 1
        return any(val == 4 for val in value_counts.values()) and hand.has_sequence(4)

    def calculate_card_probabilities(self, deck: Deck, hand: Deck):
        """
        Calculate the probability of each card to be part of the phase solution.

        All cards that are already part of the solution have a probability of 1.
        """
        pass

class Phase4Sequence8(Phase):
    """Phase 4: 8 cards in sequence"""
    deck: Deck
    phase = PhasesEnum.SEQUENCE_8

    def evaluate_hand(self, hand: Deck):
        # check if the hand has 8 cards in sequence
        return hand.has_sequence(8)

    def calculate_card_probabilities(self, deck: Deck, hand: Deck):
        """
        Calculate the probability of each card to be part of the phase solution.

        All cards that are already part of the solution have a probability of 1.
        """
        pass

class Phase5SameColor7(Phase):
    """Phase 5: 7 cards of the same color"""
    deck: Deck
    phase = PhasesEnum.SAME_COLOR_7

    def evaluate_hand(self, hand: Deck):
        # check if the hand has 7 cards of the same color
        colors = hand.get_colors()
        return max(colors.values()) >= 7

    def calculate_card_probabilities(self, deck: Deck, hand: Deck):
        """
        Calculate the probability of each card to be part of the phase solution.

        All cards that are already part of the solution have a probability of 1.
        """
        pass

class Phase6Sequence9(Phase):
    """Phase 6: 9 cards in sequence"""
    deck: Deck
    phase = PhasesEnum.SEQUENCE_9

    def evaluate_hand(self, hand: Deck):
        # check if the hand has 9 cards in sequence
        return hand.has_sequence(9)

    def calculate_card_probabilities(self, deck: Deck, hand: Deck):
        """
        Calculate the probability of each card to be part of the phase solution.

        All cards that are already part of the solution have a probability of 1.
        """
        pass


class Phase7Quadruplets2(Phase):
    """Phase 7: 2 quadruplets"""
    deck: Deck
    phase = PhasesEnum.QUADRUPLETS_2

    def evaluate_hand(self, hand: Deck):
        # check if the hand has 2 quadruplets
        numbers = hand.get_numbers()
        value_counts = {}
        for number in numbers:
            value_counts[number] = value_counts.get(number, 0) + 1
        return sum(val == 4 for val in value_counts.values()) >= 2

    def calculate_card_probabilities(self, deck: Deck, hand: Deck):
        """
        Calculate the probability of each card to be part of the phase solution.

        All cards that are already part of the solution have a probability of 1.
        """
        pass

class Phase8SameColorSequence4AndTriplet(Phase):
    """Phase 8: 1 sequence of 4 of the same color & 1 triplet"""
    deck: Deck
    phase = PhasesEnum.SAME_COLOR_SEQUENCE_4_AND_TRIPLET

    def evaluate_hand(self, hand: Deck):
        # check if the hand has a sequence of 4 of the same color and a triplet
        colors = hand.get_colors()
        numbers = hand.get_numbers()
        return hand.has_sequence(4) and max(colors.values()) >= 4 and any(val == 3 for val in value_counts.values())

    def calculate_card_probabilities(self, deck: Deck, hand: Deck):
        """
        Calculate the probability of each card to be part of the phase solution.

        All cards that are already part of the solution have a probability of 1.
        """
        pass

class Phase9Sequence5AndTriplet(Phase):
    """Phase 9: 1 sequence of 5 & 1 triplet"""
    deck: Deck
    phase = PhasesEnum.SEQUENCE_5_AND_TRIPLET

    def evaluate_hand(self, hand: Deck):
        # check if the hand has a sequence of 5 and a triplet
        numbers = hand.get_numbers()
        value_counts = {}
        for number in numbers:
            value_counts[number] = value_counts.get(number, 0) + 1
        return hand.has_sequence(5) and any(val == 3 for val in value_counts.values())

    def calculate_card_probabilities(self, deck: Deck, hand: Deck):
        """
        Calculate the probability of each card to be part of the phase solution.

        All cards that are already part of the solution have a probability of 1.
        """
        pass


class Phase10Sequence5AndSameColorSequence3(Phase):
    """Phase 10: 1 sequence of 5 & 1 sequence of 3 of the same color"""
    deck: Deck
    phase = PhasesEnum.SEQUENCE_5_AND_SAME_COLOR_SEQUENCE_3

    def evaluate_hand(self, hand: Deck):
        # check if the hand has a sequence of 5 and a sequence of 3 of the same color
        colors = hand.get_colors()
        numbers = hand.get_numbers()
        return hand.has_sequence(5) and hand.has_same_color_sequence(3)

    def calculate_card_probabilities(self, deck: Deck, hand: Deck):
        """
        Calculate the probability of each card to be part of the phase solution.

        All cards that are already part of the solution have a probability of 1.
        """
        pass






