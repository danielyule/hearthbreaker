from game.game_objects import MinionCard, Minion
from game.constants import CARD_STATUS, CHARACTER_CLASS, MINION_TYPES
__author__ = 'Daniel'


def charge(minion, game, player):
    minion.active = True

def drawForPlayer(minion, game, player):
    game.drawForPlayer(player)

class BloodfenRaptor(Minion):
    def __init__(self):
        minion = Minion(3, 2, MINION_TYPES.BEAST)
        super().__init__("Bloodfen Raptor", 2, 0, CHARACTER_CLASS.ALL, CARD_STATUS.COMMON, minion)


class NoviceEngineer(MinionCard):
    def __init__(self):
        minion = Minion(1, 2, MINION_TYPES.NONE)
        minion.afterAddToBoard = drawForPlayer
        super().__init__("Novice Engineer", 2, 0, CHARACTER_CLASS.ALL, CARD_STATUS.COMMON, minion)

class StonetuskBoar(MinionCard):
    def __init__(self):
        minion = Minion(1, 1, MINION_TYPES.BEAST)
        minion.afterAddToBoard = charge
        super().__init__("Stonetusk Boar", 1, 0, CHARACTER_CLASS.ALL, CARD_STATUS.COMMON, minion)