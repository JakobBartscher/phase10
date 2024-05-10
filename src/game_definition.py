from dataclasses import dataclass, field
from src.enums import Color, PhasesEnum
import random
from itertools import combinations
import logging

logging.basicConfig(level=logging.DEBUG)

@dataclass
class NumberCard:
    """Defines a card with a number and a color"""
    color: Color
    _number: int = field(repr=False)

    def __str__(self):
        return f"{self.color.name} {self.number}"

    def __repr__(self):
        return f"{self.color.name} {self.number}"

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, value):
        if not 1 <= value <= 12:
            raise ValueError("Number must be between 1 and 12")
        self._number = value

@dataclass
class JokerCard:
    """A Joker is a card with either 2 or 4 colors and either numbers 1-6 or 7-12"""
    _colors: list[Color] = field(repr=False)
    _numbers: list[int] = field(repr=False)

    def __str__(self):
        colors = '/'.join([str(color.name) for color in self.colors])
        numbers = f"{self.numbers[0]}-{self.numbers[-1]}"
        return f"Joker {colors} {numbers}"

    def __repr__(self):
        colors = '/'.join([str(color.name) for color in self.colors])
        numbers = f"{self.numbers[0]}-{self.numbers[-1]}"
        return f"Joker {colors} {numbers}"

    @property
    def colors(self):
        return self._colors

    @colors.setter
    def colors(self, value):
        if len(value) not in [2, 4]:
            raise ValueError("Joker must have 2 or 4 colors")
        self._colors = value

    @property
    def numbers(self):
        return self._numbers

    @numbers.setter
    def numbers(self, value):
        if value not in [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]]:
            raise ValueError("Joker must have numbers 1-6 or 7-12")
        self._numbers = value

@dataclass
class Deck:
    cards: list = field(default_factory=list)

    def __str__(self):
        return f"{[str(card) for card in self.cards]}"

    def __len__(self):
        return len(self.cards)

    def shuffle_deck(self):
        return random.shuffle(self.cards)

    def sort_deck(self):
        return self.cards.sort()

    def get_numbers(self) -> list[int]:
        """List of numbers of the cards in the deck. If the card is a Joker, it returns the list of numbers."""
        out = []
        for card in self.cards:
            if isinstance(card, NumberCard):
                out.append(card.number)
            else:
                out.append(card.numbers)
        return out

    def get_colors(self) -> list[Color]:
        """List of colors of the cards in the deck. If the card is a Joker, it returns the list of colors."""
        out = []
        for card in self.cards:
            if isinstance(card, NumberCard):
                out.append(card.color)
            else:
                out.append(card.colors)
        return out

    def get_card(self, card_idx: int):
        return self.cards[card_idx]

    def remove_card(self, card_idx: int) -> None:
        """Same as draw_card but does not return the card."""
        self.draw_card(card_idx)

    def draw_card(self, card_idx: int = 0) -> NumberCard or JokerCard or None:
        # remove the card by index from the list and return it
        if len(self.cards) == 0:
            logging.debug("Deck is empty")
            return None
        else:
            return self.cards.pop(card_idx)

    def add_card(self, card):
        # add a card to the start of the list
        return self.cards.insert(0, card)


@dataclass
class CardDeck(Deck):
    """
    Defines a deck of cards with number cards and joker cards.

    Also has a discard pile and draw pile.
    """
    def __post_init__(self):
        self.create_deck()
        self.shuffle_deck()

    def __str__(self):
        return f"Draw pile with {len(self.cards)} cards: {self.cards}"

    def __len__(self):
        return len(self.cards)

    def create_deck(self):
        # number cards
        for _ in range(2):
            for color in Color:
                for number in range(1, 13):
                    self.add_card(NumberCard(color, number))
        # 2 color joker cards
        for colors in combinations(Color, 2):
            for numbers in [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]]:
                self.add_card(JokerCard(colors, numbers))
        # 4 color joker cards
        for numbers in [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]]:
            self.add_card(JokerCard(list(Color), numbers))


@dataclass
class DiscardPile(Deck):
    def __str__(self):
        return f"Discard pile with {len(self.cards)} cards: {self.cards}"

    def __len__(self):
        return len(self.cards)


@dataclass
class Player:
    name: str
    hand_cards: Deck = field(default_factory=Deck)
    current_phase: PhasesEnum = PhasesEnum.DOUBLETS_4

    def __str__(self):
        return f"{self.name} in phase {self.current_phase.name} with cards: {self.hand_cards}"

    def draw_card(self, deck: CardDeck):
        self.hand_cards.add_card(deck.draw_card())

    def discard_card(self, card_idx: int, discard_pile: DiscardPile):
        """Discard a card from the player's hand to the discard pile."""
        card = self.hand_cards.get_card(card_idx)
        discard_pile.add_card(card)
        return self.hand_cards.remove_card(card_idx)

    def move_to_next_phase(self):
        self.current_phase = PhasesEnum(self.current_phase.value + 1)



