import hearthbreaker.cards
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.effects import GrowOnSpell
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
        class Filter:
            def __init__(self):
                self.amount = 1
                self.filter = lambda c: c.is_spell()
                self.min = 0

        mana_filter = Filter()
        minion = Minion(3, 2)
        minion.bind_once("silenced", lambda: player.mana_filters.remove(mana_filter))
        player.mana_filters.append(mana_filter)
        return minion


class KirinTorMage(MinionCard):
    def __init__(self):
        super().__init__("Kirin Tor Mage", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE)

    def create_minion(self, player):
        def first_secret_cost_zero(m):
            class Filter:
                def __init__(self):
                    # To make sure that no matter what the cost of a secret, it
                    # will be 0
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
        def increase_stats():
            if len(player.secrets) > 0:
                minion.change_attack(2)
                minion.increase_health(2)

        def silence():
            player.unbind("turn_ended", increase_stats)

        minion = Minion(3, 3)
        player.bind("turn_ended", increase_stats)
        minion.bind_once("silenced", silence)
        return minion


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
        def add_fireball(c):
            if len(player.hand) < 10:
                player.hand.append(hearthbreaker.cards.Fireball())

        minion = Minion(5, 7)
        player.bind("spell_cast", add_fireball)
        minion.bind_once("silenced", lambda: player.unbind("spell_cast", add_fireball))
        return minion
