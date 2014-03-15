
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
        minion = Minion(1, 2, MINION_TYPES.NONE)
        minion.bind('added_to_board', self.draw_for_player)

class StonetuskBoar(MinionCard):
    def __init__(self):
        super().__init__("Stonetusk Boar", 1, CHARACTER_CLASS.ALL, CARD_STATUS.BASIC)

    def create_minion(self):
        minion = Minion(1, 1, MINION_TYPES.BEAST)
        minion.charge = True
        return minion