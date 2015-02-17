import random
import unittest

from hearthbreaker.agents.basic_agents import DoNothingAgent, PredictableAgent
from hearthbreaker.cards.base import SecretCard
from hearthbreaker.cards.heroes import Malfurion, Jaina
from hearthbreaker.cards.minions.rogue import AnubarAmbusher
from hearthbreaker.engine import Game, Deck, card_lookup
from tests.agents.testing_agents import CardTestingAgent, OneCardPlayingAgent, PlayAndAttackAgent
from tests.testing_utils import generate_game_for, mock
from hearthbreaker.cards import StonetuskBoar, ArcaneIntellect, Naturalize, Abomination, NerubianEgg, SylvanasWindrunner
from hearthbreaker.game_objects import Bindable


class TestGame(unittest.TestCase):
    def setUp(self):
        random.seed(1857)

    def test_create_game(self):
        card_set1 = []
        card_set2 = []
        test_env = self

        for cardIndex in range(0, 30):
            card_set1.append(card_lookup("Stonetusk Boar"))
            card_set2.append(card_lookup("Novice Engineer"))

        deck1 = Deck(card_set1, Malfurion())
        deck2 = Deck(card_set2, Jaina())
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

        agent1 = mock.Mock(spec=MockAgent1(), wraps=MockAgent1())
        agent2 = mock.Mock(spec=MockAgent2(), wraps=MockAgent2())
        game = Game([deck1, deck2], [agent1, agent2])
        game.pre_game()

        self.assertEqual(agent1.method_calls[0][0], "do_card_check", "Agent not asked to select cards")
        self.assertEqual(agent2.method_calls[0][0], "do_card_check", "Agent not asked to select cards")

        self.assertTrue(game.players[0].deck == deck1, "Deck not assigned to player")
        self.assertTrue(game.players[1].deck == deck2, "Deck not assigned to player")

        self.assertTrue(game.players[0].agent == agent1, "Agent not stored in the hearthbreaker")
        self.assertTrue(game.players[1].agent == agent2, "Agent not stored in the hearthbreaker")

        self.assertListEqual(checked_cards[0][1:], game.players[0].hand[1:], "Cards not retained after request")
        self.assertListEqual(checked_cards[1][1:2], game.players[1].hand[1:2], "Cards not retained after request")

    def test_first_turn(self):
        card_set1 = []
        card_set2 = []

        for cardIndex in range(0, 30):
            card_set1.append(card_lookup("Stonetusk Boar"))
            card_set2.append(card_lookup("Novice Engineer"))

        deck1 = Deck(card_set1, Malfurion())
        deck2 = Deck(card_set2, Jaina())

        agent1 = mock.Mock(spec=DoNothingAgent(), wraps=DoNothingAgent())
        agent2 = mock.Mock(spec=DoNothingAgent(), wraps=DoNothingAgent())
        game = Game([deck1, deck2], [agent1, agent2])

        game.start()

    def test_secrets(self):
        for secret_type in SecretCard.__subclasses__():
            random.seed(1857)
            secret = secret_type()
            game = generate_game_for(secret_type, StonetuskBoar, CardTestingAgent, DoNothingAgent)
            for turn in range(0, secret.mana * 2 - 2):
                game.play_single_turn()

            def assert_different():
                new_events = game.events.copy()
                new_events.update(game.other_player.hero.events)
                new_events.update(game.other_player.events)
                new_events.update(game.current_player.hero.events)
                new_events.update(game.current_player.events)
                self.assertNotEqual(events, new_events, secret.name)

            def assert_same():
                new_events = game.events.copy()
                new_events.update(game.current_player.hero.events)
                new_events.update(game.current_player.events)
                new_events.update(game.other_player.hero.events)
                new_events.update(game.other_player.events)
                self.assertEqual(events, new_events)

            game.current_player.bind("turn_ended", assert_different)
            game.other_player.bind("turn_ended", assert_same)

            # save the events as they are prior to the secret being played
            events = game.events.copy()
            events.update(game.other_player.hero.events)
            events.update(game.other_player.events)
            events.update(game.current_player.hero.events)
            events.update(game.current_player.events)

            # The secret is played, but the events aren't updated until the secret is activated
            game.play_single_turn()

            self.assertEqual(1, len(game.current_player.secrets))

            # Now the events should be changed
            game.play_single_turn()

            # Now the events should be reset
            game.play_single_turn()

    def test_physical_hero_attacks(self):
        game = generate_game_for(Naturalize, ArcaneIntellect, PredictableAgent, PredictableAgent)
        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(30, game.other_player.hero.health)
        self.assertEqual(0, game.other_player.hero.armor)
        self.assertEqual(29, game.current_player.hero.health)

    def test_hero_weapon_sheath(self):
        game = generate_game_for(AnubarAmbusher, StonetuskBoar, PredictableAgent, PlayAndAttackAgent)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(28, game.current_player.hero.health)

        game.play_single_turn()
        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(26, game.other_player.hero.health)

    def test_deathrattle_ordering(self):
        game = generate_game_for(SylvanasWindrunner, [Abomination, NerubianEgg],
                                 OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(1, len(game.other_player.minions))
        game.other_player.minions[0].health = 2

        game.current_player.minions[1].die(None)
        game.check_delayed()

        # Everything should die at once, but Sylvanas shouldn't get the Nerubian because its Deathrattle will not have
        # gone yet

        self.assertEqual(1, len(game.current_player.minions))


class TestBinding(unittest.TestCase):
    def test_bind(self):
        event = mock.Mock()
        binder = Bindable()
        binder.bind("test", event)
        binder.trigger("test", 1, 5, 6)
        event.assert_called_once_with(1, 5, 6)
        binder.unbind("test", event)
        binder.trigger("test")
        event.assert_called_once_with(1, 5, 6)

    def test_bind_once(self):
        event = mock.Mock()
        event2 = mock.Mock()
        binder = Bindable()
        binder.bind_once("test", event)
        binder.bind("test", event2)
        binder.trigger("test", 1, 5, 6)
        event.assert_called_once_with(1, 5, 6)
        event2.assert_called_once_with(1, 5, 6)
        binder.trigger("test")
        event.assert_called_once_with(1, 5, 6)
        self.assertEqual(event2.call_count, 2)
