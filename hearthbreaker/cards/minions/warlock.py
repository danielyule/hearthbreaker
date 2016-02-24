from hearthbreaker.cards.base import MinionCard
from hearthbreaker.cards.heroes import Jaraxxus
from hearthbreaker.cards.weapons.warlock import BloodFury
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.game_objects import Minion
from hearthbreaker.tags.action import Summon, Kill, Damage, Discard, DestroyManaCrystal, Give, Equip, \
    Remove, Heal, ReplaceHeroWithMinion
from hearthbreaker.tags.base import Effect, Aura, Deathrattle, Battlecry, Buff, ActionTag
from hearthbreaker.tags.card_source import HandSource
from hearthbreaker.tags.condition import IsType, MinionCountIs, Not, OwnersTurn, IsHero, And, Adjacent, IsMinion
from hearthbreaker.tags.event import TurnEnded, CharacterDamaged, DidDamage, Damaged
from hearthbreaker.tags.selector import MinionSelector, PlayerSelector, \
    SelfSelector, BothPlayer, HeroSelector, CharacterSelector, RandomPicker, Attribute, EventValue, CardSelector, \
    FriendlyPlayer
from hearthbreaker.tags.status import ChangeHealth, ManaChange, ChangeAttack, Immune


class FlameImp(MinionCard):
    def __init__(self):
        super().__init__("Flame Imp", 1, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON, minion_type=MINION_TYPE.DEMON,
                         battlecry=Battlecry(Damage(3), HeroSelector()))

    def create_minion(self, player):
        return Minion(3, 2)


class PitLord(MinionCard):
    def __init__(self):
        super().__init__("Pit Lord", 4, CHARACTER_CLASS.WARLOCK, CARD_RARITY.EPIC, minion_type=MINION_TYPE.DEMON,
                         battlecry=Battlecry(Damage(5), HeroSelector()))

    def create_minion(self, player):
        return Minion(5, 6)


class Voidwalker(MinionCard):
    def __init__(self):
        super().__init__("Voidwalker", 1, CHARACTER_CLASS.WARLOCK, CARD_RARITY.FREE, minion_type=MINION_TYPE.DEMON)

    def create_minion(self, player):
        return Minion(1, 3, taunt=True)


class DreadInfernal(MinionCard):
    def __init__(self):
        super().__init__("Dread Infernal", 6, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON,
                         minion_type=MINION_TYPE.DEMON,
                         battlecry=Battlecry(Damage(1), CharacterSelector(players=BothPlayer())))

    def create_minion(self, player):
        return Minion(6, 6)


class Felguard(MinionCard):
    def __init__(self):
        super().__init__("Felguard", 3, CHARACTER_CLASS.WARLOCK, CARD_RARITY.RARE, minion_type=MINION_TYPE.DEMON,
                         battlecry=Battlecry(DestroyManaCrystal(), PlayerSelector()))

    def create_minion(self, player):
        return Minion(3, 5, taunt=True)


class Doomguard(MinionCard):
    def __init__(self):
        super().__init__("Doomguard", 5, CHARACTER_CLASS.WARLOCK, CARD_RARITY.RARE, minion_type=MINION_TYPE.DEMON,
                         battlecry=Battlecry(Discard(amount=2), PlayerSelector()))

    def create_minion(self, player):
        return Minion(5, 7, charge=True)


class Succubus(MinionCard):
    def __init__(self):
        super().__init__("Succubus", 2, CHARACTER_CLASS.WARLOCK, CARD_RARITY.FREE, minion_type=MINION_TYPE.DEMON,
                         battlecry=Battlecry(Discard(), PlayerSelector()))

    def create_minion(self, player):
        return Minion(4, 3)


