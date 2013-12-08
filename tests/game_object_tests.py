from game.constants import CHARACTER_CLASS


__author__ = 'Daniel'
import random
import unittest
from unittest.mock import Mock

from game.minions import StonetuskBoar, NoviceEngineer
from game.game_objects import Player, Board, Game, Deck, Bindable


class TestMinions(unittest.TestCase):

    def setUp(self):
        self.player_one = Player("one", Deck([None] * 30, CHARACTER_CLASS.MAGE))
        self.player_two = Player("two", Deck([None] * 30, CHARACTER_CLASS.MAGE))
        self.board = Board([self.player_one, self.player_two])

    def test_createBoar(self):
        StonetuskBoar()
        self.assertTrue(True, "Could not create boar")

    def test_addBoarToGame(self):
        boar = StonetuskBoar();

        boar.use(self.player_one, self.board)

        self.assertIn(boar.minion, self.board.minions[self.player_one], "Boar not added to board")
        self.assertEqual(self.player_one.mana, 0, "Player's mana not properly decreased")


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

        class MockAgent2:
            def do_card_check(self, cards):

                test_env.assertEqual(len(cards), 4)
                checked_cards.append(list(cards))
                return [False, True, True, False]

        agent1 = unittest.mock.Mock(spec=MockAgent1(), wraps=MockAgent1())
        agent2 = unittest.mock.Mock(spec=MockAgent2(), wraps=MockAgent2())
        game = Game([deck1, deck2], [agent1, agent2])
        self.assertEqual(agent1.method_calls[0][0], "do_card_check", "Agent not asked to select cards")
        self.assertEqual(agent2.method_calls[0][0], "do_card_check", "Agent not asked to select cards")

        self.assertTrue(game.players[0].deck == deck1, "Deck not assigned to player")
        self.assertTrue(game.players[1].deck == deck2, "Deck not assigned to player")

        self.assertTrue(game.agents[game.players[0]] == agent1, "Agent not stored in the game")
        self.assertTrue(game.agents[game.players[1]] == agent2, "Agent not stored in the game")

        self.assertListEqual(checked_cards[0][1:], game.hands[game.players[0]][:-1], "Cards not retained after request")
        self.assertListEqual(checked_cards[1][1:2], game.hands[game.players[1]][:-3], "Cards not retained after request")

    def test_FirstTurn(self):
        pass


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



if __name__ == '__main__':
    unittest.main()