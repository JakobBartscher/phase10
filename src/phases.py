from src.enums import Color, PhasesEnum
from abc import ABC, abstractmethod, abstractproperty
import abc
from game_definition import Deck, Player


class Phase(ABC):
    """Protocol of a Phase"""
    def __init__(self):
        self.phase: PhasesEnum

    @abstractmethod
    def evaluate_hand(self, hand):
        ...



class Phase1Doublets4(Phase):
    """Phase 1: 4 pairs with the same number"""
    phase = PhasesEnum.DOUBLETS_4

    def evaluate_hand(self, hand: Deck):
        # check if the hand has 4 pairs
        numbers = hand.get_numbers()

        # value counts of the numbers using a dictionary (this is faster since we need to loop through the numbers once)
        value_counts = {}
        for number in numbers:
            value_counts[number] = value_counts.get(number, 0) + 1
        return sum(val == 2 for val in value_counts.values()) >= 4




