import unittest
from io import StringIO
from os import listdir
import re
import random

from hearthbreaker.replay import Replay, RecordingGame, SavedGame
from hearthbreaker.agents.basic_agents import PredictableBot
from hearthbreaker.constants import CHARACTER_CLASS
from hearthbreaker.cards import *
import hearthbreaker.game_objects


class TestReplay(unittest.TestCase):
    def test_reading_and_writing(self):
        def process_line(line):
            line = re.sub(r'\s*,\s*', ',', line)
            line = re.sub(r'\s*\(\s*', '(', line)
            line = re.sub(r'\s+\)', ')', line)
            return re.sub(r'(^\s+)|(\s*(;.*)?$)', '', line)

        self.maxDiff = None
        for rfile in filter(lambda file: re.compile(r'.*\.rep$').match(file), listdir("tests/replays")):
            replay = Replay()
            replay.parse_replay("tests/replays/" + rfile)
            output = StringIO()
            replay.write_replay(output)
            f = open("tests/replays/" + rfile, 'r')
            file_string = f.read()
            f.close()
            file_string = "\n".join(map(process_line, file_string.split("\n")))

            self.assertEqual(output.getvalue(), file_string)

    def test_loading_game(self):
        game = SavedGame("tests/replays/example.rep")

        game.start()

        self.assertEqual(game.current_player.deck.character_class, CHARACTER_CLASS.DRUID)
        self.assertEqual(game.other_player.deck.character_class, CHARACTER_CLASS.MAGE)

        self.assertEqual(game.current_player.hero.health, 29)
        self.assertTrue(game.current_player.hero.dead)

    def test_recording_game(self):
        self.maxDiff = None
        random.seed(9876)
        deck1 = hearthbreaker.game_objects.Deck([StonetuskBoar()] * 30, CHARACTER_CLASS.MAGE)
        deck2 = hearthbreaker.game_objects.Deck([Naturalize()] * 30, CHARACTER_CLASS.DRUID)
        agent1 = PredictableBot()
        agent2 = PredictableBot()
        game = RecordingGame([deck1, deck2], [agent1, agent2])
        game.start()
        output = StringIO()
        game.replay.write_replay(output)
        f = open("tests/replays/stonetusk_innervate.rep", 'r')
        self.assertEqual(output.getvalue(), f.read())
        f.close()

    def test_option_replay(self):
        game = SavedGame("tests/replays/stonetusk_power.rep")
        game.start()
        panther = game.other_player.minions[0]
        self.assertEqual(panther.card.name, "Panther")
        self.assertEqual(panther.health, 3)
        self.assertEqual(panther.calculate_attack(), 4)
        self.assertEqual(panther.index, 0)
