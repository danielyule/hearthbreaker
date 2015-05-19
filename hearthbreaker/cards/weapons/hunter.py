from hearthbreaker.cards.base import WeaponCard
from hearthbreaker.game_objects import Weapon
from hearthbreaker.tags.action import Give, IncreaseDurability
from hearthbreaker.tags.condition import IsHero
from hearthbreaker.tags.event import AttackCompleted, SecretRevealed, CharacterAttack
from hearthbreaker.tags.selector import HeroSelector, MinionSelector, RandomPicker
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.tags.base import Effect, BuffUntil, Battlecry, ActionTag
from hearthbreaker.tags.status import ChangeAttack, Immune


class EaglehornBow(WeaponCard):
    def __init__(self):
        super().__init__("Eaglehorn Bow", 3, CHARACTER_CLASS.HUNTER,
                         CARD_RARITY.RARE)

    def create_weapon(self, player):
        return Weapon(3, 2, effects=[Effect(SecretRevealed(), ActionTag(IncreaseDurability(), HeroSelector()))])


class GladiatorsLongbow(WeaponCard):
    def __init__(self):
        super().__init__("Gladiator's Longbow", 7, CHARACTER_CLASS.HUNTER,
                         CARD_RARITY.EPIC)

    def create_weapon(self, player):
        return Weapon(5, 2, effects=[Effect(CharacterAttack(IsHero()),
                                            ActionTag(Give(BuffUntil(Immune(), AttackCompleted())), HeroSelector()))])


class Glaivezooka(WeaponCard):
    def __init__(self):
        super().__init__("Glaivezooka", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Give(ChangeAttack(1)), MinionSelector(None, picker=RandomPicker())))

    def create_weapon(self, player):
        return Weapon(2, 2)
