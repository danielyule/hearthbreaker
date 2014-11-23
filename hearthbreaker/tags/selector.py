import abc
import hearthbreaker.game_objects
from hearthbreaker.tags.base import Selector, Player
import hearthbreaker.tags.condition


class FriendlyPlayer(Player):
    def match(self, source, obj):
        return source.player is obj.player

    def get_players(self, target):
        return [target]

    def __to_json__(self):
        return "friendly"


class EnemyPlayer(Player):
    def get_players(self, target):
        return [target.opponent]

    def match(self, source, obj):
        return source.player is obj.player.opponent

    def __to_json__(self):
        return "enemy"


class BothPlayer(Player):
    def match(self, source, obj):
        return True

    def get_players(self, target):
        return [target, target.opponent]

    def __to_json__(self):
        return "both"


class PlayerOne(Player):
    def match(self, source, obj):
        return source.player is obj.player.game.players[0]

    def get_players(self, target):
        return [target.game.players[0]]

    def __to_json__(self):
        return "player_one"


class PlayerTwo(Player):
    def match(self, source, obj):
        return source.player is obj.player.game.players[1]

    def get_players(self, target):
        return [target.game.players[1]]

    def __to_json__(self):
        return "player_two"


class CurrentPlayer(Player):
    def match(self, source, obj):
        return source.player is obj.player.game.current_player

    def get_players(self, target):
        return [target.game.current_player]

    def __to_json__(self):
        return "current_player"


class OtherPlayer(Player):
    def match(self, source, obj):
        return source.player is obj.player.game.other_player

    def get_players(self, target):
        return [target.game.other_player]

    def __to_json__(self):
        return "other_player"


class CardSelector(Selector, metaclass=abc.ABCMeta):
    def __init__(self, players=FriendlyPlayer()):
        self.players = players

    def track_cards(self, player):
        pass

    def untrack_cards(self, player):
        pass

    def get_targets(self, source, obj=None):
        players = self.players.get_players(source.player)
        targets = []
        for p in players:
            for card in p.cards:
                if self.match(source, card):
                    targets.append(card)

        return targets

    @abc.abstractmethod
    def match(self, source, obj):
        pass

    def __to_json__(self):
        return {
            'name': 'card',
            'players': self.players
        }

    def __from_json__(self, players='friendly'):
        self.players = Player.from_json(players)
        return self


class SpecificCardSelector(CardSelector):
    def __init__(self, card, players=FriendlyPlayer()):
        super().__init__(players)
        self.card_index = -1
        self.__card = card

    def match(self, source, obj):
        return obj is self.__card

    def track_cards(self, player):
        if self.card_index == -1:
            try:
                self.card_index = player.hand.index(self.__card)
            except ValueError:
                return
        else:
            self.__card = player.hand[self.card_index]

        def card_played(card, index):
            if index < self.card_index:
                self.card_index -= 1

            if index == self.card_index:
                player.unbind("card_played", card_played)

        player.bind("card_played", card_played)

    def __to_json__(self):
        return {
            'name': 'specific_card',
            'card_index': self.card_index
        }

    def __from_json__(self, card_index, players='friendly'):
        self.card_index = card_index
        self.__card = None
        return self


class SecretSelector(CardSelector):
    def match(self, source, obj):
        return isinstance(obj, hearthbreaker.game_objects.SecretCard)

    def __to_json__(self):
        return {
            'name': 'secret',
            'players': self.players
        }

    def __from_json__(self, players='friendly'):
        self.players = Player.from_json(players)
        return self


class SpellSelector(CardSelector):
    def match(self, source, obj):
        return obj.is_spell()

    def __to_json__(self):
        return {
            'name': 'spell',
            'players': self.players
        }

    def __from_json__(self, players='friendly'):
        self.players = Player.from_json(players)
        return self


class BattlecrySelector(CardSelector):
    def match(self, source, obj):
        return isinstance(obj, hearthbreaker.game_objects.MinionCard) and \
            obj.create_minion(source).battlecry is not None

    def __to_json__(self):
        return {
            'name': 'battlecry',
            'players': self.players
        }

    def __from_json__(self, players='friendly'):
        self.players = Player.from_json(players)
        return self


class MinionCardSelector(CardSelector):
    def match(self, source, obj):
        return isinstance(obj, hearthbreaker.game_objects.MinionCard)

    def __to_json__(self):
        return {
            'name': 'minion_card',
            'players': self.players
        }

    def __from_json__(self, players='friendly'):
        self.players = Player.from_json(players)
        return self


class HeroSelector(Selector):
    def __init__(self, players=FriendlyPlayer()):
        self.players = players

    def get_targets(self, source, obj=None):
        return [p.hero for p in self.players.get_players(source.player)]

    def match(self, source, obj):
        return source.player is obj

    def __to_json__(self):
        return {
            'name': 'hero',
            'players': self.players
        }

    def __from_json__(self, players='friendly'):
        self.players = Player.from_json(players)
        return self


