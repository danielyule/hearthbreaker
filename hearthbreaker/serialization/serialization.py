import json
from hearthbreaker.cards import FlameImp, LightsJustice, EyeForAnEye
from hearthbreaker.engine import Game
from tests.agents.testing_agents import CardTestingAgent
from tests.testing_utils import generate_game_for


def _save_object(o):
    return o.__to_json__()


def _load_object(d):
    return Game.__from_json__(d)


def serialize(game):
    """
    Encode the given game instance as a JSON formatted string.  This string can be used to re-construct the game exactly
    as it is now

    :param heartbreaker.game_objects.Game game: The game to serialize
    :rtype: string
    """

    return json.dumps(game, default=_save_object, indent=2)


def deserialize(json_string, agents):
    """
    Decode the given game instance from a JSON formatted string.

    :param string json_string: The string representation of the game
    :rtype: :class:`hearthbreaker.engine.Game`
    """
    d = json.loads(json_string)
    return Game.__from_json__(d, agents)


if __name__ == "__main__":
    game = generate_game_for([LightsJustice, EyeForAnEye], FlameImp, CardTestingAgent, CardTestingAgent)
    for turn in range(0, 5):
        game.play_single_turn()

    print(serialize(game))
    game2 = deserialize(serialize(game), [player.agent for player in game.players])
    game2.start()
