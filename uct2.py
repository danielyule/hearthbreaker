# This is a very simple implementation of the UCT Monte Carlo Tree Search algorithm in Python 2.7.
# The function UCT(rootstate, itermax, verbose = False) is towards the bottom of the code.
# It aims to have the clearest and simplest possible code, and for the sake of clarity, the code
# is orders of magnitude less efficient than it could be made, particularly by using a 
# state.GetRandomMove() or state.DoRandomRollout() function.
# 
# Example GameState classes for Nim, OXO and Othello are included to give some idea of how you
# can write your own GameState use UCT in your 2-player game. Change the game to be played in 
# the UCTPlayGame() function at the bottom of the code.
# 
# Written by Peter Cowling, Ed Powley, Daniel Whitehouse (University of York, UK) September 2012.
# 
# Licence is granted to freely use and distribute for any sensible/legal purpose so long as this comment
# remains in any distributed code.
# 
# For more information about Monte Carlo Tree Search check out our web site at www.mcts.ai

from math import *
import random
import time
import sys, traceback
from tests.testing_utils import generate_game_for
from hearthbreaker.cards import *
from hearthbreaker.agents.basic_agents import DoNothingAgent
from hearthbreaker.game_objects import *
from hearthbreaker.constants import CHARACTER_CLASS


class MOVE:
    PRE_GAME = 1
    START_TURN = 2
    PICK_CLASS = 3
    PICK_CARD = 4
    END_TURN = 5
    HERO_POWER = 6
    SUMMON_MINION = 7
    EQUIP_WEAPON = 8
    MINION_ATTACK = 9
    HERO_ATTACK = 10
    TARGETED_SPELL = 11
    UNTARGETED_SPELL = 12

