__author__ = 'Daniel'

from hsgame.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hsgame.game_objects import MinionCard, Minion, Card


class ManaWyrm(MinionCard):
    def __init__(self):
        super().__init__("Mana Wyrm", 1, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def increase_attack(card):
            minion.increase_attack(1)
        minion = Minion(1, 3)
        player.bind("spell_cast", increase_attack)
        minion.bind_once("silenced", lambda: player.unbind("spell_cast", increase_attack))
        return minion


class SorcerersApprentice(MinionCard):
    def __init__(self):
        super().__init__("Sorcerer's Apprentice", 2, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def reduce_mana(card):
            def increase_mana(c):
                c.mana += 1
            if type(card) in Card.__subclasses__():
                if card.mana > 0:
                    card.mana -= 1
                    minion.bind("silence", increase_mana, card)
                    minion.bind("died", lambda x, c: increase_mana(c), card)

        minion = Minion(3, 2)
        for hand_card in player.hand:
            reduce_mana(hand_card)
        player.bind("card_drawn", reduce_mana)
        minion.bind_once("silence", lambda: player.unbind("card_drawn", reduce_mana))
        minion.bind_once("died", lambda x: player.unbind("card_drawn", reduce_mana))
        return minion


class WaterElemental(MinionCard):
    def __init__(self):
        super().__init__("Water Elemental", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE)

    def create_minion(self, player):
        def did_damage(amount, target):
            target.freeze()

        minion = Minion(3, 6)
        minion.bind("did_damage", did_damage)
        return minion