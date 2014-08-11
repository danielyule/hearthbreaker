import hearthbreaker.cards
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.effects import GrowOnSpell, ManaFilter, GrowIfSecret, AddCardOnSpell
from hearthbreaker.game_objects import MinionCard, Minion, SecretCard


class ManaWyrm(MinionCard):
    def __init__(self):
        super().__init__("Mana Wyrm", 1, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(1, 3, effects=[GrowOnSpell(1, 0)])


class SorcerersApprentice(MinionCard):
    def __init__(self):
        super().__init__("Sorcerer's Apprentice", 2, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(3, 2, effects=[ManaFilter(1, "spell")])


class KirinTorMage(MinionCard):
    def __init__(self):
        super().__init__("Kirin Tor Mage", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE)

    def create_minion(self, player):
        def first_secret_cost_zero(m):
            class Filter:
                def __init__(self):
                    # To make sure that no matter what the cost of a secret, it will be 0
                    self.amount = 100
                    self.filter = lambda c: type(c) in SecretCard.__subclasses__()
                    self.min = 0

            def card_used(card):
                if type(card) in SecretCard.__subclasses__():
                    player.unbind("card_used", card_used)
                    player.unbind("turn_ended", turn_ended)
                    player.mana_filters.remove(mana_filter)

            def turn_ended():
                player.unbind("card_used", card_used)
                player.mana_filters.remove(mana_filter)

            mana_filter = Filter()
            player.bind("card_used", card_used)
            player.bind_once("turn_ended", turn_ended)
            player.mana_filters.append(mana_filter)

        return Minion(4, 3, battlecry=first_secret_cost_zero)


class EtherealArcanist(MinionCard):
    def __init__(self):
        super().__init__("Ethereal Arcanist", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(3, 3, effects=[GrowIfSecret(2, 2)])


class WaterElemental(MinionCard):
    def __init__(self):
        super().__init__("Water Elemental", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def did_damage(amount, target):
            target.freeze()

        minion = Minion(3, 6)
        minion.bind("did_damage", did_damage)
        return minion


class ArchmageAntonidas(MinionCard):
    def __init__(self):
        super().__init__("Archmage Antonidas", 7, CHARACTER_CLASS.MAGE, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(5, 7, effects=[AddCardOnSpell(hearthbreaker.cards.Fireball)])