class HearthState:
    """ A state of the game, i.e. the game board.
    """
    def __init__(self):
        self.playerJustMoved = 2 # At the root pretend the player just moved is p2 - p1 has the first move
        random.seed(1857)

        #deck1 = [GoldshireFootman, GoldshireFootman, MurlocRaider, MurlocRaider, BloodfenRaptor, BloodfenRaptor,
        #         FrostwolfGrunt, FrostwolfGrunt, RiverCrocolisk, RiverCrocolisk, IronfurGrizzly, IronfurGrizzly,
        #         MagmaRager, MagmaRager, SilverbackPatriarch, SilverbackPatriarch, ChillwindYeti, ChillwindYeti,
        #         OasisSnapjaw, OasisSnapjaw, SenjinShieldmasta, SenjinShieldmasta, BootyBayBodyguard, BootyBayBodyguard,
        #         FenCreeper, FenCreeper, BoulderfistOgre, BoulderfistOgre, WarGolem, WarGolem]
        #deck2 = [Backstab, Backstab, Shadowstep, Shadowstep, Shiv, Shiv, AnubarAmbusher, AnubarAmbusher, Assassinate,
        #         Assassinate, Vanish, Vanish, AmaniBerserker, AmaniBerserker, MadBomber, MadBomber, YouthfulBrewmaster,
        #         YouthfulBrewmaster, AcolyteOfPain, AcolyteOfPain, QuestingAdventurer, RagingWorgen, RagingWorgen,
        #         AncientBrewmaster, AncientBrewmaster, DefenderOfArgus, DefenderOfArgus, GurubashiBerserker,
        #         GurubashiBerserker, RagnarosTheFirelord]
        #game = generate_game_for(deck1, deck2, DoNothingAgent, DoNothingAgent)
        #game._start_turn()

        adjacent_cards = ["Dire Wolf Alpha", "Ancient Mage", "Defender of Argus", "Sunfury Protector",
                          "Flametongue Totem", "Explosive Shot", "Cone of Cold", "Betrayal", "Void Terror",
                          "Unstable Portal", "Wee Spellstopper", "Piloted Shredder", "Piloted Sky Golem",
                          "Recombobulator"]
        self.adjacent_cards = adjacent_cards

        card_set1 = []
        class1 = CHARACTER_CLASS.MAGE
        card_set2 = []
        class2 = CHARACTER_CLASS.ALL
        game = generate_game_for(ArcaneMissiles, ArcaneMissiles, DoNothingAgent, DoNothingAgent)
        game.current_player = game.players[0]
        game.other_player = game.players[1]

        self.game = game

    def Clone(self):
        """ Create a deep clone of this game state.
        """
        st = HearthState()
        st.playerJustMoved = self.playerJustMoved
        st.game = self.game.copy()
        #st.game = copy.deepcopy(self.game)
        return st

    def DoMove(self, move):
        """ Update a state by carrying out the given move.
            Must update playerJustMoved if end_turn.
        """
        assert self.game.players[0].hero.health > 0 and self.game.players[1].hero.health > 0 and not self.game.game_ended

        def _choose_target(targets):
            if move[4] is None:
                return None
            else:
                return targets[move[4]]

        def _choose_index(targets, player):
            return move[5]

        def _choose_option(*options):
            return options[move[4]]

        if self.game.current_player.name == "one":
            self.playerJustMoved = 1
        else:
            self.playerJustMoved = 2

        # print(str(self.game.current_player.mana) + "/" + str(self.game.current_player.max_mana))
        if move[0] == MOVE.PRE_GAME:
            self.game.current_player = self.game.players[1]
            self.game.other_player = self.game.players[0]
            self.game.pre_game()
            #self.game._start_turn()
        elif move[0] == MOVE.START_TURN:
            self.game._start_turn()
        elif move[0] == MOVE.PICK_CLASS:
            self.game.current_player.deck.character_class = move[1]
            self.game.current_player.hero.character_class = move[1]
            self.game.current_player.hero.power = hearthbreaker.powers.powers(move[1])(self.game.current_player.hero)
        elif move[0] == MOVE.PICK_CARD:
            card = move[1] #copy.deepcopy(move[1])
            card.drawn = False
            self.game.current_player.deck.cards.append(card)
            
            if len(self.game.current_player.deck.cards) == 30:
                self.game.current_player = self.game.players[1]
                self.game.other_player = self.game.players[0]
        elif move[0] == MOVE.END_TURN:
            try:
                self.game._end_turn()
                self.game._start_turn()
            except:
                print(self.game.players[0].deck.__str__())
                print(self.game.players[1].deck.__str__())
                traceback.print_exc()
                sys.exit()
        elif move[0] == MOVE.HERO_POWER:
            try:
                self.game.current_player.agent.choose_target = _choose_target
                self.game.current_player.hero.power.use()
            except:
                print(self.game.players[0].deck.__str__())
                print(self.game.players[1].deck.__str__())
                traceback.print_exc()
                sys.exit()
        elif move[0] == MOVE.SUMMON_MINION:
            try:
                self.game.current_player.agent.choose_target = _choose_target
                self.game.current_player.agent.choose_index = _choose_index
                self.game.play_card(self.game.current_player.hand[move[3]])
            except:
                print(move)
                print(self.game.current_player.hand)
                print(self.game.other_player.hand)
                print(self.game.players[0].deck.__str__())
                print(self.game.players[1].deck.__str__())
                traceback.print_exc()
                sys.exit()
        elif move[0] == MOVE.EQUIP_WEAPON:
            try:
                self.game.current_player.agent.choose_target = _choose_target
                self.game.play_card(self.game.current_player.hand[move[3]])
            except:
                print(move)
                print(self.game.current_player.hand)
                print(self.game.other_player.hand)
                print(self.game.players[0].deck.__str__())
                print(self.game.players[1].deck.__str__())
                traceback.print_exc()
                sys.exit()
        elif move[2] is None:  # Passing index rather than object, hopefully the game copy fix will help with this
            try:
                self.game.play_card(self.game.current_player.hand[move[3]])
            except:
                print(move)
                print(self.game.current_player.hand)
                print(self.game.other_player.hand)
                print(self.game.players[0].deck.__str__())
                print(self.game.players[1].deck.__str__())
                traceback.print_exc()
                sys.exit()
        elif move[0] == MOVE.MINION_ATTACK:
            try:
                self.game.current_player.agent.choose_target = _choose_target
                self.game.current_player.minions[move[3]].attack()
            except:
                print(move)
                print(self.game.current_player.minions)
                print(self.game.other_player.minions)
                print(self.game.players[0].deck.__str__())
                print(self.game.players[1].deck.__str__())
                traceback.print_exc()
                sys.exit()
        elif move[0] == MOVE.HERO_ATTACK:
            try:
                self.game.current_player.agent.choose_target = _choose_target
                self.game.current_player.hero.attack()
            except:
                print(self.game.players[0].deck.__str__())
                print(self.game.players[1].deck.__str__())
                traceback.print_exc()
                sys.exit()
        elif move[0] == MOVE.TARGETED_SPELL:
            try:
                self.game.current_player.agent.choose_target = _choose_target
                self.game.play_card(self.game.current_player.hand[move[3]])
            except:
                print(move)
                print(self.game.current_player.hand)
                print(self.game.other_player.hand)
                print(self.game.players[0].deck.__str__())
                print(self.game.players[1].deck.__str__())
                traceback.print_exc()
                sys.exit()
        else:
            raise NameError("DoMove ran into unclassified card", move)

    def GetMoves(self):
        """ Get all possible moves from this state.
        """
        if self.game.game_ended or self.game.players[0].hero.health <= 0 or self.game.players[1].hero.health <= 0:
            return []
        valid_moves = []  # Move format is [string, attacker/card, target, attacker/card index, target index, summoning index]

        if not len(self.game.current_player.deck.cards) == 30 and len(self.game.other_player.deck.cards) == 30:
            valid_moves.append([MOVE.PRE_GAME])
        elif len(self.game.current_player.deck.cards) == 30 and len(self.game.other_player.deck.cards) == 30 and self.game.current_player.max_mana == 0 and self.game.turn == 0:
            valid_moves.append([MOVE.START_TURN])
        elif self.game.current_player.hero.character_class == hearthbreaker.constants.CHARACTER_CLASS.ALL:
            valid_moves.append([MOVE.PICK_CLASS, hearthbreaker.constants.CHARACTER_CLASS.DRUID])
            valid_moves.append([MOVE.PICK_CLASS, hearthbreaker.constants.CHARACTER_CLASS.HUNTER])
            valid_moves.append([MOVE.PICK_CLASS, hearthbreaker.constants.CHARACTER_CLASS.MAGE])
            valid_moves.append([MOVE.PICK_CLASS, hearthbreaker.constants.CHARACTER_CLASS.PALADIN])
            valid_moves.append([MOVE.PICK_CLASS, hearthbreaker.constants.CHARACTER_CLASS.PRIEST])
            valid_moves.append([MOVE.PICK_CLASS, hearthbreaker.constants.CHARACTER_CLASS.ROGUE])
            valid_moves.append([MOVE.PICK_CLASS, hearthbreaker.constants.CHARACTER_CLASS.SHAMAN])
            valid_moves.append([MOVE.PICK_CLASS, hearthbreaker.constants.CHARACTER_CLASS.WARLOCK])
            valid_moves.append([MOVE.PICK_CLASS, hearthbreaker.constants.CHARACTER_CLASS.WARRIOR])
        elif len(self.game.current_player.deck.cards) < 30:
            if self.game.current_player.name == "one":
                owned_cards = []
                ### BASIC ###
                # Druid
                owned_cards.extend([Innervate(), Moonfire(), Claw(), MarkOfTheWild(), WildGrowth(), HealingTouch(),
                                    SavageRoar(), Swipe(), Starfire(), IronbarkProtector()])
                # Hunter
                owned_cards.extend([HuntersMark(), ArcaneShot(), Tracking(), TimberWolf(), AnimalCompanion(), KillCommand(),
                                    MultiShot(), Houndmaster(), StarvingBuzzard(), TundraRhino()])
                # Mage
                owned_cards.extend([ArcaneMissiles(), MirrorImage(), ArcaneExplosion(), Frostbolt(), ArcaneIntellect(),
                                    FrostNova(), Fireball(), Polymorph(), WaterElemental(), Flamestrike()])
                # Paladin
                owned_cards.extend([LightsJustice(), BlessingOfMight(), HandOfProtection(), Humility(), HolyLight(),
                                    TruesilverChampion(), BlessingOfKings(), Consecration(), HammerOfWrath(),
                                    GuardianOfKings()])
                # Priest
                owned_cards.extend([HolySmite(), MindVision(), PowerWordShield(), NorthshireCleric(), DivineSpirit(),
                                    MindBlast(), ShadowWordPain(), ShadowWordDeath(), HolyNova(), MindControl()])
                # Rogue
                owned_cards.extend([Backstab(), DeadlyPoison(), SinisterStrike(), Sap(), Shiv(), FanOfKnives(),
                                    AssassinsBlade(), Assassinate(), Vanish(), Sprint()])
                # Shaman
                owned_cards.extend([AncestralHealing(), TotemicMight(), FrostShock(), RockbiterWeapon(),
                                    hearthbreaker.cards.spells.shaman.Windfury(), FlametongueTotem(), Hex(), Windspeaker(),
                                    Bloodlust(), FireElemental()])
                # Warlock
                owned_cards.extend([SacrificialPact(), Corruption(), MortalCoil(), Soulfire(), Voidwalker(), Succubus(),
                                    DrainLife(), ShadowBolt(), Hellfire(), DreadInfernal()])
                # Warrior
                owned_cards.extend([Execute(), Whirlwind(), FieryWarAxe(), Cleave(), HeroicStrike(),
                                    hearthbreaker.cards.spells.warrior.Charge(), ShieldBlock(), WarsongCommander(),
                                    KorkronElite(), ArcaniteReaper()])
                # Neutral
                owned_cards.extend([ElvenArcher(), GoldshireFootman(), GrimscaleOracle(), MurlocRaider(), StonetuskBoar(),
                                    VoodooDoctor(), AcidicSwampOoze(), BloodfenRaptor(), BluegillWarrior(),
                                    FrostwolfGrunt(), KoboldGeomancer(), MurlocTidehunter(), NoviceEngineer(),
                                    RiverCrocolisk(), DalaranMage(), IronforgeRifleman(), IronfurGrizzly(), MagmaRager(),
                                    RaidLeader(), RazorfenHunter(), ShatteredSunCleric(), SilverbackPatriarch(),
                                    Wolfrider(), ChillwindYeti(), DragonlingMechanic(), GnomishInventor(), OasisSnapjaw(),
                                    OgreMagi(), SenjinShieldmasta(), StormwindKnight(), BootyBayBodyguard(),
                                    DarkscaleHealer(), FrostwolfWarlord(), GurubashiBerserker(), Nightblade(),
                                    StormpikeCommando(), Archmage(), BoulderfistOgre(), LordOfTheArena(),
                                    RecklessRocketeer(), CoreHound(), StormwindChampion(), WarGolem()])
        
                ### CLASSIC ###
                # Druid
                owned_cards.extend([Wrath(), Starfall(), DruidOfTheClaw()])
                # Hunter
                owned_cards.extend([DeadlyShot()])
                # Mage
                owned_cards.extend([IceLance(), ManaWyrm(), SorcerersApprentice(), IceBarrier(), EtherealArcanist()])
                # Paladin
                owned_cards.extend([EyeForAnEye(), NobleSacrifice(), Repentance(), ArgentProtector()])
                # Priest
                owned_cards.extend([CircleOfHealing(), Silence(), InnerFire(), MassDispel()])
                # Rogue
                owned_cards.extend([ColdBlood(), Conceal(), Eviscerate()])
                # Shaman
                owned_cards.extend([AncestralSpirit()])
                # Warlock
                owned_cards.extend([FlameImp(), Demonfire(), SummoningPortal(), Doomguard()])
                # Warrior
                owned_cards.extend([Rampage(), Armorsmith(), MortalStrike(), Brawl()])
                # Neutral
                owned_cards.extend([Wisp(), ArgentSquire(), SouthseaDeckhand(), AmaniBerserker(), BloodsailRaider(),
                                    DireWolfAlpha(), FaerieDragon(), IronbeakOwl(), KnifeJuggler(), LootHoarder(),
                                    MadBomber(), MasterSwordsmith(), Demolisher(), HarvestGolem(), ImpMaster(),
                                    JunglePanther(), QuestingAdventurer(), TinkmasterOverspark(), CultMaster(),
                                    DefenderOfArgus(), SilvermoonGuardian(), AzureDrake(), FenCreeper(), SpitefulSmith(),
                                    StranglethornTiger(), FrostElemental()])
        
                ### PROMO ###
                owned_cards.extend([GelbinMekkatorque()])
        
                ### NAXXRAMAS ###
                # Druid
                owned_cards.extend([PoisonSeeds()])
                # Hunter
                owned_cards.extend([Webspinner()])
                # Mage
                owned_cards.extend([Duplicate()])
                # Paladin
                owned_cards.extend([Avenge()])
                # Priest
                owned_cards.extend([DarkCultist()])
                # Rogue
                owned_cards.extend([AnubarAmbusher()])
                # Shaman
                owned_cards.extend([Reincarnate()])
                # Warlock
                owned_cards.extend([Voidcaller()])
                # Warrior
                owned_cards.extend([DeathsBite()])
                # Neutral
                owned_cards.extend([Undertaker(), ZombieChow(), EchoingOoze(), HauntedCreeper(), MadScientist(),
                                    NerubarWeblord(), NerubianEgg(), UnstableGhoul(), DancingSwords(), Deathlord(),
                                    ShadeOfNaxxramas(), StoneskinGargoyle(), BaronRivendare(), WailingSoul(), Feugen(),
                                    Loatheb(), SludgeBelcher(), SpectralKnight(), Stalagg(), Maexxna(), KelThuzad()])
        
                ### GOBLINS VS GNOMES ##
                # Hunter
                owned_cards.extend([Glaivezooka()])
                # Mage
                owned_cards.extend([Flamecannon(), Snowchugger()])
                # Paladin
                owned_cards.extend([SealOfLight(), CobaltGuardian()])
                # Priest
                owned_cards.extend([Shrinkmeister()])
                # Rogue
                owned_cards.extend([OneeyedCheat(), TinkersSharpswordOil()])
                # Warrior
                owned_cards.extend([Warbot()])
                # Neutral
                # TODO: Cogmaster()
                owned_cards.extend([Mechwarper(), MicroMachine(), Puddlestomper(), ShipsCannon(), MechanicalYeti(),
                                    AntiqueHealbot()])

                card_list = filter(lambda c: c.character_class == hearthbreaker.constants.CHARACTER_CLASS.ALL or c.character_class == self.game.current_player.hero.character_class,
                                   owned_cards)
            else:
                card_list = filter(lambda c: c.character_class == hearthbreaker.constants.CHARACTER_CLASS.ALL or c.character_class == self.game.current_player.hero.character_class,
                                   get_cards())
            for card in card_list:
                counter = [x for x in self.game.current_player.deck.cards if x.name == card.name]
                
                if len(counter) < 1 or (len(counter) < 2 and card.rarity != hearthbreaker.constants.CARD_RARITY.LEGENDARY):
                    valid_moves.append([MOVE.PICK_CARD, card])
        else:
            for card in self.game.current_player.hand:
                dupe = False
                for i in range(len(valid_moves)):
                    if valid_moves[i][1].name == card.name:
                        dupe = True
                        break
                if not dupe:
                    if card.can_use(self.game.current_player, self.game) and isinstance(card, MinionCard):
                        # Minion placement is only important if there are cards available that matters on it
                        if any(any(card.name == name for name in self.adjacent_cards) for card in self.game.players[0].deck.cards) or any(any(card.name == name for name in self.adjacent_cards) for card in self.game.players[1].deck.cards):
                            # Found adjacent card, so try every possible placement
                            for i in range(len(self.game.current_player.minions) + 1):
                                if card.targetable and card.targets is not None:
                                    for j in range(len(card.targets)):
                                        valid_moves.append([MOVE.SUMMON_MINION, card, None, self.game.current_player.hand.index(card), j, i])
                                else:
                                    valid_moves.append([MOVE.SUMMON_MINION, card, None, self.game.current_player.hand.index(card), 0, i])
                        else:
                            # It doesn't matter where the minion is placed
                            if card.targetable and card.targets is not None:
                                for i in range(len(card.targets)):
                                    valid_moves.append([MOVE.SUMMON_MINION, card, None, self.game.current_player.hand.index(card), i, 0])
                            else:
                                valid_moves.append([MOVE.SUMMON_MINION, card, None, self.game.current_player.hand.index(card), 0, 0])
                    elif card.can_use(self.game.current_player, self.game) and isinstance(card, WeaponCard):
                        if card.targetable and card.targets is not None:
                            for i in range(len(card.targets)):
                                valid_moves.append([MOVE.EQUIP_WEAPON, card, None, self.game.current_player.hand.index(card), i])
                        else:
                            valid_moves.append([MOVE.EQUIP_WEAPON, card, None, self.game.current_player.hand.index(card), 0])                            
                    elif card.can_use(self.game.current_player, self.game) and isinstance(card, SecretCard):
                        valid_moves.append([MOVE.UNTARGETED_SPELL, card, None, self.game.current_player.hand.index(card), 0])
                    elif card.can_use(self.game.current_player, self.game) and not card.targetable:
                        valid_moves.append([MOVE.UNTARGETED_SPELL, card, None, self.game.current_player.hand.index(card), 0])
                    elif card.can_use(self.game.current_player, self.game) and card.targetable:
                        for i in range(len(card.targets)):
                            valid_moves.append([MOVE.TARGETED_SPELL, card, card.targets[i],
                                                self.game.current_player.hand.index(card), i])
    
            found_taunt = False
            targets = []
            for enemy in copy.copy(self.game.other_player.minions):
                if enemy.taunt and enemy.can_be_attacked():
                    found_taunt = True
                if enemy.can_be_attacked():
                    targets.append(enemy)
    
            if found_taunt:
                targets = [target for target in targets if target.taunt]
            else:
                targets.append(self.game.other_player.hero)
    
            for minion in copy.copy(self.game.current_player.minions):
                if minion.can_attack():
                    for i in range(len(targets)):
                        valid_moves.append([MOVE.MINION_ATTACK, minion, targets[i],
                                            self.game.current_player.minions.index(minion), i])
    
            if self.game.current_player.hero.can_attack():
                for i in range(len(targets)):
                    valid_moves.append([MOVE.HERO_ATTACK, self.game.current_player.hero, targets[i], None, i])
    
            if (self.game.current_player.hero.power.__str__() == "Fireblast" or \
               self.game.current_player.hero.power.__str__() == "Mind Spike" or \
               self.game.current_player.hero.power.__str__() == "Mind Shatter" or \
               self.game.current_player.hero.power.__str__() == "Lesser Heal") and \
               self.game.current_player.hero.power.can_use():
                for target in hearthbreaker.targeting.find_spell_target(self.game, lambda t: t.spell_targetable()):
                    valid_moves.append([MOVE.HERO_POWER, self.game.current_player.hero, target, 0, \
                                       hearthbreaker.targeting.find_spell_target(self.game, lambda t: \
                                                                                t.spell_targetable()).index(target)])
            elif self.game.current_player.hero.power.can_use():
                valid_moves.append([MOVE.HERO_POWER, self.game.current_player.hero, None, None, None])
    
            valid_moves.append([MOVE.END_TURN, None, None])

        return valid_moves

    def GetResult(self, playerjm):
        """ Get the game result from the viewpoint of playerjm. 
        """
        if self.game.players[0].hero.health <= 0 and self.game.players[1].hero.health <= 0:
            return 0.5
        elif self.game.players[playerjm - 1].hero.health <= 0:
            return 0
        elif self.game.players[2 - playerjm].hero.health <= 0:
            return 1
        else:  # Should not be possible to get here unless we terminate the game early.
            return 0.5

    def __repr__(self):
        s = "Turn: " + str(self.game.turn)
        s += "\n[" + str(self.game.players[0].hero.health) + " hp ~ " + str(len(self.game.players[0].hand)) + " in hand ~ " + str(self.game.players[0].deck.left) + "/" + str(len(self.game.players[0].deck.cards)) + " in deck ~ " + str(self.game.players[0].mana) + "/" + str(self.game.players[0].max_mana) + " mana] "
        for minion in copy.copy(self.game.players[0].minions):
            s += str(minion.calculate_attack()) + "/" + str(minion.health) + ":"
        s += "\n[" + str(self.game.players[1].hero.health) + " hp ~ " + str(len(self.game.players[1].hand)) + " in hand ~ " + str(self.game.players[1].deck.left) + "/" + str(len(self.game.players[1].deck.cards)) + " in deck ~ " + str(self.game.players[1].mana) + "/" + str(self.game.players[1].max_mana) + " mana] "
        for minion in copy.copy(self.game.players[1].minions):
            s += str(minion.calculate_attack()) + "/" + str(minion.health) + ":"
        s += "\n" + "Current Player: " + str(self.game.current_player.name)
        return s


