import random
from enum import Enum

# Enum for card colors
class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3
    YELLOW = 4

# Enum for card types
class Type(Enum):
    NUMBER = 1
    REVERSE = 2
    SKIP = 3
    DRAW_TWO = 4
    WILD = 5
    WILD_DRAW_FOUR = 6

# Card class
class Card:
    def __init__(self, color, type, number=None):
        self.color = color
        self.type = type
        self.number = number

    def __str__(self):
        if self.type == Type.NUMBER:
            return f"{Color(self.color).name} {self.number}"
        else:
            return f"{'WILD' if self.color is None else Color(self.color).name} {Type(self.type).name}"

    def __eq__(self, other):
        return (self.color, self.type, self.number) == (other.color, other.type, other.number)

# Deck class
class Deck:
    def __init__(self):
        self.cards = []
        self.build()

    def build(self):
        for color in [Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW]:
            for i in range(10):  # Number cards from 0 to 9
                self.cards.append(Card(color, Type.NUMBER, i))
                if i != 0:  # Add duplicate 1-9 cards
                    self.cards.append(Card(color, Type.NUMBER, i))
            for _ in range(2):  # Add two of each special card per color
                self.cards.append(Card(color, Type.REVERSE))
                self.cards.append(Card(color, Type.SKIP))
                self.cards.append(Card(color, Type.DRAW_TWO))
        for _ in range(4):  # Add four of each wild card
            self.cards.append(Card(None, Type.WILD))
            self.cards.append(Card(None, Type.WILD_DRAW_FOUR))
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop()

# Player class
class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def draw(self, deck):
        self.hand.append(deck.draw())

    def play(self, card):
        self.hand.remove(card)

# Game class
class Game:
    def __init__(self):
        self.deck = Deck()
        self.players = [Player("Player 1"), Player("Player 2"), Player("Player 3")]
        self.current_player = 0
        self.direction = 1
        self.discard_pile = []
        self.current_color = None  # Keep track of the current color after a Wild/Wild Draw Four card

    def start_game(self):
        # Deal 7 cards to each player
        for player in self.players:
            for _ in range(7):
                player.draw(self.deck)
        
        # Start the discard pile with a non-wild card
        while True:
            first_card = self.deck.draw()
            if first_card.type not in [Type.WILD, Type.WILD_DRAW_FOUR]:
                self.discard_pile.append(first_card)
                self.current_color = first_card.color  # Set the initial color
                break

    def next_turn(self):
        self.current_player = (self.current_player + self.direction) % len(self.players)

    def check_win(self):
        for player in self.players:
            if len(player.hand) == 0:
                return True
        return False

    def play_card(self, player, card):
        # Handle special cards
        if card.type == Type.REVERSE:
            self.direction *= -1
        elif card.type == Type.SKIP:
            self.next_turn()  # Skip the next player
        elif card.type == Type.DRAW_TWO:
            next_player = (self.current_player + self.direction) % len(self.players)
            self.players[next_player].draw(self.deck)
            self.players[next_player].draw(self.deck)
        elif card.type == Type.WILD or card.type == Type.WILD_DRAW_FOUR:
            # Ask player to choose the new color
            self.choose_new_color(player)

            if card.type == Type.WILD_DRAW_FOUR:
                next_player = (self.current_player + self.direction) % len(self.players)
                for _ in range(4):
                    self.players[next_player].draw(self.deck)
        else:
            self.current_color = card.color  # Set the current color to the played card's color
        
        self.discard_pile.append(card)
        player.play(card)

    def choose_new_color(self, player):
        while True:
            new_color = input(f"{player.name}, choose a new color (RED, GREEN, BLUE, YELLOW): ").strip().upper()
            if new_color in Color.__members__:
                self.current_color = Color[new_color]
                break
            else:
                print("Invalid color choice. Try again.")

    def is_playable(self, card, top_discard):
        # A card is playable if it matches the color, the type, or is a wild card
        if card.type in [Type.WILD, Type.WILD_DRAW_FOUR]:
            return True
        return (card.color == self.current_color or 
                (top_discard.type == Type.NUMBER and card.number == top_discard.number) or
                card.type == top_discard.type)

# Main class
class UnoGame:
    def __init__(self):
        self.game = Game()

    def play(self):
        self.game.start_game()
        while not self.game.check_win():
            current_player = self.game.players[self.game.current_player]
            print(f"\nCurrent player: {current_player.name}")
            print("Hand:")

            for i, card in enumerate(current_player.hand):
                print(f"{i}: {card}")

            top_discard = self.game.discard_pile[-1]
            print(f"Top of discard pile: {top_discard} (Current color: {Color(self.game.current_color).name})")

            card_to_play = input("Enter the index of the card to play or 'draw' to draw a card: ").strip()

            if card_to_play.lower() == 'draw':
                current_player.draw(self.game.deck)
            else:
                try:
                    index = int(card_to_play)
                    card = current_player.hand[index]

                    # Check if the card is in the player's hand and is playable
                    if self.game.is_playable(card, top_discard):
                        self.game.play_card(current_player, card)
                    else:
                        print("Card not playable. Try again.")
                        continue
                except (ValueError, IndexError):
                    print("Invalid input. Try again.")
                    continue

            if not self.game.check_win():
                self.game.next_turn()
        
        print(f"Winner: {self.game.players[self.game.current_player].name}")

# Create a new game
game = UnoGame()
game.play()
