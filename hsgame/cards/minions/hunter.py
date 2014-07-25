from hsgame.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hsgame.game_objects import MinionCard, Minion
import hsgame.targeting


class TimberWolf(MinionCard):
    def __init__(self):
        super().__init__("Timber Wolf", 1, CHARACTER_CLASS.HUNTER,
                         CARD_RARITY.FREE)

    def create_minion(self, player):

        def add_effect(m, p):
            def copy_minion(new_minion, new_owner):
                add_effect(new_minion, new_owner)
            m.add_aura(1, 0, [p], lambda mini: mini is not m and mini.minion_type is MINION_TYPE.BEAST)
            m.bind("copied", copy_minion)

        minion = Minion(1, 1, MINION_TYPE.BEAST)
        add_effect(minion, player)
        return minion


class SavannahHighmane(MinionCard):
    def __init__(self):
        super().__init__("Savannah Highmane", 6, CHARACTER_CLASS.HUNTER, CARD_RARITY.RARE)

    def create_minion(self, player):
        def summon_hyenas(m):
            class Hyena(MinionCard):
                def __init__(self):
                    super().__init__("Hyena", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.SPECIAL)

                def create_minion(self, player):
                    return Minion(2, 2, MINION_TYPE.BEAST)

            Hyena().summon(m.player, player.game, m.index)
            Hyena().summon(m.player, player.game, m.index)

        return Minion(6, 5, MINION_TYPE.BEAST, deathrattle=summon_hyenas)


class Houndmaster(MinionCard):
    def __init__(self):
        super().__init__("Houndmaster", 4, CHARACTER_CLASS.HUNTER, CARD_RARITY.FREE,
                         hsgame.targeting.find_friendly_minion_battlecry_target,
                         lambda m: m.minion_type is MINION_TYPE.BEAST)

    def create_minion(self, player):
        def buff_beast(m):
            if self.target is not None:
                self.target.increase_health(2)
                self.target.change_attack(2)
                self.target.taunt = True

        return Minion(4, 3, battlecry=buff_beast)


class KingKrush(MinionCard):
    def __init__(self):
        super().__init__("King Krush", 9, CHARACTER_CLASS.HUNTER, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        minion = Minion(8, 8, MINION_TYPE.BEAST)
        minion.charge = True
        return minion


class StarvingBuzzard(MinionCard):
    def __init__(self):
        super().__init__("Starving Buzzard", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def apply_effect(m, p):
            def check_beast_draw(new_minion):
                if new_minion.minion_type is MINION_TYPE.BEAST and new_minion is not minion:
                    p.draw()

            p.bind("minion_placed", check_beast_draw)
            m.bind_once("silenced", lambda: p.unbind("minion_placed", check_beast_draw))
            m.bind("copied", apply_effect)

        minion = Minion(2, 1, MINION_TYPE.BEAST)
        apply_effect(minion, player)
        return minion


class TundraRhino(MinionCard):
    def __init__(self):
        super().__init__("Tundra Rhino", 5, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def apply_effect(m, p):
            def check_beast_charge(played_minion):
                if played_minion.minion_type is MINION_TYPE.BEAST:
                    played_minion.charge = True
                    played_minion.exhausted = False

            p.bind("minion_played", check_beast_charge)
            m.bind_once("silenced", lambda: p.unbind("minion_played", check_beast_charge))
            m.bind("copied", apply_effect)
        minion = Minion(2, 5, MINION_TYPE.BEAST)
        apply_effect(minion, player)
        return minion


class ScavengingHyena(MinionCard):
    def __init__(self):
        super().__init__("Scavenging Hyena", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def apply_effect(m, p):
            def hyena_grow(dead_minion, by):
                if dead_minion is not minion and dead_minion.minion_type is MINION_TYPE.BEAST:
                    m.change_attack(2)
                    m.increase_health(1)

            p.bind("minion_died", hyena_grow)
            m.bind_once("silenced", lambda: p.game.unbind("minion_died", hyena_grow))
            m.bind("copied", apply_effect)

        minion = Minion(2, 2, MINION_TYPE.BEAST)
        apply_effect(minion, player)
        return minion