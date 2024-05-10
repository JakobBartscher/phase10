from dataclasses import dataclass, field
from src.game_definition import CardDeck, DiscardPile, Player


@dataclass
class Phase10Game:
    """
    Defines all the cards and rules of the game Phase 10.
    The game has the following cards:
        - 96 number cards (24 of each color)
        - 2 joker cards with all colors (1 with numbers 1-6 and 1 with numbers 7-12)
        - 12 Joker cards with 2 colors (6 with numbers 1-6 and 6 with numbers 7-12, 1 of each color combination)

    The game has the following phases:
        - 4 doublets (2 cards of the same number)
        - 6 cards of the same color
        - 1 sequence of 4 & 1 quadruplet (4 cards numbers in sequence, 4 cards of the same number)
        - sequence of 8 (8 cards numbers in sequence)
        - 7 cards of the same color
        - sequence of 9 (9 cards numbers in sequence)
        - 2 quadruplets (4 cards of the same number)
        - sequence of 4 of the same color & 1 triplet (4 cards of the same color in sequence, 3 cards of the same number)
        - sequence of 5 & 1 triplet (5 cards numbers in sequence, 3 cards of the same number)
        - sequence of 5 & sequence of 3 of the same color (5 cards numbers in sequence, 3 cards of the same color in sequence)

    You have 10 cards in your hand and must draw a card from the deck or the discard pile, when it is your turn.
    You must discard a card at the end of your turn. When you complete a phase you get 10 newly shuffled cards
    and must complete the next phase.

    The player who completes all the phases first wins the game.
    """
    number_of_players: int = 2
    _players: list[Player] = field(default_factory=list)
    # create the deck
    deck = CardDeck()
    discard_pile = DiscardPile()

    @property
    def players(self):
        return self._players

    @players.setter
    def players(self, value):
        self._players = value

    def __post_init__(self):
        self.create_players()

    def create_players(self):
        assert self.number_of_players in range(2, 7), "Number of players must be between 2 and 6"
        self.players = [Player(f"Player {i+1}") for i in range(self.number_of_players)]

    def set_up_game(self):
        """Set up the game by giving each player 10 cards from the deck"""
        # give each player 10 cards from the deck (1 card at a time)
        for i in range(10):
            for player in self.players:
                player.draw_card(self.deck)

    def evaluate_hand(self, player: Player):
        """Evaluate the hand of a player"""
        # check if the player has completed the current phase
        # if the player has completed the phase, move to the next phase

        # if he player has not completed the phase, calculate the optimal card to discard. This is the card that is the
        # least likely to be useful in the future. This is calculated by checking the additional cards needed to complete
        # the phase when the card is used. The card that has the highest number of additional cards needed is the optimal
        # card to discard. If there are multiple cards with the same number of additional cards needed, any of them can be
        # discarded.

        pass


if __name__ == "__main__":
    game = Phase10Game()
    game.set_up_game()
    for player in game.players:
        print(player)