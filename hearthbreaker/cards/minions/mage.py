import hearthbreaker.cards
from hearthbreaker.cards.base import MinionCard
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.game_objects import Minion
from hearthbreaker.tags.action import AddCard, Give, GiveAura, Damage
from hearthbreaker.tags.base import Effect, Aura, Battlecry, AuraUntil
from hearthbreaker.tags.condition import HasSecret, GreaterThan, IsType, Adjacent, IsSecret
from hearthbreaker.tags.event import SpellCast, DidDamage, TurnEnded, CardPlayed
from hearthbreaker.tags.selector import SecretSelector, SpellSelector, SelfSelector, PlayerSelector, TargetSelector, \
    CharacterSelector, EnemyPlayer, RandomPicker, MinionSelector, Count
from hearthbreaker.tags.status import ChangeAttack, ChangeHealth, Frozen, NoSpellTarget, ManaChange


class ManaWyrm(MinionCard):
    def __init__(self):
        super().__init__("Mana Wyrm", 1, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(1, 3, effects=[Effect(SpellCast(), ChangeAttack(1), SelfSelector())])


class SorcerersApprentice(MinionCard):
    def __init__(self):
        super().__init__("Sorcerer's Apprentice", 2, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(3, 2, auras=[Aura(ManaChange(-1), SpellSelector())])


class KirinTorMage(MinionCard):
    def __init__(self):
        super().__init__("Kirin Tor Mage", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE,
                         battlecry=Battlecry(GiveAura([AuraUntil(ManaChange(-100), SecretSelector(),
                                                                 CardPlayed(IsSecret()))]), PlayerSelector()))

    def create_minion(self, player):
        return Minion(4, 3)


class EtherealArcanist(MinionCard):
    def __init__(self):
        super().__init__("Ethereal Arcanist", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(3, 3, effects=[Effect(TurnEnded(HasSecret()), Give(ChangeAttack(2)), SelfSelector()),
                                     Effect(TurnEnded(HasSecret()), Give(ChangeHealth(2)), SelfSelector())])


class WaterElemental(MinionCard):
    def __init__(self):
        super().__init__("Water Elemental", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(3, 6, effects=[Effect(DidDamage(), Give(Frozen()), TargetSelector())])


class ArchmageAntonidas(MinionCard):
    def __init__(self):
        super().__init__("Archmage Antonidas", 7, CHARACTER_CLASS.MAGE, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(5, 7, effects=[Effect(SpellCast(), AddCard(hearthbreaker.cards.Fireball()), PlayerSelector())])


class Snowchugger(MinionCard):
    def __init__(self):
        super().__init__("Snowchugger", 2, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON, MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(2, 3, effects=[Effect(DidDamage(), Give(Frozen()), TargetSelector())])


class SpellbenderMinion(MinionCard):
    def __init__(self):
        super().__init__("Spellbender", 0, CHARACTER_CLASS.MAGE, CARD_RARITY.SPECIAL, ref_name="Spellbender (minion)")

    def create_minion(self, p):
        return Minion(1, 3)


class MirrorImageMinion(MinionCard):
    def __init__(self):
        super().__init__("Mirror Image", 0, CHARACTER_CLASS.MAGE, CARD_RARITY.SPECIAL, ref_name="Mirror Image (minion)")

    def create_minion(self, p):
        return Minion(0, 2, taunt=True)


class GoblinBlastmage(MinionCard):
    def __init__(self):
        super().__init__("Goblin Blastmage", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE,
                         battlecry=Battlecry(Damage(1), CharacterSelector(None, EnemyPlayer(), RandomPicker(4)),
                                             GreaterThan(Count(MinionSelector(IsType(MINION_TYPE.MECH))), value=0)))

    def create_minion(self, player):
        return Minion(5, 4)


class SootSpewer(MinionCard):
    def __init__(self):
        super().__init__("Soot Spewer", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE, MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(3, 3, spell_damage=1)


class WeeSpellstopper(MinionCard):
    def __init__(self):
        super().__init__("Wee Spellstopper", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.EPIC)

    def create_minion(self, player):
        return Minion(2, 5, auras=[Aura(NoSpellTarget(), MinionSelector(Adjacent()))])
