import unittest
from io import StringIO
from os import listdir

from hsgame.replay import Replay
from hsgame.agents.basic_agents import PredictableBot
from hsgame.constants import CHARACTER_CLASS
import hsgame.game_objects
from hsgame.cards import *
from tests.testing_agents import MinionPlayingAgent, EnemyMinionSpellTestingAgent
import sys

import random
__author__ = 'Daniel'

class TestReplay(unittest.TestCase):

    def test_reading_and_writing(self):
        self.maxDiff = None
        for rfile in listdir("replays"):
            replay = Replay()
            replay.parse_replay("replays/" + rfile)
            output = StringIO()
            replay.write_replay(output)
            f = open("replays/" + rfile, 'r')
            self.assertEqual(output.getvalue(), f.read())

    def test_loading_game(self):
        replay = Replay()
        replay.parse_replay("replays/example.rep")
        game = hsgame.game_objects.SavedGame(replay)

        game.start()

        self.assertEqual(game.current_player.deck.character_class, CHARACTER_CLASS.DRUID)
        self.assertEqual(game.other_player.deck.character_class, CHARACTER_CLASS.MAGE)

        self.assertEqual(game.current_player.health, 29)
        self.assertTrue(game.current_player.dead)


    def test_recording_game(self):
        self.maxDiff = None
        random.seed(9876)
        deck1 = hsgame.game_objects.Deck([StonetuskBoar()] * 30, CHARACTER_CLASS.MAGE)
        deck2 = hsgame.game_objects.Deck([Naturalize()]* 30, CHARACTER_CLASS.DRUID)
        agent1 = PredictableBot()
        agent2 = PredictableBot()
        game = hsgame.game_objects.RecordingGame([deck1, deck2], [agent1, agent2])
        game.start()
        output = StringIO()
        game.replay.write_replay(output)
        f = open("replays/stonetusk_innervate.rep", 'r')
        self.assertEqual(output.getvalue(), f.read())

    def test_option_replay(self):
        replay = Replay()
        replay.parse_replay("replays/stonetusk_power.rep")
        game = hsgame.game_objects.SavedGame(replay)
        game.start()
        panther = game.other_player.minions[0]
        self.assertEqual(panther.card.name, "Panther")
        self.assertEqual(panther.defense, 3)
        self.assertEqual(panther.attack_power, 4)
        self.assertEqual(panther.index, 0)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        card1 = hsgame.game_objects.card_lookup(sys.argv[1])
        card2 = hsgame.game_objects.card_lookup(sys.argv[2])
        print(card1, card2)


