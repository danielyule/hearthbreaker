import json
import unittest
from io import StringIO
from os import listdir
from os.path import isdir
import re
import random

from hearthbreaker.replay import Replay, RecordingGame, SavedGame
from hearthbreaker.agents.basic_agents import PredictableBot
from hearthbreaker.constants import CHARACTER_CLASS
from hearthbreaker.cards import *
import hearthbreaker.game_objects
from tests.agents.testing_agents import PredictableAgentWithoutHeroPower, MinionPlayingAgent


class TestReplay(unittest.TestCase):

    def __compare_json(self, json1, json2):
        return json.loads(json1) == json.loads(json2)

    def test_reading_and_writing(self):
        file_match = re.compile(r'.*\.rep$')
        files = []

        def get_files_from(folder_name):
            for file in listdir(folder_name):
                if file_match.match(file):
                    files.append(folder_name + "/" + file)
                elif isdir(folder_name + "/" + file):
                    get_files_from(folder_name + "/" + file)

        get_files_from("tests/replays")

        for rfile in files:
            replay = Replay()
            replay.read_replay_json(rfile)
            output = StringIO()
            replay.write_replay_json(output)
            f = open(rfile, 'r')
            file_string = f.read()
            f.close()

            self.assertEqual(output.getvalue(), file_string, "File '" + rfile + "' did not match")

    def test_loading_game(self):
        game = SavedGame("tests/replays/example.hsreplay")

        game.start()

        self.assertEqual(game.current_player.deck.character_class, CHARACTER_CLASS.DRUID)
        self.assertEqual(game.other_player.deck.character_class, CHARACTER_CLASS.MAGE)

        self.assertEqual(game.current_player.hero.health, 29)
        self.assertTrue(game.current_player.hero.dead)

    def test_recording_game(self):
        self.maxDiff = None
        random.seed(9876)
        deck1 = hearthbreaker.game_objects.Deck([StonetuskBoar() for i in range(0, 30)], CHARACTER_CLASS.MAGE)
        deck2 = hearthbreaker.game_objects.Deck([Naturalize() for i in range(0, 30)], CHARACTER_CLASS.DRUID)
        agent1 = PredictableBot()
        agent2 = PredictableBot()
        game = RecordingGame([deck1, deck2], [agent1, agent2])
        game.start()
        output = StringIO()
        game.replay.write_replay_json(output)
        f = open("tests/replays/stonetusk_innervate.hsreplay", 'r')
        dif = self.__compare_json(output.getvalue(), f.read())
        self.assertTrue(dif)
        f.close()

    def test_option_replay(self):
        game = SavedGame("tests/replays/stonetusk_power.hsreplay")
        game.start()
        self.assertEqual(1, len(game.other_player.minions))
        panther = game.other_player.minions[0]
        self.assertEqual(panther.card.name, "Panther")
        self.assertEqual(panther.health, 3)
        self.assertEqual(panther.calculate_attack(), 4)
        self.assertEqual(panther.index, 0)

    def test_random_character_saving(self):
        deck1 = hearthbreaker.game_objects.Deck([RagnarosTheFirelord() for i in range(0, 30)], CHARACTER_CLASS.MAGE)
        deck2 = hearthbreaker.game_objects.Deck([StonetuskBoar() for i in range(0, 30)], CHARACTER_CLASS.DRUID)
        agent1 = PredictableAgentWithoutHeroPower()
        agent2 = MinionPlayingAgent()
        random.seed(4879)
        game = RecordingGame([deck1, deck2], [agent1, agent2])
        for turn in range(0, 17):
            game.play_single_turn()

        output = StringIO()
        game.replay.write_replay_json(output)
        random.seed(4879)
        new_game = SavedGame(StringIO(output.getvalue()))
        new_game.pre_game()
        for turn in range(0, 17):
            new_game.play_single_turn()

        self.assertEqual(2, len(new_game.current_player.minions))
        self.assertEqual(30, new_game.other_player.hero.health)
        self.assertEqual(5, len(new_game.other_player.minions))

    def test_json_saving(self):
        self.maxDiff = 6000
        deck1 = hearthbreaker.game_objects.Deck([RagnarosTheFirelord() for i in range(0, 30)], CHARACTER_CLASS.MAGE)
        deck2 = hearthbreaker.game_objects.Deck([StonetuskBoar() for i in range(0, 30)], CHARACTER_CLASS.DRUID)
        agent1 = PredictableAgentWithoutHeroPower()
        agent2 = MinionPlayingAgent()
        random.seed(4879)
        game = RecordingGame([deck1, deck2], [agent1, agent2])
        game.pre_game()
        for turn in range(0, 17):
            game.play_single_turn()

        output = StringIO()
        game.replay.write_replay_json(output)
        inp = StringIO(output.getvalue())
        new_replay = Replay.__new__(Replay)
        new_replay.read_replay_json(inp)
        old_output = output.getvalue()
        other_output = StringIO()
        new_replay.write_replay_json(other_output)
        self.assertEqual(other_output.getvalue(), old_output)
