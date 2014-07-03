import random
import unittest
from hsgame.agents.basic_agents import PredictableBot, DoNothingBot
from hsgame.cards import HuntersMark, MogushanWarden, AvengingWrath, CircleOfHealing, AlAkirTheWindlord
from tests.testing_utils import generate_game_for


class TestPowers(unittest.TestCase):
    def setUp(self):
        random.seed(1857)

    def test_hunter_power(self):
        game = generate_game_for(HuntersMark, MogushanWarden, PredictableBot, DoNothingBot)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(28, game.other_player.hero.health)

    def test_PaladinPower(self):
        game = generate_game_for(AvengingWrath, MogushanWarden, PredictableBot, DoNothingBot)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].attack_power)
        self.assertEqual(1, game.current_player.minions[0].health)
        self.assertEqual("Silver Hand Recruit", game.current_player.minions[0].card.name)

    def test_PriestPower(self):
        game = generate_game_for(CircleOfHealing, MogushanWarden, PredictableBot, DoNothingBot)

        game.players[1].hero.health = 20

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(22, game.players[1].hero.health)

    def test_ShamanPower(self):
        game = generate_game_for(AlAkirTheWindlord, MogushanWarden, PredictableBot, DoNothingBot)

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
        self.assertEqual(1, game.players[0].minions[3].spell_damage)

        # All Totems are out, nothing should be summoned
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(4, len(game.players[0].minions))