class PlayerSelector(Selector):
    def __init__(self, players=FriendlyPlayer()):
        self.players = players

    def get_targets(self, source, obj=None):
        return self.players.get_players(source.player)

    def match(self, source, obj):
        return source.player is obj

    def __to_json__(self):
        return {
            'name': 'player',
            'players': self.players
        }

    def __from_json__(self, players='friendly'):
        self.players = Player.from_json(players)
        return self


class MinionSelector(Selector):
    def __init__(self, condition=hearthbreaker.tags.condition.MinionIsNotTarget(), players=FriendlyPlayer()):
        self.condition = condition
        self.players = players

    def get_targets(self, source, obj=None):
        players = self.players.get_players(source.player)
        targets = []
        for p in players:
            for minion in p.minions:
                if self.match(source, minion):
                    targets.append(minion)

        return targets

    def match(self, source, obj):
        if self.condition:
            return isinstance(obj, hearthbreaker.game_objects.Minion) and self.players.match(source, obj)\
                and self.condition.evaluate(source, obj)
        else:
            return isinstance(obj, hearthbreaker.game_objects.Minion) and self.players.match(source, obj)

    def __to_json__(self):
        if self.condition:
            return {
                'name': 'minion',
                'condition': self.condition,
                'players': self.players
            }
        return {
            'name': 'minion',
            'players': self.players
        }

    def __from_json__(self, players, condition=None):
        if condition:
            self.condition = hearthbreaker.tags.condition.Condition.from_json(**condition)
        else:
            self.condition = None
        self.players = Player.from_json(players)
        return self


class CharacterSelector(Selector):
    def __init__(self, condition=hearthbreaker.tags.condition.MinionIsNotTarget(), players=FriendlyPlayer()):
        self.condition = condition
        self.players = players

    def get_targets(self, source, obj=None):
        players = self.players.get_players(source.player)
        targets = []
        for p in players:
            for minion in p.minions:
                if self.match(source, minion):
                    targets.append(minion)
            if self.match(source, p.hero):
                targets.append(p.hero)

        return targets

    def match(self, source, obj):
        if self.condition:
            return isinstance(obj, hearthbreaker.game_objects.Character) and self.players.match(source, obj) \
                and self.condition.evaluate(source, obj)
        else:
            return isinstance(obj, hearthbreaker.game_objects.Character) and self.players.match(source, obj)

    def __to_json__(self):
        if self.condition:
            return {
                'name': 'character',
                'condition': self.condition,
                'players': self.players
            }
        return {
            'name': 'character',
            'players': self.players
        }

    def __from_json__(self, players, condition=None):
        if condition:
            self.condition = hearthbreaker.tags.condition.Condition.from_json(**condition)
        else:
            self.condition = None
        self.players = Player.from_json(players)
        return self


class SelfSelector(Selector):
    def get_targets(self, source, obj=None):
        return [source]

    def match(self, source, obj):
        return source is obj

    def __to_json__(self):
        return {
            'name': 'self'
        }


class TargetSelector(Selector):

    def __init__(self, condition=None):
        super().__init__()
        self.condition = condition

    def get_targets(self, source, obj=None):
        if not self.condition or self.condition.evaluate(source, obj):
            return [obj]
        return []

    def match(self, source, obj):
        return False

    def __to_json__(self):
        if self.condition:
            return {
                'name': 'target',
                'condition': self.condition,
            }
        return {
            'name': 'target',
        }

    def __from_json__(self, condition=None):
        if condition:
            self.condition = hearthbreaker.tags.condition.Condition.from_json(**condition)
        else:
            self.condition = None
        return self


class RandomSelector(Selector):
    def match(self, source, obj):
        return self.selector.match(source, obj)

    def __init__(self, selector):
        self.selector = selector

    def get_targets(self, source, obj=None):
        targets = self.selector.get_targets(source, obj)
        if len(targets) > 0:
            return [source.player.game.random_choice(targets)]
        return []

    def __to_json__(self):
        return {
            'name': 'random',
            'selector': self.selector
        }

    def __from_json__(self, selector):
        self.selector = Selector.from_json(**selector)
        return self


class WeaponSelector(Selector):
    def __init__(self, players=FriendlyPlayer()):
        self.players = players

    def get_targets(self, source, obj=None):
        return [p.hero for p in self.players.get_players(source.player)]

    def match(self, source, obj):
        return source.player is obj

    def __to_json__(self):
        return {
            'name': 'weapon',
            'players': self.players
        }

    def __from_json__(self, players='friendly'):
        self.players = Player.from_json(players)
        return self
