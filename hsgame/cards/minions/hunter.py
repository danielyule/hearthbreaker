from hsgame.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hsgame.game_objects import MinionCard, Minion


class TimberWolf(MinionCard):
    def __init__(self):
        super().__init__("Timber Wolf", 1, CHARACTER_CLASS.HUNTER,
                         CARD_RARITY.FREE)

    def create_minion(self, player):

        def add_effect(m, index):
            m.add_aura(1, 0, lambda mini: mini is not minion and mini.minion_type is MINION_TYPE.BEAST)

        minion = Minion(1, 1, MINION_TYPE.BEAST)
        minion.bind("added_to_board", add_effect)
        return minion
