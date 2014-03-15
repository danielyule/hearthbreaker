import unittest
from io import StringIO
from os import listdir

from hsgame.replay import Replay
from hsgame.agents.basic_agents import PredictableBot
from hsgame.constants import CHARACTER_CLASS
import hsgame.game_objects
from hsgame.cards import *
from tests.testing_agents import MinionPlayingAgent, EnemyMinionSpellTestingAgent

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

        game.play_single_turn()


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

