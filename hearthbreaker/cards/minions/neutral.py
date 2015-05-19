from hearthbreaker.cards.base import SpellCard, MinionCard
from hearthbreaker.game_objects import Minion
from hearthbreaker.tags.action import Heal, Summon, Draw, \
    Kill, Damage, ResurrectFriendly, Steal, Duplicate, Give, SwapWithHand, AddCard, Transform, ApplySecret, \
    Silence, Bounce, GiveManaCrystal, Equip, GiveAura, Replace, SetHealth, ChangeTarget, Discard, \
    RemoveDivineShields, DecreaseDurability, IncreaseDurability, IncreaseWeaponAttack, Destroy, GiveEffect, SwapStats
from hearthbreaker.tags.base import Effect, Deathrattle, CardQuery, CARD_SOURCE, Battlecry, Aura, \
    BuffUntil, Buff, AuraUntil, ActionTag
from hearthbreaker.tags.condition import Adjacent, IsType, MinionHasDeathrattle, IsMinion, IsSecret, \
    MinionIsTarget, IsSpell, IsDamaged, InGraveyard, ManaCost, OpponentMinionCountIsGreaterThan, AttackGreaterThan, \
    IsWeapon, HasStatus, AttackLessThanOrEqualTo, CardRarity, OneIn, NotCurrentTarget, HasDivineShield, HasSecret, \
    BaseAttackEqualTo, GreaterThan, And, TargetAdjacent, Matches, HasBattlecry, Not
from hearthbreaker.tags.event import TurnEnded, CardPlayed, MinionSummoned, TurnStarted, DidDamage, AfterAdded, \
    SpellCast, CharacterHealed, CharacterDamaged, MinionDied, CardUsed, Damaged, Attack, CharacterAttack, MinionPlaced
from hearthbreaker.tags.selector import MinionSelector, BothPlayer, SelfSelector, \
    PlayerSelector, TargetSelector, EnemyPlayer, CharacterSelector, WeaponSelector, \
    HeroSelector, OtherPlayer, UserPicker, RandomPicker, CurrentPlayer, Count, Attribute, CardSelector, \
    Difference, LastDrawnSelector, RandomAmount, DeadMinionSelector
from hearthbreaker.constants import CARD_RARITY, CHARACTER_CLASS, MINION_TYPE
from hearthbreaker.tags.status import ChangeAttack, ChangeHealth, Charge, Taunt, Windfury, CantAttack, \
    SpellDamage, DoubleDeathrattle, Frozen, ManaChange, DivineShield, MegaWindfury
import hearthbreaker.targeting
import copy


class BloodfenRaptor(MinionCard):
    def __init__(self):
        super().__init__("Bloodfen Raptor", 2, CHARACTER_CLASS.ALL, CARD_RARITY.FREE, minion_type=MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(3, 2)


class ElvenArcher(MinionCard):
    def __init__(self):
        super().__init__("Elven Archer", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Damage(1), CharacterSelector(players=BothPlayer(), picker=UserPicker())))

    def create_minion(self, player):
        return Minion(1, 1)


class NoviceEngineer(MinionCard):
    def __init__(self):
        super().__init__("Novice Engineer", 2, CHARACTER_CLASS.ALL, CARD_RARITY.FREE,
                         battlecry=Battlecry(Draw(), PlayerSelector()))

    def create_minion(self, player):
        return Minion(1, 1)


