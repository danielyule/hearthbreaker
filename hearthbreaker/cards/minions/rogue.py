from hearthbreaker.cards.base import MinionCard
from hearthbreaker.cards.minions.neutral import Nerubian
from hearthbreaker.cards.spells.neutral import GallywixsCoin
from hearthbreaker.game_objects import Minion
from hearthbreaker.tags.action import Kill, Bounce, Summon, Give, Damage, ChangeTarget, AddCard, IncreaseWeaponAttack
from hearthbreaker.tags.base import Effect, Deathrattle, Battlecry, Buff, ActionTag
from hearthbreaker.tags.card_source import LastCard
from hearthbreaker.tags.condition import IsMinion, IsType, NotCurrentTarget, OneIn, Not, HasCardName, \
    OpponentMinionCountIsGreaterThan, And, IsDamaged
from hearthbreaker.tags.event import DidDamage, MinionSummoned, TurnEnded, Attack, SpellCast
from hearthbreaker.tags.selector import TargetSelector, MinionSelector, PlayerSelector, UserPicker, \
    BothPlayer, CharacterSelector, RandomPicker, SelfSelector, EnemyPlayer, FriendlyPlayer, Attribute, WeaponSelector
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.tags.status import Stealth, ChangeAttack, ChangeHealth


class DefiasBandit(MinionCard):
    def __init__(self):
        super().__init__("Defias Bandit", 1, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON, False)

    def create_minion(self, player):
        return Minion(2, 1)


class DefiasRingleader(MinionCard):
    def __init__(self):
        super().__init__("Defias Ringleader", 2, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON,
                         combo=Battlecry(Summon(DefiasBandit()), PlayerSelector()))

    def create_minion(self, player):
        return Minion(2, 2)


class EdwinVanCleef(MinionCard):
    def __init__(self):
        super().__init__("Edwin VanCleef", 3, CHARACTER_CLASS.ROGUE, CARD_RARITY.LEGENDARY,
                         battlecry=Battlecry(Give([Buff(ChangeAttack(Attribute("cards_played", PlayerSelector()), 2)),
                                                   Buff(ChangeHealth(Attribute("cards_played", PlayerSelector()), 2))]),
                                             SelfSelector()))

    def create_minion(self, player):
        return Minion(2, 2)


class Kidnapper(MinionCard):
    def __init__(self):
        super().__init__("Kidnapper", 6, CHARACTER_CLASS.ROGUE, CARD_RARITY.EPIC,
                         combo=Battlecry(Bounce(), MinionSelector(picker=UserPicker(), players=BothPlayer())))

    def create_minion(self, player):
        return Minion(5, 3)


class MasterOfDisguise(MinionCard):
    def __init__(self):
        super().__init__("Master of Disguise", 4, CHARACTER_CLASS.ROGUE, CARD_RARITY.RARE,
                         battlecry=Battlecry(Give(Stealth()), MinionSelector(picker=UserPicker())))

    def create_minion(self, player):
        return Minion(4, 4)


class PatientAssassin(MinionCard):
    def __init__(self):
        super().__init__("Patient Assassin", 2, CHARACTER_CLASS.ROGUE, CARD_RARITY.EPIC)

    def create_minion(self, player):
        return Minion(1, 1, stealth=True, effects=[Effect(DidDamage(), ActionTag(Kill(), TargetSelector(IsMinion())))])


class SI7Agent(MinionCard):
    def __init__(self):
        super().__init__("SI:7 Agent", 3, CHARACTER_CLASS.ROGUE, CARD_RARITY.RARE,
                         combo=Battlecry(Damage(2), CharacterSelector(
                             players=BothPlayer(), picker=UserPicker())
                         ))

    def create_minion(self, player):
        return Minion(3, 3)


class AnubarAmbusher(MinionCard):
    def __init__(self):
        super().__init__("Anub'ar Ambusher", 4, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(5, 5, deathrattle=Deathrattle(Bounce(), MinionSelector(picker=RandomPicker())))


class OneeyedCheat(MinionCard):
    def __init__(self):
        super().__init__("One-eyed Cheat", 2, CHARACTER_CLASS.ROGUE, CARD_RARITY.RARE, minion_type=MINION_TYPE.PIRATE)

    def create_minion(self, player):
        return Minion(4, 1, effects=[Effect(MinionSummoned(IsType(MINION_TYPE.PIRATE)),
                                            ActionTag(Give(Stealth()), SelfSelector()))])


class IronSensei(MinionCard):
    def __init__(self):
        super().__init__("Iron Sensei", 3, CHARACTER_CLASS.ROGUE, CARD_RARITY.RARE, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(2, 2, effects=[Effect(TurnEnded(), ActionTag(Give([Buff(ChangeAttack(2)), Buff(ChangeHealth(2))]),
                                            MinionSelector(IsType(MINION_TYPE.MECH), picker=RandomPicker())))])


class OgreNinja(MinionCard):
    def __init__(self):
        super().__init__("Ogre Ninja", 5, CHARACTER_CLASS.ROGUE, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(6, 6, stealth=True, effects=[Effect(Attack(),
                                                          ActionTag(ChangeTarget(
                                                              CharacterSelector(NotCurrentTarget(),
                                                                                EnemyPlayer(),
                                                                                RandomPicker())),
                                                                    SelfSelector(),
                                                                    And(OneIn(2),
                                                                        OpponentMinionCountIsGreaterThan(0))))])


class TradePrinceGallywix(MinionCard):
    def __init__(self):
        super().__init__("Trade Prince Gallywix", 6, CHARACTER_CLASS.ROGUE, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(5, 8, effects=[Effect(SpellCast(Not(HasCardName("Gallywix's Coin")), EnemyPlayer()),
                                            ActionTag(AddCard(LastCard()),
                                            PlayerSelector(FriendlyPlayer()))),
                                     Effect(SpellCast(Not(HasCardName("Gallywix's Coin")), EnemyPlayer()),
                                            ActionTag(AddCard(GallywixsCoin()),
                                            PlayerSelector(EnemyPlayer())))])


class GoblinAutoBarber(MinionCard):
    def __init__(self):
        super().__init__("Goblin Auto-Barber", 2, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON,
                         minion_type=MINION_TYPE.MECH, battlecry=Battlecry(IncreaseWeaponAttack(1), WeaponSelector()))

    def create_minion(self, player):
        return Minion(3, 2)


class DarkIronSkulker(MinionCard):
    def __init__(self):
        super().__init__("Dark Iron Skulker", 5, CHARACTER_CLASS.ROGUE, CARD_RARITY.RARE,
                         battlecry=Battlecry(Damage(2), MinionSelector(condition=Not(IsDamaged()),
                                                                       players=EnemyPlayer())))

    def create_minion(self, player):
        return Minion(4, 3)


class Anubarak(MinionCard):
    def __init__(self):
        super().__init__("Anub'arak", 9, CHARACTER_CLASS.ROGUE, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(8, 4, deathrattle=[Deathrattle(Bounce(), SelfSelector()),
                                         Deathrattle(Summon(Nerubian()), PlayerSelector())])
