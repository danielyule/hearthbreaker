from hsgame.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hsgame.game_objects import MinionCard, Minion
from hsgame.cards.battlecries import deal_one_damage_all_characters, \
    destroy_own_crystal, discard_one, discard_two, flame_imp, pit_lord
import copy


class FlameImp(MinionCard):
    def __init__(self):
        super().__init__("Flame Imp", 1, CHARACTER_CLASS.WARLOCK,
                         CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(3, 2, MINION_TYPE.DEMON, battlecry=flame_imp)


class PitLord(MinionCard):
    def __init__(self):
        super().__init__("Pit Lord", 4, CHARACTER_CLASS.WARLOCK,
                         CARD_RARITY.EPIC)

    def create_minion(self, player):
        return Minion(5, 6, MINION_TYPE.DEMON, battlecry=pit_lord)


class VoidWalker(MinionCard):
    def __init__(self):
        super().__init__("Voidwalker", 1, CHARACTER_CLASS.WARLOCK,
                         CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(1, 3, MINION_TYPE.DEMON, taunt=True)


class DreadInfernal(MinionCard):
    def __init__(self):
        super().__init__("Dread Infernal", 6, CHARACTER_CLASS.WARLOCK,
                         CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(6, 6, MINION_TYPE.DEMON,
                      battlecry=deal_one_damage_all_characters)


class Felguard(MinionCard):
    def __init__(self):
        super().__init__("Felguard", 3, CHARACTER_CLASS.WARLOCK,
                         CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(3, 5, MINION_TYPE.DEMON, battlecry=destroy_own_crystal, taunt=True)


class Doomguard(MinionCard):
    def __init__(self):
        super().__init__("Doomguard", 5, CHARACTER_CLASS.WARLOCK,
                         CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(5, 7, MINION_TYPE.DEMON, battlecry=discard_two, charge=True)


class Succubus(MinionCard):
    def __init__(self):
        super().__init__("Succubus", 2, CHARACTER_CLASS.WARLOCK, CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(4, 3, MINION_TYPE.DEMON, battlecry=discard_one)


class SummoningPortal(MinionCard):
    def __init__(self):
        super().__init__("Summoning Portal", 4, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON)

    def create_minion(self, player):
        class Filter:
            def __init__(self):
                self.amount = 2
                self.filter = lambda c: isinstance(c, MinionCard)
                self.min = 1

        mana_filter = Filter()
        minion = Minion(0, 4)
        minion.bind_once("silenced", lambda: player.mana_filters.remove(mana_filter))
        player.mana_filters.append(mana_filter)
        return minion


class BloodImp(MinionCard):
    def __init__(self):
        super().__init__("Blood Imp", 1, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def buff_ally_health():
            targets = copy.copy(player.game.current_player.minions)
            targets.remove(minion)
            if len(targets) > 0:
                target = targets[player.game.random(0, len(targets) - 1)]
                target.increase_health(1)

        minion = Minion(0, 1, MINION_TYPE.DEMON)
        minion.stealth = True
        player.bind("turn_ended", buff_ally_health)
        minion.bind_once("silenced", lambda: player.unbind("turn_ended", buff_ally_health))
        return minion
