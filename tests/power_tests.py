import random
import unittest

from hearthbreaker.agents.basic_agents import PredictableAgent, DoNothingAgent
from tests.agents.testing_agents import CardTestingAgent
from hearthbreaker.cards import HuntersMark, MogushanWarden, AvengingWrath, CircleOfHealing, AlAkirTheWindlord, Shadowform, \
    DefiasRingleader, Doomguard, ArcaneIntellect, Swipe, ArathiWeaponsmith, MassDispel
from hearthbreaker.powers import MindSpike, MindShatter
from tests.testing_utils import generate_game_for


class TestPowers(unittest.TestCase):
    def setUp(self):
        random.seed(1857)

    def test_DruidPower(self):
        game = generate_game_for(Swipe, MogushanWarden, PredictableAgent, DoNothingAgent)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, game.players[0].hero.armor)
        self.assertEqual(29, game.players[1].hero.health)

    def test_HunterPower(self):
        game = generate_game_for(HuntersMark, MogushanWarden, PredictableAgent, DoNothingAgent)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(28, game.other_player.hero.health)

    def test_MagePower(self):
        game = generate_game_for(ArcaneIntellect, MogushanWarden, PredictableAgent, DoNothingAgent)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(29, game.players[1].hero.health)

    def test_PaladinPower(self):
        game = generate_game_for(AvengingWrath, MogushanWarden, PredictableAgent, DoNothingAgent)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].calculate_attack())
        self.assertEqual(1, game.current_player.minions[0].health)
        self.assertEqual("Silver Hand Recruit", game.current_player.minions[0].card.name)

    def test_PriestPower(self):
        game = generate_game_for(CircleOfHealing, MogushanWarden, PredictableAgent, DoNothingAgent)

        game.players[1].hero.health = 20

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(22, game.players[1].hero.health)

    def test_MindSpike(self):
        game = generate_game_for(Shadowform, MogushanWarden, PredictableAgent, DoNothingAgent)

        game.players[0].hero.power = MindSpike(game.players[0].hero)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(28, game.players[1].hero.health)

    def test_MindShatter(self):
        game = generate_game_for(Shadowform, Shadowform, PredictableAgent, DoNothingAgent)

        game.players[0].hero.power = MindShatter(game.players[0].hero)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(27, game.players[1].hero.health)

    def test_RoguePower(self):
        game = generate_game_for(DefiasRingleader, MogushanWarden, PredictableAgent, DoNothingAgent)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, game.players[0].hero.weapon.base_attack)
        self.assertEqual(1, game.players[0].hero.weapon.durability)
        self.assertEqual(29, game.players[1].hero.health)

    def test_ShamanPower(self):
        game = generate_game_for(AlAkirTheWindlord, MassDispel, PredictableAgent, CardTestingAgent)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Stoneclaw Totem", game.players[0].minions[0].card.name)
        self.assertTrue(game.players[0].minions[0].taunt)

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Healing Totem", game.players[0].minions[1].card.name)

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual("Searing Totem", game.players[0].minions[2].card.name)

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(4, len(game.players[0].minions))
        self.assertEqual("Wrath of Air Totem", game.players[0].minions[3].card.name)
        self.assertEqual(1, game.players[0].spell_damage)

        # All Totems are out, nothing should be summoned
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(4, len(game.players[0].minions))

    def test_WarlockPower(self):
        game = generate_game_for(Doomguard, MogushanWarden, PredictableAgent, DoNothingAgent)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(28, game.players[0].hero.health)
        self.assertEqual(6, len(game.players[0].hand))

    def test_WarriorPower(self):
        game = generate_game_for(ArathiWeaponsmith, MogushanWarden, PredictableAgent, DoNothingAgent)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(2, game.players[0].hero.armor)

    def test_double_power_use(self):
        testing_env = self

        class PowerTestingAgent(DoNothingAgent):
            def __init__(self):
                super().__init__()
                self.turn = 0

            def do_turn(self, player):
                self.turn += 1
                if self.turn is 4:
                    player.hero.power.use()
                    testing_env.assertFalse(player.hero.power.can_use())
                elif self.turn is 7:
                    player.hero.power.use()
                    player.game.play_card(player.hand[0])
                    testing_env.assertTrue(player.hero.power.can_use())

        game = generate_game_for(Shadowform, MogushanWarden, PowerTestingAgent, DoNothingAgent)
        for turn in range(0, 13):
            game.play_single_turn()
