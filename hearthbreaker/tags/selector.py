import abc
from hearthbreaker.tags.base import Selector, Player, Picker, Function, Amount, Condition
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
    def pick(self, source, targets):
        return targets

    def __to_json__(self):
        return {
            'name': "all"
        }


class UserPicker(Picker):
    def pick(self, source, targets):
        if source.card.current_target:
            return [source.card.current_target]
        filtered_targets = [target for target in filter(lambda t: t.player is source.player or not t.stealth, targets)]
        if len(filtered_targets) > 0:
            source.card.current_target = source.player.agent.choose_target(filtered_targets)
            return [source.card.current_target]
        return filtered_targets

    def __to_json__(self):
        return {
            'name': "user"
        }


class RandomPicker(Picker):
    def __init__(self, count=1):
        self.count = count

    def pick(self, source, targets):
        for i in range(self.count):
            if len(targets) > 0:
                yield source.player.game.random_choice(targets)
            targets = [target for target in filter(lambda t: not (t.is_minion() and t.dead), targets)]

    def __to_json__(self):
        return {
            'name': "random",
            'count': self.count
        }


class CardSelector(Selector, metaclass=abc.ABCMeta):
    def __init__(self, players=FriendlyPlayer(), condition=None):
        self.players = players
        self.condition = condition

    def get_targets(self, source, obj=None):
        players = self.players.get_players(source.player)
        targets = []
        for p in players:
            for card in p.hand:
                if self.match(source, card):
                    targets.append(card)

        return targets

    def match(self, source, obj):
        if self.condition:
            return obj.is_card() and self.players.match(source, obj) and self.condition.evaluate(source, obj)
        return obj.is_card() and self.players.match(source, obj)

    def __to_json__(self):
        if self.condition:
            return {
                'name': 'card',
                'players': self.players,
                'condition': self.condition,
            }
        return {
            'name': 'card',
            'players': self.players
        }

    def __from_json__(self, players='friendly', condition=None):
        self.players = Player.from_json(players)
        if condition:
            self.condition = Condition.from_json(**condition)
        else:
            self.condition = None
        return self


class LastDrawnSelector(CardSelector):
    def __init__(self, players=FriendlyPlayer()):
        super().__init__(players)

    def get_targets(self, source, obj=None):
        if source.player.fatigue > 0:
            return []
        players = self.players.get_players(source.player)
        return [player.hand[-1] for player in players]

    def match(self, source, obj):
        return obj in self.get_targets(source, obj)

    def __to_json__(self):
        return {
            'name': 'last_drawn',
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
        return self.picker.pick(source, possible_targets)

    def match(self, source, obj):
        return obj.is_hero() and self.players.match(source, obj)

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
        return self.picker.pick(source, possible_targets)

    def match(self, source, obj):
        if self.condition:
            return not obj.is_card() and obj.is_minion() and not obj.dead and self.players.match(source, obj)\
                and self.condition.evaluate(source, obj)
        else:
            return obj.is_minion() and self.players.match(source, obj) and not obj.dead

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


class DeadMinionSelector(Selector):
    def __init__(self, condition=None, players=FriendlyPlayer()):
        self.condition = condition
        self.players = players

    def get_targets(self, source, obj=None):
        players = self.players.get_players(source.player)
        targets = []
        for p in players:
            for minion in p.dead_this_turn:
                if self.match(source, minion):
                    targets.append(minion)

        return targets

    def match(self, source, obj):
        if self.condition:
            return not obj.is_card() and obj.is_minion() and self.players.match(source, obj) \
                and self.condition.evaluate(source, obj)
        else:
            return obj.is_minion() and self.players.match(source, obj)

    def __to_json__(self):
        if self.condition:
            return {
                'name': 'dead_minion',
                'condition': self.condition,
                'players': self.players,
            }
        return {
            'name': 'minion',
            'players': self.players,
        }

    def __from_json__(self, players, condition=None):
        if condition:
            self.condition = hearthbreaker.tags.condition.Condition.from_json(**condition)
        else:
            self.condition = None
        self.players = Player.from_json(players)
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
        return self.picker.pick(source, possible_targets)

    def match(self, source, obj):
        if self.condition:
            return not obj.is_card() and not obj.dead and self.players.match(source, obj) \
                and self.condition.evaluate(source, obj)
        else:
            return not obj.is_card() and not obj.dead and self.players.match(source, obj)

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


class ConstantSelector(Selector):
    def __init__(self, targets):
        self.targets = targets

    def match(self, source, obj):
        return obj.is_character() and obj.born in self.targets

    def get_targets(self, source, target=None):
        result = []
        for t in self.targets:
            for player in target.game.players:
                for minion in player.minions:
                    if minion.born == t:
                        result.append(minion)
        return result

    def __to_json__(self):
        return {
            'name': 'constant',
            'targets': self.targets
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
        return obj.is_weapon() and self.players.match(source, obj)

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

    def do(self, target, *args):
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

    def do(self, target, *args):
        targets = self.selector.get_targets(target)
        total = 0
        for t in targets:
            if self.attribute == "damage":
                total += t.calculate_max_health() - t.health
            elif self.attribute == 'mana':
                total += t.card.mana
            elif self.attribute == "attack":
                total += t.calculate_attack()
            else:
                total += getattr(t, self.attribute)
        return total

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


class Difference(Function, metaclass=Amount):
    def __init__(self, value):
        self.value = value

    def do(self, target, *args):
        return max(0, self.value - self.get_amount(target, target, *args))

    def __to_json__(self):
        return {
            'name': 'difference',
            'value': self.value,
        }

    def __from_json__(self, value):
        self.value = value
        return self


class RandomAmount(Function):
    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum

    def do(self, target, *args):
        return target.player.game._generate_random_between(self.minimum, self.maximum)

    def __to_json__(self):
        return {
            'name': 'random_amount',
            'minimum': self.minimum,
            'maximum': self.maximum,
        }


class EventValue(Function):
    def __init__(self):
        pass

    def do(self, target, *args):
        return args[0]

    def __to_json__(self):
        return {
            'name': 'event_value'
        }