class StonetuskBoar(MinionCard):
    def __init__(self):
        super().__init__("Stonetusk Boar", 1, CHARACTER_CLASS.ALL, CARD_RARITY.FREE, minion_type=MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(1, 1, charge=True)


class IronbeakOwl(MinionCard):
    def __init__(self):
        super().__init__("Ironbeak Owl", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.BEAST,
                         battlecry=Battlecry(Silence(), MinionSelector(players=BothPlayer(), picker=UserPicker())))

    def create_minion(self, player):
        return Minion(2, 1)


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
        super().__init__("Faerie Dragon", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.DRAGON)

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
        super().__init__("Twilight Drake", 4, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, minion_type=MINION_TYPE.DRAGON,
                         battlecry=Battlecry(Give(Buff(ChangeHealth(Count(CardSelector())))), SelfSelector()))

    def create_minion(self, player):
        return Minion(4, 1)


class MagmaRager(MinionCard):
    def __init__(self):
        super().__init__("Magma Rager", 3, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(5, 1)


class DireWolfAlpha(MinionCard):
    def __init__(self):
        super().__init__("Dire Wolf Alpha", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(2, 2, auras=[Aura(ChangeAttack(1), MinionSelector(Adjacent()))])


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
        return Minion(1, 4, spell_damage=1)


class Malygos(MinionCard):
    def __init__(self):
        super().__init__("Malygos", 9, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, minion_type=MINION_TYPE.DRAGON)

    def create_minion(self, player):
        return Minion(4, 12, spell_damage=5)


class AzureDrake(MinionCard):
    def __init__(self):
        super().__init__("Azure Drake", 5, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, minion_type=MINION_TYPE.DRAGON,
                         battlecry=Battlecry(Draw(), PlayerSelector()))

    def create_minion(self, player):
        return Minion(4, 4, spell_damage=1)


class OgreMagi(MinionCard):
    def __init__(self):
        super().__init__("Ogre Magi", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(4, 4, spell_damage=1)


class Spellbreaker(MinionCard):
    def __init__(self):
        super().__init__("Spellbreaker", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.NONE,
                         battlecry=Battlecry(Silence(), MinionSelector(players=BothPlayer(), picker=UserPicker())))

    def create_minion(self, player):
        return Minion(4, 3)


class BloodmageThalnos(MinionCard):
    def __init__(self):
        super().__init__("Bloodmage Thalnos", 2, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(1, 1, spell_damage=1, deathrattle=Deathrattle(Draw(), PlayerSelector()))


class LootHoarder(MinionCard):
    def __init__(self):
        super().__init__("Loot Hoarder", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(2, 1, deathrattle=Deathrattle(Draw(), PlayerSelector()))


class LeperGnome(MinionCard):
    def __init__(self):
        super().__init__("Leper Gnome", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(2, 1, deathrattle=Deathrattle(Damage(2), HeroSelector(EnemyPlayer())))


class IronforgeRifleman(MinionCard):
    def __init__(self):
        super().__init__("Ironforge Rifleman", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.NONE,
                         battlecry=Battlecry(Damage(1), CharacterSelector(players=BothPlayer(), picker=UserPicker())))

    def create_minion(self, player):
        return Minion(2, 2)


class GnomishInventor(MinionCard):
    def __init__(self):
        super().__init__("Gnomish Inventor", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Draw(), PlayerSelector()))

    def create_minion(self, player):
        return Minion(2, 4)


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
        super().__init__("Ironfur Grizzly", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(3, 3, taunt=True)


class LordOfTheArena(MinionCard):
    def __init__(self):
        super().__init__("Lord of the Arena", 6, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(6, 5, taunt=True)


class MurlocRaider(MinionCard):
    def __init__(self):
        super().__init__("Murloc Raider", 1, CHARACTER_CLASS.ALL, CARD_RARITY.FREE, minion_type=MINION_TYPE.MURLOC)

    def create_minion(self, player):
        return Minion(2, 1)


class ManaAddict(MinionCard):
    def __init__(self):
        super().__init__("Mana Addict", 2, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(1, 3, effects=[Effect(SpellCast(), ActionTag(Give(BuffUntil(ChangeAttack(2), TurnEnded())),
                                            SelfSelector()))])


class OasisSnapjaw(MinionCard):
    def __init__(self):
        super().__init__("Oasis Snapjaw", 4, CHARACTER_CLASS.ALL, CARD_RARITY.FREE, minion_type=MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(2, 7)


class RecklessRocketeer(MinionCard):
    def __init__(self):
        super().__init__("Reckless Rocketeer", 6, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(5, 2, charge=True)


class RiverCrocolisk(MinionCard):
    def __init__(self):
        super().__init__("River Crocolisk", 2, CHARACTER_CLASS.ALL, CARD_RARITY.FREE, minion_type=MINION_TYPE.BEAST)

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
        super().__init__("Silverback Patriarch", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         minion_type=MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(1, 4, taunt=True)


class JunglePanther(MinionCard):
    def __init__(self):
        super().__init__("Jungle Panther", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.BEAST)

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
                         battlecry=Battlecry(Damage(2), CharacterSelector(players=BothPlayer(), picker=UserPicker())))

    def create_minion(self, player):
        return Minion(4, 2)


class StormwindKnight(MinionCard):
    def __init__(self):
        super().__init__("Stormwind Knight", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(2, 5, charge=True)


class StranglethornTiger(MinionCard):
    def __init__(self):
        super().__init__("Stranglethorn Tiger", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         minion_type=MINION_TYPE.BEAST)

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
        super().__init__("Young Dragonhawk", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.BEAST)

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
        super().__init__("Core Hound", 7, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(9, 5)


class VoodooDoctor(MinionCard):
    def __init__(self):
        super().__init__("Voodoo Doctor", 1, CHARACTER_CLASS.ALL, CARD_RARITY.FREE,
                         battlecry=Battlecry(Heal(2), CharacterSelector(players=BothPlayer(), picker=UserPicker())))

    def create_minion(self, player):
        return Minion(2, 1)


class EarthenRingFarseer(MinionCard):
    def __init__(self):
        super().__init__("Earthen Ring Farseer", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Heal(3), CharacterSelector(players=BothPlayer(), picker=UserPicker())))

    def create_minion(self, player):
        return Minion(3, 3)


class ArcaneGolem(MinionCard):
    def __init__(self):
        super().__init__("Arcane Golem", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE,
                         battlecry=Battlecry(GiveManaCrystal(), PlayerSelector(players=EnemyPlayer())))

    def create_minion(self, player):
        return Minion(4, 2, charge=True)


class PriestessOfElune(MinionCard):
    def __init__(self):
        super().__init__("Priestess of Elune", 6, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Heal(4), HeroSelector()))

    def create_minion(self, player):
        return Minion(5, 4)


class DarkscaleHealer(MinionCard):
    def __init__(self):
        super().__init__("Darkscale Healer", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Heal(2), CharacterSelector()))

    def create_minion(self, player):
        return Minion(4, 5)


class ArgentCommander(MinionCard):
    def __init__(self):
        super().__init__("Argent Commander", 6, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(4, 2, divine_shield=True, charge=True)


class BluegillWarrior(MinionCard):
    def __init__(self):
        super().__init__("Bluegill Warrior", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.MURLOC)

    def create_minion(self, player):
        return Minion(2, 1, charge=True)


class Wisp(MinionCard):
    def __init__(self):
        super().__init__("Wisp", 0, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(1, 1)


class Nightblade(MinionCard):
    def __init__(self):
        super().__init__("Nightblade", 5, CHARACTER_CLASS.ALL, CARD_RARITY.FREE,
                         battlecry=Battlecry(Damage(3), HeroSelector(EnemyPlayer())))

    def create_minion(self, player):
        return Minion(4, 4)


class ShatteredSunCleric(MinionCard):
    def __init__(self):
        super().__init__("Shattered Sun Cleric", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Give([Buff(ChangeAttack(1)), Buff(ChangeHealth(1))]),
                                             MinionSelector(picker=UserPicker())))

    def create_minion(self, player):
        return Minion(3, 2)


class TheBlackKnight(MinionCard):
    def __init__(self):
        super().__init__("The Black Knight", 6, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY,
                         battlecry=Battlecry(Kill(), MinionSelector(HasStatus("taunt"), EnemyPlayer(), UserPicker())))

    def create_minion(self, player):
        return Minion(4, 5)


class AbusiveSergeant(MinionCard):
    def __init__(self):
        super().__init__("Abusive Sergeant", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Give(BuffUntil(ChangeAttack(2), TurnEnded(player=CurrentPlayer()))),
                                             MinionSelector(players=BothPlayer(), picker=UserPicker())))

    def create_minion(self, player):
        return Minion(2, 1)


class DarkIronDwarf(MinionCard):
    def __init__(self):
        super().__init__("Dark Iron Dwarf", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Give(BuffUntil(ChangeAttack(2), TurnEnded(player=CurrentPlayer()))),
                                             MinionSelector(players=BothPlayer(), picker=UserPicker())))

    def create_minion(self, player):
        return Minion(4, 4)


class Abomination(MinionCard):
    def __init__(self):
        super().__init__("Abomination", 5, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(4, 4, deathrattle=Deathrattle(Damage(2), CharacterSelector(players=BothPlayer())), taunt=True)


class FenCreeper(MinionCard):
    def __init__(self):
        super().__init__("Fen Creeper", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(3, 6, taunt=True)


class VentureCoMercenary(MinionCard):
    def __init__(self):
        super().__init__("Venture Co. Mercenary", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(7, 6, auras=[Aura(ManaChange(3), CardSelector(condition=IsMinion()))])


class AmaniBerserker(MinionCard):
    def __init__(self):
        super().__init__("Amani Berserker", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(2, 3, enrage=[Aura(ChangeAttack(3), SelfSelector())])


class Squire(MinionCard):
    def __init__(self):
        super().__init__("Squire", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False)

    def create_minion(self, player):
        return Minion(2, 2)


class SilverHandKnight(MinionCard):
    def __init__(self):
        super().__init__("Silver Hand Knight", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Summon(Squire()), PlayerSelector()))

    def create_minion(self, player):
        return Minion(4, 4)


class StormwindChampion(MinionCard):
    def __init__(self):
        super().__init__("Stormwind Champion", 7, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(6, 6, auras=[Aura(ChangeAttack(1), MinionSelector()), Aura(ChangeHealth(1), MinionSelector())])


class Deathwing(MinionCard):
    def __init__(self):
        super().__init__("Deathwing", 10, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, minion_type=MINION_TYPE.DRAGON,
                         battlecry=(Battlecry(Kill(), MinionSelector(players=BothPlayer())),
                                    Battlecry(Discard(amount=Count(CardSelector())), PlayerSelector())))

    def create_minion(self, player):
        return Minion(12, 12)


class Alexstrasza(MinionCard):
    def __init__(self):
        super().__init__("Alexstrasza", 9, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, minion_type=MINION_TYPE.DRAGON,
                         battlecry=Battlecry(SetHealth(15), HeroSelector(players=BothPlayer(), picker=UserPicker())))

    def create_minion(self, player):
        return Minion(8, 8)


class EmperorCobra(MinionCard):
    def __init__(self):
        super().__init__("Emperor Cobra", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, minion_type=MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(2, 3, effects=[Effect(DidDamage(), ActionTag(Kill(), TargetSelector(IsMinion())))])


class CrazedAlchemist(MinionCard):
    def __init__(self):
        super().__init__("Crazed Alchemist", 2, CHARACTER_CLASS.ALL, CARD_RARITY.RARE,
                         battlecry=Battlecry(SwapStats('health', 'attack', False), MinionSelector(players=BothPlayer(),
                                                                                                  picker=UserPicker())))

    def create_minion(self, player):
        return Minion(2, 2)


class AcidicSwampOoze(MinionCard):
    def __init__(self):
        super().__init__("Acidic Swamp Ooze", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Destroy(), WeaponSelector(EnemyPlayer())))

    def create_minion(self, player):
        return Minion(3, 2)


class AncientBrewmaster(MinionCard):
    def __init__(self):
        super().__init__("Ancient Brewmaster", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Bounce(), MinionSelector(picker=UserPicker())))

    def create_minion(self, player):
        return Minion(5, 4)


class YouthfulBrewmaster(MinionCard):
    def __init__(self):
        super().__init__("Youthful Brewmaster", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Bounce(), MinionSelector(picker=UserPicker())))

    def create_minion(self, player):
        return Minion(3, 2)


class BaronGeddon(MinionCard):
    def __init__(self):
        super().__init__("Baron Geddon", 7, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(7, 5, effects=[Effect(TurnEnded(), ActionTag(Damage(2),
                                                                   CharacterSelector(players=BothPlayer())))])


class AngryChicken(MinionCard):
    def __init__(self):
        super().__init__("Angry Chicken", 1, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, minion_type=MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(1, 1, enrage=[Aura(ChangeAttack(5), SelfSelector())])


class RagingWorgen(MinionCard):
    def __init__(self):
        super().__init__("Raging Worgen", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(3, 3, enrage=[Aura(ChangeAttack(1), SelfSelector()), Aura(Windfury(), SelfSelector())])


class TaurenWarrior(MinionCard):
    def __init__(self):
        super().__init__("Tauren Warrior", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(2, 3, taunt=True, enrage=[Aura(ChangeAttack(3), SelfSelector())])


class SpitefulSmith(MinionCard):
    def __init__(self):
        super().__init__("Spiteful Smith", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(4, 6, enrage=[Aura(ChangeAttack(2), WeaponSelector())])


class BloodKnight(MinionCard):
    def __init__(self):
        super().__init__("Blood Knight", 3, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC,
                         battlecry=(Battlecry([Give([Buff(ChangeAttack(Count(MinionSelector(HasDivineShield(),
                                                                                            BothPlayer())), 3)),
                                                     Buff(ChangeHealth(Count(MinionSelector(HasDivineShield(),
                                                                                            BothPlayer())), 3))])],
                                              SelfSelector()),
                                    Battlecry(RemoveDivineShields(),
                                              (MinionSelector(HasDivineShield(), BothPlayer())))))

    def create_minion(self, player):
        return Minion(3, 3)


class FrostwolfWarlord(MinionCard):
    def __init__(self):
        super().__init__("Frostwolf Warlord", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Give([Buff(ChangeAttack(Count(MinionSelector()))),
                                                   Buff(ChangeHealth(Count(MinionSelector())))]),
                                             SelfSelector()))

    def create_minion(self, player):
        return Minion(4, 4)


class RaidLeader(MinionCard):
    def __init__(self):
        super().__init__("Raid Leader", 3, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(2, 2, auras=[Aura(ChangeAttack(1), MinionSelector())])


class MechanicalDragonling(MinionCard):
    def __init__(self):
        super().__init__("Mechanical Dragonling", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False,
                         minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(2, 1)


class DragonlingMechanic(MinionCard):
    def __init__(self):
        super().__init__("Dragonling Mechanic", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Summon(MechanicalDragonling()), PlayerSelector()))

    def create_minion(self, player):
        return Minion(2, 4)


class MurlocScout(MinionCard):
    def __init__(self):
        super().__init__("Murloc Scout", 0, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False,
                         minion_type=MINION_TYPE.MURLOC)

    def create_minion(self, player):
        return Minion(1, 1)


class MurlocTidehunter(MinionCard):
    def __init__(self):
        super().__init__("Murloc Tidehunter", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         minion_type=MINION_TYPE.MURLOC, battlecry=Battlecry(Summon(MurlocScout()), PlayerSelector()))

    def create_minion(self, player):
        return Minion(2, 1)


class Boar(MinionCard):
    def __init__(self):
        super().__init__("Boar", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False, minion_type=MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(1, 1)


class RazorfenHunter(MinionCard):
    def __init__(self):
        super().__init__("Razorfen Hunter", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Summon(Boar()), PlayerSelector()))

    def create_minion(self, player):
        return Minion(2, 3)


class KnifeJuggler(MinionCard):
    def __init__(self):
        super().__init__("Knife Juggler", 2, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(3, 2, effects=[Effect(AfterAdded(), ActionTag(Damage(1),
                                            CharacterSelector(players=EnemyPlayer(),
                                                              picker=RandomPicker(),
                                                              condition=None)))])


class BaineBloodhoof(MinionCard):
    def __init__(self):
        super().__init__("Baine Bloodhoof", 4, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, False)

    def create_minion(self, player):
        return Minion(4, 5)


class CairneBloodhoof(MinionCard):
    def __init__(self):
        super().__init__("Cairne Bloodhoof", 6, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(4, 5, deathrattle=Deathrattle(Summon(BaineBloodhoof()), PlayerSelector()))


class DamagedGolem(MinionCard):
    def __init__(self):
        super().__init__("Damaged Golem", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False,
                         minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(2, 1)


class HarvestGolem(MinionCard):
    def __init__(self):
        super().__init__("Harvest Golem", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(2, 3, deathrattle=Deathrattle(Summon(DamagedGolem()), PlayerSelector()))


class FinkleEinhorn(MinionCard):
    def __init__(self):
        super().__init__("Finkle Einhorn", 2, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, False)

    def create_minion(self, player):
        return Minion(3, 3)


class TheBeast(MinionCard):
    def __init__(self):
        super().__init__("The Beast", 6, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, minion_type=MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(9, 7, deathrattle=Deathrattle(Summon(FinkleEinhorn()), PlayerSelector(EnemyPlayer())))


class SylvanasWindrunner(MinionCard):
    def __init__(self):
        super().__init__("Sylvanas Windrunner", 6, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(5, 5, deathrattle=Deathrattle(Steal(), MinionSelector(players=EnemyPlayer(),
                                                                            picker=RandomPicker())))


class StampedingKodo(MinionCard):
    def __init__(self):
        super().__init__("Stampeding Kodo", 5, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, minion_type=MINION_TYPE.BEAST,
                         battlecry=Battlecry(Kill(), MinionSelector(AttackLessThanOrEqualTo(2), EnemyPlayer(),
                                                                    RandomPicker())))

    def create_minion(self, player):
        return Minion(3, 5)


class FrostElemental(MinionCard):
    def __init__(self):
        super().__init__("Frost Elemental", 6, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Give(Frozen()), CharacterSelector(players=BothPlayer(),
                                                                               picker=UserPicker())))

    def create_minion(self, player):
        return Minion(5, 5)


class Demolisher(MinionCard):
    def __init__(self):
        super().__init__("Demolisher", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(1, 4, effects=[Effect(TurnStarted(), ActionTag(Damage(2),
                                            CharacterSelector(players=EnemyPlayer(), picker=RandomPicker())))])


class Doomsayer(MinionCard):
    def __init__(self):
        super().__init__("Doomsayer", 2, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC)

    def create_minion(self, player):
        return Minion(0, 7, effects=[Effect(TurnStarted(), ActionTag(Kill(),
                                            MinionSelector(condition=None, players=BothPlayer())))])


class Gruul(MinionCard):
    def __init__(self):
        super().__init__("Gruul", 8, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(7, 7, effects=[Effect(TurnEnded(player=BothPlayer()), ActionTag(Give([Buff(ChangeAttack(1)),
                                                                                            Buff(ChangeHealth(1))]),
                                                                                      SelfSelector()))])


class Gnoll(MinionCard):
    def __init__(self):
        super().__init__("Gnoll", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False)

    def create_minion(self, player):
        return Minion(2, 2, taunt=True)


class Hogger(MinionCard):
    def __init__(self):
        super().__init__("Hogger", 6, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(4, 4, effects=[Effect(TurnEnded(), ActionTag(Summon(Gnoll()), PlayerSelector()))])


class Imp(MinionCard):
    def __init__(self):
        super().__init__("Imp", 1, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, False, minion_type=MINION_TYPE.DEMON)

    def create_minion(self, player):
        return Minion(1, 1)


class ImpMaster(MinionCard):
    def __init__(self):
        super().__init__("Imp Master", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(1, 5, effects=[Effect(TurnEnded(), ActionTag(Damage(1), SelfSelector())),
                                     Effect(TurnEnded(), ActionTag(Summon(Imp()), PlayerSelector()))])


class InjuredBlademaster(MinionCard):
    def __init__(self):
        super().__init__("Injured Blademaster", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE,
                         battlecry=Battlecry(Damage(4), SelfSelector()))

    def create_minion(self, player):
        return Minion(4, 7)


class MasterSwordsmith(MinionCard):
    def __init__(self):
        super().__init__("Master Swordsmith", 2, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(1, 3, effects=[Effect(TurnEnded(), ActionTag(Give(ChangeAttack(1)),
                                                                   MinionSelector(picker=RandomPicker())))])


class NatPagle(MinionCard):
    def __init__(self):
        super().__init__("Nat Pagle", 2, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(0, 4, effects=[Effect(TurnStarted(), ActionTag(Draw(), PlayerSelector(), OneIn(2)))])


class Nozdormu(MinionCard):
    def __init__(self):
        super().__init__("Nozdormu", 9, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, minion_type=MINION_TYPE.DRAGON)

    def create_minion(self, player):             # Strictly worse than Alexstrasza
        return Minion(8, 8)                      # Is the effect even applicable to AI?


class RagnarosTheFirelord(MinionCard):
    def __init__(self):
        super().__init__("Ragnaros the Firelord", 8, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(8, 8, effects=[Effect(TurnEnded(), ActionTag(Damage(8),
                                            CharacterSelector(players=EnemyPlayer(), picker=RandomPicker())))],
                      buffs=[Buff(CantAttack())])


class AncientWatcher(MinionCard):
    def __init__(self):
        super().__init__("Ancient Watcher", 2, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(4, 5, buffs=[Buff(CantAttack())])


class ColdlightOracle(MinionCard):
    def __init__(self):
        super().__init__("Coldlight Oracle", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, minion_type=MINION_TYPE.MURLOC,
                         battlecry=Battlecry(Draw(2), PlayerSelector(players=BothPlayer())))

    def create_minion(self, player):
        return Minion(2, 2)


class ColdlightSeer(MinionCard):
    def __init__(self):
        super().__init__("Coldlight Seer", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, minion_type=MINION_TYPE.MURLOC,
                         battlecry=Battlecry(Give(ChangeHealth(2)),
                                             MinionSelector(IsType(MINION_TYPE.MURLOC), BothPlayer())))

    def create_minion(self, player):
        return Minion(2, 3)


class GrimscaleOracle(MinionCard):
    def __init__(self):
        super().__init__("Grimscale Oracle", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.MURLOC)

    def create_minion(self, player):
        return Minion(1, 1, auras=[Aura(ChangeAttack(1),
                                        MinionSelector(IsType(MINION_TYPE.MURLOC), BothPlayer()))])


class MurlocWarleader(MinionCard):
    def __init__(self):
        super().__init__("Murloc Warleader", 3, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC, minion_type=MINION_TYPE.MURLOC)

    def create_minion(self, player):
        return Minion(3, 3, auras=[Aura(ChangeAttack(2),
                                        MinionSelector(IsType(MINION_TYPE.MURLOC), BothPlayer())),
                                   Aura(ChangeHealth(1),
                                        MinionSelector(IsType(MINION_TYPE.MURLOC), BothPlayer()))])


class BigGameHunter(MinionCard):
    def __init__(self):
        super().__init__("Big Game Hunter", 3, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC,
                         battlecry=Battlecry(Kill(), MinionSelector(AttackGreaterThan(6), BothPlayer())))

    def create_minion(self, player):
        return Minion(4, 2)


class BloodsailCorsair(MinionCard):
    def __init__(self):
        super().__init__("Bloodsail Corsair", 1, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, minion_type=MINION_TYPE.PIRATE,
                         battlecry=Battlecry(DecreaseDurability(), HeroSelector(EnemyPlayer())))

    def create_minion(self, player):
        return Minion(1, 2)


class BloodsailRaider(MinionCard):
    def __init__(self):
        super().__init__("Bloodsail Raider", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.PIRATE,
                         battlecry=Battlecry(Give(Buff(ChangeAttack(Attribute("base_attack", WeaponSelector())))),
                                             SelfSelector()))

    def create_minion(self, player):
        return Minion(2, 3)


class CaptainGreenskin(MinionCard):
    def __init__(self):
        super().__init__("Captain Greenskin", 5, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY,
                         minion_type=MINION_TYPE.PIRATE,
                         battlecry=Battlecry([IncreaseWeaponAttack(1), IncreaseDurability()], HeroSelector()))

    def create_minion(self, player):
        return Minion(5, 4)


class HungryCrab(MinionCard):
    def __init__(self):
        super().__init__("Hungry Crab", 1, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC, minion_type=MINION_TYPE.BEAST,
                         battlecry=(Battlecry(Kill(), MinionSelector(IsType(MINION_TYPE.MURLOC), BothPlayer())),
                                    Battlecry(Give([Buff(ChangeAttack(2)), Buff(ChangeHealth(2))]), SelfSelector())))

    def create_minion(self, player):
        return Minion(1, 2)


class MadBomber(MinionCard):
    def __init__(self):
        super().__init__("Mad Bomber", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Damage(1), CharacterSelector(players=BothPlayer(),
                                                                          picker=RandomPicker(3))))

    def create_minion(self, player):
        return Minion(3, 2)


class ManaWraith(MinionCard):
    def __init__(self):
        super().__init__("Mana Wraith", 2, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(2, 2, auras=[Aura(ManaChange(1), CardSelector(BothPlayer(), IsMinion()))])


class MindControlTech(MinionCard):
    def __init__(self):
        super().__init__("Mind Control Tech", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE,
                         battlecry=Battlecry(Steal(),
                                             MinionSelector(players=EnemyPlayer(), condition=None,
                                                            picker=RandomPicker()), OpponentMinionCountIsGreaterThan(3))
                         )

    def create_minion(self, player):
        return Minion(3, 3)


class MurlocTidecaller(MinionCard):
    def __init__(self):
        super().__init__("Murloc Tidecaller", 1, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, minion_type=MINION_TYPE.MURLOC)

    def create_minion(self, player):
        return Minion(1, 2, effects=[(Effect(MinionSummoned(IsType(MINION_TYPE.MURLOC), player=BothPlayer()),
                                             ActionTag(Give(ChangeAttack(1)), SelfSelector())))])


class Onyxia(MinionCard):
    def __init__(self):
        super().__init__("Onyxia", 9, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, minion_type=MINION_TYPE.DRAGON,
                         battlecry=Battlecry(Summon(Whelp(), 6), PlayerSelector()))

    def create_minion(self, player):
        return Minion(8, 8)


class Whelp(MinionCard):
    def __init__(self):
        super().__init__("Whelp", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False, minion_type=MINION_TYPE.DRAGON)

    def create_minion(self, player):
        return Minion(1, 1)


class SouthseaCaptain(MinionCard):
    def __init__(self):
        super().__init__("Southsea Captain", 3, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC, minion_type=MINION_TYPE.PIRATE)

    def create_minion(self, player):
        return Minion(3, 3, auras=[Aura(ChangeAttack(1), MinionSelector(IsType(MINION_TYPE.PIRATE))),
                                   Aura(ChangeHealth(1), MinionSelector(IsType(MINION_TYPE.PIRATE)))])


class SouthseaDeckhand(MinionCard):
    def __init__(self):
        super().__init__("Southsea Deckhand", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         minion_type=MINION_TYPE.PIRATE)

    def create_minion(self, player):
        return Minion(2, 1, buffs=[Buff(Charge(), GreaterThan(Count(WeaponSelector()), value=0))])


class YoungPriestess(MinionCard):
    def __init__(self):
        super().__init__("Young Priestess", 1, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(2, 1, effects=[Effect(TurnEnded(), ActionTag(Give(ChangeHealth(1)),
                                                                   MinionSelector(picker=RandomPicker())))])


class AcolyteOfPain(MinionCard):
    def __init__(self):
        super().__init__("Acolyte of Pain", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(1, 3, effects=[Effect(Damaged(), ActionTag(Draw(), PlayerSelector()))])


class CultMaster(MinionCard):
    def __init__(self):
        super().__init__("Cult Master", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(4, 2, effects=[Effect(MinionDied(), ActionTag(Draw(), PlayerSelector()))])


class Secretkeeper(MinionCard):
    def __init__(self):
        super().__init__("Secretkeeper", 1, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(1, 2, effects=[Effect(SpellCast(IsSecret(), BothPlayer()),
                                            ActionTag(Give([Buff(ChangeAttack(1)), Buff(ChangeHealth(1))]),
                                                      SelfSelector()))])


class VioletApprentice(MinionCard):
    def __init__(self):
        super().__init__("Violet Apprentice", 0, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False)

    def create_minion(self, player):
        return Minion(1, 1)


class VioletTeacher(MinionCard):
    def __init__(self):
        super().__init__("Violet Teacher", 4, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(3, 5, effects=[Effect(SpellCast(), ActionTag(Summon(VioletApprentice()), PlayerSelector()))])


class GadgetzanAuctioneer(MinionCard):
    def __init__(self):
        super().__init__("Gadgetzan Auctioneer", 6, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(4, 4, effects=[Effect(SpellCast(), ActionTag(Draw(), PlayerSelector()))])


class FlameOfAzzinoth(MinionCard):
    def __init__(self):
        super().__init__("Flame of Azzinoth", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False)

    def create_minion(self, player):
        return Minion(2, 1)


class IllidanStormrage(MinionCard):
    def __init__(self):
        super().__init__("Illidan Stormrage", 6, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY,
                         minion_type=MINION_TYPE.DEMON)

    def create_minion(self, player):
        return Minion(7, 5, effects=[Effect(CardPlayed(), ActionTag(Summon(FlameOfAzzinoth()), PlayerSelector()))])


class FlesheatingGhoul(MinionCard):
    def __init__(self):
        super().__init__("Flesheating Ghoul", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(2, 3, effects=[Effect(MinionDied(player=BothPlayer()), ActionTag(Give(ChangeAttack(1)),
                                                                                       SelfSelector()))])


class Lightwarden(MinionCard):
    def __init__(self):
        super().__init__("Lightwarden", 1, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(1, 2, effects=[Effect(CharacterHealed(player=BothPlayer()),
                                            ActionTag(Give(ChangeAttack(2)), SelfSelector()))])


class QuestingAdventurer(MinionCard):
    def __init__(self):
        super().__init__("Questing Adventurer", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(2, 2, effects=[Effect(CardPlayed(), ActionTag(Give([Buff(ChangeAttack(1)),
                                                                          Buff(ChangeHealth(1))]), SelfSelector()))])


class GurubashiBerserker(MinionCard):
    def __init__(self):
        super().__init__("Gurubashi Berserker", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(2, 7, effects=[
            Effect(CharacterDamaged(condition=MinionIsTarget()), ActionTag(Give(ChangeAttack(3)), SelfSelector()))])


class AncientMage(MinionCard):
    def __init__(self):
        super().__init__("Ancient Mage", 4, CHARACTER_CLASS.ALL, CARD_RARITY.RARE,
                         battlecry=Battlecry(Give(SpellDamage(1)), MinionSelector(condition=Adjacent())))

    def create_minion(self, player):
        return Minion(2, 5)


class DefenderOfArgus(MinionCard):
    def __init__(self):
        super().__init__("Defender of Argus", 4, CHARACTER_CLASS.ALL, CARD_RARITY.RARE,
                         battlecry=Battlecry(Give([
                             Buff(Taunt()),
                             Buff(ChangeAttack(1)),
                             Buff(ChangeHealth(1))
                         ]), MinionSelector(Adjacent())))

    def create_minion(self, player):
        return Minion(2, 3)


class SunfuryProtector(MinionCard):
    def __init__(self):
        super().__init__("Sunfury Protector", 2, CHARACTER_CLASS.ALL, CARD_RARITY.RARE,
                         battlecry=Battlecry(Give(Buff(Taunt())), MinionSelector(Adjacent())))

    def create_minion(self, player):
        return Minion(2, 3)


class HarrisonJones(MinionCard):
    def __init__(self):
        super().__init__("Harrison Jones", 5, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY,
                         battlecry=(Battlecry(Draw(Attribute("durability", WeaponSelector(EnemyPlayer()))),
                                              PlayerSelector()),
                                    Battlecry(Destroy(), WeaponSelector(EnemyPlayer()))))

    def create_minion(self, player):
        return Minion(5, 4)


class Bananas(SpellCard):
    def __init__(self):
        super().__init__("Bananas", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.change_attack(1)
        self.target.increase_health(1)


class KingMukla(MinionCard):
    def __init__(self):
        super().__init__("King Mukla", 3, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, minion_type=MINION_TYPE.BEAST,
                         battlecry=Battlecry(AddCard(Bananas(), 2), PlayerSelector(EnemyPlayer())))

    def create_minion(self, player):
        return Minion(5, 5)


class LeeroyJenkins(MinionCard):
    def __init__(self):
        super().__init__("Leeroy Jenkins", 5, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY,
                         battlecry=Battlecry(Summon(Whelp(), 2), PlayerSelector(players=EnemyPlayer())))

    def create_minion(self, player):
        return Minion(6, 2, charge=True)


class MountainGiant(MinionCard):
    def __init__(self):
        super().__init__("Mountain Giant", 12, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC,
                         buffs=[Buff(ManaChange(Count(CardSelector()), -1))])

    def create_minion(self, player):
        return Minion(8, 8)


class MoltenGiant(MinionCard):
    def __init__(self):
        super().__init__("Molten Giant", 20, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC,
                         buffs=[Buff(ManaChange(Attribute("damage", HeroSelector()), -1))])

    def create_minion(self, player):
        return Minion(8, 8)


class SeaGiant(MinionCard):
    def __init__(self):
        super().__init__("Sea Giant", 10, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC,
                         buffs=[Buff(ManaChange(Count(MinionSelector(None, BothPlayer())), -1))])

    def create_minion(self, player):
        return Minion(8, 8)


class DreadCorsair(MinionCard):
    def __init__(self):
        super().__init__("Dread Corsair", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.PIRATE,
                         buffs=[Buff(ManaChange(Attribute("attack", WeaponSelector()), -1))])

    def create_minion(self, player):
        return Minion(3, 3, taunt=True)


class CaptainsParrot(MinionCard):
    def __init__(self):
        super().__init__("Captain's Parrot", 2, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC, minion_type=MINION_TYPE.BEAST,
                         battlecry=Battlecry(AddCard(CardQuery(conditions=[IsType(MINION_TYPE.PIRATE)],
                                                               source=CARD_SOURCE.MY_DECK)), PlayerSelector()))

    def create_minion(self, player):
        return Minion(1, 1)


class TinkmasterOverspark(MinionCard):
    def __init__(self):
        super().__init__("Tinkmaster Overspark", 3, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY,
                         battlecry=Battlecry(Transform(CardQuery(source=CARD_SOURCE.LIST,
                                                                 source_list=[Devilsaur(), Squirrel()])),
                                             MinionSelector(players=BothPlayer(), picker=RandomPicker())))

    def create_minion(self, player):
        return Minion(3, 3)


class Squirrel(MinionCard):
    def __init__(self):
        super().__init__("Squirrel", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False, minion_type=MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(1, 1)


class Devilsaur(MinionCard):
    def __init__(self):
        super().__init__("Devilsaur", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False, minion_type=MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(5, 5)


class AlarmoBot(MinionCard):
    def __init__(self):
        super().__init__("Alarm-o-Bot", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(0, 3, effects=[Effect(TurnStarted(), ActionTag(SwapWithHand(), PlayerSelector()))])


class IAmMurloc(SpellCard):
    def __init__(self):
        super().__init__("I Am Murloc", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False)

    def use(self, player, game):
        super().use(player, game)

        for i in range(0, player.game.random_amount(3, 5)):
            Murloc().summon(player, player.game, len(player.minions))

    def can_use(self, player, game):
        return super().can_use(player, game) and len(player.minions) < 7


class PowerOfTheHorde(SpellCard):
    def __init__(self):
        super().__init__("Power of the Horde", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False)

    def use(self, player, game):
        super().use(player, game)

        horde_list = [FrostwolfGrunt(), TaurenWarrior(), ThrallmarFarseer(),
                      SilvermoonGuardian(), SenjinShieldmasta(), CairneBloodhoof()]
        horde_summon = game.random_choice(horde_list)
        horde_summon.summon(player, player.game, len(player.minions))

    def can_use(self, player, game):
        return super().can_use(player, game) and len(player.minions) < 7


class RoguesDoIt(SpellCard):
    def __init__(self):
        super().__init__("Rogues Do It...", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False,
                         hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.damage(player.effective_spell_damage(4), self)
        player.draw()


class EliteTaurenChieftain(MinionCard):
    def __init__(self):
        super().__init__("Elite Tauren Chieftain", 5, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY,
                         battlecry=Battlecry(AddCard(CardQuery(source=CARD_SOURCE.LIST,
                                                               source_list=[IAmMurloc(),
                                                                            PowerOfTheHorde(),
                                                                            RoguesDoIt()])),
                                             PlayerSelector(BothPlayer())))

    def create_minion(self, player):
        return Minion(5, 5)


class Murloc(MinionCard):
    def __init__(self):
        super().__init__("Murloc", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False, minion_type=MINION_TYPE.MURLOC)

    def create_minion(self, p):
        return Minion(1, 1)


class MillhouseManastorm(MinionCard):
    def __init__(self):
        super().__init__("Millhouse Manastorm", 2, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY,
                         battlecry=Battlecry(GiveAura(AuraUntil(ManaChange(-100), CardSelector(condition=IsSpell()),
                                                                TurnEnded())),
                                             PlayerSelector(players=EnemyPlayer())))

    def create_minion(self, player):
        return Minion(4, 4)


class PintSizedSummoner(MinionCard):
    def __init__(self):
        super().__init__("Pint-Sized Summoner", 2, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(2, 2, effects=[Effect(TurnStarted(), ActionTag(GiveAura(AuraUntil(ManaChange(-1),
                                                                                        CardSelector(
                                                                                            condition=IsMinion()),
                                                                              MinionPlaced())),
                                            PlayerSelector()))])


class OldMurkEye(MinionCard):
    def __init__(self):
        super().__init__("Old Murk-Eye", 4, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, minion_type=MINION_TYPE.MURLOC)

    def create_minion(self, player):
        return Minion(2, 4, charge=True, buffs=[Buff(ChangeAttack(Count(MinionSelector(IsType(MINION_TYPE.MURLOC),
                                                                                       BothPlayer()))))])


class Dream(SpellCard):
    def __init__(self):
        super().__init__("Dream", 0, CHARACTER_CLASS.DREAM, CARD_RARITY.COMMON, False,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.bounce()


class YseraAwakens(SpellCard):
    def __init__(self):
        super().__init__("Ysera Awakens", 2, CHARACTER_CLASS.DREAM, CARD_RARITY.COMMON, False)

    def use(self, player, game):
        super().use(player, game)
        targets = copy.copy(player.game.other_player.minions)
        targets.extend(player.game.current_player.minions)
        targets.append(player.game.other_player.hero)
        targets.append(player.game.current_player.hero)
        targets = filter(lambda m: not m.is_minion() or m.card.name != "Ysera", targets)
        for minion in targets:
            minion.damage(player.effective_spell_damage(5), self)


class Nightmare(SpellCard):
    def __init__(self):
        super().__init__("Nightmare", 0, CHARACTER_CLASS.DREAM, CARD_RARITY.COMMON, False,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.add_buff(Buff(ChangeAttack(5)))
        self.target.add_buff(Buff(ChangeHealth(5)))
        self.target.add_effect(Effect(TurnStarted(player=CurrentPlayer()), ActionTag(Kill(), SelfSelector())))


class LaughingSister(MinionCard):
    def __init__(self):
        super().__init__("Laughing Sister", 3, CHARACTER_CLASS.DREAM, CARD_RARITY.COMMON, False)

    def create_minion(self, player):
        return Minion(3, 5, spell_targetable=False)


class EmeraldDrake(MinionCard):
    def __init__(self):
        super().__init__("Emerald Drake", 4, CHARACTER_CLASS.DREAM, CARD_RARITY.COMMON, False, MINION_TYPE.DRAGON)

    def create_minion(self, player):
        return Minion(7, 6)


class Ysera(MinionCard):
    def __init__(self):
        super().__init__("Ysera", 9, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, minion_type=MINION_TYPE.DRAGON)

    def create_minion(self, player):
        dream_card_list = [EmeraldDrake(), LaughingSister(), Nightmare(), YseraAwakens(), Dream()]
        return Minion(4, 12, effects=[Effect(TurnEnded(),
                                             ActionTag(AddCard(CardQuery(source=CARD_SOURCE.LIST,
                                                                         source_list=dream_card_list)),
                                             PlayerSelector()))])


class Chicken(MinionCard):
    def __init__(self):
        super().__init__("Chicken", 0, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False,
                         MINION_TYPE.BEAST)

    def create_minion(self, p):
        return Minion(1, 1)


class GelbinMekkatorque(MinionCard):
    def __init__(self):
        super().__init__("Gelbin Mekkatorque", 6, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY,
                         battlecry=Battlecry(Summon(CardQuery(source=CARD_SOURCE.LIST,
                                                              source_list=[Emboldener3000(),
                                                                           HomingChicken(),
                                                                           Poultryizer(),
                                                                           RepairBot()])), PlayerSelector()))

    def create_minion(self, player):
        return Minion(6, 6)


class Emboldener3000(MinionCard):
    def __init__(self):
        super().__init__("Emboldener 3000", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False,
                         minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(0, 4, effects=[Effect(TurnEnded(), ActionTag(Give([Buff(ChangeAttack(1)),
                                                                   Buff(ChangeHealth(1))]),
                                            MinionSelector(condition=None,
                                                           players=BothPlayer(),
                                                           picker=RandomPicker())))])


class HomingChicken(MinionCard):
    def __init__(self):
        super().__init__("Homing Chicken", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False,
                         minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(0, 1, effects=[Effect(TurnStarted(), ActionTag(Kill(), SelfSelector())),
                                     Effect(TurnStarted(), ActionTag(Draw(3), PlayerSelector()))])


class Poultryizer(MinionCard):
    def __init__(self):
        super().__init__("Poultryizer", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(0, 3, effects=[Effect(TurnStarted(), ActionTag(Transform(Chicken()),
                                            MinionSelector(None, BothPlayer(), RandomPicker())))])


class RepairBot(MinionCard):
    def __init__(self):
        super().__init__("Repair Bot", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(0, 3, effects=[Effect(TurnEnded(), ActionTag(Heal(6),
                                            CharacterSelector(IsDamaged(), BothPlayer(), RandomPicker())))])


class LorewalkerCho(MinionCard):
    def __init__(self):
        super().__init__("Lorewalker Cho", 2, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(0, 4, effects=[Effect(SpellCast(player=BothPlayer()),
                                            ActionTag(AddCard(CardQuery(source=CARD_SOURCE.LAST_CARD)),
                                            PlayerSelector(OtherPlayer())))])


class WildPyromancer(MinionCard):
    def __init__(self):
        super().__init__("Wild Pyromancer", 2, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(3, 2, effects=[Effect(CardUsed(IsSpell()), ActionTag(Damage(1),
                                                                           MinionSelector(condition=None,
                                                                                          players=BothPlayer())))])


class FacelessManipulator(MinionCard):
    def __init__(self):
        super().__init__("Faceless Manipulator", 5, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC,
                         battlecry=Battlecry(Replace(), MinionSelector(players=BothPlayer(), picker=UserPicker())))

    def create_minion(self, player):
        return Minion(3, 3)


class Nerubian(MinionCard):
    def __init__(self):
        super().__init__("Nerubian", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, False)

    def create_minion(self, p):
        return Minion(4, 4)


class NerubianEgg(MinionCard):
    def __init__(self):
        super().__init__("Nerubian Egg", 2, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(0, 2, deathrattle=Deathrattle(Summon(Nerubian()), PlayerSelector()))


class Maexxna(MinionCard):
    def __init__(self):
        super().__init__("Maexxna", 6, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, minion_type=MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(2, 8, effects=[Effect(DidDamage(), ActionTag(Kill(), TargetSelector(IsMinion())))])


class SpectralSpider(MinionCard):
    def __init__(self):
        super().__init__("Spectral Spider", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False)

    def create_minion(self, player):
        return Minion(1, 1)


class HauntedCreeper(MinionCard):
    def __init__(self):
        super().__init__("Haunted Creeper", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(1, 2, deathrattle=Deathrattle(Summon(SpectralSpider(), 2), PlayerSelector()))


class NerubarWeblord(MinionCard):
    def __init__(self):
        super().__init__("Nerub'ar Weblord", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(1, 4, auras=[Aura(ManaChange(2), CardSelector(BothPlayer(), HasBattlecry()))])


class UnstableGhoul(MinionCard):
    def __init__(self):
        super().__init__("Unstable Ghoul", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(1, 3, deathrattle=Deathrattle(Damage(1), MinionSelector(players=BothPlayer())), taunt=True)


class Loatheb(MinionCard):
    def __init__(self):
        super().__init__("Loatheb", 5, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY,
                         battlecry=Battlecry(GiveAura(AuraUntil(ManaChange(5), CardSelector(condition=IsSpell()),
                                                                TurnEnded())),
                                             PlayerSelector(players=EnemyPlayer())))

    def create_minion(self, player):
        return Minion(5, 5)


class StoneskinGargoyle(MinionCard):
    def __init__(self):
        super().__init__("Stoneskin Gargoyle", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(1, 4, effects=[Effect(TurnStarted(), ActionTag(Heal(10000), SelfSelector()))])


class Slime(MinionCard):
    def __init__(self):
        super().__init__("Slime", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False)

    def create_minion(self, p):
        return Minion(1, 2, taunt=True)


class SludgeBelcher(MinionCard):
    def __init__(self):
        super().__init__("Sludge Belcher", 5, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(3, 5, taunt=True, deathrattle=Deathrattle(Summon(Slime()), PlayerSelector()))


class BaronRivendare(MinionCard):
    def __init__(self):
        super().__init__("Baron Rivendare", 4, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(1, 7, auras=[Aura(DoubleDeathrattle(), PlayerSelector())])


class DancingSwords(MinionCard):
    def __init__(self):
        super().__init__("Dancing Swords", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(4, 4, deathrattle=Deathrattle(Draw(2), PlayerSelector(EnemyPlayer())))


class Deathlord(MinionCard):
    def __init__(self):
        super().__init__("Deathlord", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(2, 8, taunt=True, deathrattle=Deathrattle(Summon(CardQuery(conditions=[IsMinion()],
                                                                                 source=CARD_SOURCE.MY_DECK)),
                                                                PlayerSelector(EnemyPlayer())))


class SpectralKnight(MinionCard):
    def __init__(self):
        super().__init__("Spectral Knight", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(4, 6, spell_targetable=False)


class Undertaker(MinionCard):
    def __init__(self):
        super().__init__("Undertaker", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(1, 2, effects=[Effect(MinionSummoned(MinionHasDeathrattle()), ActionTag(Give(ChangeAttack(1)),
                                                                                              SelfSelector()))])


class WailingSoul(MinionCard):
    def __init__(self):
        super().__init__("Wailing Soul", 4, CHARACTER_CLASS.ALL, CARD_RARITY.RARE,
                         battlecry=Battlecry(Silence(), MinionSelector()))

    def create_minion(self, player):
        return Minion(3, 5)


class ZombieChow(MinionCard):
    def __init__(self):
        super().__init__("Zombie Chow", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(2, 3, deathrattle=Deathrattle(Heal(5), HeroSelector(EnemyPlayer())))


class Thaddius(MinionCard):
    def __init__(self):
        super().__init__("Thaddius", 10, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, False)

    def create_minion(self, player):
        return Minion(11, 11)


class Feugen(MinionCard):
    def __init__(self):
        super().__init__("Feugen", 5, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(4, 7, deathrattle=Deathrattle(Summon(Thaddius()), PlayerSelector(), InGraveyard(Stalagg())))


class Stalagg(MinionCard):
    def __init__(self):
        super().__init__("Stalagg", 5, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(7, 4, deathrattle=Deathrattle(Summon(Thaddius()), PlayerSelector(), InGraveyard(Feugen())))


class MadScientist(MinionCard):
    def __init__(self):
        super().__init__("Mad Scientist", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(2, 2, deathrattle=Deathrattle(ApplySecret(CARD_SOURCE.MY_DECK), PlayerSelector()))


class EchoingOoze(MinionCard):
    def __init__(self):
        super().__init__("Echoing Ooze", 2, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC,
                         battlecry=Battlecry(GiveEffect(Effect(TurnEnded(),
                                                               ActionTag(Duplicate(SelfSelector()), PlayerSelector()))),
                                             PlayerSelector()))

    def create_minion(self, player):
        return Minion(1, 2)


class ShadeOfNaxxramas(MinionCard):
    def __init__(self):
        super().__init__("Shade of Naxxramas", 3, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC)

    def create_minion(self, player):
        return Minion(2, 2, stealth=True, effects=[Effect(TurnStarted(), ActionTag(Give([Buff(ChangeAttack(1)),
                                                                                         Buff(ChangeHealth(1))]),
                                                                                   SelfSelector()))])


class KelThuzad(MinionCard):
    def __init__(self):
        super().__init__("Kel'Thuzad", 8, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(6, 8, effects=[Effect(TurnEnded(player=BothPlayer()), ActionTag(ResurrectFriendly(),
                                                                                      PlayerSelector()))])


class PilotedShredder(MinionCard):
    def __init__(self):
        super().__init__("Piloted Shredder", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(4, 3, deathrattle=Deathrattle(Summon(CardQuery(conditions=[ManaCost(2), IsMinion()])),
                                                    PlayerSelector()))


class PilotedSkyGolem(MinionCard):
    def __init__(self):
        super().__init__("Piloted Sky Golem", 6, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(6, 4, deathrattle=Deathrattle(Summon(CardQuery(conditions=[ManaCost(4), IsMinion()])),
                                                    PlayerSelector()))


class SneedsOldShredder(MinionCard):
    def __init__(self):
        super().__init__("Sneed's Old Shredder", 8, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY,
                         minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(5, 7, deathrattle=Deathrattle(Summon(CardQuery(conditions=[CardRarity(CARD_RARITY.LEGENDARY),
                                                                                 IsMinion()])),
                                                    PlayerSelector()))


class AntiqueHealbot(MinionCard):
    def __init__(self):
        super().__init__("Antique Healbot", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.MECH,
                         battlecry=Battlecry(Heal(8), HeroSelector()))

    def create_minion(self, player):
        return Minion(3, 3)


class AnnoyoTron(MinionCard):
    def __init__(self):
        super().__init__("Annoy-o-Tron", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(1, 2, divine_shield=True, taunt=True)


class ArcaneNullifierX21(MinionCard):
    def __init__(self):
        super().__init__("Arcane Nullifier X-21", 4, CHARACTER_CLASS.ALL, CARD_RARITY.RARE,
                         minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(2, 5, taunt=True, spell_targetable=False)


class Blingtron3000(MinionCard):
    def __init__(self):
        super().__init__("Blingtron 3000", 5, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, minion_type=MINION_TYPE.MECH,
                         battlecry=Battlecry(Equip(CardQuery(conditions=[IsWeapon()])),
                                             PlayerSelector(players=BothPlayer())))

    def create_minion(self, player):
        return Minion(3, 4)


class BombLobber(MinionCard):
    def __init__(self):
        super().__init__("Bomb Lobber", 5, CHARACTER_CLASS.ALL, CARD_RARITY.RARE,
                         battlecry=Battlecry(Damage(4), MinionSelector(None, EnemyPlayer(), RandomPicker())))

    def create_minion(self, player):
        return Minion(3, 3)


class BurlyRockjawTrogg(MinionCard):
    def __init__(self):
        super().__init__("Burly Rockjaw Trogg", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(3, 5, effects=[Effect(SpellCast(player=EnemyPlayer()), ActionTag(Give(ChangeAttack(2)),
                                                                                       SelfSelector()))])


class Mechwarper(MinionCard):
    def __init__(self):
        super().__init__("Mechwarper", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(2, 3, auras=[Aura(ManaChange(-1), CardSelector(condition=IsType(MINION_TYPE.MECH)))])


class Frog(MinionCard):
    def __init__(self):
        super().__init__("Frog", 0, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False, minion_type=MINION_TYPE.BEAST)

    def create_minion(self, p):
        return Minion(0, 1, taunt=True)


class ClockworkGiant(MinionCard):
    def __init__(self):
        super().__init__("Clockwork Giant", 12, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC, minion_type=MINION_TYPE.MECH,
                         buffs=[Buff(ManaChange(Count(CardSelector(EnemyPlayer())), -1))])

    def create_minion(self, player):
        return Minion(8, 8)


class ClockworkGnome(MinionCard):
    def __init__(self):
        super().__init__("Clockwork Gnome", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        from hearthbreaker.cards.spells.neutral import spare_part_list
        return Minion(2, 1,
                      deathrattle=Deathrattle(AddCard(CardQuery(source=CARD_SOURCE.LIST, source_list=spare_part_list)),
                                              PlayerSelector()))


class BoomBot(MinionCard):
    def __init__(self):
        super().__init__("Boom Bot", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(1, 1, deathrattle=Deathrattle(Damage(RandomAmount(1, 4)),
                                                    CharacterSelector(players=EnemyPlayer(), picker=RandomPicker())))


class DoctorBoom(MinionCard):
    def __init__(self):
        super().__init__("Dr. Boom", 7, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY,
                         battlecry=Battlecry(Summon(BoomBot(), 2), PlayerSelector()))

    def create_minion(self, player):
        return Minion(7, 7)


class TargetDummy(MinionCard):
    def __init__(self):
        super().__init__("Target Dummy", 0, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(0, 2, taunt=True)


class ExplosiveSheep(MinionCard):
    def __init__(self):
        super().__init__("Explosive Sheep", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(1, 1, deathrattle=Deathrattle(Damage(2), CharacterSelector(players=BothPlayer())), taunt=True)


class Puddlestomper(MinionCard):
    def __init__(self):
        super().__init__("Puddlestomper", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.MURLOC)

    def create_minion(self, player):
        return Minion(3, 2)


class MicroMachine(MinionCard):
    def __init__(self):
        super().__init__("Micro Machine", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(1, 2, effects=[Effect(TurnStarted(player=BothPlayer()), ActionTag(Give(ChangeAttack(1)),
                                                                                        SelfSelector()))])


class MechanicalYeti(MinionCard):
    def __init__(self):
        super().__init__("Mechanical Yeti", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        from hearthbreaker.cards.spells.neutral import spare_part_list
        return Minion(4, 5,
                      deathrattle=Deathrattle(AddCard(CardQuery(source=CARD_SOURCE.LIST, source_list=spare_part_list)),
                                              PlayerSelector(BothPlayer())))


class SpiderTank(MinionCard):
    def __init__(self):
        super().__init__("Spider Tank", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(3, 4)


class GilblinStalker(MinionCard):
    def __init__(self):
        super().__init__("Gilblin Stalker", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(2, 3, stealth=True)


class ShipsCannon(MinionCard):
    def __init__(self):
        super().__init__("Ship's Cannon", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(2, 3, effects=[Effect(MinionSummoned(IsType(MINION_TYPE.PIRATE)), ActionTag(Damage(2),
                                            CharacterSelector(None, EnemyPlayer(), RandomPicker())))])


class OgreBrute(MinionCard):
    def __init__(self):
        super().__init__("Ogre Brute", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(4, 4, effects=[Effect(Attack(), ActionTag(ChangeTarget(CharacterSelector(NotCurrentTarget(),
                                                                                               EnemyPlayer(),
                                                                                               RandomPicker())),
                                            SelfSelector(), And(OneIn(2), OpponentMinionCountIsGreaterThan(0))))])


class MogorTheOgre(MinionCard):
    def __init__(self):
        super().__init__("Mogor the Ogre", 6, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(7, 6, effects=[Effect(CharacterAttack(None, BothPlayer()), ActionTag(ChangeTarget(
            CharacterSelector(NotCurrentTarget(), EnemyPlayer(), RandomPicker())), TargetSelector(),
            And(OneIn(2), OpponentMinionCountIsGreaterThan(0))))])


class Toshley(MinionCard):
    def __init__(self):
        from hearthbreaker.cards.spells.neutral import spare_part_list
        super().__init__("Toshley", 6, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY,
                         battlecry=Battlecry(AddCard(CardQuery(source=CARD_SOURCE.LIST, source_list=spare_part_list)),
                                             PlayerSelector()))

    def create_minion(self, player):
        from hearthbreaker.cards.spells.neutral import spare_part_list
        return Minion(5, 7,
                      deathrattle=Deathrattle(AddCard(CardQuery(source=CARD_SOURCE.LIST, source_list=spare_part_list)),
                                              PlayerSelector()))


class ForceTankMAX(MinionCard):
    def __init__(self):
        super().__init__("Force-Tank MAX", 8, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(7, 7, divine_shield=True)


class FelReaver(MinionCard):
    def __init__(self):
        super().__init__("Fel Reaver", 5, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(8, 8, effects=[Effect(CardPlayed(player=EnemyPlayer()),
                                            ActionTag(Discard(3, query=CardQuery(source=CARD_SOURCE.MY_DECK)),
                                                      PlayerSelector()))])


class MadderBomber(MinionCard):
    def __init__(self):
        super().__init__("Madder Bomber", 5, CHARACTER_CLASS.ALL, CARD_RARITY.RARE,
                         battlecry=Battlecry(Damage(1), CharacterSelector(players=BothPlayer(),
                                                                          picker=RandomPicker(6))))

    def create_minion(self, player):
        return Minion(5, 4)


class Gazlowe(MinionCard):
    def __init__(self):
        super().__init__("Gazlowe", 6, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(3, 6, effects=[Effect(SpellCast(ManaCost(1)),
                                            ActionTag(AddCard(CardQuery(conditions=[IsType(MINION_TYPE.MECH)])),
                                            PlayerSelector()))])


class MiniMage(MinionCard):
    def __init__(self):
        super().__init__("Mini-Mage", 4, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC)

    def create_minion(self, player):
        return Minion(4, 1, stealth=True, spell_damage=1)


class SaltyDog(MinionCard):
    def __init__(self):
        super().__init__("Salty Dog", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.PIRATE)

    def create_minion(self, player):
        return Minion(7, 4)


class GnomereganInfantry(MinionCard):
    def __init__(self):
        super().__init__("Gnomeregan Infantry", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(1, 4, charge=True, taunt=True)


class FlyingMachine(MinionCard):
    def __init__(self):
        super().__init__("Flying Machine", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(1, 4, windfury=True)


class LostTallstrider(MinionCard):
    def __init__(self):
        super().__init__("Lost Tallstrider", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(5, 4)


class HemetNesingwary(MinionCard):
    def __init__(self):
        super().__init__("Hemet Nesingwary", 5, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY,
                         battlecry=Battlecry(Kill(), MinionSelector(IsType(MINION_TYPE.BEAST), players=BothPlayer(),
                                                                    picker=UserPicker())))

    def create_minion(self, player):
        return Minion(6, 3)


class Illuminator(MinionCard):
    def __init__(self):
        super().__init__("Illuminator", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(2, 4, effects=[Effect(TurnEnded(HasSecret()), ActionTag(Heal(4), HeroSelector()))])


class MekgineerThermaplugg(MinionCard):
    def __init__(self):
        super().__init__("Mekgineer Thermaplugg", 9, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY,
                         minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(9, 7, effects=[Effect(MinionDied(player=EnemyPlayer()), ActionTag(Summon(LeperGnome()),
                                                                                        PlayerSelector()))])


class StonesplinterTrogg(MinionCard):
    def __init__(self):
        super().__init__("Stonesplinter Trogg", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(2, 3, effects=[Effect(SpellCast(player=EnemyPlayer()),
                                            ActionTag(Give(ChangeAttack(1)), SelfSelector()))])


class TroggzorTheEarthinator(MinionCard):
    def __init__(self):
        super().__init__("Troggzor the Earthinator", 7, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(6, 6, effects=[Effect(SpellCast(player=EnemyPlayer()), ActionTag(Summon(BurlyRockjawTrogg()),
                                            PlayerSelector()))])


class Hobgoblin(MinionCard):
    def __init__(self):
        super().__init__("Hobgoblin", 3, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC)

    def create_minion(self, player):
        return Minion(2, 3, effects=[Effect(MinionPlaced(BaseAttackEqualTo(1)),
                                     ActionTag(Give([Buff(ChangeHealth(2)), Buff(ChangeAttack(2))]),
                                               TargetSelector()))])


class Cogmaster(MinionCard):
    def __init__(self):
        super().__init__("Cogmaster", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(1, 2, auras=[Aura(ChangeAttack(2), SelfSelector(),
                                        GreaterThan(Count(MinionSelector(IsType(MINION_TYPE.MECH))), value=0))])


class GoblinSapper(MinionCard):
    def __init__(self):
        super().__init__("Goblin Sapper", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(2, 4, buffs=[Buff(ChangeAttack(4), GreaterThan(Count(CardSelector(EnemyPlayer())), value=5))])


class TinkertownTechnician(MinionCard):
    def __init__(self):
        from hearthbreaker.cards.spells.neutral import spare_part_list
        super().__init__("Tinkertown Technician", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         battlecry=(Battlecry(Give([Buff(ChangeAttack(1)), Buff(ChangeHealth(1))]), SelfSelector(),
                                              GreaterThan(Count(MinionSelector(IsType(MINION_TYPE.MECH))), value=0)),
                                    Battlecry(AddCard(CardQuery(source=CARD_SOURCE.LIST, source_list=spare_part_list)),
                                              PlayerSelector(),
                                              GreaterThan(Count(MinionSelector(IsType(MINION_TYPE.MECH))), value=0))))

    def create_minion(self, player):
        return Minion(3, 3)


class Junkbot(MinionCard):
    def __init__(self):
        super().__init__("Junkbot", 5, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(1, 5, effects=[Effect(MinionDied(IsType(MINION_TYPE.MECH)),
                                     ActionTag(Give([Buff(ChangeAttack(2)), Buff(ChangeHealth(2))]), SelfSelector()))])


class Jeeves(MinionCard):
    def __init__(self):
        super().__init__("Jeeves", 4, CHARACTER_CLASS.ALL, CARD_RARITY.RARE, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(1, 4, effects=[Effect(TurnEnded(player=BothPlayer()),
                                            ActionTag(Draw(Difference(Count(CardSelector(players=CurrentPlayer())),
                                                                      value=3)),
                                            PlayerSelector(CurrentPlayer())))])


class LilExorcist(MinionCard):
    def __init__(self):
        super().__init__("Lil' Exorcist", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE,
                         battlecry=Battlecry(Give([Buff(ChangeAttack(Count(MinionSelector(MinionHasDeathrattle(),
                                                                                          EnemyPlayer())))),
                                                   Buff(ChangeHealth(Count(MinionSelector(MinionHasDeathrattle(),
                                                                                          EnemyPlayer()))))]),
                                             SelfSelector()))

    def create_minion(self, player):
        return Minion(2, 3, taunt=True)


class Recombobulator(MinionCard):
    def __init__(self):
        super().__init__("Recombobulator", 2, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC,
                         battlecry=Battlecry(Transform(CardQuery(conditions=[
                             ManaCost(Attribute("mana", SelfSelector())), IsMinion()])),
                             MinionSelector(picker=UserPicker())))

    def create_minion(self, player):
        return Minion(3, 2)


class EnhanceoMechano(MinionCard):
    def __init__(self):
        super().__init__("Enhance-o Mechano", 4, CHARACTER_CLASS.ALL, CARD_RARITY.EPIC, minion_type=MINION_TYPE.MECH,
                         battlecry=Battlecry(Give([
                                                  Buff(Windfury()),
                                                  Buff(Taunt()),
                                                  Buff(DivineShield())],
                                                  RandomPicker()),
                                             MinionSelector()))

    def create_minion(self, player):
        return Minion(3, 2)


class FoeReaper4000(MinionCard):
    def __init__(self):
        super().__init__("Foe Reaper 4000", 8, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(6, 9, effects=[Effect(Attack(IsMinion()), ActionTag(Damage(Attribute("attack", SelfSelector())),
                                            MinionSelector(TargetAdjacent(), EnemyPlayer())))])


class KezanMystic(MinionCard):
    def __init__(self):
        super().__init__("Kezan Mystic", 4, CHARACTER_CLASS.ALL, CARD_RARITY.RARE,
                         battlecry=Battlecry(ApplySecret(CARD_SOURCE.ENEMY_SECRETS), PlayerSelector()))

    def create_minion(self, player):
        return Minion(4, 3)


class V07TR0N(MinionCard):
    def __init__(self):
        super().__init__("V-07-TR-0N", 8, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, False, MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(4, 8, charge=True, buffs=[Buff(MegaWindfury())])


class MimironsHead(MinionCard):
    def __init__(self):
        super().__init__("Mimiron's Head", 5, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(4, 5, effects=[Effect(TurnStarted(), [ActionTag(Kill(), MinionSelector(IsType(MINION_TYPE.MECH,
                                                                                                    True)),
                                            GreaterThan(Count(MinionSelector(IsType(MINION_TYPE.MECH, True))),
                                                        value=2)),
                                            ActionTag(Summon(V07TR0N()), PlayerSelector())])])


class GnomishChicken(MinionCard):
    def __init__(self):
        super().__init__("Chicken", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False, minion_type=MINION_TYPE.BEAST,
                         ref_name="Chicken (Gnomish Experimenter)")

    def create_minion(self, player):
        return Minion(1, 1)


class GnomishExperimenter(MinionCard):
    def __init__(self):
        super().__init__("Gnomish Experimenter", 3, CHARACTER_CLASS.ALL, CARD_RARITY.RARE,
                         battlecry=(Battlecry(Draw(), PlayerSelector()), Battlecry(Transform(GnomishChicken()),
                                                                                   LastDrawnSelector(),
                                                                                   Matches(LastDrawnSelector(),
                                                                                           IsMinion()))))

    def create_minion(self, player):
        return Minion(3, 2)


class HungryDragon(MinionCard):
    def __init__(self):
        super().__init__("Hungry Dragon", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.DRAGON,
                         battlecry=(Battlecry(Summon(CardQuery(conditions=[ManaCost(1), IsMinion()])),
                                              PlayerSelector(EnemyPlayer()))))

    def create_minion(self, player):
        return Minion(5, 6)


class BlackwingTechnician(MinionCard):
    def __init__(self):
        super().__init__("Blackwing Technician", 3, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         battlecry=(Battlecry(Give([Buff(ChangeAttack(1)), Buff(ChangeHealth(1))]), SelfSelector(),
                                              GreaterThan(Count(CardSelector(condition=IsType(MINION_TYPE.DRAGON))),
                                                          value=0))))

    def create_minion(self, player):
        return Minion(2, 4)


class GrimPatron(MinionCard):
    def __init__(self):
        super().__init__("Grim Patron", 5, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(3, 3, effects=[Effect(Damaged(), [ActionTag(Summon(GrimPatron()), PlayerSelector(),
                                                                  GreaterThan(Attribute("health", SelfSelector()),
                                                                              value=0))])])


class EmperorThaurissan(MinionCard):
    def __init__(self):
        super().__init__("Emperor Thaurissan", 6, CHARACTER_CLASS.ALL, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(5, 5, effects=[Effect(TurnEnded(), [ActionTag(Give(Buff(ManaChange(-1))), CardSelector())])])


class VolcanicDrake(MinionCard):
    def __init__(self):
        super().__init__("Volcanic Drake", 6, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, minion_type=MINION_TYPE.DRAGON,
                         buffs=[Buff(ManaChange(Count(DeadMinionSelector(players=BothPlayer())), -1))])

    def create_minion(self, player):
        return Minion(6, 4)


class BlackwingCorruptor(MinionCard):
    def __init__(self):
        super().__init__("Blackwing Corruptor", 5, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Damage(3), CharacterSelector(players=BothPlayer(), picker=UserPicker()),
                                             GreaterThan(Count(CardSelector(condition=IsType(MINION_TYPE.DRAGON))),
                                                         value=0)))

    def create_minion(self, player):
        return Minion(5, 4)


class DrakonidCrusher(MinionCard):
    def __init__(self):
        super().__init__("Drakonid Crusher", 6, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON,
                         minion_type=MINION_TYPE.DRAGON,
                         battlecry=(Battlecry(Give([Buff(ChangeAttack(3)), Buff(ChangeHealth(3))]), SelfSelector(),
                                              Not(GreaterThan(Attribute('health', HeroSelector(EnemyPlayer())),
                                                              value=15)))))

    def create_minion(self, player):
        return Minion(6, 6)


class BlackWhelp(MinionCard):
    def __init__(self):
        super().__init__("Black Whelp", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False, MINION_TYPE.DRAGON)

    def create_minion(self, player):
        return Minion(2, 1)


class DragonEgg(MinionCard):
    def __init__(self):
        super().__init__("Dragon Egg", 1, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(0, 2, effects=[Effect(Damaged(), ActionTag(Summon(BlackWhelp()), PlayerSelector()))])
