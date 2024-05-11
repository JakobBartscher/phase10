from src.game_components import CardDeck, DiscardPile, Player, JokerCard, NumberCard, Deck
from src.enums import Color, PhasesEnum
from src.phases import get_phase

def card_generator_from_debug_dict(cards_dict: dict):
    color_map = {
        "RED": Color.RED,
        "GREEN": Color.GREEN,
        "YELLOW": Color.YELLOW,
        "PURPLE": Color.PURPLE
    }

    cards = []
    for i, key in enumerate(cards_dict.keys()):
        if "Joker" in key:
            colors, numbers = key.split(" ")[-2:]
            colors = [color_map[color] for color in colors.split("/")]
            s, e = numbers.split("-")
            numbers = [int(num) for num in range(int(s), int(e) + 1)]
            cards.append(JokerCard(i, colors, numbers))
        else:
            color, number = key.split(" ")[-2:]
            cards.append(NumberCard(i, color_map[color], int(number)))

    out = Deck(cards)
    out.reindex_cards()
    return out


def test_phase1_all_solved():
    cards_dict = {
        "RED 3": 1,
        "RED 9": 0.14,
        "GREEN 4": 1,
        "i1 GREEN 8": 1,
        "i2 GREEN 8": 1,
        "YELLOW 4": 1,
        "PURPLE 3": 1,
        "PURPLE 6": 1,
        "Joker RED/GREEN/YELLOW/PURPLE 1-6": 1,
        "Joker RED/YELLOW 1-6": 0
    }
    hand_cards = card_generator_from_debug_dict(cards_dict)
    discard_pile = DiscardPile()
    deck = CardDeck()


    player = Player("Player 1", hand_cards=hand_cards)
    phase_evaluator = get_phase(PhasesEnum.DOUBLETS_4, deck, discard_pile)

    result, probs = phase_evaluator.evaluate_hand(player.hand_cards)
    print(result, probs)




if __name__ == "__main__":
    test_phase1_all_solved()



