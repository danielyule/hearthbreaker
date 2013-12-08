from game.game_objects import Card, MinionCard, Minion
from game.constants import CARD_STATUS, CHARACTER_CLASS
cardList = {}
def createCards():
    def addCard(card):
        cardList[card.name] = card
    cardList = {}
    addCard(MinionCard("Stonetusk Boar", 1, 1, 1, CHARACTER_CLASS.ALL, CARD_STATUS.COMMON))
