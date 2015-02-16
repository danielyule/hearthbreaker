import abc
from hearthbreaker.constants import MINION_TYPE
from hearthbreaker.tags.base import Selector, Player, Picker, Function
import hearthbreaker.tags.condition


class FriendlyPlayer(Player):
    def match(self, source, obj):
        return obj.player is source.player

    def get_players(self, target):
        return [target]

    def __to_json__(self):
        return "friendly"


class EnemyPlayer(Player):
    def get_players(self, target):
        return [target.opponent]

    def match(self, source, obj):
        return obj.player is source.player.opponent

    def __to_json__(self):
        return "enemy"


class BothPlayer(Player):
    def match(self, source, obj):
        return True

    def get_players(self, target):
        return [target.opponent, target]

    def __to_json__(self):
        return "both"


class PlayerOne(Player):
    def match(self, source, obj):
        return obj.player is source.player.game.players[0]

    def get_players(self, target):
        return [target.game.players[0]]

    def __to_json__(self):
        return "player_one"


class PlayerTwo(Player):
    def match(self, source, obj):
        return obj.player is source.player.game.players[1]

    def get_players(self, target):
        return [target.game.players[1]]

    def __to_json__(self):
        return "player_two"


class CurrentPlayer(Player):
    def match(self, source, obj):
        return obj.player is source.player.game.current_player

    def get_players(self, target):
        return [target.game.current_player]

    def __to_json__(self):
        return "current_player"


class OtherPlayer(Player):
    def match(self, source, obj):
        return obj.player is source.player.game.other_player

    def get_players(self, target):
        return [target.game.other_player]

    def __to_json__(self):
        return "other_player"


class AllPicker(Picker):
    def pick(self, targets, player):
        return targets

    def __to_json__(self):
        return {
            'name': "all"
        }


class UserPicker(Picker):
    def pick(self, targets, player):
        filtered_targets = [target for target in filter(lambda t: t.player is player or not t.stealth, targets)]
        if len(filtered_targets) > 0:
            return [player.agent.choose_target(filtered_targets)]
        return filtered_targets

    def __to_json__(self):
        return {
            'name': "user"
        }


class RandomPicker(Picker):
    def __init__(self, count=1):
        self.count = count

    def pick(self, targets, player):
        for i in range(self.count):
            if len(targets) > 0:
                yield player.game.random_choice(targets)
            targets = [target for target in filter(lambda t: not (t.is_minion() and t.dead), targets)]

    def __to_json__(self):
        return {
            'name': "random",
            'count': self.count
        }


class CardSelector(Selector, metaclass=abc.ABCMeta):
    def __init__(self, players=FriendlyPlayer()):
        self.players = players

    def get_targets(self, source, obj=None):
        players = self.players.get_players(source.player)
        targets = []
        for p in players:
            for card in p.hand:
                if self.match(source, card):
                    targets.append(card)

        return targets

    def match(self, source, obj):
        return self.players.match(source, obj)

    def __to_json__(self):
        return {
            'name': 'card',
            'players': self.players
        }

    def __from_json__(self, players='friendly'):
        self.players = Player.from_json(players)
        return self


class SecretSelector(CardSelector):
    def match(self, source, obj):
        return super().match(source, obj) and obj.is_secret()

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
        return super().match(source, obj) and obj.is_spell()

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
        return super().match(source, obj) and obj.is_minion() and obj.is_card() and obj.battlecry is not ()

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
        return super().match(source, obj) and obj.is_minion()

    def __to_json__(self):
        return {
            'name': 'minion_card',
            'players': self.players
        }

    def __from_json__(self, players='friendly'):
        self.players = Player.from_json(players)
        return self


class MechCardSelector(MinionCardSelector):
    def match(self, source, obj):
        return super().match(source, obj) and obj.minion_type == MINION_TYPE.MECH

    def __to_json__(self):
        return {
            'name': 'mech_card',
            'players': self.players
        }

    def __from_json__(self, players='friendly'):
        self.players = Player.from_json(players)
        return self


