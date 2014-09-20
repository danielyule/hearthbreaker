import json
from hearthbreaker.cards import Assassinate, Voidcaller, FlameImp, ArgentSquire, BoulderfistOgre, StonetuskBoar
from hearthbreaker.game_objects import Game
from tests.agents.testing_agents import MinionPlayingAgent, SpellTestingAgent
import tests.copy_tests
from tests.testing_utils import generate_game_for


class SerializationCopyTests(tests.copy_tests.TestMinionCopying):
    def setUp(self):
        def _save_object(o):
            return o.__to_json__()

        def serialization_copy(old_game):
            game_json = json.dumps(old_game, default=_save_object, indent=2)
            d = json.loads(game_json)
            return Game.__from_json__(d, [player.agent for player in old_game.players])

        super().setUp()
        Game.copy = serialization_copy

    def test_Voidcaller(self):
        game = generate_game_for(Assassinate, [Voidcaller, FlameImp, ArgentSquire, BoulderfistOgre, StonetuskBoar],
                                 SpellTestingAgent, MinionPlayingAgent)

        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Voidcaller", game.current_player.minions[0].card.name)
        game = game.copy()
        game.play_single_turn()
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual("Voidcaller", game.other_player.minions[0].card.name)
