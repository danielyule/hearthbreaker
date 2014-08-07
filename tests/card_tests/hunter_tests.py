import random
import unittest

from hearthbreaker.agents.basic_agents import DoNothingBot
from tests.agents.testing_agents import SpellTestingAgent, MinionPlayingAgent, WeaponTestingAgent, \
    PredictableAgentWithoutHeroPower, SelfSpellTestingAgent, EnemyMinionSpellTestingAgent, OneSpellTestingAgent
from tests.testing_utils import generate_game_for, mock
from hearthbreaker.cards import *


class TestHunter(unittest.TestCase):
    def setUp(self):
        random.seed(1857)

    def test_HuntersMark(self):
        game = generate_game_for(HuntersMark, MogushanWarden, SpellTestingAgent, MinionPlayingAgent)

        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(7, game.current_player.minions[0].health)
        self.assertEqual(7, game.current_player.minions[0].calculate_max_health())

        # This will play all the hunter's marks currently in the player's hand
        game.play_single_turn()
        self.assertEqual(1, game.other_player.minions[0].health)
        self.assertEqual(1, game.other_player.minions[0].calculate_max_health())

    def test_TimberWolf(self):
        game = generate_game_for([StonetuskBoar, FaerieDragon, KoboldGeomancer, TimberWolf],
                                 StonetuskBoar, SpellTestingAgent, DoNothingBot)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[3].calculate_attack())
        self.assertEqual(3, game.current_player.minions[2].calculate_attack())
        self.assertEqual(2, game.current_player.minions[1].calculate_attack())
        self.assertEqual(1, game.current_player.minions[0].calculate_attack())

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(6, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[5].calculate_attack())
        self.assertEqual(3, game.current_player.minions[4].calculate_attack())
        self.assertEqual(2, game.current_player.minions[3].calculate_attack())
        self.assertEqual(1, game.current_player.minions[2].calculate_attack())
        self.assertEqual(2, game.current_player.minions[1].calculate_attack())
        self.assertEqual(3, game.current_player.minions[0].calculate_attack())

        game.current_player.minions[1].die(None)
        game.current_player.minions[1].activate_delayed()
        self.assertEqual(5, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[4].calculate_attack())
        self.assertEqual(3, game.current_player.minions[3].calculate_attack())
        self.assertEqual(2, game.current_player.minions[2].calculate_attack())
        self.assertEqual(1, game.current_player.minions[1].calculate_attack())
        self.assertEqual(3, game.current_player.minions[0].calculate_attack())

        game.current_player.minions[3].die(None)
        game.current_player.minions[3].activate_delayed()
        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[3].calculate_attack())
        self.assertEqual(2, game.current_player.minions[2].calculate_attack())
        self.assertEqual(1, game.current_player.minions[1].calculate_attack())
        self.assertEqual(3, game.current_player.minions[0].calculate_attack())

        wolf = game.current_player.minions[1]
        wolf.die(None)
        wolf.activate_delayed()
        self.assertEqual(3, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[2].calculate_attack())
        self.assertEqual(2, game.current_player.minions[1].calculate_attack())
        self.assertEqual(3, game.current_player.minions[0].calculate_attack())

    def test_ArcaneShot(self):
        game = generate_game_for(ArcaneShot, StonetuskBoar, SpellTestingAgent, DoNothingBot)
        game.players[0].spell_damage = 1
        game.play_single_turn()
        self.assertEqual(27, game.other_player.hero.health)

    def test_BestialWrath(self):

        def verify_bwrath():
            self.assertEqual(2, game.other_player.minions[0].temp_attack)
            self.assertTrue(game.other_player.minions[0].immune)

        def verify_silence():
            self.assertFalse(game.other_player.minions[0].immune)
            self.assertEqual(0, game.other_player.minions[0].temp_attack)

        game = generate_game_for(StonetuskBoar, [BestialWrath, BestialWrath, BestialWrath, Silence, BoulderfistOgre],
                                 MinionPlayingAgent, EnemyMinionSpellTestingAgent)
        game.play_single_turn()
        game.other_player.bind_once("turn_ended", verify_bwrath)
        game.play_single_turn()
        self.assertEqual(1, len(game.other_player.minions))
        self.assertFalse(game.other_player.minions[0].immune)
        self.assertEqual(0, game.other_player.minions[0].temp_attack)

        game.play_single_turn()
        game.other_player.bind_once("turn_ended", verify_silence)
        game.play_single_turn()
        self.assertEqual(2, len(game.other_player.minions))
        self.assertFalse(game.other_player.minions[0].immune)
        self.assertEqual(0, game.other_player.minions[0].temp_attack)
        self.assertEqual(2, len(game.players[1].hand))

    def test_Flare(self):

        game = generate_game_for(Vaporize, [WorgenInfiltrator, WorgenInfiltrator, ArcaneShot, Flare],
                                 SpellTestingAgent, SpellTestingAgent)

        for turn in range(0, 5):
            game.play_single_turn()

        # Vaporize is in place and two Infiltrators are down
        self.assertEqual(1, len(game.current_player.secrets))
        self.assertEqual(2, len(game.other_player.minions))
        self.assertTrue(game.other_player.minions[0].stealth)
        self.assertTrue(game.other_player.minions[1].stealth)
        self.assertEqual(4, len(game.other_player.hand))

        old_play = game.other_player.agent.do_turn

        def _play_and_attack(player):
            old_play(player)
            player.minions[2].attack()

        # Flare, The Coin, two Worgens and Arcane shot are played
        # Arcane shot kills one of the active Worgens, because Flare has removed its stealth
        game.other_player.agent.do_turn = _play_and_attack
        game.play_single_turn()
        self.assertEqual(0, len(game.other_player.secrets))
        self.assertEqual(3, len(game.current_player.minions))
        self.assertFalse(game.current_player.minions[2].stealth)
        self.assertEqual(1, len(game.current_player.hand))

    def test_EaglehornBow(self):
        game = generate_game_for([Snipe, EaglehornBow], StonetuskBoar, PredictableAgentWithoutHeroPower,
                                 MinionPlayingAgent)

        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(1, game.players[0].hero.weapon.durability)
        self.assertEqual(3, game.players[0].hero.weapon.base_attack)

        # Snipe should trigger, granting our weapon +1 durability
        game.play_single_turn()

        self.assertEqual(2, game.players[0].hero.weapon.durability)
        self.assertEqual(3, game.players[0].hero.weapon.base_attack)

    def test_GladiatorsLongbow(self):
        game = generate_game_for(GladiatorsLongbow, WaterElemental, WeaponTestingAgent,
                                 MinionPlayingAgent)
        for turn in range(0, 13):
            game.play_single_turn()

        self.assertEqual(3, len(game.other_player.minions))
        self.assertEqual(1, game.other_player.minions[0].health)
        self.assertEqual(30, game.current_player.hero.health)
        self.assertFalse(game.current_player.hero.frozen)
        self.assertFalse(game.current_player.hero.immune)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(4, len(game.other_player.minions))
        self.assertEqual(1, game.other_player.minions[0].health)
        self.assertEqual(1, game.other_player.minions[1].health)
        self.assertEqual(30, game.current_player.hero.health)
        self.assertFalse(game.current_player.hero.frozen)
        self.assertFalse(game.current_player.hero.immune)
        self.assertEqual(0, len(game.current_player.events))

    def test_Tracking(self):
        game = generate_game_for([Tracking, Tracking, Tracking, Tracking,
                                  StonetuskBoar, BloodfenRaptor, KoboldGeomancer],
                                 StonetuskBoar, SpellTestingAgent, DoNothingBot)

        game.play_single_turn()
        self.assertEqual(4, len(game.current_player.hand))
        self.assertEqual("Stonetusk Boar", game.current_player.hand[3].name)
        self.assertEqual(23, game.current_player.deck.left)

    def test_ExplosiveTrap(self):
        game = generate_game_for(ExplosiveTrap, StonetuskBoar, SpellTestingAgent, PredictableAgentWithoutHeroPower)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.secrets))
        self.assertEqual(1, len(game.other_player.minions))

        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.secrets))
        self.assertEqual(0, len(game.current_player.minions))
        self.assertEqual(28, game.current_player.hero.health)
        self.assertEqual(29, game.other_player.hero.health)

        random.seed(1857)
        game = generate_game_for(ExplosiveTrap, Frostbolt, SpellTestingAgent, SpellTestingAgent)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(1, len(game.other_player.secrets))
        self.assertEqual(30, game.current_player.hero.health)
        self.assertEqual(27, game.other_player.hero.health)

    def test_FreezingTrap(self):
        game = generate_game_for(FreezingTrap, BluegillWarrior, SpellTestingAgent, PredictableAgentWithoutHeroPower)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(4, len(game.players[0].hand))
        self.assertEqual(7, len(game.players[1].hand))
        self.assertEqual(4, game.players[1].hand[6].mana_cost(game.players[1]))
        self.assertEqual(1, len(game.players[0].secrets))
        self.assertEqual(30, game.players[0].hero.health)
        game.play_single_turn()
        self.assertEqual(5, len(game.players[0].hand))
        game.play_single_turn()
        self.assertEqual(0, len(game.current_player.minions))
        self.assertEqual(30, game.players[0].hero.health)
        self.assertEqual(8, len(game.players[1].hand))
        self.assertEqual(4, game.players[1].hand[5].mana_cost(game.players[1]))
        self.assertEqual(4, game.players[1].hand[7].mana_cost(game.players[1]))

    def test_FreezingTrap_many_cards(self):
        class FreezingTrapAgent(DoNothingBot):
            def do_turn(self, player):
                if player.mana == 6:
                    game.play_card(player.hand[0])
                if player.mana == 7:
                    player.minions[0].attack()
        game = generate_game_for(FreezingTrap, BoulderfistOgre, SpellTestingAgent, FreezingTrapAgent)

        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        death_mock = mock.Mock()
        game.players[1].minions[0].bind_once("died", death_mock)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(10, len(game.current_player.hand))
        self.assertEqual(0, len(game.current_player.minions))
        for card in game.current_player.hand:
            if card.name != "The Coin":
                self.assertEqual(6, card.mana_cost(game.current_player))
        self.assertEqual(30, game.other_player.hero.health)
        death_mock.assert_called_once_with(None)

    def test_Misdirection(self):
        game = generate_game_for(Misdirection, StonetuskBoar, SpellTestingAgent, PredictableAgentWithoutHeroPower)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(28, game.other_player.hero.health)
        self.assertEqual(1, len(game.current_player.minions))  # The boar has been misdirected into another boar
        self.assertEqual(30, game.current_player.hero.health)

    def test_FreezingTrapAndMisdirection(self):
        game = generate_game_for([Misdirection, FreezingTrap], Wolfrider,
                                 SpellTestingAgent, PredictableAgentWithoutHeroPower)

        for turn in range(0, 6):
            game.play_single_turn()
        # Misdirection was played first so it triggers first redirecting the atttack to the enemy hero, but
        # Freezing Trap triggers, bouncing the charging Wolfrider
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(8, len(game.players[1].hand))
        self.assertEqual(5, game.players[1].hand[7].mana_cost(game.players[1]))
        self.assertEqual(4, len(game.players[0].hand))
        self.assertEqual(30, game.other_player.hero.health)
        self.assertEqual(30, game.current_player.hero.health)
        # self.assertEqual(0, len(game.players[0].secrets))

        game.play_single_turn()  # Should be able to play both Misdirection and Freezing Trap again

        # self.assertEqual(3, len(game.players[0].hand))

    def test_Snipe(self):
        game = generate_game_for([MagmaRager, OasisSnapjaw, FeralSpirit], Snipe, SpellTestingAgent, SpellTestingAgent)

        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(0, len(game.current_player.minions))

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(3, game.current_player.minions[0].health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(3, len(game.current_player.minions))
        self.assertEqual(3, game.current_player.minions[0].health)
        self.assertEqual(3, game.current_player.minions[1].health)
        self.assertEqual(3, game.current_player.minions[2].health)

    def test_SavannahHighmane(self):
        game = generate_game_for(SavannahHighmane, SiphonSoul, MinionPlayingAgent, SpellTestingAgent)
        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Hyena", game.players[0].minions[0].card.name)
        self.assertEqual("Hyena", game.players[0].minions[1].card.name)

    def test_Houndmaster(self):
        game = generate_game_for([Houndmaster, StonetuskBoar], IronfurGrizzly, SpellTestingAgent, MinionPlayingAgent)
        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[0].health)
        self.assertEqual(3, game.players[1].minions[0].calculate_attack())
        self.assertEqual(3, game.players[1].minions[0].health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[0].health)
        self.assertEqual(3, game.players[0].minions[1].calculate_attack())
        self.assertEqual(3, game.players[0].minions[1].health)
        self.assertTrue(game.players[0].minions[1].taunt)
        self.assertEqual("Stonetusk Boar", game.players[0].minions[1].card.name)
        self.assertEqual(4, game.players[0].minions[2].calculate_attack())
        self.assertEqual(3, game.players[0].minions[2].health)

    def test_DeadlyShot(self):
        game = generate_game_for(DeadlyShot, SenjinShieldmasta, SpellTestingAgent, MinionPlayingAgent)
        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(7, len(game.players[0].hand))
        self.assertEqual(1, len(game.players[1].minions))
        # Can't use until a unit is on the field
        game.play_single_turn()

        self.assertEqual(7, len(game.players[0].hand))
        self.assertEqual(0, len(game.players[1].minions))

    def test_MultiShot(self):
        game = generate_game_for(MultiShot, SenjinShieldmasta, SpellTestingAgent, MinionPlayingAgent)
        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(8, len(game.players[0].hand))
        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(5, game.players[1].minions[0].health)
        self.assertEqual(5, game.players[1].minions[1].health)
        # Can't use until 2 units are on the field
        game.play_single_turn()

        self.assertEqual(8, len(game.players[0].hand))
        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(2, game.players[1].minions[0].health)
        self.assertEqual(2, game.players[1].minions[1].health)

    def test_ExplosiveShot(self):
        game = generate_game_for(IronfurGrizzly, ExplosiveShot, MinionPlayingAgent, SpellTestingAgent)
        for turn in range(0, 9):
            game.play_single_turn()

        game.players[1].agent.choose_target = lambda targets: targets[len(targets) - 2]
        self.assertEqual(3, len(game.players[0].minions))

        game.play_single_turn()
        # Explosive Shot the middle Grizzly
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual(1, game.players[0].minions[1].health)

    def test_KillCommand(self):
        game = generate_game_for([KillCommand, StonetuskBoar], StonetuskBoar, SelfSpellTestingAgent, MinionPlayingAgent)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(27, game.players[0].hero.health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(22, game.players[0].hero.health)

    def test_UnleashTheHounds(self):
        game = generate_game_for(UnleashTheHounds, StonetuskBoar, SpellTestingAgent, MinionPlayingAgent)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual("Hound", game.players[0].minions[0].card.name)
        self.assertEqual("Hound", game.players[0].minions[1].card.name)

    def test_StarvingBuzzard(self):
        game = generate_game_for(StarvingBuzzard, StonetuskBoar, MinionPlayingAgent, MinionPlayingAgent)
        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(4, len(game.players[0].hand))
        self.assertEqual(5, len(game.players[1].hand))

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(4, len(game.players[0].hand))
        self.assertEqual(5, len(game.players[1].hand))

        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(5, len(game.players[0].hand))
        self.assertEqual(5, len(game.players[1].hand))

    def test_BuzzardAndOwl(self):
        game = generate_game_for([StarvingBuzzard, IronbeakOwl], StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 7):
            game.play_single_turn()

        # The buzzard should be silenced, but only after drawing a card from the owl
        self.assertEqual(5, len(game.current_player.hand))
        self.assertEqual(0, len(game.current_player.minions[1].effects))

    def test_TundraRhino(self):
        game = generate_game_for([StonetuskBoar, OasisSnapjaw, TundraRhino], StonetuskBoar,
                                 PredictableAgentWithoutHeroPower, DoNothingBot)
        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(27, game.players[1].hero.health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(26, game.players[1].hero.health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(21, game.players[1].hero.health)
        self.assertTrue(game.players[0].minions[0].charge)
        self.assertTrue(game.players[0].minions[1].charge)
        self.assertTrue(game.players[0].minions[2].charge)

        game.players[0].minions[2].silence()
        self.assertTrue(game.players[0].minions[2].charge)

    def test_TundraRhino_with_silence(self):
        game = generate_game_for([StonetuskBoar, OasisSnapjaw, TundraRhino, Silence], StonetuskBoar,
                                 PredictableAgentWithoutHeroPower, DoNothingBot)
        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(26, game.players[1].hero.health)

        game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(23, game.players[1].hero.health)

        self.assertFalse(game.players[0].minions[0].charge)
        self.assertFalse(game.players[0].minions[1].charge)
        self.assertTrue(game.players[0].minions[2].charge)

    def test_AnimalCompanion(self):
        game = generate_game_for(AnimalCompanion, StonetuskBoar, SpellTestingAgent, DoNothingBot)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Leokk", game.players[0].minions[0].card.name)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Leokk", game.players[0].minions[0].card.name)
        self.assertEqual("Misha", game.players[0].minions[1].card.name)
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(5, game.players[0].minions[1].calculate_attack())

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual("Leokk", game.players[0].minions[0].card.name)
        self.assertEqual("Misha", game.players[0].minions[1].card.name)
        self.assertEqual("Huffer", game.players[0].minions[2].card.name)

    def test_ScavengingHyena(self):
        game = generate_game_for([ScavengingHyena, ScavengingHyena, Consecration], [StonetuskBoar, ShadowBolt],
                                 MinionPlayingAgent, OneSpellTestingAgent)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[1].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual(2, game.players[0].minions[1].health)

        game.play_single_turn()  # Kills 1 Hyena, other Hyena grows

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[0].health)

    def test_SnakeTrap(self):
        game = generate_game_for([SnakeTrap, IronfurGrizzly], BluegillWarrior,
                                 SpellTestingAgent, PredictableAgentWithoutHeroPower)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(1, len(game.players[0].secrets))

        game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(0, len(game.players[0].secrets))

    def test_Webspinner(self):
        game = generate_game_for(Webspinner, MortalCoil, MinionPlayingAgent, SpellTestingAgent)
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(4, len(game.other_player.hand))
        self.assertEqual(ScavengingHyena, type(game.other_player.hand[3]))

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(5, len(game.other_player.hand))
        self.assertEqual(SilverbackPatriarch, type(game.other_player.hand[4]))

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(6, len(game.other_player.hand))
        self.assertEqual(IronbeakOwl, type(game.other_player.hand[5]))

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(7, len(game.other_player.hand))
        self.assertEqual(DireWolfAlpha, type(game.other_player.hand[6]))

        # Skip over the hyena

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(8, len(game.other_player.hand))
        self.assertEqual(IronbeakOwl, type(game.other_player.hand[7]))

        # Skip over the Patriarch
        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(9, len(game.other_player.hand))
        self.assertEqual(KingMukla, type(game.other_player.hand[8]))

        # Skip over the Ironbeak Owl
        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(10, len(game.other_player.hand))
        self.assertEqual(ScavengingHyena, type(game.other_player.hand[9]))

        # Skip over the Wolf
        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(10, len(game.other_player.hand))
        self.assertEqual(IronfurGrizzly, type(game.other_player.hand[9]))
