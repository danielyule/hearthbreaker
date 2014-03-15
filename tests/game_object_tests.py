import copy
from hsgame.agents.basic_agents import DoNothingBot
from hsgame.constants import CHARACTER_CLASS


__author__ = 'Daniel'
import random
import unittest
from unittest.mock import Mock, call

from hsgame.cards.minions import StonetuskBoar, NoviceEngineer
from hsgame.cards.spells import *
from hsgame.game_objects import Player, Game, Deck, Bindable

from tests.testing_agents import SelfSpellTestingAgent, EnemySpellTestingAgent, MinionPlayingAgent, EnemyMinionSpellTestingAgent


class StackedDeck(Deck):

    def __init__(self, card_pattern, character_class):
        cards = []
        while len(cards) + len(card_pattern) < 30:
            cards.extend(copy.deepcopy(card_pattern))

        cards.extend(card_pattern[:30 - len(cards)])
        super().__init__(cards, character_class)

    def draw(self, random):
        for card_index in range(0, 30):
            if not self.used[card_index]:
                self.used[card_index] = True
                return self.cards[card_index]

        return None


def generate_game_for(card1, card2, first_agent_type, second_agent_type):

    card1 = card1()
    card2 = card2()
    if card1.character_class == CHARACTER_CLASS.ALL:
        class1 = CHARACTER_CLASS.MAGE
    else:
        class1 = card1.character_class

    if card2.character_class == CHARACTER_CLASS.ALL:
        class2 = CHARACTER_CLASS.MAGE
    else:
        class2 = card2.character_class

    deck1 = StackedDeck([card1], class1)
    deck2 = StackedDeck([card2], class2)
    game = Game([deck1, deck2], [first_agent_type(), second_agent_type()])
    game.current_player = game.players[1]
    game.pre_game()
    return game


def check_mana_cost(cost):
    def create_func(func):
        def run(self):
            game = func(self)
            self.assertEqual(game.current_player.mana, game.current_player.max_mana - cost,
                             "Mana cost was not correct in " + str(func))

        return run

    return create_func


class TestSpells(unittest.TestCase):

    def setUp(self):
        random.seed(1337)

    @check_mana_cost(-2)  # This spell costs 0, but adds two mana, making it effectively a cost of -2
    def test_Ennervate(self):
        game = generate_game_for(Innervate, StonetuskBoar, SelfSpellTestingAgent, DoNothingBot)
        game.play_single_turn()
        self.assertEqual(3, game.current_player.mana)
        return game

    @check_mana_cost(0)
    def test_Moonfire(self):
        game = generate_game_for(Moonfire, StonetuskBoar, EnemySpellTestingAgent, MinionPlayingAgent)
        game.play_single_turn()
        self.assertEqual(29, game.other_player.health)
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





        def mock_choose(*options):
            return options[1]


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
        agent.choose_option = Mock(side_effect=mock_choose)

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

        self.assertEqual("SummonPanther", game.current_player.minions[0].card.__class__.__name__)
        self.assertEqual(3, game.current_player.minions[0].attack_power)
        self.assertEqual(2, game.current_player.minions[0].max_defense)

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


class TestGame(unittest.TestCase):

    def setUp(self):
        random.seed(1337)

    def test_createGame(self):
        card_set1 = []
        card_set2 = []
        test_env = self

        for cardIndex in range(0, 30):
            card_set1.append(StonetuskBoar())
            card_set2.append(NoviceEngineer())

        deck1 = Deck(card_set1, CHARACTER_CLASS.DRUID)
        deck2 = Deck(card_set2, CHARACTER_CLASS.MAGE)
        checked_cards = []

        class MockAgent1:
            def do_card_check(self, cards):

                test_env.assertEqual(len(cards), 3)
                checked_cards.append(list(cards))
                return [False, True, True]

            def set_game(self, game):
                pass

        class MockAgent2:
            def do_card_check(self, cards):

                test_env.assertEqual(len(cards), 4)
                checked_cards.append(list(cards))
                return [False, True, True, False]

            def set_game(self, game):
                pass

        agent1 = unittest.mock.Mock(spec=MockAgent1(), wraps=MockAgent1())
        agent2 = unittest.mock.Mock(spec=MockAgent2(), wraps=MockAgent2())
        game = Game([deck1, deck2], [agent1, agent2])
        game.pre_game()
        self.assertEqual(agent1.method_calls[0][0], "set_game", "Agent not asked to select cards")
        self.assertEqual(agent2.method_calls[0][0], "set_game", "Agent not asked to select cards")

        self.assertEqual(agent1.method_calls[1][0], "do_card_check", "Agent not asked to select cards")
        self.assertEqual(agent2.method_calls[1][0], "do_card_check", "Agent not asked to select cards")

        self.assertTrue(game.players[0].deck == deck1, "Deck not assigned to player")
        self.assertTrue(game.players[1].deck == deck2, "Deck not assigned to player")

        self.assertTrue(game.players[0].agent == agent1, "Agent not stored in the hsgame")
        self.assertTrue(game.players[1].agent == agent2, "Agent not stored in the hsgame")

        self.assertListEqual(checked_cards[0][1:], game.players[0].hand[:-1], "Cards not retained after request")
        self.assertListEqual(checked_cards[1][1:2], game.players[1].hand[:-3], "Cards not retained after request")

    def test_FirstTurn(self):
        card_set1 = []
        card_set2 = []
        test_env = self

        for cardIndex in range(0, 30):
            card_set1.append(StonetuskBoar())
            card_set2.append(NoviceEngineer())

        deck1 = Deck(card_set1, CHARACTER_CLASS.DRUID)
        deck2 = Deck(card_set2, CHARACTER_CLASS.MAGE)


        agent1 = unittest.mock.Mock(spec=DoNothingBot(), wraps=DoNothingBot())
        agent2 = unittest.mock.Mock(spec=DoNothingBot(), wraps=DoNothingBot())
        game = Game([deck1, deck2], [agent1, agent2])

        game.start()


class TestBinding(unittest.TestCase):

    def test_bind(self):
        event = Mock()
        binder = Bindable()
        binder.bind("test", event)
        binder.trigger("test", 1, 5, 6, arg1="something", args2="whatever")
        event.assert_called_once_with(1, 5, 6, arg1="something", args2="whatever")
        binder.unbind("test", event)
        binder.trigger("test")
        event.assert_called_once_with(1, 5, 6, arg1="something", args2="whatever")

    def test_bind_once(self):
        event = Mock()
        event2 = Mock()
        binder = Bindable()
        binder.bind_once("test", event)
        binder.bind("test", event2)
        binder.trigger("test", 1, 5, 6, arg1="something", args2="whatever")
        event.assert_called_once_with(1, 5, 6, arg1="something", args2="whatever")
        event2.assert_called_once_with(1, 5, 6, arg1="something", args2="whatever")
        binder.trigger("test")
        event.assert_called_once_with(1, 5, 6, arg1="something", args2="whatever")
        self.assertEqual(event2.call_count, 2)

    def test_bind_with_different_args(self):
        event = Mock()
        event2 = Mock()
        binder = Bindable()
        binder.bind("test", event, 5)
        binder.bind("test", event2)
        binder.trigger("test")
        event.assert_called_with(5)
        event2.assert_called_with()


#Create a test for Mulligan cards

if __name__ == '__main__':
    unittest.main()