class SummoningPortal(MinionCard):
    def __init__(self):
        super().__init__("Summoning Portal", 4, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(0, 4, auras=[Aura(ManaChange(-2, 1, minimum=1), CardSelector(condition=IsMinion()))])


class BloodImp(MinionCard):
    def __init__(self):
        super().__init__("Blood Imp", 1, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON, minion_type=MINION_TYPE.DEMON)

    def create_minion(self, player):
        return Minion(0, 1, stealth=True,
                      effects=[Effect(TurnEnded(), ActionTag(Give(ChangeHealth(1)),
                                                             MinionSelector(picker=RandomPicker())))])


class LordJaraxxus(MinionCard):
    def __init__(self):
        super().__init__("Lord Jaraxxus", 9, CHARACTER_CLASS.WARLOCK, CARD_RARITY.LEGENDARY,
                         minion_type=MINION_TYPE.DEMON,
                         battlecry=(Battlecry(ReplaceHeroWithMinion(Jaraxxus()), HeroSelector()),
                                    Battlecry(Remove(), SelfSelector()),
                                    Battlecry(Equip(BloodFury()), PlayerSelector())))

    def create_minion(self, player):
        return Minion(3, 15)


class Infernal(MinionCard):
    def __init__(self):
        super().__init__("Infernal", 6, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON, False,
                         minion_type=MINION_TYPE.DEMON)

    def create_minion(self, player):
        return Minion(6, 6)


class VoidTerror(MinionCard):
    def __init__(self):
        super().__init__("Void Terror", 3, CHARACTER_CLASS.WARLOCK, CARD_RARITY.RARE, minion_type=MINION_TYPE.DEMON,
                         battlecry=(Battlecry(
                             Give([Buff(ChangeHealth(Attribute("health", MinionSelector(Adjacent())))),
                                   Buff(ChangeAttack(Attribute("attack", MinionSelector(Adjacent()))))]),
                             SelfSelector()), Battlecry(Kill(), MinionSelector(Adjacent()))))

    def create_minion(self, player):
        return Minion(3, 3)


class Voidcaller(MinionCard):
    def __init__(self):
        super().__init__("Voidcaller", 4, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON, minion_type=MINION_TYPE.DEMON)

    def create_minion(self, player):
        return Minion(3, 4, deathrattle=Deathrattle(Summon(HandSource(FriendlyPlayer(), [IsType(MINION_TYPE.DEMON)])),
                                                    PlayerSelector()))


class AnimaGolem(MinionCard):
    def __init__(self):
        super().__init__("Anima Golem", 6, CHARACTER_CLASS.WARLOCK, CARD_RARITY.EPIC, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(9, 9, effects=[Effect(TurnEnded(MinionCountIs(1), BothPlayer()),
                                            ActionTag(Kill(), SelfSelector()))])


class Imp(MinionCard):
    def __init__(self):
        super().__init__("Imp", 1, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON, False, minion_type=MINION_TYPE.DEMON,
                         ref_name="Imp (warlock)")

    def create_minion(self, player):
        return Minion(1, 1)


class WorthlessImp(MinionCard):
    def __init__(self):
        super().__init__("Worthless Imp", 1, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON, False, MINION_TYPE.DEMON)

    def create_minion(self, p):
        return Minion(1, 1)


class FelCannon(MinionCard):
    def __init__(self):
        super().__init__("Fel Cannon", 4, CHARACTER_CLASS.WARLOCK, CARD_RARITY.RARE, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(3, 5, effects=[Effect(TurnEnded(), ActionTag(Damage(2),
                                                                   MinionSelector(Not(IsType(MINION_TYPE.MECH, True)),
                                                                                  BothPlayer(), RandomPicker())))])


class MalGanis(MinionCard):
    def __init__(self):
        super().__init__("Mal'Ganis", 9, CHARACTER_CLASS.WARLOCK, CARD_RARITY.LEGENDARY, minion_type=MINION_TYPE.DEMON)

    def create_minion(self, player):
        return Minion(9, 7, auras=[Aura(ChangeHealth(2), MinionSelector(IsType(MINION_TYPE.DEMON))),
                                   Aura(ChangeAttack(2), MinionSelector(IsType(MINION_TYPE.DEMON))),
                                   Aura(Immune(), HeroSelector())])


class FloatingWatcher(MinionCard):
    def __init__(self):
        super().__init__("Floating Watcher", 5, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON,
                         minion_type=MINION_TYPE.DEMON)

    def create_minion(self, player):
        return Minion(4, 4, effects=[Effect(CharacterDamaged(And(IsHero(), OwnersTurn())),
                                            ActionTag(Give([Buff(ChangeAttack(2)), Buff(ChangeHealth(2))]),
                                            SelfSelector()))])


class MistressOfPain(MinionCard):
    def __init__(self):
        super().__init__("Mistress of Pain", 2, CHARACTER_CLASS.WARLOCK, CARD_RARITY.RARE,
                         minion_type=MINION_TYPE.DEMON)

    def create_minion(self, player):
        return Minion(1, 4, effects=[Effect(DidDamage(), ActionTag(Heal(EventValue()), HeroSelector()))])


class ImpGangBoss(MinionCard):
    def __init__(self):
        super().__init__("Imp Gang Boss", 3, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON, minion_type=MINION_TYPE.DEMON)

    def create_minion(self, player):
        return Minion(2, 4, effects=[Effect(Damaged(), ActionTag(Summon(Imp()), PlayerSelector()))])
