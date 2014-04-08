from unittest.mock import Mock, call
from hsgame.agents.basic_agents import DoNothingBot
from hsgame.game_objects import Game
from tests.testing_agents import *

__author__ = 'Daniel'

import random
from tests.testing_utils import check_mana_cost, generate_game_for, StackedDeck
from hsgame.cards.spells.druid import *
from hsgame.cards.minions import *
import unittest


class TestSpells(unittest.TestCase):

    def setUp(self):
        random.seed(1857)

    @check_mana_cost(-8)  # This spell costs 0, but adds two mana, making it effectively a cost of -2 each time it
                          # is called.
    def test_Innervate(self):
        game = generate_game_for(Innervate, StonetuskBoar, SelfSpellTestingAgent, DoNothingBot)
        #triggers all four innervate cards the player is holding.
        game.play_single_turn()
        self.assertEqual(9, game.current_player.mana)
        return game

    @check_mana_cost(0)
    def test_Moonfire(self):
        game = generate_game_for(Moonfire, StonetuskBoar, EnemySpellTestingAgent, MinionPlayingAgent)
        game.play_single_turn()
        self.assertEqual(26, game.other_player.health)
        return game

    @check_mana_cost(1)
    def test_Claw(self):
        testing_env = self

        class ClawAgent(EnemySpellTestingAgent):
            def do_turn(self, player):
                super().do_turn(player)
                testing_env.assertEqual(2, self.game.current_player.attack_power)
                testing_env.assertEqual(2, self.game.current_player.armour)

        game = generate_game_for(Claw, StonetuskBoar, ClawAgent, MinionPlayingAgent)
        game.play_single_turn()
        return game

    @check_mana_cost(1)
    def test_Naturalize(self):
        game = generate_game_for(StonetuskBoar, Naturalize, MinionPlayingAgent, EnemyMinionSpellTestingAgent)
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(5, len(game.other_player.hand))
        return game

    def test_Savagery(self):

        class SavageryAgent(EnemyMinionSpellTestingAgent):
            def do_turn(self, player):
                if player.mana > 2:
                    player.power.use()
                    super().do_turn(player)

        game = generate_game_for(Savagery, BloodfenRaptor, SavageryAgent, MinionPlayingAgent)

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(1, game.other_player.minions[0].defense)

    def test_ClawAndSavagery(self):
        deck1 = StackedDeck([BloodfenRaptor()], CHARACTER_CLASS.PRIEST)
        deck2 = StackedDeck([Claw(), Claw(), Savagery()], CHARACTER_CLASS.DRUID)
        game = Game([deck1, deck2], [MinionPlayingAgent(), EnemyMinionSpellTestingAgent()])
        game.current_player = game.players[1]
        game.pre_game()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))

        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))







    @check_mana_cost(2)
    def test_MarkOfTheWild(self):
        game = generate_game_for(MarkOfTheWild, StonetuskBoar, EnemyMinionSpellTestingAgent, MinionPlayingAgent)
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(3, game.other_player.minions[0].attack_power)
        self.assertEqual(3, game.other_player.minions[0].defense)
        self.assertEqual(3, game.other_player.minions[0].max_defense)

        #Test that this spell is being silenced properly as well
        game.other_player.minions[0].silence()
        self.assertEqual(1, game.other_player.minions[0].attack_power)
        self.assertEqual(1, game.other_player.minions[0].defense)
        self.assertEqual(1, game.other_player.minions[0].max_defense)


        return game
    @check_mana_cost(2)
    def test_PowerOfTheWild(self):
        deck1 = StackedDeck([StonetuskBoar(), StonetuskBoar(), PowerOfTheWild()], CHARACTER_CLASS.DRUID)
        deck2 = StackedDeck([StonetuskBoar()], CHARACTER_CLASS.MAGE)







        #This is a test of the +1/+1 option of the Power Of the Wild Card
        game = Game([deck1, deck2], [MinionPlayingAgent(), MinionPlayingAgent()])
        game.current_player = game.players[1]

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(2, game.current_player.minions[0].attack_power)
        self.assertEqual(2, game.current_player.minions[0].defense)
        self.assertEqual(2, game.current_player.minions[0].max_defense)
        self.assertEqual(2, game.current_player.minions[1].attack_power)
        self.assertEqual(2, game.current_player.minions[1].max_defense)

        #This is a test of the "Summon Panther" option of the Power of the Wild Card

        agent = MinionPlayingAgent()
        agent.choose_option = Mock(side_effect=lambda *options: options[1])

        deck1 = StackedDeck([StonetuskBoar(), StonetuskBoar(), PowerOfTheWild()], CHARACTER_CLASS.DRUID)
        deck2 = StackedDeck([StonetuskBoar()], CHARACTER_CLASS.MAGE)
        game = Game([deck1, deck2], [agent, MinionPlayingAgent()])
        game.current_player = game.players[1]

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual("Panther", game.current_player.minions[2].card.__class__.__name__)
        self.assertEqual(3, game.current_player.minions[2].attack_power)
        self.assertEqual(2, game.current_player.minions[2].max_defense)

        return game


    @check_mana_cost(3)  # Although this spell costs 2, it affects the max_mana, which throws off the check
    def test_WildGrowth(self):
        game = generate_game_for(WildGrowth, StonetuskBoar, SelfSpellTestingAgent, DoNothingBot)
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(3, game.current_player.max_mana)
        return game

    @check_mana_cost(3)
    def test_HealingTouch(self):
        game = generate_game_for(HealingTouch, StonetuskBoar, SelfSpellTestingAgent, DoNothingBot)
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.other_player.health = 20
        game.play_single_turn()
        self.assertEqual(28, game.current_player.health)
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(30, game.current_player.health)
        return game

    @check_mana_cost(3)
    def test_MarkOfNature(self):
        deck1 = StackedDeck([StonetuskBoar(), StonetuskBoar(), MarkOfNature()], CHARACTER_CLASS.DRUID)
        deck2 = StackedDeck([StonetuskBoar()], CHARACTER_CLASS.MAGE)
        game = Game([deck1, deck2], [MinionPlayingAgent(), MinionPlayingAgent()])

        game.current_player = 1
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(5, game.other_player.minions[0].attack_power)

        def mock_choose(*options):
            return options[1]
        deck1 = StackedDeck([StonetuskBoar(), StonetuskBoar(), MarkOfNature()], CHARACTER_CLASS.DRUID)
        deck2 = StackedDeck([StonetuskBoar()], CHARACTER_CLASS.MAGE)
        agent = MinionPlayingAgent()
        agent.choose_option = Mock(side_effect=mock_choose)
        game = Game([deck1, deck2], [agent, MinionPlayingAgent()])

        game.current_player = 1
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(5, game.other_player.minions[0].max_defense)
        self.assertEqual(5, game.other_player.minions[0].defense)
        self.assertTrue(game.other_player.minions[0].taunt)

        return game

    def test_SavageRoar(self):
        deck1 = StackedDeck([StonetuskBoar(), StonetuskBoar(), SavageRoar()], CHARACTER_CLASS.DRUID)
        deck2 = StackedDeck([StonetuskBoar()], CHARACTER_CLASS.MAGE)
        game = Game([deck1, deck2], [MinionPlayingAgent(), MinionPlayingAgent()])

        game.current_player = 1
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        minion_increase_mock = Mock()

        game.other_player.minions[0].bind("attack_increased", minion_increase_mock)
        game.other_player.minions[1].bind("attack_increased", minion_increase_mock)

        player_increase_mock = Mock()

        game.other_player.bind("attack_increased", player_increase_mock)


        game.play_single_turn()

        self.assertEqual(0, game.current_player.mana)

        #Make sure the attack got increased
        self.assertListEqual([call(2), call(2)], minion_increase_mock.call_args_list)
        self.assertListEqual([call(2)], player_increase_mock.call_args_list)

        #And make sure that it went down again
        self.assertEqual(0, game.current_player.minions[0].temp_attack)
        self.assertEqual(0, game.current_player.minions[1].temp_attack)
        self.assertEqual(0, game.current_player.attack_power)

        return game