class HeroSelector(Selector):
    def __init__(self, players=FriendlyPlayer(), picker=AllPicker()):
        self.players = players
        self.picker = picker

    def get_targets(self, source, obj=None):
        return [p.hero for p in self.players.get_players(source.player)]

    def choose_targets(self, source, target=None):
        possible_targets = self.get_targets(source, target)
        return self.picker.pick(possible_targets, source.player)

    def match(self, source, obj):
        return source.player is obj

    def __to_json__(self):
        return {
            'name': 'hero',
            'players': self.players,
            'picker': self.picker
        }

    def __from_json__(self, picker, players='friendly'):
        self.players = Player.from_json(players)
        self.picker = Picker.from_json(**picker)
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
    def __init__(self, condition=hearthbreaker.tags.condition.MinionIsNotTarget(), players=FriendlyPlayer(),
                 picker=AllPicker()):
        self.condition = condition
        self.players = players
        self.picker = picker

    def get_targets(self, source, obj=None):
        players = self.players.get_players(source.player)
        targets = []
        for p in players:
            for minion in p.minions:
                if self.match(source, minion):
                    targets.append(minion)

        return targets

    def choose_targets(self, source, target=None):
        possible_targets = self.get_targets(source, target)
        return self.picker.pick(possible_targets, source.player)

    def match(self, source, obj):
        if self.condition:
            return obj.is_minion() and self.players.match(source, obj)\
                and self.condition.evaluate(source, obj)
        else:
            return obj.is_minion() and self.players.match(source, obj)

    def __to_json__(self):
        if self.condition:
            return {
                'name': 'minion',
                'condition': self.condition,
                'players': self.players,
                'picker': self.picker
            }
        return {
            'name': 'minion',
            'players': self.players,
            'picker': self.picker
        }

    def __from_json__(self, players, picker, condition=None):
        if condition:
            self.condition = hearthbreaker.tags.condition.Condition.from_json(**condition)
        else:
            self.condition = None
        self.players = Player.from_json(players)
        self.picker = Picker.from_json(**picker)
        return self


class CharacterSelector(Selector):
    def __init__(self, condition=hearthbreaker.tags.condition.MinionIsNotTarget(), players=FriendlyPlayer(),
                 picker=AllPicker()):
        self.condition = condition
        self.players = players
        self.picker = picker

    def get_targets(self, source, obj=None):
        players = self.players.get_players(source.player)
        targets = []
        for p in players:
            for minion in p.minions:
                if self.match(source, minion):
                    targets.append(minion)
        for p in players:  # Done in this order for historical reasons.
            if self.match(source, p.hero):
                targets.append(p.hero)

        return targets

    def choose_targets(self, source, target=None):
        possible_targets = self.get_targets(source, target)
        return self.picker.pick(possible_targets, source.player)

    def match(self, source, obj):
        if self.condition:
            return not obj.is_card() and self.players.match(source, obj) \
                and self.condition.evaluate(source, obj)
        else:
            return not obj.is_card() and self.players.match(source, obj)

    def __to_json__(self):
        if self.condition:
            return {
                'name': 'character',
                'condition': self.condition,
                'players': self.players,
                'picker': self.picker
            }
        return {
            'name': 'character',
            'players': self.players,
            'picker': self.picker,
        }

    def __from_json__(self, players, picker, condition=None):
        if condition:
            self.condition = hearthbreaker.tags.condition.Condition.from_json(**condition)
        else:
            self.condition = None
        self.players = Player.from_json(players)
        self.picker = Picker.from_json(**picker)
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


class WeaponSelector(Selector):
    def __init__(self, players=FriendlyPlayer()):
        self.players = players

    def get_targets(self, source, obj=None):
        return [p.hero.weapon for p in self.players.get_players(source.player) if p.hero.weapon]

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


class Count(Function):
    def __init__(self, selector):
        self.selector = selector

    def do(self, target):
        return len(self.selector.get_targets(target))

    def __to_json__(self):
        return {
            'name': 'count',
            'selector': self.selector
        }

    def __from_json__(self, selector):
        self.selector = Selector.from_json(**selector)
        return self


class Attribute(Function):
    def __init__(self, attribute, selector):
        self.attribute = attribute
        self.selector = selector

    def do(self, target):
        targets = self.selector.get_targets(target)
        if len(targets) > 0 and targets[0]:
            if self.attribute == "damage":
                return targets[0].calculate_max_health() - targets[0].health
            return getattr(targets[0], self.attribute)
        return 0

    def __to_json__(self):
        return {
            'name': 'attribute',
            'attribute': self.attribute,
            'selector': self.selector
        }

    def __from_json__(self, attribute, selector):
        self.attribute = attribute
        self.selector = Selector.from_json(**selector)
        return self