class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
        Crashes if state not specified.
    """
    def __init__(self, move = None, parent = None, state = None):
        self.move = move # the move that got us to this node - "None" for the root node
        self.parentNode = parent # "None" for the root node
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        if move and (move[0] == MOVE.END_TURN or move[0] == MOVE.PRE_GAME or move[0] == MOVE.START_TURN):
            self.untriedMoves = []
        else:
            self.untriedMoves = state.GetMoves() # future child nodes
        self.playerJustMoved = state.playerJustMoved # the only part of the state that the Node needs later
        
    def UCTSelectChild(self):
        """ Use the UCB1 formula to select a child node. Often a constant UCTK is applied so we have
            lambda c: c.wins/c.visits + UCTK * sqrt(2*log(self.visits)/c.visits to vary the amount of
            exploration versus exploitation.
        """
        s = sorted(self.childNodes, key = lambda c: c.wins/c.visits + sqrt(2*log(self.visits)/c.visits))[-1]
        return s
    
    def AddChild(self, m, s):
        """ Remove m from untriedMoves and add a new child node for this move.
            Return the added child node
        """
        n = Node(move = m, parent = self, state = s)
        self.untriedMoves.remove(m)
        self.childNodes.append(n)
        return n
    
    def Update(self, result):
        """ Update this node - one additional visit and result additional wins. result must be from the viewpoint of playerJustmoved.
        """
        self.visits += 1
        self.wins += result

    def __repr__(self):
        return "[M:" + str(self.move) + " W/V:" + str(self.wins) + "/" + str(self.visits) + " U:" + str(self.untriedMoves) + "]"

    def TreeToString(self, indent):
        s = self.IndentString(indent) + str(self)
        for c in sorted(self.childNodes, key = lambda c: c.visits):
             s += c.TreeToString(indent+1)
        return s

    def IndentString(self,indent):
        s = "\n"
        for i in range (1,indent+1):
            s += "| "
        return s

    def ChildrenToString(self):
        s = ""
        for c in sorted(self.childNodes, key = lambda c: c.visits):
             s += str(c) + "\n"
        return s[:-2]

    def clean(self):
        for child in self.childNodes:
            child.clean()
        del self.childNodes
        del self.parentNode
        del self.untriedMoves


def UCT(rootstate, seconds, verbose = False):
    """ Conduct a UCT search for seconds starting from rootstate.
        Return the best move from the rootstate.
        Assumes 2 alternating players (player 1 starts), with game results in the range [0.0, 1.0]."""
    rootnode = Node(state = rootstate)

    iterations = 0
    future = time.time() + seconds
    while time.time() < future:
        node = rootnode
        state = rootstate.Clone()

        # Select
        while node.untriedMoves == [] and node.childNodes != []: # node is fully expanded and non-terminal
            node = node.UCTSelectChild()
            state.DoMove(node.move)

        # Expand
        if node.untriedMoves != []: # if we can expand (i.e. state/node is non-terminal)
            m = random.choice(node.untriedMoves)
            state.DoMove(m)
            node = node.AddChild(m, state) # add child and descend tree

        # Rollout - this can often be made orders of magnitude quicker using a state.GetRandomMove() function
        while state.GetMoves() != []: # while state is non-terminal
            state.DoMove(random.choice(state.GetMoves()))

        # Backpropagate
        while node != None: # backpropagate from the expanded node and work back to the root node
            node.Update(state.GetResult(node.playerJustMoved)) # state is terminal. Update node with result from POV of node.playerJustMoved
            node = node.parentNode

        iterations += 1

    # Output some information about the tree - can be omitted
    if (verbose): print(rootnode.TreeToString(0))
    else: print(rootnode.ChildrenToString())

    print("Iterations: " + str(iterations) + "\n")

    bestmove = sorted(rootnode.childNodes, key = lambda c: c.visits)[-1].move # return the move that was most visited
    rootnode.clean()
    del rootnode
    
    return bestmove


def UCTPlayGame():
    """ Play a sample game between two UCT players where each player gets a different number 
        of UCT iterations (= simulations = tree nodes).
    """
    state = HearthState()
    while (state.GetMoves() != []):
        print(str(state))
        m = UCT(rootstate = state, seconds = 12000, verbose = False)
        print("Best Move: " + str(m) + "\n")
        state.DoMove(m)

        print(state.game.players[0].deck.__str__())
        print(state.game.players[1].deck.__str__())
        print()
    if state.GetResult(state.playerJustMoved) == 1.0:
        print("Player " + str(state.playerJustMoved) + " wins!")
    elif state.GetResult(state.playerJustMoved) == 0.0:
        print("Player " + str(3 - state.playerJustMoved) + " wins!")
    else: print("Nobody wins!")


if __name__ == "__main__":
    """ Play a single game to the end using UCT for both players. 
    """
    UCTPlayGame()
