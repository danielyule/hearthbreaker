from hearthbreaker.tags.action import Kill, Bounce, Summon, Give, Stealth, Damage
from hearthbreaker.tags.base import Effect, Deathrattle, Battlecry
from hearthbreaker.tags.condition import IsMinion
from hearthbreaker.tags.event import DidDamage
from hearthbreaker.tags.selector import TargetSelector, MinionSelector, PlayerSelector, UserPicker, \
    BothPlayer, CharacterSelector, RandomPicker
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.game_objects import MinionCard, Minion


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
        minion = Minion(2, 2)
        for combo in range(0, player.cards_played):
            minion.increase_health(2)
            minion.change_attack(2)

        return minion


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
