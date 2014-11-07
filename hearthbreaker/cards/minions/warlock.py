from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.tags.action import ChangeHealth, ManaChange, SummonFromHand
from hearthbreaker.tags.base import Effect, Aura, Deathrattle
from hearthbreaker.tags.condition import MinionIsType
from hearthbreaker.tags.event import TurnEnded
from hearthbreaker.tags.selector import RandomSelector, MinionSelector, MinionCardSelector, PlayerSelector
from hearthbreaker.game_objects import MinionCard, Minion, WeaponCard, Weapon
from hearthbreaker.cards.battlecries import deal_one_damage_all_characters, \
    destroy_own_crystal, discard_one, discard_two, flame_imp, pit_lord
from hearthbreaker.powers import JaraxxusPower


class FlameImp(MinionCard):
    def __init__(self):
        super().__init__("Flame Imp", 1, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON, MINION_TYPE.DEMON)

    def create_minion(self, player):
        return Minion(3, 2, battlecry=flame_imp)


class PitLord(MinionCard):
    def __init__(self):
        super().__init__("Pit Lord", 4, CHARACTER_CLASS.WARLOCK, CARD_RARITY.EPIC, MINION_TYPE.DEMON)

    def create_minion(self, player):
        return Minion(5, 6, battlecry=pit_lord)


class VoidWalker(MinionCard):
    def __init__(self):
        super().__init__("Voidwalker", 1, CHARACTER_CLASS.WARLOCK, CARD_RARITY.FREE, MINION_TYPE.DEMON)

    def create_minion(self, player):
        return Minion(1, 3, taunt=True)


class DreadInfernal(MinionCard):
    def __init__(self):
        super().__init__("Dread Infernal", 6, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON, MINION_TYPE.DEMON)

    def create_minion(self, player):
        return Minion(6, 6, battlecry=deal_one_damage_all_characters)


class Felguard(MinionCard):
    def __init__(self):
        super().__init__("Felguard", 3, CHARACTER_CLASS.WARLOCK, CARD_RARITY.RARE, MINION_TYPE.DEMON)

    def create_minion(self, player):
        return Minion(3, 5, battlecry=destroy_own_crystal, taunt=True)


class Doomguard(MinionCard):
    def __init__(self):
        super().__init__("Doomguard", 5, CHARACTER_CLASS.WARLOCK, CARD_RARITY.RARE, MINION_TYPE.DEMON)

    def create_minion(self, player):
        return Minion(5, 7, battlecry=discard_two, charge=True)


class Succubus(MinionCard):
    def __init__(self):
        super().__init__("Succubus", 2, CHARACTER_CLASS.WARLOCK, CARD_RARITY.FREE, MINION_TYPE.DEMON)

    def create_minion(self, player):
        return Minion(4, 3, battlecry=discard_one)


class SummoningPortal(MinionCard):
    def __init__(self):
        super().__init__("Summoning Portal", 4, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(0, 4, auras=[Aura(ManaChange(2, 1, MinionCardSelector()), PlayerSelector())])


class BloodImp(MinionCard):
    def __init__(self):
        super().__init__("Blood Imp", 1, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON, MINION_TYPE.DEMON)

    def create_minion(self, player):
        return Minion(0, 1, stealth=True,
                      effects=[Effect(TurnEnded(), ChangeHealth(1), RandomSelector(MinionSelector()))])


class LordJaraxxus(MinionCard):
    def __init__(self):
        super().__init__("Lord Jaraxxus", 9, CHARACTER_CLASS.WARLOCK, CARD_RARITY.LEGENDARY, MINION_TYPE.DEMON)

    def create_minion(self, player):
        def summon_jaraxxus(minion):
            class BloodFury(WeaponCard):
                def __init__(self):
                    super().__init__("Blood Fury", 3, CHARACTER_CLASS.LORD_JARAXXUS, CARD_RARITY.SPECIAL)

                def create_weapon(self, player):
                    return Weapon(3, 8)

            minion.remove_from_board()
            player.trigger("minion_played", minion)
            player.hero.health = minion.health
            player.hero.base_health = minion.base_health + minion.health_delta
            player.hero.character_class = CHARACTER_CLASS.LORD_JARAXXUS
            player.hero.power = JaraxxusPower(player.hero)
            blood_fury = BloodFury()
            weapon = blood_fury.create_weapon(player)
            weapon.card = blood_fury
            weapon.player = player
            weapon.game = player.game
            weapon.equip(player)

        return Minion(3, 15, battlecry=summon_jaraxxus)


class VoidTerror(MinionCard):
    def __init__(self):
        super().__init__("Void Terror", 3, CHARACTER_CLASS.WARLOCK, CARD_RARITY.RARE, MINION_TYPE.DEMON)

    def create_minion(self, player):
        def consume_adjacent(m):
            bonus_attack = 0
            bonus_health = 0
            if m.index > 0:
                minion = m.player.minions[m.index - 1]
                bonus_attack += minion.calculate_attack()
                bonus_health += minion.health
                minion.die(None)

            if m.index < len(m.player.minions) - 1:
                minion = m.player.minions[m.index + 1]
                bonus_attack += minion.calculate_attack()
                bonus_health += minion.health
                minion.die(None)

            m.change_attack(bonus_attack)
            m.increase_health(bonus_health)
        return Minion(3, 3, battlecry=consume_adjacent)


class Voidcaller(MinionCard):
    def __init__(self):
        super().__init__("Voidcaller", 4, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON, MINION_TYPE.DEMON)

    def create_minion(self, player):
        return Minion(3, 4, deathrattle=Deathrattle(SummonFromHand(MinionIsType(MINION_TYPE.DEMON)), PlayerSelector()))
