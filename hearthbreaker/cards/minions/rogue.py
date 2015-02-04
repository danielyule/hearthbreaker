from hearthbreaker.tags.action import Kill, Bounce, Summon, Give, Damage, ChangeTarget
from hearthbreaker.tags.base import Effect, Deathrattle, Battlecry, Buff
from hearthbreaker.tags.condition import IsMinion, IsType, NotCurrentTarget, OneIn
from hearthbreaker.tags.event import DidDamage, MinionSummoned, TurnEnded, Attack
from hearthbreaker.tags.selector import TargetSelector, MinionSelector, PlayerSelector, UserPicker, \
    BothPlayer, CharacterSelector, RandomPicker, SelfSelector, EnemyPlayer
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.game_objects import MinionCard, Minion
from hearthbreaker.tags.status import Stealth, ChangeAttack, ChangeHealth


class DefiasBandit(MinionCard):
    def __init__(self):
        super().__init__("Defias Bandit", 1, CHARACTER_CLASS.ROGUE, CARD_RARITY.SPECIAL)

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
        super().__init__("Edwin VanCleef", 3, CHARACTER_CLASS.ROGUE, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        if player.cards_played:
            buff_amount = player.cards_played * 2
            return Minion(2, 2, buffs=[Buff(ChangeAttack(buff_amount)), Buff(ChangeHealth(buff_amount))])
        else:
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
        return Minion(1, 1, stealth=True, effects=[Effect(DidDamage(), Kill(), TargetSelector(IsMinion()))])


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
        super().__init__("One-eyed Cheat", 2, CHARACTER_CLASS.ROGUE, CARD_RARITY.RARE, MINION_TYPE.PIRATE)

    def create_minion(self, player):
        return Minion(4, 1, effects=[Effect(MinionSummoned(IsType(MINION_TYPE.PIRATE)),
                                            Give(Stealth()), SelfSelector())])


class IronSensei(MinionCard):
    def __init__(self):
        super().__init__("Iron Sensei", 3, CHARACTER_CLASS.ROGUE, CARD_RARITY.RARE, MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(2, 2, effects=[Effect(TurnEnded(), Give([Buff(ChangeAttack(2)), Buff(ChangeHealth(2))]),
                                            MinionSelector(IsType(MINION_TYPE.MECH), picker=RandomPicker()))])


class OgreNinja(MinionCard):
    def __init__(self):
        super().__init__("Ogre Ninja", 5, CHARACTER_CLASS.ROGUE, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(6, 6, stealth=True, effects=[Effect(Attack(), ChangeTarget(CharacterSelector(NotCurrentTarget(),
                                                                                                   EnemyPlayer(),
                                                                                                   RandomPicker())),
                                                          SelfSelector(), OneIn(2))])
