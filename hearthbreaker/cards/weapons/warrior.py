from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.tags.action import Damage, IncreaseDurability
from hearthbreaker.tags.base import Deathrattle, Effect
from hearthbreaker.tags.condition import IsMinion
from hearthbreaker.tags.event import Attack
from hearthbreaker.tags.selector import MinionSelector, BothPlayer, HeroSelector
from hearthbreaker.game_objects import WeaponCard, Weapon


class FieryWarAxe(WeaponCard):
    def __init__(self):
        super().__init__("Fiery War Axe", 2, CHARACTER_CLASS.WARRIOR, CARD_RARITY.FREE)

    def create_weapon(self, player):
        return Weapon(3, 2)


class ArcaniteReaper(WeaponCard):
    def __init__(self):
        super().__init__("Arcanite Reaper", 5, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON)

    def create_weapon(self, player):
        return Weapon(5, 2)


class Gorehowl(WeaponCard):
    def __init__(self):
        super().__init__("Gorehowl", 7, CHARACTER_CLASS.WARRIOR, CARD_RARITY.EPIC)

    def create_weapon(self, player):
        return Weapon(7, 1, effects=[Effect(Attack(IsMinion()), IncreaseDurability(), HeroSelector())])


class DeathsBite(WeaponCard):
    def __init__(self):
        super().__init__("Death's Bite", 4, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON)

    def create_weapon(self, player):
        return Weapon(4, 2, deathrattle=Deathrattle(Damage(1), MinionSelector(players=BothPlayer())))
