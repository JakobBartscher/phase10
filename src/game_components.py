from dataclasses import dataclass, field
from src.enums import Color, PhasesEnum
import random
from itertools import combinations
import logging
from functools import cached_property
from functools import total_ordering

@total_ordering
class Card:
    def __lt__(self, other):
        if isinstance(self, NumberCard) and isinstance(other, JokerCard):
            return True
        elif isinstance(self, JokerCard) and isinstance(other, NumberCard):
            return False
        elif isinstance(self, NumberCard) and isinstance(other, NumberCard):
            if self.color != other.color:
                return self.color.value < other.color.value
            else:
                return self.number < other.number
        else:  # both are JokerCards
            if self.colors[0] != other.colors[0]:
                return self.colors[0].value < other.colors[0].value
            else:
                return self.numbers[0] < other.numbers[0]

    def __eq__(self, other):
        return not self < other and not other < self

logging.basicConfig(level=logging.DEBUG)

@dataclass
class NumberCard(Card):
    """Defines a card with a number and a color"""
    idx: int
    color: Color
    _number: int = field(repr=False)

    def __str__(self):
        return f"{self.color.name} {self.number}"

    def __repr__(self):
        return f"{self.color.name} {self.number}"

    def __hash__(self):
        return hash(f"i{self.idx} {self.color.name} {self.number}")

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, value):
        if not 1 <= value <= 12:
            raise ValueError("Number must be between 1 and 12")
        self._number = value

@dataclass
class JokerCard(Card):
    """A Joker is a card with either 2 or 4 colors and either numbers 1-6 or 7-12"""
    idx: int
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

    def __hash__(self):
        return hash(self.__repr__())

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
    cards: list[Card] = field(default_factory=list)
    _size: int = 0
    _is_sorted: bool = False

    def __str__(self):
        return f"{[str(card) for card in self.cards]}"

    def __len__(self):
        return len(self.cards)

    def __hash__(self):
        return hash([f"{i}{card.__repr__()}" for i, card in enumerate(self.cards)])

    def __iter__(self):
        return iter(self.cards)

    def shuffle_deck(self) -> None:
        random.shuffle(self.cards)
        self.reindex_cards()

    def sort_deck(self) -> None:
        if not self._is_sorted:
            self.cards.sort()
            self._is_sorted = True
            self.reindex_cards()

    def reindex_cards(self):
        for i, card in enumerate(self.cards):
            card.idx = i

    def sorted_number_cards(self) -> list[NumberCard]:
        return sorted(self.number_cards, key=lambda x: x.number)

    # @cached_property
    @property
    def get_numbers(self) -> list[int]:
        """List of numbers of the cards in the deck. If the card is a Joker, it returns the list of numbers."""
        out = []
        for card in self.cards:
            if isinstance(card, NumberCard):
                out.append(card.number)
            else:
                out.append(card.numbers)
        return out

    # @cached_property
    @property
    def get_colors(self) -> list[Color]:
        """List of colors of the cards in the deck. If the card is a Joker, it returns the list of colors."""
        out = []
        for card in self.cards:
            if isinstance(card, NumberCard):
                out.append(card.color)
            else:
                out.append(card.colors)
        return out

    def get_card(self, card_idx: int = 0):
        if len(self.cards) == 0:
            logging.debug("Deck is empty")
            return None
        else:
            return self.cards[card_idx]

    # @cached_property
    @property
    def jokers(self):
        return [card for card in self.cards if isinstance(card, JokerCard)]

    # @cached_property
    @property
    def number_cards(self):
        return [card for card in self.cards if isinstance(card, NumberCard)]

    def remove_card(self, card_idx: int) -> None:
        """Same as draw_card but does not return the card."""
        self.draw_card(card_idx)
        self._size -= 1

    def draw_card(self, card_idx: int = 0) -> NumberCard or JokerCard or None:
        # remove the card by index from the list and return it
        if len(self.cards) == 0:
            logging.debug("Deck is empty")
            return None
        else:
            self._size -= 1
            return self.cards.pop(card_idx)

    def add_card(self, card):
        # add a card to the start of the list
        self._is_sorted = False
        self._size += 1
        return self.cards.insert(0, card)

    def card_value_counts(self, percentage=False) -> dict:
        """Return a dictionary with the card values as keys and the counts as values."""
        value_counts = {}
        for card in self.cards:
            value_counts[card] = value_counts.get(card, 0) + 1

        if percentage:
            total = len(self.cards)
            for key in value_counts:
                value_counts[key] /= total
        return value_counts

    def number_value_counts(self, include_jokers=True, percentage=False) -> dict:
        """
        Return a dictionary with the numbers as keys and the counts as values.
        Jokers are counted for all their numbers.
        """
        value_counts = {}
        for card in self.cards:
            if isinstance(card, NumberCard):
                value_counts[card.number] = value_counts.get(card.number, 0) + 1
            elif isinstance(card, JokerCard):
                if include_jokers:
                    # add all numbers of the joker card
                    for number in card.numbers:
                        value_counts[number] = value_counts.get(number, 0) + 1
            else:
                raise ValueError("Card must be either a NumberCard or JokerCard")

        if percentage:
            total = len(self.cards)
            for key in value_counts:
                value_counts[key] /= total
        return value_counts

    def color_value_counts(self, include_jokers=True, percentage=False) -> dict:
        """
        Return a dictionary with the colors as keys and the counts as values.
        Jokers are counted for all their colors.
        """
        value_counts = {}
        for card in self.cards:
            if isinstance(card, NumberCard):
                value_counts[card.color] = value_counts.get(card.color, 0) + 1
            elif isinstance(card, JokerCard):
                if include_jokers:
                    # add all colors of the joker card
                    for color in card.colors:
                        value_counts[color] = value_counts.get(color, 0) + 1
            else:
                raise ValueError("Card must be either a NumberCard or JokerCard")

        if percentage:
            total = len(self.cards)
            for key in value_counts:
                value_counts[key] /= total
        return value_counts

    def merge_decks(self, other_deck, copy_deck=False):
        """Merge the deck with another deck."""
        if copy_deck:
            other_deck = other_deck.copy()
            new_deck = self.copy()
            new_deck.cards.extend(other_deck.cards)
            new_deck._size += other_deck._size
            new_deck._is_sorted = False
            return new_deck
        else:
            self.cards.extend(other_deck.cards)
            self._is_sorted = False
            self._size += other_deck._size
            other_deck.cards = []
            return self

    def copy(self):
        return Deck(self.cards.copy())


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
                    self.add_card(NumberCard(self._size, color, number))
        # 2 color joker cards
        for colors in combinations(Color, 2):
            for numbers in [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]]:
                self.add_card(JokerCard(self._size, colors, numbers))
        # 4 color joker cards
        for numbers in [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]]:
            self.add_card(JokerCard(self._size, list(Color), numbers))


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
    finished_all_phases: bool = False

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
        if not self.current_phase.value == 10:
            self.current_phase = PhasesEnum(self.current_phase.value + 1)
        else:
            self.finished_all_phases = True



