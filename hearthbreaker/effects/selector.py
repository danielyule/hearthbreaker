import abc

import hearthbreaker.game_objects
from hearthbreaker.effects.base import Selector


class SecretSelector(Selector):
    def match(self, obj):
        return isinstance(obj, hearthbreaker.game_objects.SecretCard)

    def __to_json__(self):
        return {
            'type': 'secret',
        }


class Player(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_players(self, target):
        pass


class FriendlyPlayer(Player):
    def get_players(self, target):
        return [target]
