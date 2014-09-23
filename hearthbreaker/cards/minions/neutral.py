from hearthbreaker.cards.battlecries import draw_card, silence, deal_one_damage, \
    gain_one_health_for_each_card_in_hand, deal_two_damage, heal_two, \
    heal_three, give_enemy_crystal, darkscale_healer, priestess_of_elune, \
    destroy_target, two_temp_attack, nightblade, ssc, deathwing, return_to_hand, opponent_draw_two, \
    put_friendly_minion_on_board_from_enemy_deck
from hearthbreaker.effects.minion import StatsAura, IncreaseBattlecryMinionCost, DoubleDeathrattle, Buff, \
    ResurrectFriendlyMinionsAtEndOfTurn, Kill, Heal, Damage, Draw
from hearthbreaker.effects.player import PlayerManaFilter, DuplicateMinion
from hearthbreaker.game_objects import Minion, MinionCard, SecretCard, Card
from hearthbreaker.constants import CARD_RARITY, CHARACTER_CLASS, MINION_TYPE
import hearthbreaker.targeting
import copy


class BloodfenRaptor(MinionCard):
    def __init__(self):
        super().__init__("Bloodfen Raptor", 2, CHARACTER_CLASS.ALL, CARD_RARITY.FREE, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(3, 2)


class ElvenArcher(MinionCard):
    def __init__(self):
        super().__init__("Elven Archer", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         targeting_func=hearthbreaker.targeting.find_battlecry_target)

    def create_minion(self, player):
        return Minion(1, 1, battlecry=deal_one_damage)


class NoviceEngineer(MinionCard):
    def __init__(self):
        super().__init__("Novice Engineer", 2, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(1, 1, battlecry=draw_card)


class StonetuskBoar(MinionCard):
    def __init__(self):
        super().__init__("Stonetusk Boar", 1, CHARACTER_CLASS.ALL, CARD_RARITY.FREE, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(1, 1, charge=True)


class IronbeakOwl(MinionCard):
    def __init__(self):
        super().__init__("Ironbeak Owl", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, MINION_TYPE.BEAST,
                         hearthbreaker.targeting.find_minion_battlecry_target)

    def create_minion(self, player):
        return Minion(2, 1, battlecry=silence)


class WarGolem(MinionCard):
    def __init__(self):
        super().__init__("War Golem", 7, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(7, 7)


class MogushanWarden(MinionCard):
    def __init__(self):
        super().__init__("Mogu'shan Warden", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(1, 7, taunt=True)


class FaerieDragon(MinionCard):
    def __init__(self):
        super().__init__("Faerie Dragon", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, MINION_TYPE.DRAGON)

    def create_minion(self, player):
        return Minion(3, 2, spell_targetable=False)


class KoboldGeomancer(MinionCard):
    def __init__(self):
        super().__init__("Kobold Geomancer", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(2, 2, spell_damage=1)


class ArgentSquire(MinionCard):
    def __init__(self):
        super().__init__("Argent Squire", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(1, 1, divine_shield=True)


class SilvermoonGuardian(MinionCard):
    def __init__(self):
        super().__init__("Silvermoon Guardian", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(3, 3, divine_shield=True)


class TwilightDrake(MinionCard):
    def __init__(self):
        super().__init__("Twilight Drake", 4, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, MINION_TYPE.DRAGON)

    def create_minion(self, player):
        return Minion(4, 1, battlecry=gain_one_health_for_each_card_in_hand)


class MagmaRager(MinionCard):
    def __init__(self):
        super().__init__("Magma Rager", 3, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(5, 1)


class DireWolfAlpha(MinionCard):
    def __init__(self):
        super().__init__("Dire Wolf Alpha", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(2, 2, effects=[StatsAura(1, 0, minion_filter="adjacent")])


class WorgenInfiltrator(MinionCard):
    def __init__(self):
        super().__init__("Worgen Infiltrator", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(2, 1, stealth=True)


class Archmage(MinionCard):
    def __init__(self):
        super().__init__("Archmage", 6, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(4, 7, spell_damage=1)


class DalaranMage(MinionCard):
    def __init__(self):
        super().__init__("Dalaran Mage", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        minion = Minion(1, 4)
        minion.spell_damage = 1
        return minion


class Malygos(MinionCard):
    def __init__(self):
        super().__init__("Malygos", 9, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, MINION_TYPE.DRAGON)

    def create_minion(self, player):
        minion = Minion(4, 12)
        minion.spell_damage = 5
        return minion


class AzureDrake(MinionCard):
    def __init__(self):
        super().__init__("Azure Drake", 5, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, MINION_TYPE.DRAGON)

    def create_minion(self, player):
        minion = Minion(4, 4, battlecry=draw_card)
        minion.spell_damage = 1
        return minion


class OgreMagi(MinionCard):
    def __init__(self):
        super().__init__("Ogre Magi", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        minion = Minion(4, 4)
        minion.spell_damage = 1
        return minion


class Spellbreaker(MinionCard):
    def __init__(self):
        super().__init__("Spellbreaker", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, MINION_TYPE.NONE,
                         hearthbreaker.targeting.find_minion_battlecry_target)

    def create_minion(self, player):
        return Minion(4, 3, battlecry=silence)


class BloodmageThalnos(MinionCard):
    def __init__(self):
        super().__init__("Bloodmage Thalnos", 2, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        minion = Minion(1, 1, deathrattle=draw_card)
        minion.spell_damage = 1
        return minion


class LootHoarder(MinionCard):
    def __init__(self):
        super().__init__("Loot Hoarder", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        minion = Minion(2, 1, deathrattle=draw_card)
        return minion


class LeperGnome(MinionCard):
    def __init__(self):
        super().__init__("Leper Gnome", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def deal_enemy_hero_two_damage(minion):
            if minion.player is minion.player.game.current_player:
                player.game.other_player.hero.damage(2, None)
                player.game.other_player.hero.activate_delayed()

            else:
                player.game.current_player.hero.damage(2, None)
                player.game.current_player.hero.activate_delayed()

        return Minion(2, 1, deathrattle=deal_enemy_hero_two_damage)


class IronforgeRifleman(MinionCard):
    def __init__(self):
        super().__init__("Ironforge Rifleman", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, MINION_TYPE.NONE,
                         hearthbreaker.targeting.find_battlecry_target)

    def create_minion(self, player):
        return Minion(2, 2, battlecry=deal_one_damage)


class GnomishInventor(MinionCard):
    def __init__(self):
        super().__init__("Gnomish Inventor", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(2, 4, battlecry=draw_card)


class GoldshireFootman(MinionCard):
    def __init__(self):
        super().__init__("Goldshire Footman", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(1, 2, taunt=True)


class FrostwolfGrunt(MinionCard):
    def __init__(self):
        super().__init__("Frostwolf Grunt", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(2, 2, taunt=True)


class IronfurGrizzly(MinionCard):
    def __init__(self):
        super().__init__("Ironfur Grizzly", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(3, 3, taunt=True)


class LordOfTheArena(MinionCard):
    def __init__(self):
        super().__init__("Lord of the Arena", 6, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(6, 5, taunt=True)


class MurlocRaider(MinionCard):
    def __init__(self):
        super().__init__("Murloc Raider", 1, CHARACTER_CLASS.ALL, CARD_RARITY.FREE, MINION_TYPE.MURLOC)

    def create_minion(self, player):
        return Minion(2, 1)


class ManaAddict(MinionCard):
    def __init__(self):
        super().__init__("Mana Addict", 2, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        def increase_attack(card):
            minion.change_temp_attack(2)

        minion = Minion(1, 3)
        player.bind("spell_cast", increase_attack)
        minion.bind_once("silenced", lambda: player.unbind("spell_cast", increase_attack))
        return minion


class OasisSnapjaw(MinionCard):
    def __init__(self):
        super().__init__("Oasis Snapjaw", 4, CHARACTER_CLASS.ALL, CARD_RARITY.FREE, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(2, 7)


class RecklessRocketeer(MinionCard):
    def __init__(self):
        super().__init__("Reckless Rocketeer", 6, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(5, 2, charge=True)


class RiverCrocolisk(MinionCard):
    def __init__(self):
        super().__init__("River Crocolisk", 2, CHARACTER_CLASS.ALL, CARD_RARITY.FREE, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(2, 3)


class SenjinShieldmasta(MinionCard):
    def __init__(self):
        super().__init__("Sen'jin Shieldmasta", 4, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(3, 5, taunt=True)


class ScarletCrusader(MinionCard):
    def __init__(self):
        super().__init__("Scarlet Crusader", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(3, 1, divine_shield=True)


class Shieldbearer(MinionCard):
    def __init__(self):
        super().__init__("Shieldbearer", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(0, 4, taunt=True)


class SilverbackPatriarch(MinionCard):
    def __init__(self):
        super().__init__("Silverback Patriarch", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(1, 4, taunt=True)


class JunglePanther(MinionCard):
    def __init__(self):
        super().__init__("Jungle Panther", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(4, 2, stealth=True)


class RavenholdtAssassin(MinionCard):
    def __init__(self):
        super().__init__("Ravenholdt Assassin", 7, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(7, 5, stealth=True)


class StormpikeCommando(MinionCard):
    def __init__(self):
        super().__init__("Stormpike Commando", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         targeting_func=hearthbreaker.targeting.find_battlecry_target)

    def create_minion(self, player):
        return Minion(4, 2, battlecry=deal_two_damage)


class StormwindKnight(MinionCard):
    def __init__(self):
        super().__init__("Stormwind Knight", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(2, 5, charge=True)


class StranglethornTiger(MinionCard):
    def __init__(self):
        super().__init__("Stranglethorn Tiger", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(5, 5, stealth=True)


class Sunwalker(MinionCard):
    def __init__(self):
        super().__init__("Sunwalker", 6, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(4, 5, divine_shield=True, taunt=True)


class ThrallmarFarseer(MinionCard):
    def __init__(self):
        super().__init__("Thrallmar Farseer", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(2, 3, windfury=True)


class WindfuryHarpy(MinionCard):
    def __init__(self):
        super().__init__("Windfury Harpy", 6, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(4, 5, windfury=True)


class YoungDragonhawk(MinionCard):
    def __init__(self):
        super().__init__("Young Dragonhawk", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(1, 1, windfury=True)


class Wolfrider(MinionCard):
    def __init__(self):
        super().__init__("Wolfrider", 3, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(3, 1, charge=True)


class BootyBayBodyguard(MinionCard):
    def __init__(self):
        super().__init__("Booty Bay Bodyguard", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(5, 4, taunt=True)


class BoulderfistOgre(MinionCard):
    def __init__(self):
        super().__init__("Boulderfist Ogre", 6, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(6, 7)


class ChillwindYeti(MinionCard):
    def __init__(self):
        super().__init__("Chillwind Yeti", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(4, 5)


class CoreHound(MinionCard):
    def __init__(self):
        super().__init__("Core Hound", 7, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(9, 5)


class VoodooDoctor(MinionCard):
    def __init__(self):
        super().__init__("Voodoo Doctor", 1, CHARACTER_CLASS.ALL, CARD_RARITY.FREE,
                         targeting_func=hearthbreaker.targeting.find_battlecry_target)

    def create_minion(self, player):
        return Minion(2, 1, battlecry=heal_two)


class EarthenRingFarseer(MinionCard):
    def __init__(self):
        super().__init__("Earthen Ring Farseer", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         targeting_func=hearthbreaker.targeting.find_battlecry_target)

    def create_minion(self, player):
        return Minion(3, 3, battlecry=heal_three)


class ArcaneGolem(MinionCard):
    def __init__(self):
        super().__init__("Arcane Golem", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(4, 2, battlecry=give_enemy_crystal, charge=True)


class PriestessOfElune(MinionCard):
    def __init__(self):
        super().__init__("Priestess of Elune", 6, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(5, 4, battlecry=priestess_of_elune)


class DarkscaleHealer(MinionCard):
    def __init__(self):
        super().__init__("Darkscale Healer", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(4, 5, battlecry=darkscale_healer)


class ArgentCommander(MinionCard):
    def __init__(self):
        super().__init__("Argent Commander", 6, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(4, 2, divine_shield=True, charge=True)


class BluegillWarrior(MinionCard):
    def __init__(self):
        super().__init__("Bluegill Warrior", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, MINION_TYPE.MURLOC)

    def create_minion(self, player):
        return Minion(2, 1, charge=True)


class Wisp(MinionCard):
    def __init__(self):
        super().__init__("Wisp", 0, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(1, 1)


class Nightblade(MinionCard):
    def __init__(self):
        super().__init__("Nightblade", 5, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(4, 4, battlecry=nightblade)


class ShatteredSunCleric(MinionCard):
    def __init__(self):
        super().__init__("Shattered Sun Cleric", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         targeting_func=hearthbreaker.targeting.find_friendly_minion_battlecry_target)

    def create_minion(self, player):
        return Minion(3, 2, battlecry=ssc)


class TheBlackKnight(MinionCard):
    def __init__(self):
        super().__init__("The Black Knight", 6, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY,
                         targeting_func=hearthbreaker.targeting.find_enemy_minion_battlecry_target,
                         filter_func=lambda minion: minion.taunt)

    def create_minion(self, player):
        return Minion(4, 5, battlecry=destroy_target)


class AbusiveSergeant(MinionCard):
    def __init__(self):
        super().__init__("Abusive Sergeant", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         targeting_func=hearthbreaker.targeting.find_minion_battlecry_target)

    def create_minion(self, player):
        return Minion(2, 1, battlecry=two_temp_attack)


class DarkIronDwarf(MinionCard):
    def __init__(self):
        super().__init__("Dark Iron Dwarf", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         targeting_func=hearthbreaker.targeting.find_minion_battlecry_target)

    def create_minion(self, player):
        return Minion(4, 4, battlecry=two_temp_attack)


class Abomination(MinionCard):
    def __init__(self):
        super().__init__("Abomination", 5, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        def deal_two_to_all(minion):
            for target in hearthbreaker.targeting.find_battlecry_target(player.game, lambda x: True):
                target.damage(2, self)
            player.game.check_delayed()

        return Minion(4, 4, deathrattle=deal_two_to_all, taunt=True)


class FenCreeper(MinionCard):
    def __init__(self):
        super().__init__("Fen Creeper", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        minion = Minion(3, 6)
        minion.taunt = True
        return minion


class VentureCoMercenary(MinionCard):
    def __init__(self):
        super().__init__("Venture Co. Mercenary", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def apply_effect(m, p):
            class Filter:
                def __init__(self):
                    self.amount = -3
                    self.filter = lambda c: isinstance(c, MinionCard)
                    self.min = 0

            filter = Filter()
            minion.bind_once("silenced", lambda: player.mana_filters.remove(filter))
            player.mana_filters.append(filter)
            minion.bind("copied", apply_effect)
        minion = Minion(7, 6)
        apply_effect(minion, player)
        return minion


class AmaniBerserker(MinionCard):
    def __init__(self):
        super().__init__("Amani Berserker", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def increase_attack():
            minion.change_attack(3)

        def decrease_attack():
            minion.change_attack(-3)

        def silenced():
            minion.unbind("enraged", increase_attack)
            minion.unbind("unenraged", decrease_attack)

        minion = Minion(2, 3)
        minion.bind("enraged", increase_attack)
        minion.bind("unenraged", decrease_attack)
        minion.bind("silenced", silenced)
        return minion


class SilverHandKnight(MinionCard):
    def __init__(self):
        super().__init__("Silver Hand Knight", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def summon_squire(m):
            class Squire(MinionCard):
                def __init__(self):
                    super().__init__("Squire", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL)

                def create_minion(self, player):
                    return Minion(2, 2)

            Squire().summon(player, player.game, m.index + 1)

        return Minion(4, 4, battlecry=summon_squire)


class StormwindChampion(MinionCard):
    def __init__(self):
        super().__init__("Stormwind Champion", 7, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        minion = Minion(6, 6, effects=[StatsAura(attack=1, health=1)])
        return minion


class Deathwing(MinionCard):
    def __init__(self):
        super().__init__("Deathwing", 10, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, MINION_TYPE.DRAGON)

    def create_minion(self, player):
        return Minion(12, 12, battlecry=deathwing)


class Alexstrasza(MinionCard):
    def __init__(self):
        super().__init__("Alexstrasza", 9, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, MINION_TYPE.DRAGON,
                         hearthbreaker.targeting.find_hero_target)

    def create_minion(self, player):
        def set_hero_health(player):
            self.target.health = 15
        return Minion(8, 8, battlecry=set_hero_health)


class EmperorCobra(MinionCard):
    def __init__(self):
        super().__init__("Emperor Cobra", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(2, 3, effects=[Kill("did_damage", "minion", "other")])


class CrazedAlchemist(MinionCard):
    def __init__(self):
        super().__init__("Crazed Alchemist", 2, CHARACTER_CLASS.ALL, CARD_RARITY.RARE,
                         targeting_func=hearthbreaker.targeting.find_minion_battlecry_target)

    def create_minion(self, player):
        def swap(minion):
            if self.target is not None:
                temp_attack = self.target.calculate_attack()
                temp_health = self.target.health
                self.target.change_attack(temp_health - self.target.base_attack)
                if temp_attack < self.target.base_health:
                    self.target.decrease_health(self.target.base_health - temp_attack)
                elif temp_attack > self.target.base_health:
                    self.target.increase_health(temp_attack - self.target.base_health)
                self.target.health = self.target.calculate_max_health()
                if self.target.health is 0:
                    self.target.die(None)
        return Minion(2, 2, battlecry=swap)


class AcidicSwampOoze(MinionCard):
    def __init__(self):
        super().__init__("Acidic Swamp Ooze", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def destroy_enemy_weapon(player):
            if player.game.other_player.hero.weapon is not None:
                player.game.other_player.hero.weapon.destroy()
        return Minion(3, 2, battlecry=destroy_enemy_weapon)


class AncientBrewmaster(MinionCard):
    def __init__(self):
        super().__init__("Ancient Brewmaster", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         targeting_func=hearthbreaker.targeting.find_friendly_minion_battlecry_target)

    def create_minion(self, player):
        return Minion(5, 4, battlecry=return_to_hand)


class YouthfulBrewmaster(MinionCard):
    def __init__(self):
        super().__init__("Youthful Brewmaster", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         targeting_func=hearthbreaker.targeting.find_friendly_minion_battlecry_target)

    def create_minion(self, player):
        return Minion(3, 2, battlecry=return_to_hand)


class BaronGeddon(MinionCard):
    def __init__(self):
        super().__init__("Baron Geddon", 7, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        def baron_damage():
            targets = copy.copy(player.game.other_player.minions)
            targets.extend(player.game.current_player.minions)
            targets.append(player.game.other_player.hero)
            targets.append(player.game.current_player.hero)
            targets.remove(minion)
            for target in targets:
                target.damage(2, None)

        minion = Minion(7, 5)
        player.bind("turn_ended", baron_damage)
        minion.bind_once("silenced", lambda: player.unbind("turn_ended", baron_damage))
        return minion


class AngryChicken(MinionCard):
    def __init__(self):
        super().__init__("Angry Chicken", 1, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, MINION_TYPE.BEAST)

    def create_minion(self, player):
        def increase_attack():
            minion.change_attack(5)

        def decrease_attack():
            minion.change_attack(-5)

        def silenced():
            minion.unbind("enraged", increase_attack)
            minion.unbind("unenraged", decrease_attack)

        minion = Minion(1, 1)
        minion.bind("enraged", increase_attack)
        minion.bind("unenraged", decrease_attack)
        minion.bind("silenced", silenced)
        return minion


class RagingWorgen(MinionCard):
    def __init__(self):
        super().__init__("Raging Worgen", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def increase_attack():
            minion.change_attack(1)
            minion.windfury = True

        def decrease_attack():
            minion.change_attack(-1)
            minion.windfury = False

        def silenced():
            minion.unbind("enraged", increase_attack)
            minion.unbind("unenraged", decrease_attack)

        minion = Minion(3, 3)
        minion.bind("enraged", increase_attack)
        minion.bind("unenraged", decrease_attack)
        minion.bind("silenced", silenced)
        return minion


class TaurenWarrior(MinionCard):
    def __init__(self):
        super().__init__("Tauren Warrior", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def increase_attack():
            minion.change_attack(3)

        def decrease_attack():
            minion.change_attack(-3)

        def silenced():
            minion.unbind("enraged", increase_attack)
            minion.unbind("unenraged", decrease_attack)

        minion = Minion(2, 3)
        minion.taunt = True
        minion.bind("enraged", increase_attack)
        minion.bind("unenraged", decrease_attack)
        minion.bind("silenced", silenced)
        return minion


class SpitefulSmith(MinionCard):
    def __init__(self):
        super().__init__("Spiteful Smith", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def increase_weapon_attack():
            if player.hero.weapon:
                player.hero.weapon.base_attack += 2
                if player.game.current_player is player:
                    player.hero.change_temp_attack(2)

        def decrease_weapon_attack():
            if player.hero.weapon:
                player.hero.weapon.base_attack -= 2
                if player.game.current_player is player:
                    player.hero.change_temp_attack(-2)

        def weapon_equipped():
            if minion.enraged:
                increase_weapon_attack()

        def silenced():
            minion.unbind("enraged", increase_weapon_attack)
            minion.unbind("unenraged", decrease_weapon_attack)
            player.hero.unbind("weapon_equipped", weapon_equipped)

        minion = Minion(4, 6)
        minion.bind("enraged", increase_weapon_attack)
        minion.bind("unenraged", decrease_weapon_attack)
        player.hero.bind("weapon_equipped", weapon_equipped)
        minion.bind("silenced", silenced)
        return minion


class BloodKnight(MinionCard):
    def __init__(self):
        super().__init__("Blood Knight", 3, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC)

    def create_minion(self, player):
        def collect_divine_shields(minion):
            shields_stolen = 0
            targets = hearthbreaker.targeting.find_minion_battlecry_target(player.game, lambda m: m.divine_shield)
            if targets is not None:
                for target in targets:
                    shields_stolen += 1
                    target.divine_shield = False
                for i in range(0, shields_stolen):
                    minion.increase_health(3)
                    minion.change_attack(3)
        return Minion(3, 3, battlecry=collect_divine_shields)


class FrostwolfWarlord(MinionCard):
    def __init__(self):
        super().__init__("Frostwolf Warlord", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def buff_from_allies(minion):
            for i in range(0, len(minion.player.minions) - 1):
                minion.increase_health(1)
                minion.change_attack(1)
        return Minion(4, 4, battlecry=buff_from_allies)


class RaidLeader(MinionCard):
    def __init__(self):
        super().__init__("Raid Leader", 3, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(2, 2, effects=[StatsAura(1, 0)])


class DragonlingMechanic(MinionCard):
    def __init__(self):
        super().__init__("Dragonling Mechanic", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def summon_dragonling(m):
            class MechanicalDragonling(MinionCard):
                def __init__(self):
                    super().__init__("Mechanical Dragonling", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL)

                def create_minion(self, player):
                    return Minion(2, 1)
                # Apparently not a dragon
            MechanicalDragonling().summon(player, player.game, m.index)

        return Minion(2, 4, battlecry=summon_dragonling)


class MurlocTidehunter(MinionCard):
    def __init__(self):
        super().__init__("Murloc Tidehunter", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, MINION_TYPE.MURLOC)

    def create_minion(self, player):
        def summon_murlocscout(m):
            class MurlocScout(MinionCard):
                def __init__(self):
                    super().__init__("Murloc Scout", 0, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL, MINION_TYPE.MURLOC)

                def create_minion(self, player):
                    return Minion(1, 1)

            MurlocScout().summon(player, player.game, m.index)

        return Minion(2, 1, battlecry=summon_murlocscout)


class RazorfenHunter(MinionCard):
    def __init__(self):
        super().__init__("Razorfen Hunter", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def summon_boar(m):
            class Boar(MinionCard):
                def __init__(self):
                    super().__init__("Boar", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL, MINION_TYPE.BEAST)

                def create_minion(self, player):
                    return Minion(1, 1)

            Boar().summon(player, player.game, m.index)

        return Minion(2, 3, battlecry=summon_boar)


class KnifeJuggler(MinionCard):
    def __init__(self):
        super().__init__("Knife Juggler", 2, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(3, 2, effects=[Damage("after_added", 1, minion_filter="minion", target="random_enemy")])


class CairneBloodhoof(MinionCard):
    def __init__(self):
        super().__init__("Cairne Bloodhoof", 6, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        def summon_baine(m):
            class BaineBloodhoof(MinionCard):
                def __init__(self):
                    super().__init__("Baine Bloodhoof", 4, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL)

                def create_minion(self, player):
                    return Minion(4, 5)

            BaineBloodhoof().summon(player, player.game, m.index)

        return Minion(4, 5, deathrattle=summon_baine)


class HarvestGolem(MinionCard):
    def __init__(self):
        super().__init__("Harvest Golem", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def summon_damaged_golem(minion):
            class DamagedGolem(MinionCard):
                def __init__(self):
                    super().__init__("Damaged Golem", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL)

                def create_minion(self, player):
                    return Minion(2, 1)

            DamagedGolem().summon(minion.player, minion.game, minion.index)

        return Minion(2, 3, deathrattle=summon_damaged_golem)


class TheBeast(MinionCard):
    def __init__(self):
        super().__init__("The Beast", 6, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, MINION_TYPE.BEAST)

    def create_minion(self, player):
        def summon_finkle(minion):
            class FinkleEinhorn(MinionCard):
                def __init__(self):
                    super().__init__("Finkle Einhorn", 2, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL)

                def create_minion(self, player):
                    return Minion(3, 3)
            finkle_owner = []
            finkle_owner.append(player.game.current_player)
            finkle_owner.append(player.game.other_player)
            finkle_owner.remove(minion.player)
            owner = finkle_owner.pop()
            FinkleEinhorn().summon(owner, minion.game, len(owner.minions))

        return Minion(9, 7, deathrattle=summon_finkle)


class SylvanasWindrunner(MinionCard):
    def __init__(self):
        super().__init__("Sylvanas Windrunner", 6, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        def assume_direct_control(m):

            targets = copy.copy(m.player.opponent.minions)
            if len(targets) > 0:
                target = targets[player.game.random(0, len(targets) - 1)]
                new_minion = target.copy(m.player)
                target.remove_from_board()
                new_minion.add_to_board(len(m.player.minions))

        return Minion(5, 5, deathrattle=assume_direct_control)


class StampedingKodo(MinionCard):
    def __init__(self):
        super().__init__("Stampeding Kodo", 5, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, MINION_TYPE.BEAST)

    def create_minion(self, player):
        def random_destroy(m):
            targets = hearthbreaker.targeting.find_enemy_minion_battlecry_target(player.game,
                                                                                 lambda x: x.calculate_attack() <= 2)
            if targets is not None:
                target = targets[player.game.random(0, len(targets) - 1)]
                target.die(None)

        return Minion(3, 5, battlecry=random_destroy)


class FrostElemental(MinionCard):
    def __init__(self):
        super().__init__("Frost Elemental", 6, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         targeting_func=hearthbreaker.targeting.find_battlecry_target)

    def create_minion(self, player):
        def freeze_em(m):
            self.target.freeze()
        return Minion(5, 5, battlecry=freeze_em)


class Demolisher(MinionCard):
    def __init__(self):
        super().__init__("Demolisher", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        def two_random_damage():
            targets = copy.copy(player.game.other_player.minions)
            targets.append(player.game.other_player.hero)
            target = targets[player.game.random(0, len(targets) - 1)]
            target.damage(2, None)

        minion = Minion(1, 4)
        player.bind("turn_started", two_random_damage)
        minion.bind_once("silenced", lambda: player.unbind("turn_started", two_random_damage))
        return minion


class Doomsayer(MinionCard):
    def __init__(self):
        super().__init__("Doomsayer", 2, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC)

    def create_minion(self, player):
        def destroy_all():
            targets = copy.copy(player.game.other_player.minions)
            targets.extend(player.game.current_player.minions)
            for target in targets:
                target.die(None)

        minion = Minion(0, 7)
        player.bind("turn_started", destroy_all)
        minion.bind_once("silenced", lambda: player.unbind("turn_started", destroy_all))
        return minion


class Gruul(MinionCard):
    def __init__(self):
        super().__init__("Gruul", 8, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        def gruul_self_buff():
            minion.change_attack(1)
            minion.increase_health(1)

        minion = Minion(7, 7)
        player.game.current_player.bind("turn_ended", gruul_self_buff)
        minion.bind_once("silenced", lambda: player.game.current_player.unbind("turn_ended", gruul_self_buff))
        player.game.other_player.bind("turn_ended", gruul_self_buff)
        minion.bind_once("silenced", lambda: player.game.other_player.unbind("turn_ended", gruul_self_buff))
        return minion


class Hogger(MinionCard):
    def __init__(self):
        super().__init__("Hogger", 6, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        def summon_gnoll():
            class Gnoll(MinionCard):
                def __init__(self):
                    super().__init__("Gnoll", 2, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL)

                def create_minion(self, player):
                    minion = Minion(2, 2)
                    minion.taunt = True
                    return minion

            Gnoll().summon(player, player.game, minion.index + 1)
        minion = Minion(4, 4)
        player.bind("turn_ended", summon_gnoll)
        minion.bind_once("silenced", lambda: player.unbind("turn_ended", summon_gnoll))
        return minion


class ImpMaster(MinionCard):
    def __init__(self):
        super().__init__("Imp Master", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        def summon_imp():
            class Imp(MinionCard):
                def __init__(self):
                    super().__init__("Imp", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL, MINION_TYPE.DEMON)

                def create_minion(self, player):
                    return Minion(1, 1)

            minion.damage(1, None)
            player.game.check_delayed()
            Imp().summon(player, player.game, minion.index + 1)
        minion = Minion(1, 5)
        player.bind("turn_ended", summon_imp)
        minion.bind_once("silenced", lambda: player.unbind("turn_ended", summon_imp))
        return minion


class InjuredBlademaster(MinionCard):
    def __init__(self):
        super().__init__("Injured Blademaster", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        def self_damage(m):
            m.damage(4, None)
        return Minion(4, 7, battlecry=self_damage)


class MasterSwordsmith(MinionCard):
    def __init__(self):
        super().__init__("Master Swordsmith", 2, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        def buff_ally_attack():
            targets = copy.copy(player.game.current_player.minions)
            targets.remove(minion)
            if len(targets) > 0:
                target = targets[player.game.random(0, len(targets) - 1)]
                target.change_attack(1)

        minion = Minion(1, 3)
        player.bind("turn_ended", buff_ally_attack)
        minion.bind_once("silenced", lambda: player.unbind("turn_ended", buff_ally_attack))
        return minion


class NatPagle(MinionCard):
    def __init__(self):
        super().__init__("Nat Pagle", 2, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(0, 4, effects=[Draw("turn_started", probability=0.5)])


class Nozdormu(MinionCard):
    def __init__(self):
        super().__init__("Nozdormu", 9, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, MINION_TYPE.DRAGON)

    def create_minion(self, player):             # Strictly worse than Alexstrasza
        return Minion(8, 8)                      # Is the effect even applicable to AI?


class RagnarosTheFirelord(MinionCard):
    def __init__(self):
        super().__init__("Ragnaros the Firelord", 8, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        def eight_random_damage():
            targets = copy.copy(player.game.other_player.minions)
            targets.append(player.game.other_player.hero)
            target = targets[player.game.random(0, len(targets) - 1)]
            target.damage(8, None)

        def cant_attack():
            minion.active = False

        minion = Minion(8, 8)
        player.bind("turn_started", cant_attack)
        minion.bind_once("silenced", lambda: player.unbind("turn_started", cant_attack))
        player.bind("turn_ended", eight_random_damage)
        minion.bind_once("silenced", lambda: player.unbind("turn_ended", eight_random_damage))
        return minion


class AncientWatcher(MinionCard):
    def __init__(self):
        super().__init__("Ancient Watcher", 2, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        def cant_attack():
            minion.active = False

        minion = Minion(4, 5)
        player.bind("turn_started", cant_attack)
        minion.bind_once("silenced", lambda: player.unbind("turn_started", cant_attack))
        return minion


class ColdlightOracle(MinionCard):
    def __init__(self):
        super().__init__("Coldlight Oracle", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, MINION_TYPE.MURLOC)

    def create_minion(self, player):
        def both_draw_two(m):
            player.game.other_player.draw()
            player.game.other_player.draw()
            player.game.current_player.draw()
            player.game.current_player.draw()
        return Minion(2, 2, battlecry=both_draw_two)


class ColdlightSeer(MinionCard):
    def __init__(self):
        super().__init__("Coldlight Seer", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, MINION_TYPE.MURLOC)

    def create_minion(self, player):
        def buff_murlocs(m):
            murloc = hearthbreaker.targeting.find_friendly_minion_spell_target(
                player.game, lambda x: x.card.minion_type is MINION_TYPE.MURLOC and x is not m)
            for target in murloc:
                target.increase_health(2)

        return Minion(2, 3, battlecry=buff_murlocs)


class GrimscaleOracle(MinionCard):
    def __init__(self):
        super().__init__("Grimscale Oracle", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, MINION_TYPE.MURLOC)

    def create_minion(self, player):
        return Minion(1, 1, effects=[StatsAura(1, 0, minion_filter="murloc", players="both")])


class MurlocWarleader(MinionCard):
    def __init__(self):
        super().__init__("Murloc Warleader", 3, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC, MINION_TYPE.MURLOC)

    def create_minion(self, player):
        return Minion(3, 3, effects=[StatsAura(2, 1, minion_filter="murloc", players="both")])


class BigGameHunter(MinionCard):
    def __init__(self):
        super().__init__("Big Game Hunter", 3, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC,
                         targeting_func=hearthbreaker.targeting.find_minion_battlecry_target,
                         filter_func=lambda minion: minion.calculate_attack() >= 7)

    def create_minion(self, player):
        return Minion(4, 2, battlecry=destroy_target)


class BloodsailCorsair(MinionCard):
    def __init__(self):
        super().__init__("Bloodsail Corsair", 1, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, MINION_TYPE.PIRATE)

    def create_minion(self, player):
        def reduce_durability(m):
            if player.game.other_player.hero.weapon is not None:
                if player.game.other_player.hero.weapon.durability > 1:
                    player.game.other_player.hero.weapon.durability -= 1
                else:
                    player.game.other_player.hero.weapon.destroy()

        return Minion(1, 2, battlecry=reduce_durability)


class BloodsailRaider(MinionCard):
    def __init__(self):
        super().__init__("Bloodsail Raider", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, MINION_TYPE.PIRATE)

    def create_minion(self, player):
        def gain_weapon_attack(m):
            if player.hero.weapon is not None:
                m.change_attack(player.hero.weapon.base_attack)

        return Minion(2, 3, battlecry=gain_weapon_attack)


class CaptainGreenskin(MinionCard):
    def __init__(self):
        super().__init__("Captain Greenskin", 5, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, MINION_TYPE.PIRATE)

    def create_minion(self, player):
        def buff_weapon(m):
            if player.hero.weapon is not None:
                player.hero.weapon.base_attack += 1
                player.hero.weapon.durability += 1

        return Minion(5, 4, battlecry=buff_weapon)


class HungryCrab(MinionCard):
    def __init__(self):
        super().__init__("Hungry Crab", 1, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC, MINION_TYPE.BEAST,
                         hearthbreaker.targeting.find_minion_battlecry_target,
                         lambda minion: minion.card.minion_type is MINION_TYPE.MURLOC)

    def create_minion(self, player):
        def devour_murloc(m):
            if m.card.target is not None:
                m.card.target.die(None)
                m.change_attack(2)
                m.increase_health(2)

        return Minion(1, 2, battlecry=devour_murloc)


class MadBomber(MinionCard):
    def __init__(self):
        super().__init__("Mad Bomber", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def three_bombs(m):
            for i in range(0, 3):
                targets = copy.copy(player.game.other_player.minions)
                targets.extend(player.game.current_player.minions)
                targets.append(player.game.other_player.hero)
                targets.append(player.game.current_player.hero)
                targets.remove(m)
                target = targets[player.game.random(0, len(targets) - 1)]
                target.damage(1, None)

        return Minion(3, 2, battlecry=three_bombs)


class ManaWraith(MinionCard):
    def __init__(self):
        super().__init__("Mana Wraith", 2, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        class Filter:
            def __init__(self):
                self.amount = -1
                self.filter = lambda c: isinstance(c, MinionCard)
                self.min = 0

        filter = Filter()
        minion = Minion(2, 2)
        minion.bind_once("silenced", lambda: player.game.current_player.mana_filters.remove(filter))
        player.game.current_player.mana_filters.append(filter)
        minion.bind_once("silenced", lambda: player.game.other_player.mana_filters.remove(filter))
        player.game.other_player.mana_filters.append(filter)
        return minion


class MindControlTech(MinionCard):
    def __init__(self):
        super().__init__("Mind Control Tech", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        def mind_control(m):
            if len(player.game.other_player.minions) >= 4:
                targets = copy.copy(player.game.other_player.minions)
                target = targets[player.game.random(0, len(targets) - 1)]
                new_minion = target.copy(player)
                target.remove_from_board()
                new_minion.add_to_board(len(player.minions))

        return Minion(3, 3, battlecry=mind_control)


class MurlocTidecaller(MinionCard):
    def __init__(self):
        super().__init__("Murloc Tidecaller", 1, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, MINION_TYPE.MURLOC)

    def create_minion(self, player):
        def check_murloc(m):
            if m is not minion and m.card.minion_type is MINION_TYPE.MURLOC:
                minion.change_attack(1)

        minion = Minion(1, 2)
        player.game.current_player.bind("minion_played", check_murloc)
        minion.bind_once("silenced", lambda: player.game.current_player.unbind("minion_played", check_murloc))
        player.game.other_player.bind("minion_played", check_murloc)
        minion.bind_once("silenced", lambda: player.game.other_player.unbind("minion_played", check_murloc))
        return minion


class Onyxia(MinionCard):
    def __init__(self):
        super().__init__("Onyxia", 9, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, MINION_TYPE.DRAGON)

    def create_minion(self, player):
        def summon_whelps(m):
            class Whelp(MinionCard):
                def __init__(self):
                    super().__init__("Whelp", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL, MINION_TYPE.DRAGON)

                def create_minion(self, player):
                    return Minion(1, 1)
            whelp = Whelp()
            for i in range(len(player.minions), 7):
                whelp.summon(player, player.game, i)

        return Minion(8, 8, battlecry=summon_whelps)


class SouthseaCaptain(MinionCard):
    def __init__(self):
        super().__init__("Southsea Captain", 3, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC, MINION_TYPE.PIRATE)

    def create_minion(self, player):
        return Minion(3, 3, effects=[StatsAura(1, 1, minion_filter="pirate")])


class SouthseaDeckhand(MinionCard):
    def __init__(self):
        super().__init__("Southsea Deckhand", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, MINION_TYPE.PIRATE)

    def create_minion(self, player):
        def charge_if_weapon(m):
            if player.hero.weapon is not None:
                m.charge = True

        return Minion(2, 1, battlecry=charge_if_weapon)


class YoungPriestess(MinionCard):
    def __init__(self):
        super().__init__("Young Priestess", 1, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        def buff_ally_health():
            targets = copy.copy(player.game.current_player.minions)
            targets.remove(minion)
            if len(targets) > 0:
                target = targets[player.game.random(0, len(targets) - 1)]
                target.increase_health(1)

        minion = Minion(2, 1)
        player.bind("turn_ended", buff_ally_health)
        minion.bind_once("silenced", lambda: player.unbind("turn_ended", buff_ally_health))
        return minion


class AcolyteOfPain(MinionCard):
    def __init__(self):
        super().__init__("Acolyte of Pain", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def acolyte_draw(amount, player):
            minion.player.draw()
        minion = Minion(1, 3)
        minion.bind("damaged", acolyte_draw)
        minion.bind_once("silenced", lambda: minion.unbind("damaged", acolyte_draw))
        return minion


class CultMaster(MinionCard):
    def __init__(self):
        super().__init__("Cult Master", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def cult_draw(m, by):
            if m is not minion:
                m.player.draw()

        minion = Minion(4, 2)
        player.bind("minion_died", cult_draw)
        minion.bind_once("silenced", lambda: player.unbind("minion_died", cult_draw))
        return minion


class Secretkeeper(MinionCard):
    def __init__(self):
        super().__init__("Secretkeeper", 1, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        def keeper_grow(card):
            if isinstance(card, SecretCard):
                minion.change_attack(1)
                minion.increase_health(1)

        minion = Minion(1, 2)
        player.game.current_player.bind("spell_cast", keeper_grow)
        minion.bind_once("silenced", lambda: player.game.current_player.unbind("spell_cast", keeper_grow))
        player.game.other_player.bind("spell_cast", keeper_grow)
        minion.bind_once("silenced", lambda: player.game.other_player.unbind("spell_cast", keeper_grow))
        return minion


class VioletTeacher(MinionCard):
    def __init__(self):
        super().__init__("Violet Teacher", 4, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        def summon_apprentice(card):
            class VioletApprentice(MinionCard):
                def __init__(self):
                    super().__init__("Violet Apprentice", 0, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL)

                def create_minion(self, player):
                    return Minion(1, 1)
            apprentice = VioletApprentice()
            apprentice.summon(minion.player, minion.player.game, minion.index + 1)

        minion = Minion(3, 5)
        player.bind("spell_cast", summon_apprentice)
        minion.bind_once("silenced", lambda: player.unbind("spell_cast", summon_apprentice))
        return minion


class GadgetzanAuctioneer(MinionCard):
    def __init__(self):
        super().__init__("Gadgetzan Auctioneer", 5, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        def miracle_draw(card):
            minion.player.draw()

        minion = Minion(4, 4)
        player.bind("spell_cast", miracle_draw)
        minion.bind_once("silenced", lambda: player.unbind("spell_cast", miracle_draw))
        return minion


class IllidanStormrage(MinionCard):
    def __init__(self):
        super().__init__("Illidan Stormrage", 6, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, MINION_TYPE.DEMON)

    def create_minion(self, player):
        def summon_flame(card):
            class FlameOfAzzinoth(MinionCard):
                def __init__(self):
                    super().__init__("Flame of Azzinoth", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL)

                def create_minion(self, player):
                    return Minion(2, 1)
            if card is not self:
                flame = FlameOfAzzinoth()
                flame.summon(minion.player, minion.player.game, minion.index + 1)

        minion = Minion(7, 5)
        player.bind("card_used", summon_flame)
        minion.bind_once("silenced", lambda: player.unbind("card_played", summon_flame))
        return minion


class FlesheatingGhoul(MinionCard):
    def __init__(self):
        super().__init__("Flesheating Ghoul", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def ghoul_grow(m, by):
            if m is not minion:
                minion.change_attack(1)

        minion = Minion(2, 3)
        player.game.players[0].bind("minion_died", ghoul_grow)
        minion.bind_once("silenced", lambda: player.game.players[0].unbind("minion_died", ghoul_grow))
        player.game.players[1].bind("minion_died", ghoul_grow)
        minion.bind_once("silenced", lambda: player.game.players[1].unbind("minion_died", ghoul_grow))
        return minion


class Lightwarden(MinionCard):
    def __init__(self):
        super().__init__("Lightwarden", 1, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        def lightwarden_grow():
            minion.change_attack(2)

        minion = Minion(1, 2)
        player.game.bind("minion_healed", lightwarden_grow)
        minion.bind_once("silenced", lambda: player.game.unbind("minion_healed", lightwarden_grow))
        return minion


class QuestingAdventurer(MinionCard):
    def __init__(self):
        super().__init__("Questing Adventurer", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(2, 2, effects=[Buff("played", "card", "self", attack=1, health=1)])


class GurubashiBerserker(MinionCard):
    def __init__(self):
        super().__init__("Gurubashi Berserker", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def gurubashi_grow(amount, player):
            minion.change_attack(3)

        minion = Minion(2, 7)
        minion.bind("damaged", gurubashi_grow)
        minion.bind_once("silenced", lambda: minion.unbind("damaged", gurubashi_grow))
        return minion


class AncientMage(MinionCard):
    def __init__(self):
        super().__init__("Ancient Mage", 4, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        def give_spell_damage(m):
            if m.index > 0:
                minion = m.player.minions[m.index - 1]
                minion.spell_damage += 1
                m.player.spell_damage += 1

            if m.index < len(m.player.minions) - 1:
                minion = m.player.minions[m.index + 1]
                minion.spell_damage += 1
                m.player.spell_damage += 1

        return Minion(2, 5, battlecry=give_spell_damage)


class DefenderOfArgus(MinionCard):
    def __init__(self):
        super().__init__("Defender of Argus", 4, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        def give_argus_buff(m):
            if m.index > 0:
                minion = m.player.minions[m.index - 1]
                minion.taunt = True
                minion.change_attack(1)
                minion.increase_health(1)

            if m.index < len(m.player.minions) - 1:
                minion = m.player.minions[m.index + 1]
                minion.taunt = True
                minion.change_attack(1)
                minion.increase_health(1)

        return Minion(2, 3, battlecry=give_argus_buff)


class SunfuryProtector(MinionCard):
    def __init__(self):
        super().__init__("Sunfury Protector", 2, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        def give_argus_buff(m):
            if m.index > 0:
                minion = m.player.minions[m.index - 1]
                minion.taunt = True

            if m.index < len(m.player.minions) - 1:
                minion = m.player.minions[m.index + 1]
                minion.taunt = True

        return Minion(2, 3, battlecry=give_argus_buff)


class HarrisonJones(MinionCard):
    def __init__(self):
        super().__init__("Harrison Jones", 5, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        def destroy_enemy_weapon(m):
            if player.game.other_player.hero.weapon is not None:
                for i in range(0, player.game.other_player.hero.weapon.durability):
                    m.player.draw()
                m.player.game.other_player.hero.weapon.destroy()

        return Minion(5, 4, battlecry=destroy_enemy_weapon)


class KingMukla(MinionCard):
    def __init__(self):
        super().__init__("King Mukla", 3, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, MINION_TYPE.BEAST)

    def create_minion(self, player):
        def give_bananas(m):
            class Bananas(Card):
                def __init__(self):
                    super().__init__("Bananas", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL,
                                     hearthbreaker.targeting.find_minion_spell_target)

                def use(self, player, game):
                    super().use(player, game)
                    self.target.change_attack(1)
                    self.target.increase_health(1)
            player.game.other_player.hand.append(Bananas())
            player.game.other_player.hand.append(Bananas())

        return Minion(5, 5, battlecry=give_bananas)


class LeeroyJenkins(MinionCard):
    def __init__(self):
        super().__init__("Leeroy Jenkins", 5, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        def summon_whelps(m):
            class Whelp(MinionCard):
                def __init__(self):
                    super().__init__("Whelp", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL, MINION_TYPE.DRAGON)

                def create_minion(self, player):
                    return Minion(1, 1)
            whelp = Whelp()
            whelp.summon(player.game.other_player, player.game, len(player.game.other_player.minions))
            whelp.summon(player.game.other_player, player.game, len(player.game.other_player.minions))

        minion = Minion(6, 2, battlecry=summon_whelps)
        minion.charge = True
        return minion


class MountainGiant(MinionCard):
    def __init__(self):
        super().__init__("Mountain Giant", 12, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC)

    def create_minion(self, player):
        return Minion(8, 8)

    def mana_cost(self, player):
        cost = super().mana_cost(player) - len(player.hand)
        return cost


class MoltenGiant(MinionCard):
    def __init__(self):
        super().__init__("Molten Giant", 20, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC)

    def create_minion(self, player):
        return Minion(8, 8)

    def mana_cost(self, player):
        cost = super().mana_cost(player) - player.hero.calculate_max_health() + player.hero.health
        if cost < 0:
            return 0
        return cost


class SeaGiant(MinionCard):
    def __init__(self):
        super().__init__("Sea Giant", 10, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC)

    def create_minion(self, player):
        return Minion(8, 8)

    def mana_cost(self, player):
        cost = super().mana_cost(player) - len(player.game.players[0].minions) - len(player.game.players[1].minions)
        if cost < 0:
            return 0
        return cost


class DreadCorsair(MinionCard):
    def __init__(self):
        super().__init__("Dread Corsair", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, MINION_TYPE.PIRATE)

    def create_minion(self, player):
        return Minion(3, 3, taunt=True)

    def mana_cost(self, player):
        if player.hero.weapon:
            cost = super().mana_cost(player) - player.hero.weapon.base_attack
        else:
            return 4
        if cost < 0:
            return 0
        return cost


class CaptainsParrot(MinionCard):
    def __init__(self):
        super().__init__("Captain's Parrot", 2, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC, MINION_TYPE.BEAST)

    def create_minion(self, player):
        def draw_pirate(m):
            minions = []
            for i in range(0, 30):
                if not m.player.deck.used[i] and isinstance(m.player.deck.cards[i], MinionCard) and \
                        m.player.deck.cards[i].minion_type == MINION_TYPE.PIRATE:
                    minions.append(i)
            if len(minions) > 0:
                index = minions.pop(player.game.random(0, len(minions) - 1))
                m.player.deck.used[index] = True
                m.player.deck.left -= 1
                m.player.hand.append(m.player.deck.cards[index])
                self.trigger("card_drawn", m.player.deck.cards[index])

        return Minion(1, 1, battlecry=draw_pirate)


class TinkmasterOverspark(MinionCard):
    def __init__(self):
        super().__init__("Tinkmaster Overspark", 3, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        def transform_random(m):
            class Squirrel(MinionCard):
                def __init__(self):
                    super().__init__("Squirrel", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL, MINION_TYPE.BEAST)

                def create_minion(self, player):
                    return Minion(1, 1)

            class Devilsaur(MinionCard):
                def __init__(self):
                    super().__init__("Devilsaur", 5, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL, MINION_TYPE.BEAST)

                def create_minion(self, player):
                    return Minion(5, 5)

            squirrel = Squirrel()
            devilsaur = Devilsaur()
            targets = copy.copy(player.game.other_player.minions)
            targets.extend(player.game.current_player.minions)
            targets.remove(m)
            if len(targets) > 0:
                target = targets[player.game.random(0, len(targets) - 1)]
                if player.game.random(0, 1) == 1:
                    minion = squirrel.create_minion(None)
                    minion.card = squirrel
                    target.replace(minion)
                else:
                    minion = devilsaur.create_minion(None)
                    minion.card = devilsaur
                    target.replace(minion)

        return Minion(3, 3, battlecry=transform_random)


class AlarmoBot(MinionCard):
    def __init__(self):
        super().__init__("Alarm-o-Bot", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        def swap_with_hand():
            swap_targets = []
            for i in range(0, len(player.hand)):
                if isinstance(player.hand[i], MinionCard):
                    swap_targets.append(player.hand[i])
            if len(swap_targets) > 0:
                swap_target = swap_targets[player.game.random(0, len(swap_targets) - 1)]
                index = minion.index
                minion.bounce()
                player.hand.remove(swap_target)
                swap_target.summon(player, player.game, index)

        minion = Minion(0, 3)
        player.bind("turn_started", swap_with_hand)
        minion.bind_once("silenced", lambda: player.unbind("turn_started", swap_with_hand))
        return minion


class EliteTaurenChieftain(MinionCard):
    def __init__(self):
        super().__init__("Elite Tauren Chieftain", 5, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        def both_may_rock(m):
            class IAmMurloc(Card):
                def __init__(self):
                    super().__init__("I Am Murloc", 4, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL)

                def use(self, player, game):
                    super().use(player, game)

                    class Murloc(MinionCard):
                        def __init__(self):
                            super().__init__("Murloc", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL, MINION_TYPE.MURLOC)

                        def create_minion(self, p):
                            return Minion(1, 1)

                    for i in range(0, player.game.random(3, 5)):
                        Murloc().summon(player, player.game, len(player.minions))

            class PowerOfTheHorde(Card):
                def __init__(self):
                    super().__init__("Power of the Horde", 4, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL)

                def use(self, player, game):
                    super().use(player, game)

                    horde_list = [FrostwolfGrunt(), TaurenWarrior(), ThrallmarFarseer(),
                                  SilvermoonGuardian(), SenjinShieldmasta(), CairneBloodhoof()]
                    horde_summon = horde_list[player.game.random(0, 5)]
                    horde_summon.summon(player, player.game, len(player.minions))

            class RoguesDoIt(Card):
                def __init__(self):
                    super().__init__("Rogues Do It...", 4, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL,
                                     hearthbreaker.targeting.find_spell_target)

                def use(self, player, game):
                    super().use(player, game)

                    self.target.damage(player.effective_spell_damage(4), self)
                    player.draw()

            etc_card_list = [IAmMurloc(), PowerOfTheHorde(), RoguesDoIt()]
            for p in player.game.players:
                if len(p.hand) < 10:
                    p.hand.append(etc_card_list[player.game.random(0, 2)])
                else:
                    self.trigger("card_destroyed", etc_card_list[player.game.random(0, 2)])

        return Minion(5, 5, battlecry=both_may_rock)


class MillhouseManastorm(MinionCard):
    def __init__(self):
        super().__init__("Millhouse Manastorm", 2, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        def free_spells(m):
            class Filter:
                def __init__(self):
                    self.amount = 10
                    self.filter = lambda c: c.is_spell()
                    self.min = 0

            free = Filter()

            def start_free_spells():
                player.game.other_player.mana_filters.append(free)

            def end_free_spells():
                player.game.other_player.mana_filters.remove(free)

            player.game.other_player.bind_once("turn_started", start_free_spells)
            player.game.other_player.bind_once("turn_ended", end_free_spells)

        return Minion(4, 4, battlecry=free_spells)


class PintSizedSummoner(MinionCard):
    def __init__(self):
        super().__init__("Pint-Sized Summoner", 2, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        class Filter:
            def __init__(self):
                self.amount = 1
                self.filter = lambda c: isinstance(c, MinionCard)
                self.min = 0

        lesser = Filter()

        def start_discounted_minion():
            player.mana_filters.append(lesser)

        def end_discounted_minion(m):
            player.mana_filters.remove(lesser)

        def subbind():
            player.bind_once("minion_played", end_discounted_minion)
            minion.bind_once("silenced", lambda: player.unbind("minion_played", end_discounted_minion))

        minion = Minion(2, 2)
        player.bind("turn_started", start_discounted_minion)
        player.bind("turn_started", subbind)
        minion.bind_once("silenced", lambda: player.unbind("turn_started", start_discounted_minion))
        minion.bind_once("silenced", lambda: player.unbind("turn_started", subbind))
        return minion


class OldMurkEye(MinionCard):
    def __init__(self):
        super().__init__("Old Murk-Eye", 4, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, MINION_TYPE.MURLOC)

    def create_minion(self, player):
        def set_base_attack(m):
            targets = copy.copy(player.game.current_player.minions)
            targets.extend(player.game.other_player.minions)
            for target in targets:
                if target is not m and target.card.minion_type is MINION_TYPE.MURLOC:
                    minion.change_attack(1)

        def check_murloc(m):
            if m is not minion and m.card.minion_type is MINION_TYPE.MURLOC:
                minion.change_attack(1)

        def rip_murloc(m, by):
            if m is not minion and m.card.minion_type is MINION_TYPE.MURLOC:
                minion.change_attack(-1)

        minion = Minion(2, 4, battlecry=set_base_attack, charge=True)
        player.game.current_player.bind("minion_played", check_murloc)
        minion.bind_once("silenced", lambda: player.game.current_player.unbind("minion_played", check_murloc))
        player.game.other_player.bind("minion_played", check_murloc)
        minion.bind_once("silenced", lambda: player.game.other_player.unbind("minion_played", check_murloc))
        player.game.current_player.bind("minion_died", rip_murloc)
        minion.bind_once("silenced", lambda: player.game.current_player.unbind("minion_died", rip_murloc))
        player.game.other_player.bind("minion_died", rip_murloc)
        minion.bind_once("silenced", lambda: player.game.other_player.unbind("minion_died", rip_murloc))
        return minion


class Ysera(MinionCard):
    def __init__(self):
        super().__init__("Ysera", 9, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, MINION_TYPE.DRAGON)

    def create_minion(self, player):
        def dream_card():
            class Dream(Card):
                def __init__(self):
                    super().__init__("Dream", 0, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL,
                                     hearthbreaker.targeting.find_minion_spell_target)

                def use(self, player, game):
                    super().use(player, game)
                    self.target.bounce()

            class YseraAwakens(Card):
                def __init__(self):
                    super().__init__("Ysera Awakens", 2, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL)

                def use(self, player, game):
                    super().use(player, game)
                    targets = copy.copy(player.game.other_player.minions)
                    targets.extend(player.game.current_player.minions)
                    targets.append(player.game.other_player.hero)
                    targets.append(player.game.current_player.hero)
                    for minion in targets:
                        if isinstance(minion, Minion) and minion.card.name == "Ysera":
                            targets.remove(minion)
                    for minion in targets:
                        minion.damage(player.effective_spell_damage(5), self)

            class Nightmare(Card):
                def __init__(self):
                    super().__init__("Nightmare", 0, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL,
                                     hearthbreaker.targeting.find_minion_spell_target)

                def use(self, player, game):
                    super().use(player, game)
                    self.target.change_attack(5)
                    self.target.increase_health(5)

                    def death():
                        self.target.die(None)
                        game.check_delayed()

                    player.bind("turn_started", death)
                    self.target.bind_once("silenced", lambda: player.unbind("turn_started", death))

            class PlayfulSister(MinionCard):
                def __init__(self):
                    super().__init__("Playful Sister", 3, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL)

                def create_minion(self, player):
                    def silence():
                        minion.spell_targettable = lambda: True

                    minion = Minion(3, 5)
                    minion.spell_targettable = lambda: False
                    minion.bind("silenced", silence)
                    return minion

            class EmeraldDrake(MinionCard):
                def __init__(self):
                    super().__init__("Emerald Drake", 4, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL, MINION_TYPE.DRAGON)

                def create_minion(self, player):
                    return Minion(7, 6)
            dream_card_list = [EmeraldDrake(), PlayfulSister(), Nightmare(), YseraAwakens(), Dream()]
            if len(player.hand) < 10:
                player.hand.append(dream_card_list[player.game.random(0, 4)])
            else:
                self.trigger("card_destroyed", dream_card_list[player.game.random(0, 4)])
        minion = Minion(4, 12)
        player.bind("turn_ended", dream_card)
        minion.bind_once("silenced", lambda: player.unbind("turn_ended", dream_card))
        return minion


class GelbinMekkatorque(MinionCard):
    def __init__(self):
        super().__init__("Gelbin Mekkatorque", 6, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        def awesome_invention(m):
            class Emboldener3000(MinionCard):
                def __init__(self):
                    super().__init__("Emboldener 3000", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL)

                def create_minion(self, player):
                    def random_buff():
                        targets = copy.copy(player.game.other_player.minions)
                        targets.extend(player.game.current_player.minions)
                        target = targets[player.game.random(0, len(targets) - 1)]
                        target.change_attack(1)
                        target.increase_health(1)
                    minion = Minion(0, 4)
                    player.bind("turn_ended", random_buff)
                    minion.bind_once("silenced", lambda: player.unbind("turn_ended", random_buff))
                    return minion

            class HomingChicken(MinionCard):
                def __init__(self):
                    super().__init__("Homing Chicken", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL)

                def create_minion(self, player):
                    def death_draw():
                        minion.die(None)
                        for i in range(0, 3):
                            player.draw()
                    minion = Minion(0, 1)
                    player.bind_once("turn_started", death_draw)
                    minion.bind_once("silenced", lambda: player.unbind("turn_started", death_draw))
                    return minion

            class Poultryizer(MinionCard):
                def __init__(self):
                    super().__init__("Poultryizer", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL)

                def create_minion(self, player):
                    def poultrymorph():
                        targets = copy.copy(player.game.other_player.minions)
                        targets.extend(player.game.current_player.minions)
                        target = targets[player.game.random(0, len(targets) - 1)]

                        class Chicken(MinionCard):
                            def __init__(self):
                                super().__init__("Chicken", 0, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL,
                                                 MINION_TYPE.BEAST)

                            def create_minion(self, p):
                                return Minion(1, 1)

                        chicken = Chicken()
                        minion = chicken.create_minion(None)
                        minion.card = chicken
                        target.replace(minion)
                    minion = Minion(0, 3)
                    player.bind("turn_started", poultrymorph)
                    minion.bind_once("silenced", lambda: player.unbind("turn_started", poultrymorph))
                    return minion

            class RepairBot(MinionCard):
                def __init__(self):
                    super().__init__("Repair Bot", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL)

                def create_minion(self, player):
                    def repair():
                        targets = []
                        for m in hearthbreaker.targeting.find_spell_target(
                                player.game, lambda x: x.health != x.calculate_max_health()):
                            targets.append(m)
                        if len(targets) > 0:
                            repairee = targets[player.game.random(0, len(targets) - 1)]
                            repairee.heal(player.effective_heal_power(6), self)
                    minion = Minion(0, 3)
                    player.bind("turn_ended", repair)
                    minion.bind_once("silenced", lambda: player.unbind("turn_ended", repair))
                    return minion
            invention_list = [Emboldener3000(), HomingChicken(), Poultryizer(), RepairBot()]
            invention = invention_list[player.game.random(0, 3)]
            invention.summon(player, player.game, m.index + 1)
        return Minion(6, 6, battlecry=awesome_invention)


class LorewalkerCho(MinionCard):
    def __init__(self):
        super().__init__("Lorewalker Cho", 2, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        def pass_spell(card):
            if len(player.game.other_player.hand) < 10:
                card_type = type(card)
                player.game.other_player.hand.append(card_type())

        minion = Minion(0, 4)
        player.game.current_player.bind("spell_cast", pass_spell)
        minion.bind_once("silenced", lambda: player.game.current_player.unbind("spell_cast", pass_spell))
        player.game.other_player.bind("spell_cast", pass_spell)
        minion.bind_once("silenced", lambda: player.game.other_player.unbind("spell_cast", pass_spell))
        return minion


class WildPyromancer(MinionCard):
    def __init__(self):
        super().__init__("Wild Pyromancer", 2, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        def one_damage_to_all_minions(card):
            if card.is_spell():
                targets = copy.copy(player.game.other_player.minions)
                targets.extend(player.game.current_player.minions)
                for target in targets:
                    target.damage(1, None)
        minion = Minion(3, 2)
        player.bind("card_used", one_damage_to_all_minions)  # This activates before the spell, not after
        minion.bind_once("silenced", lambda: player.unbind("card_used", one_damage_to_all_minions))
        return minion


class FacelessManipulator(MinionCard):
    def __init__(self):
        super().__init__("Faceless Manipulator", 5, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC,
                         targeting_func=hearthbreaker.targeting.find_minion_battlecry_target)

    def create_minion(self, player):
        def copy_minion(minion):
            if self.target:
                new_minion = self.target.copy(player)
                minion.replace(new_minion)

        return Minion(3, 3, battlecry=copy_minion)


class NerubianEgg(MinionCard):
    def __init__(self):
        super().__init__("Nerubian Egg", 2, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        def summon_nerubian(m):
            class Nerubian(MinionCard):
                def __init__(self):
                    super().__init__("Nerubian", 3, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL)

                def create_minion(self, p):
                    return Minion(4, 4)

            Nerubian().summon(m.player, m.player.game, m.index)

        return Minion(0, 2, deathrattle=summon_nerubian)


class Maexxna(MinionCard):
    def __init__(self):
        super().__init__("Maexxna", 6, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, MINION_TYPE.BEAST)

    def create_minion(self, player):
            return Minion(2, 8, effects=[Kill("did_damage", "minion", "other")])


class HauntedCreeper(MinionCard):
    def __init__(self):
        super().__init__("Haunted Creeper", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, MINION_TYPE.BEAST)

    def create_minion(self, player):
        def summon_spiders(minion):
            class SpectralSpider(MinionCard):
                def __init__(self):
                    super().__init__("Spectral Spider", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL)

                def create_minion(self, player):
                    return Minion(1, 1)

            SpectralSpider().summon(minion.player, minion.game, minion.index)
            SpectralSpider().summon(minion.player, minion.game, minion.index)

        return Minion(1, 2, deathrattle=summon_spiders)


class NerubarWeblord(MinionCard):
    def __init__(self):
        super().__init__("Nerub'ar Weblord", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(1, 4, effects=[IncreaseBattlecryMinionCost(2)])


class UnstableGhoul(MinionCard):
    def __init__(self):
        super().__init__("Unstable Ghoul", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def deal_one_to_minions(minion):
            for target in hearthbreaker.targeting.find_minion_battlecry_target(minion.game, lambda x: True):
                target.damage(1, self)
                minion.game.check_delayed()

        return Minion(1, 3, deathrattle=deal_one_to_minions, taunt=True)


class Loatheb(MinionCard):
    def __init__(self):
        super().__init__("Loatheb", 5, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        def increase_card_cost(minion):
            minion.player.opponent.add_effect(PlayerManaFilter(-5, "spell", "turn_ended"))

        return Minion(5, 5, battlecry=increase_card_cost)


class StoneskinGargoyle(MinionCard):
    def __init__(self):
        super().__init__("Stoneskin Gargoyle", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(1, 4, effects=[Heal("turn_started", 10000, target="self")])


class SludgeBelcher(MinionCard):
    def __init__(self):
        super().__init__("Sludge Belcher", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def summon_slime(minion):
            class Slime(MinionCard):
                def __init__(self):
                    super().__init__("Slime", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL)

                def create_minion(self, p):
                    return Minion(1, 2, taunt=True)

            Slime().summon(minion.player, minion.game, minion.index)

        return Minion(3, 5, taunt=True, deathrattle=summon_slime)


class BaronRivendare(MinionCard):
    def __init__(self):
        super().__init__("Baron Rivendare", 4, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(1, 7, effects=[DoubleDeathrattle()])


class DancingSwords(MinionCard):
    def __init__(self):
        super().__init__("Dancing Swords", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(4, 4, deathrattle=opponent_draw_two)


class Deathlord(MinionCard):
    def __init__(self):
        super().__init__("Deathlord", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(2, 8, taunt=True, deathrattle=put_friendly_minion_on_board_from_enemy_deck)


class SpectralKnight(MinionCard):
    def __init__(self):
        super().__init__("Spectral Knight", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(4, 6, spell_targetable=False)


class Undertaker(MinionCard):
    def __init__(self):
        super().__init__("Undertaker", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(1, 2, effects=[Buff("summoned", "deathrattle", "self", 1, 1, "friendly")])


class WailingSoul(MinionCard):
    def __init__(self):
        super().__init__("Wailing Soul", 4, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        def silence_other_minions(minion):
            for mini in player.minions:
                if mini is not minion:
                    mini.silence()
        return Minion(3, 5, battlecry=silence_other_minions)


class ZombieChow(MinionCard):
    def __init__(self):
        super().__init__("Zombie Chow", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def restore_5_health(minion):
            minion.player.opponent.hero.heal(minion.player.effective_heal_power(5), minion)

        return Minion(2, 3, deathrattle=restore_5_health)


class Thaddius(MinionCard):
    def __init__(self):
        super().__init__("Thaddius", 10, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL)

    def create_minion(self, player):
        return Minion(11, 11)


class Feugen(MinionCard):
    def __init__(self):
        super().__init__("Feugen", 5, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        def summon_thaddius(minion):
            if "Stalagg" in minion.player.graveyard:
                Thaddius().summon(minion.player, minion.game, minion.index)

        return Minion(4, 7, deathrattle=summon_thaddius)


class Stalagg(MinionCard):
    def __init__(self):
        super().__init__("Stalagg", 5, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        def summon_thaddius(minion):
            if "Feugen" in minion.player.graveyard:
                Thaddius().summon(minion.player, minion.game, minion.index)

        return Minion(7, 4, deathrattle=summon_thaddius)


class MadScientist(MinionCard):
    def __init__(self):
        super().__init__("Mad Scientist", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def play_secret(minion):
            secret_indices = []
            for index in range(0, 30):
                if not minion.player.deck.used[index] and \
                        isinstance(minion.player.deck.cards[index], SecretCard) and \
                        minion.player.deck.cards[index].name not in [secret.name for secret in minion.player.secrets]:
                    secret_indices.append(index)
            if len(secret_indices) > 0:
                secret_index = secret_indices[minion.game.random(0, len(secret_indices) - 1)]
                secret = minion.player.deck.cards[secret_index]
                minion.player.secrets.append(secret)
                minion.player.deck.used[secret_index] = True
                if minion.player is minion.game.other_player:
                    secret.player = minion.player
                    secret.activate(minion.player)

        return Minion(2, 2, deathrattle=play_secret)


class EchoingOoze(MinionCard):
    def __init__(self):
        super().__init__("Echoing Ooze", 2, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC)

    def create_minion(self, player):
        def duplicate_at_end(minion):
            player.add_effect(DuplicateMinion(minion, "turn_ended"))
        return Minion(1, 2, battlecry=duplicate_at_end)


class ShadeOfNaxxramas(MinionCard):
    def __init__(self):
        super().__init__("Shade of Naxxramas", 3, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC)

    def create_minion(self, player):
        return Minion(2, 2, stealth=True, effects=[Buff("turn_started", attack=1, health=1, players="friendly")])


class KelThuzad(MinionCard):
    def __init__(self):
        super().__init__("Kel'Thuzad", 8, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(6, 8, effects=[ResurrectFriendlyMinionsAtEndOfTurn()])
