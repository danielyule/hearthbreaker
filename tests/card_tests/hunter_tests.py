import random
import unittest

from hearthbreaker.agents.basic_agents import DoNothingAgent, PredictableAgent
from hearthbreaker.constants import MINION_TYPE
from tests.agents.testing_agents import CardTestingAgent, OneCardPlayingAgent, WeaponTestingAgent, \
    PlayAndAttackAgent, SelfSpellTestingAgent
from tests.testing_utils import generate_game_for, mock
from hearthbreaker.cards import *


class TestHunter(unittest.TestCase):
    def setUp(self):
        random.seed(1857)

    def test_HuntersMark(self):
        game = generate_game_for(HuntersMark, MogushanWarden, CardTestingAgent, OneCardPlayingAgent)

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
                                 StonetuskBoar, CardTestingAgent, DoNothingAgent)
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
        game = generate_game_for(ArcaneShot, StonetuskBoar, CardTestingAgent, DoNothingAgent)
        game.players[0].spell_damage = 1
        game.play_single_turn()
        self.assertEqual(27, game.other_player.hero.health)

    def test_BestialWrath(self):

        def verify_bwrath():
            self.assertEqual(5, game.players[0].minions[0].calculate_attack())
            self.assertTrue(game.players[0].minions[0].immune)

        def verify_silence():
            self.assertFalse(game.players[0].minions[0].immune)
            self.assertEqual(1, game.players[0].minions[0].calculate_attack())

        game = generate_game_for([StonetuskBoar, BestialWrath, BestialWrath, BestialWrath, Silence, Archmage], Wisp,
                                 CardTestingAgent, DoNothingAgent)
        game.play_single_turn()
        game.play_single_turn()

        game.players[0].bind_once("turn_ended", verify_bwrath)

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertFalse(game.players[0].minions[0].immune)
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())

        game.play_single_turn()
        game.players[0].bind_once("turn_ended", verify_silence)
        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertFalse(game.players[0].minions[0].immune)
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(1, len(game.players[0].hand))

    def test_Flare(self):

        game = generate_game_for(Vaporize, [WorgenInfiltrator, WorgenInfiltrator],
                                 CardTestingAgent, CardTestingAgent)

        for turn in range(0, 5):
            game.play_single_turn()

        # Vaporize is in place and two Infiltrators are down
        self.assertEqual(1, len(game.current_player.secrets))
        self.assertEqual(3, len(game.other_player.minions))
        self.assertTrue(game.other_player.minions[0].stealth)
        self.assertTrue(game.other_player.minions[1].stealth)
        self.assertEqual(4, len(game.other_player.hand))

        old_play = game.other_player.agent.do_turn

        def _play_and_attack(player):
            flare = Flare()
            flare.target = None
            flare.use(player, player.game)
            old_play(player)
            player.minions[4].attack()

        game.other_player.agent.do_turn = _play_and_attack
        game.play_single_turn()

        # All of the Worgens should still be alive, because Vaporize is gone.
        self.assertEqual(0, len(game.other_player.secrets))
        self.assertEqual(7, len(game.current_player.minions))
        for minion in game.current_player.minions[4:]:
            self.assertFalse(minion.stealth)

    def test_EaglehornBow(self):
        game = generate_game_for([Snipe, EaglehornBow], StonetuskBoar, PlayAndAttackAgent,
                                 OneCardPlayingAgent)

        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(1, game.players[0].weapon.durability)
        self.assertEqual(3, game.players[0].weapon.base_attack)

        # Snipe should trigger, granting our weapon +1 durability
        game.play_single_turn()

        self.assertEqual(2, game.players[0].weapon.durability)
        self.assertEqual(3, game.players[0].weapon.base_attack)

    def test_GladiatorsLongbow(self):
        game = generate_game_for(GladiatorsLongbow, WaterElemental, WeaponTestingAgent,
                                 OneCardPlayingAgent)
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
                                 StonetuskBoar, CardTestingAgent, DoNothingAgent)

        game.players[0].agent.choose_option = lambda options, player: options[0]
        game.play_single_turn()
        self.assertEqual(4, len(game.current_player.hand))
        self.assertEqual("Stonetusk Boar", game.current_player.hand[3].name)
        self.assertEqual(23, game.current_player.deck.left)

    def test_ExplosiveTrap(self):
        game = generate_game_for(ExplosiveTrap, StonetuskBoar, CardTestingAgent, PlayAndAttackAgent)

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
        game = generate_game_for(ExplosiveTrap, Frostbolt, CardTestingAgent, CardTestingAgent)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(1, len(game.other_player.secrets))
        self.assertEqual(30, game.current_player.hero.health)
        self.assertEqual(27, game.other_player.hero.health)

    def test_FreezingTrap(self):
        game = generate_game_for(FreezingTrap, BluegillWarrior, CardTestingAgent, PlayAndAttackAgent)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(4, len(game.players[0].hand))
        self.assertEqual(7, len(game.players[1].hand))
        self.assertEqual(4, game.players[1].hand[6].mana_cost())
        self.assertEqual(0, len(game.players[0].secrets))
        self.assertEqual(30, game.players[0].hero.health)
        game.play_single_turn()
        self.assertEqual(4, len(game.players[0].hand))
        game.play_single_turn()
        self.assertEqual(0, len(game.current_player.minions))
        self.assertEqual(30, game.players[0].hero.health)
        self.assertEqual(8, len(game.players[1].hand))
        self.assertEqual(4, game.players[1].hand[5].mana_cost())
        self.assertEqual(4, game.players[1].hand[7].mana_cost())

    def test_FreezingTrap_many_cards(self):
        class FreezingTrapAgent(DoNothingAgent):
            def do_turn(self, player):
                if player.mana == 6:
                    game.play_card(player.hand[0])
                if player.mana == 7:
                    player.minions[0].attack()
        game = generate_game_for(FreezingTrap, BoulderfistOgre, CardTestingAgent, FreezingTrapAgent)

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
                self.assertEqual(6, card.mana_cost())
        self.assertEqual(30, game.other_player.hero.health)
        death_mock.assert_called_once_with(None)

    def test_Misdirection(self):
        game = generate_game_for(Misdirection, StonetuskBoar, CardTestingAgent, PlayAndAttackAgent)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(28, game.other_player.hero.health)
        self.assertEqual(1, len(game.current_player.minions))  # The boar has been misdirected into another boar
        self.assertEqual(30, game.current_player.hero.health)

    def test_MisdirectionToHero(self):
        game = generate_game_for(Misdirection, BluegillWarrior, CardTestingAgent, PlayAndAttackAgent)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(30, game.other_player.hero.health)  # The murloc should be misdirected
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(28, game.current_player.hero.health)

    def test_FreezingTrapAndMisdirection(self):
        game = generate_game_for([Misdirection, FreezingTrap], Wolfrider,
                                 CardTestingAgent, PlayAndAttackAgent)

        for turn in range(0, 6):
            game.play_single_turn()
        # Misdirection was played first so it triggers first redirecting the atttack to the enemy hero, but
        # Freezing Trap triggers, bouncing the charging Wolfrider
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(8, len(game.players[1].hand))
        self.assertEqual(5, game.players[1].hand[7].mana_cost())
        self.assertEqual(4, len(game.players[0].hand))
        self.assertEqual(30, game.other_player.hero.health)
        self.assertEqual(30, game.current_player.hero.health)
        self.assertEqual(0, len(game.players[0].secrets))

        game.play_single_turn()  # Should be able to play both Misdirection and Freezing Trap again

        self.assertEqual(3, len(game.players[0].hand))

    def test_Snipe(self):
        game = generate_game_for([MagmaRager, OasisSnapjaw, FeralSpirit], Snipe, CardTestingAgent, CardTestingAgent)

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

    def test_ExplosiveTrap_hero(self):
        game = generate_game_for(ExplosiveTrap, Naturalize, OneCardPlayingAgent, PredictableAgent)
        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.secrets))
        self.assertEqual(30, game.current_player.hero.health)
        self.assertEqual(30, game.other_player.hero.health)

        game.play_single_turn()
        self.assertEqual(0, len(game.other_player.secrets))
        self.assertEqual(29, game.current_player.hero.health)
        self.assertEqual(29, game.other_player.hero.health)

    def test_SavannahHighmane(self):
        game = generate_game_for(SavannahHighmane, SiphonSoul, OneCardPlayingAgent, CardTestingAgent)
        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Hyena", game.players[0].minions[0].card.name)
        self.assertEqual("Hyena", game.players[0].minions[1].card.name)

    def test_Houndmaster(self):
        game = generate_game_for([Houndmaster, StonetuskBoar], IronfurGrizzly, CardTestingAgent, OneCardPlayingAgent)
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
        game = generate_game_for(DeadlyShot, SenjinShieldmasta, CardTestingAgent, OneCardPlayingAgent)
        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(7, len(game.players[0].hand))
        self.assertEqual(1, len(game.players[1].minions))
        # Can't use until a unit is on the field
        game.play_single_turn()

        self.assertEqual(7, len(game.players[0].hand))
        self.assertEqual(0, len(game.players[1].minions))

    def test_MultiShot(self):
        game = generate_game_for(MultiShot, SenjinShieldmasta, CardTestingAgent, OneCardPlayingAgent)
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
        game = generate_game_for(IronfurGrizzly, ExplosiveShot, OneCardPlayingAgent, CardTestingAgent)
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
        game = generate_game_for([KillCommand, StonetuskBoar], StonetuskBoar,
                                 SelfSpellTestingAgent, OneCardPlayingAgent)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(27, game.players[0].hero.health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(22, game.players[0].hero.health)

    def test_UnleashTheHounds(self):
        game = generate_game_for(UnleashTheHounds, StonetuskBoar, CardTestingAgent, OneCardPlayingAgent)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual("Hound", game.players[0].minions[0].card.name)
        self.assertEqual("Hound", game.players[0].minions[1].card.name)

    def test_StarvingBuzzard(self):
        game = generate_game_for(StarvingBuzzard, StonetuskBoar, OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(4, len(game.players[1].minions))
        self.assertEqual(7, len(game.players[0].hand))
        self.assertEqual(5, len(game.players[1].hand))

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(5, len(game.players[1].minions))
        self.assertEqual(7, len(game.players[0].hand))
        self.assertEqual(4, len(game.players[1].hand))

        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(5, len(game.players[1].minions))
        self.assertEqual(8, len(game.players[0].hand))
        self.assertEqual(4, len(game.players[1].hand))

    def test_BuzzardAndOwl(self):
        game = generate_game_for([StarvingBuzzard, IronbeakOwl], StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

        for turn in range(0, 11):
            game.play_single_turn()

        # The buzzard should be silenced, but only after drawing a card from the owl
        self.assertEqual(8, len(game.current_player.hand))
        self.assertEqual(0, len(game.current_player.minions[1].effects))

    def test_TundraRhino(self):
        game = generate_game_for([StonetuskBoar, OasisSnapjaw, TundraRhino], StonetuskBoar,
                                 PlayAndAttackAgent, DoNothingAgent)
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
        self.assertTrue(game.players[0].minions[0].charge())
        self.assertTrue(game.players[0].minions[1].charge())
        self.assertTrue(game.players[0].minions[2].charge())

        game.players[0].minions[2].silence()
        self.assertTrue(game.players[0].minions[2].charge())

    def test_TundraRhino_with_silence(self):
        game = generate_game_for([StonetuskBoar, OasisSnapjaw, TundraRhino, Silence], StonetuskBoar,
                                 PlayAndAttackAgent, DoNothingAgent)
        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(26, game.players[1].hero.health)

        game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(23, game.players[1].hero.health)

        self.assertFalse(game.players[0].minions[0].charge())
        self.assertFalse(game.players[0].minions[1].charge())
        self.assertTrue(game.players[0].minions[2].charge())

    def test_AnimalCompanion(self):
        game = generate_game_for(AnimalCompanion, StonetuskBoar, CardTestingAgent, DoNothingAgent)
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
                                 OneCardPlayingAgent, OneCardPlayingAgent)
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
                                 CardTestingAgent, PlayAndAttackAgent)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(1, len(game.players[0].secrets))

        game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(0, len(game.players[0].secrets))

    def test_SnakeTrap_full_board(self):
        game = generate_game_for([SnakeTrap, Onyxia], KingKrush, CardTestingAgent, PlayAndAttackAgent)

        for turn in range(0, 17):
            game.play_single_turn()

        self.assertEqual(7, len(game.current_player.minions))
        self.assertEqual(1, len(game.current_player.secrets))
        self.assertEqual(0, len(game.other_player.minions))

        game.play_single_turn()     # Player 2 will play King Krush, which will charge a whelp
        self.assertEqual(1, len(game.other_player.secrets))  # The snake trap will not be proced as the board is full
        self.assertEqual(6, len(game.other_player.minions))
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(30, game.other_player.hero.health)

    def test_Webspinner(self):
        game = generate_game_for(Webspinner, MortalCoil, OneCardPlayingAgent, CardTestingAgent)
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(4, len(game.other_player.hand))
        self.assertEqual(MINION_TYPE.BEAST, game.other_player.hand[3].minion_type)

    def test_CallPet(self):
        game = generate_game_for([CallPet, CallPet, MoltenGiant, MoltenGiant, MoltenGiant, KingKrush, MoltenGiant,
                                  MoltenGiant], MortalCoil, CardTestingAgent, DoNothingAgent)
        for turn in range(0, 4):
            game.play_single_turn()

        # King Krush should cost 4 less (9 - 4 = 5)
        self.assertEqual(5, len(game.players[0].hand))
        self.assertEqual(5, game.players[0].hand[4].mana_cost())

        for turn in range(0, 2):
            game.play_single_turn()

        # Molten Giant should not be affected since it's not a beast
        self.assertEqual(20, game.players[0].hand[5].mana_cost())

    def test_CobraShot(self):
        game = generate_game_for(CobraShot, StonetuskBoar, CardTestingAgent, CardTestingAgent)
        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(30, game.players[1].hero.health)
        self.assertEqual(7, len(game.players[1].minions))

        game.play_single_turn()

        self.assertEqual(27, game.players[1].hero.health)
        self.assertEqual(6, len(game.players[1].minions))

    def test_Glaivezooka(self):
        game = generate_game_for([StonetuskBoar, Glaivezooka], StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())

        game.play_single_turn()

        self.assertEqual(2, game.players[0].weapon.base_attack)
        self.assertEqual(2, game.players[0].weapon.durability)
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())

    def test_MetaltoothLeaper(self):
        game = generate_game_for([MetaltoothLeaper, Wisp], SpiderTank, OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[1].calculate_attack())
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(3, game.players[1].minions[1].calculate_attack())
        self.assertEqual(3, game.players[1].minions[0].calculate_attack())

        # The second leaper will buff the first, but won't be buffed by anything
        game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[0].calculate_attack())
        self.assertEqual(1, game.players[0].minions[1].calculate_attack())
        self.assertEqual(5, game.players[0].minions[2].calculate_attack())

    def test_KingOfBeasts(self):
        game = generate_game_for([StonetuskBoar, StonetuskBoar, StonetuskBoar, KingOfBeasts], StonetuskBoar,
                                 OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(9):
            game.play_single_turn()

        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.minions[0].calculate_attack())

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(5, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.minions[1].calculate_attack())

    def test_Gahzrilla(self):
        game = generate_game_for([Gahzrilla, ShatteredSunCleric, RaidLeader], ArcaneExplosion,
                                 OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(13):
            game.play_single_turn()

        self.assertEqual(6, game.current_player.minions[0].calculate_attack())

        game.play_single_turn()

        # Arcane explosion damages the Gahz'rilla, doubling its attack
        self.assertEqual(12, game.other_player.minions[0].calculate_attack())

        # The buff from the cleric is applies after the double, increases by 1
        game.play_single_turn()
        self.assertEqual(13, game.current_player.minions[1].calculate_attack())

        # Should double exactly the current attack
        game.play_single_turn()
        self.assertEqual(26, game.other_player.minions[1].calculate_attack())

        # Raid leader gives a +1 Bonus
        game.play_single_turn()
        self.assertEqual(27, game.current_player.minions[2].calculate_attack())

        # The raid leader's aura is not included in the double, but is applied afterwards
        # Tested by @jleclanche for patch 2.1.0.7785
        game.play_single_turn()
        self.assertEqual(53, game.other_player.minions[1].calculate_attack())

    def testGahzrilla_temp_buff(self):
        env = self

        class TestAgent(CardTestingAgent):
            def do_turn(self, player):
                super().do_turn(player)
                if turn == 14:
                    # Gahz'rilla's double comes after the buff from abusive, so total attack is
                    # (6 + 2) * 2 = 16
                    env.assertEqual(16, game.current_player.minions[0].calculate_attack())

        game = generate_game_for([Gahzrilla, AbusiveSergeant, Hellfire], StonetuskBoar,
                                 TestAgent, DoNothingAgent)

        for turn in range(15):
            game.play_single_turn()

        # After the buff wears off, the double no longer includes it, so the total attack is
        # 6 * 2 = 12
        # Tested by @jleclanche for patch 2.1.0.7785
        self.assertEqual(12, game.current_player.minions[0].calculate_attack())

    def test_ogre_misdirection(self):
        game = generate_game_for(OgreBrute, Misdirection, PlayAndAttackAgent, OneCardPlayingAgent)
        random.seed(1850)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(26, game.players[0].hero.health)
        self.assertEqual(30, game.players[1].hero.health)

    def test_FeignDeath(self):
        game = generate_game_for([HauntedCreeper, LootHoarder, Malorne, FeignDeath], StonetuskBoar,
                                 OneCardPlayingAgent, DoNothingAgent)

        for turn in range(14):
            game.play_single_turn()

        self.assertEqual(3, len(game.other_player.minions))
        self.assertEqual(7, len(game.other_player.hand))

        game.play_single_turn()
        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual(8, len(game.current_player.hand))

    def test_SteamwheedleSniper(self):
        game = generate_game_for(SteamwheedleSniper, StonetuskBoar, PredictableAgent, DoNothingAgent)
        for turn in range(9):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(22, game.other_player.hero.health)
        self.assertEqual(1, game.current_player.minions[1].health)
        self.assertEqual(3, game.current_player.minions[0].health)

    def test_Quickshot(self):
        game = generate_game_for(QuickShot, Wisp, CardTestingAgent, CardTestingAgent)
        for turn in range(2):
            game.play_single_turn()
        self.assertEqual(5, len(game.players[1].minions))
        self.assertEqual(4, len(game.players[0].hand))

        game.play_single_turn()
        # We should have played a quick shot and not drawn a card
        self.assertEqual(30, game.players[1].hero.health)
        self.assertEqual(4, len(game.players[1].minions))
        self.assertEqual(4, len(game.players[0].hand))

        game.play_single_turn()
        game.play_single_turn()
        # We should have played a quick shot and not drawn a card
        self.assertEqual(30, game.players[1].hero.health)
        self.assertEqual(4, len(game.players[1].minions))
        self.assertEqual(4, len(game.players[0].hand))

        game.play_single_turn()
        game.play_single_turn()
        # We should have played two shots and not drawn a card
        self.assertEqual(30, game.players[1].hero.health)
        self.assertEqual(3, len(game.players[1].minions))
        self.assertEqual(3, len(game.players[0].hand))

        game.play_single_turn()
        game.play_single_turn()
        # We should have played two shots and not drawn a card
        self.assertEqual(30, game.players[1].hero.health)
        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(2, len(game.players[0].hand))

        game.play_single_turn()
        game.play_single_turn()
        # We should have played three shots and not drawn a card
        self.assertEqual(30, game.players[1].hero.health)
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(1, len(game.players[0].hand))

        game.play_single_turn()
        game.play_single_turn()
        # We should have played three shots, one of which was drawn, and have one card left over
        self.assertEqual(24, game.players[1].hero.health)
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(1, len(game.players[0].hand))

    def test_CoreRager(self):
        game = generate_game_for([CoreRager, Deathwing], Wisp, OneCardPlayingAgent, DoNothingAgent)
        for turn in range(18):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        self.assertEqual(4, game.players[0].minions[0].health)

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))  # Deathwing discards whole hand
        self.assertEqual(12, game.players[0].minions[0].calculate_attack())
        self.assertEqual(12, game.players[0].minions[0].health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))  # Deathwing the sequel
        self.assertEqual(12, game.players[0].minions[0].calculate_attack())
        self.assertEqual(12, game.players[0].minions[0].health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))  # Core Rager activates battlecry
        self.assertEqual(7, game.players[0].minions[0].calculate_attack())
        self.assertEqual(7, game.players[0].minions[0].health)

    def test_Acidmaw(self):
        game = generate_game_for([Acidmaw, ArcaneExplosion, InjuredBlademaster], OasisSnapjaw,
                                 CardTestingAgent, OneCardPlayingAgent)

        for turn in range(14):
            game.play_single_turn()

        # Three snapjaws
        self.assertEqual(4, len(game.current_player.minions))

        # One Acidmaw
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual("Acidmaw", game.other_player.minions[0].card.name)

        game.play_single_turn()
        # The snapjaws are dead from the arcane explosion
        self.assertEqual(0, len(game.other_player.minions))

        # The blademaster dies as well.
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Acidmaw", game.current_player.minions[0].card.name)

    def test_BearTrap(self):
        game = generate_game_for(BearTrap, StonetuskBoar, CardTestingAgent, PlayAndAttackAgent)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(1, len(game.players[0].secrets))

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[0].secrets))

    def test_BearTrap_full_board(self):
        game = generate_game_for([BearTrap, Onyxia], KingKrush, CardTestingAgent, PlayAndAttackAgent)

        for turn in range(0, 17):
            game.play_single_turn()

        self.assertEqual(7, len(game.current_player.minions))
        self.assertEqual(1, len(game.current_player.secrets))
        self.assertEqual(0, len(game.other_player.minions))

        game.other_player.agent.choose_target = lambda x: game.players[0].hero

        game.play_single_turn()     # Player 2 will play King Krush, which will charge the enemy hero's face
        self.assertEqual(1, len(game.other_player.secrets))  # The bear trap will not be proced as the board is full
        self.assertEqual(7, len(game.other_player.minions))
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(22, game.other_player.hero.health)

    def test_Powershot(self):
        game = generate_game_for(ManaWyrm, Powershot, OneCardPlayingAgent, CardTestingAgent)
        for turn in range(0, 5):
            game.play_single_turn()

        game.players[1].agent.choose_target = lambda targets: targets[len(targets) - 2]
        self.assertEqual(3, len(game.players[0].minions))

        game.play_single_turn()

        # Powershot the middle Wyrm
        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual(1, game.players[0].minions[1].health)
        self.assertEqual(1, game.players[0].minions[2].health)
