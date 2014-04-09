from hsgame.cards.battlecries import draw_card, silence
from hsgame.game_objects import Minion, MinionCard
from hsgame.constants import CARD_STATUS, CHARACTER_CLASS, MINION_TYPES
__author__ = 'Daniel'


class BloodfenRaptor(MinionCard):
    def __init__(self):
        super().__init__("Bloodfen Raptor", 2, CHARACTER_CLASS.ALL, CARD_STATUS.BASIC)

    def create_minion(self):
        return Minion(3, 2, MINION_TYPES.BEAST)


class NoviceEngineer(MinionCard):
    def __init__(self):
        super().__init__("Novice Engineer", 2, CHARACTER_CLASS.ALL, CARD_STATUS.BASIC)

    def create_minion(self):
        minion = Minion(1, 1, MINION_TYPES.NONE)
        minion.bind('added_to_board', draw_card())
        return minion

class StonetuskBoar(MinionCard):
    def __init__(self):
        super().__init__("Stonetusk Boar", 1, CHARACTER_CLASS.ALL, CARD_STATUS.BASIC)

    def create_minion(self):
        minion = Minion(1, 1, MINION_TYPES.BEAST)
        minion.charge = True
        return minion

class IronbeakOwl(MinionCard):
    def __init__(self):
        super().__init__("Ironbeak Owl", 2, CHARACTER_CLASS.ALL, CARD_STATUS.EXPERT)

    def create_minion(self):
        minion = Minion(2, 1, MINION_TYPES.BEAST)
        minion.bind('added_to_board', silence)
        return minion