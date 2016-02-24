import hearthbreaker.cards
from hearthbreaker.cards.base import MinionCard
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.game_objects import Minion
from hearthbreaker.tags.action import AddCard, Give, GiveAura, Damage
from hearthbreaker.tags.base import Effect, Aura, Battlecry, AuraUntil, ActionTag
from hearthbreaker.tags.condition import HasSecret, GreaterThan, IsType, Adjacent, IsSecret, IsSpell
from hearthbreaker.tags.event import SpellCast, DidDamage, TurnEnded, CardPlayed, Drawn, CardUsed
from hearthbreaker.tags.selector import SelfSelector, PlayerSelector, TargetSelector, \
    CharacterSelector, EnemyPlayer, RandomPicker, MinionSelector, Count, BothPlayer, CardSelector
from hearthbreaker.tags.status import ChangeAttack, ChangeHealth, Frozen, NoSpellTarget, ManaChange


class ManaWyrm(MinionCard):
    def __init__(self):
        super().__init__("Mana Wyrm", 1, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(1, 3, effects=[Effect(SpellCast(), ActionTag(Give(ChangeAttack(1)), SelfSelector()))])


class SorcerersApprentice(MinionCard):
    def __init__(self):
        super().__init__("Sorcerer's Apprentice", 2, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(3, 2, auras=[Aura(ManaChange(-1), CardSelector(condition=IsSpell()))])


class KirinTorMage(MinionCard):
    def __init__(self):
        super().__init__("Kirin Tor Mage", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE,
                         battlecry=Battlecry(GiveAura([AuraUntil(ManaChange(-100), CardSelector(condition=IsSecret()),
                                                                 CardPlayed(IsSecret()))]), PlayerSelector()))

    def create_minion(self, player):
        return Minion(4, 3)


class EtherealArcanist(MinionCard):
    def __init__(self):
        super().__init__("Ethereal Arcanist", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(3, 3, effects=[Effect(TurnEnded(HasSecret()), ActionTag(Give(ChangeAttack(2)), SelfSelector())),
                                     Effect(TurnEnded(HasSecret()), ActionTag(Give(ChangeHealth(2)), SelfSelector()))])


class Sheep(MinionCard):
    def __init__(self):
        super().__init__("Sheep", 0, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False, MINION_TYPE.BEAST)

    def create_minion(self, p):
        return Minion(1, 1)


class WaterElemental(MinionCard):
    def __init__(self):
        super().__init__("Water Elemental", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(3, 6, effects=[Effect(DidDamage(), ActionTag(Give(Frozen()), TargetSelector()))])


class ArchmageAntonidas(MinionCard):
    def __init__(self):
        super().__init__("Archmage Antonidas", 7, CHARACTER_CLASS.MAGE, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(5, 7, effects=[Effect(SpellCast(), ActionTag(AddCard(hearthbreaker.cards.Fireball()),
                                                                   PlayerSelector()))])


class Snowchugger(MinionCard):
    def __init__(self):
        super().__init__("Snowchugger", 2, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(2, 3, effects=[Effect(DidDamage(), ActionTag(Give(Frozen()), TargetSelector()))])


class SpellbenderMinion(MinionCard):
    def __init__(self):
        super().__init__("Spellbender", 0, CHARACTER_CLASS.MAGE, CARD_RARITY.EPIC, False,
                         ref_name="Spellbender (minion)")

    def create_minion(self, p):
        return Minion(1, 3)


class MirrorImageMinion(MinionCard):
    def __init__(self):
        super().__init__("Mirror Image", 0, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON, False,
                         ref_name="Mirror Image (minion)")

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
        super().__init__("Soot Spewer", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(3, 3, spell_damage=1)


class WeeSpellstopper(MinionCard):
    def __init__(self):
        super().__init__("Wee Spellstopper", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.EPIC)

    def create_minion(self, player):
        return Minion(2, 5, auras=[Aura(NoSpellTarget(), MinionSelector(Adjacent()))])


class FlameLeviathan(MinionCard):
    def __init__(self):
        super().__init__("Flame Leviathan", 7, CHARACTER_CLASS.MAGE, CARD_RARITY.LEGENDARY,
                         minion_type=MINION_TYPE.MECH,
                         effects=[Effect(Drawn(), ActionTag(Damage(2), CharacterSelector(None, BothPlayer())))])

    def create_minion(self, player):
        return Minion(7, 7)


class Flamewaker(MinionCard):
    def __init__(self):
        super().__init__("Flamewaker", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(2, 4, effects=[Effect(CardUsed(IsSpell()),
                                            ActionTag(Damage(1),
                                                      CharacterSelector(None, EnemyPlayer(), RandomPicker(2))))])
