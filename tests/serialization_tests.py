import json
from hearthbreaker.game_objects import Game
import tests.copy_tests


class SerializationCopyTests(tests.copy_tests.TestMinionCopying):
    def setUp(self):
        def _save_object(o):
            return o.__to_json__()

        def serialization_copy(old_game):
            game_json = json.dumps(old_game, default=_save_object, indent=2)
            d = json.loads(game_json)
            return Game.__from_json__(d, [player.agent for player in old_game.players])

        super().setUp()
        self._old_copy = Game.copy
        Game.copy = serialization_copy

    def tearDown(self):
        super().tearDown()
        Game.copy = self._old_copy
