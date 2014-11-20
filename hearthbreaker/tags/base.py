import abc
import json
import string
import hearthbreaker


class JSONObject(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __to_json__(self):
        pass

    @staticmethod
    @abc.abstractclassmethod
    def from_json(action, selector):
        pass

    def eq(self, other):
        return str(self) == str(other)

    def __str__(self):
        return json.dumps(self.__to_json__(), default=lambda o: o.__to_json__(), sort_keys=True)


class Aura(JSONObject):
    def __init__(self, action, selector):
        self.target = None
        self.action = action
        self.selector = selector

    def set_target(self, target):
        self.target = target

    def apply(self):
        targets = self.selector.get_targets(self.target)
        for target in targets:
            self.action.act(self.target, target)

    def unapply(self):
        targets = self.selector.get_targets(self.target)
        for target in targets:
            self.action.unact(self.target, target)

    def match(self, obj):
        return self.selector.match(self.target, obj)

    def __to_json__(self):
        return {
            'action': self.action,
            'selector': self.selector
        }

    @staticmethod
    def from_json(action, selector):
        action = Action.from_json(**action)
        selector = Selector.from_json(**selector)
        return Aura(action, selector)


class AuraUntil(Aura):
    def __init__(self, action, selector, until):
        super().__init__(action, selector)
        self.until = until

    def apply(self):
        super().apply()
        self.until.bind(self.target, self.__until__)

    def unapply(self):
        self.until.unbind(self.target, self.__until__)
        super().unapply()

    def __until__(self, *args):
        if isinstance(self.selector, hearthbreaker.tags.selector.SelfSelector):
            self.target.remove_aura(self)
        else:
            self.target.player.remove_aura(self)

    def __to_json__(self):
        return {
            'action': self.action,
            'selector': self.selector,
            'until': self.until
        }

    @staticmethod
    def from_json(action, selector, until):
        action = Action.from_json(**action)
        selector = Selector.from_json(**selector)
        until = Event.from_json(**until)
        return AuraUntil(action, selector, until)


class Player(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_players(self, target):
        pass

    @abc.abstractmethod
    def match(self, source, obj):
        pass

    @staticmethod
    def from_json(name):
        from hearthbreaker.tags.selector import FriendlyPlayer, EnemyPlayer, BothPlayer, PlayerOne,\
            PlayerTwo, CurrentPlayer
        if name == "friendly":
            return FriendlyPlayer()
        elif name == "enemy":
            return EnemyPlayer()
        elif name == "both":
            return BothPlayer()
        elif name == "player_one":
            return PlayerOne()
        elif name == "player_two":
            return PlayerTwo()
        elif name == "current_player":
            return CurrentPlayer


class Selector(JSONObject, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_targets(self, source, target=None):
        pass

    @abc.abstractmethod
    def match(self, source, obj):
        pass

    @staticmethod
    def from_json(name, **kwargs):
        import hearthbreaker.tags.selector as selector_mod

        cls_name = string.capwords(name, '_').replace("_", "") + "Selector"
        cls = getattr(selector_mod, cls_name)
        obj = cls.__new__(cls)
        return obj.__from_json__(**kwargs)

    def __from_json__(self, **kwargs):
        self.__init__(**kwargs)
        return self


class Action(JSONObject, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def act(self, actor, target):
        pass

    @staticmethod
    def from_json(name, **kwargs):
        import hearthbreaker.tags.action as action_mod

        cls_name = string.capwords(name, '_').replace("_", "")
        cls = getattr(action_mod, cls_name)
        obj = cls.__new__(cls)
        return obj.__from_json__(**kwargs)

    def __from_json__(self, **kwargs):
        self.__init__(**kwargs)
        return self

    def track_changes(self, player):
        pass


class ReversibleAction(Action, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def unact(self, actor, target):
        pass


class MinionAction(ReversibleAction, metaclass=abc.ABCMeta):
    pass


class Event(JSONObject, metaclass=abc.ABCMeta):
    def __init__(self, event_name, condition=None):
        self.event_name = event_name
        self.condition = condition
        self.__func__ = None
        self.__target__ = None

    @abc.abstractmethod
    def bind(self, target, func):
        pass

    @abc.abstractmethod
    def unbind(self, target, func):
        pass

    def __action__(self, *args):
        if self.condition.evaluate(self.__target__, *args):
            self.__func__(*args)

    @staticmethod
    def from_json(event_name, **kwargs):
        import hearthbreaker.tags.event as event_mod

        cls_name = string.capwords(event_name, '_').replace("_", "")
        cls = getattr(event_mod, cls_name)
        obj = cls.__new__(cls)
        return obj.__from_json__(**kwargs)

    def __from_json__(self, condition=None):
        if condition:
            condition = Condition.from_json(**condition)
            self.__init__(condition)
        else:
            self.__init__()
        return self

    def __to_json__(self):
        if self.condition:
            return {
                'event_name': self.event_name,
                'condition': self.condition
            }
        return {
            'event_name': self.event_name
        }


class MinionEvent(Event):
    def bind(self, target, func):
        if self.condition:
            self.__target__ = target
            self.__func__ = func
            target.bind(self.event_name, self.__action__)
        else:
            target.bind(self.event_name, func)

    def unbind(self, target, func):
        if self.condition:
            target.unbind(self.event_name, self.__action__)
        else:
            target.unbind(self.event_name, func)


class PlayerEvent(Event):
    def __init__(self, event_name, condition, player):
        super().__init__(event_name, condition)
        self.player = player

    def bind(self, target, func):
        for player in self.player.get_players(target.player):
            if self.condition:
                self.__target__ = target
                self.__func__ = func
                player.bind(self.event_name, self.__action__)
            else:
                player.bind(self.event_name, func)

    def unbind(self, target, func):
        for player in self.player.get_players(target.player):
            if self.condition:
                player.unbind(self.event_name, self.__action__)
            else:
                player.unbind(self.event_name, func)

    def __to_json__(self):
        super_json = super().__to_json__()
        super_json.update({
            'player': self.player
        })
        return super_json

    def __from_json__(self, player, condition=None):
        if condition:
            condition = Condition.from_json(**condition)
        player = Player.from_json(player)
        self.__init__(condition, player)
        return self


class Effect(JSONObject):
    def __init__(self, event, action, selector):
        self.event = event
        if isinstance(action, ReversibleAction):
            from hearthbreaker.tags.action import Give
            self.action = Give(action)
        else:
            self.action = action
        self.selector = selector
        self.target = None

    def apply(self):
        self.event.bind(self.target, self._find_target)
        self.action.track_changes(self.target.player)

    def unapply(self):
        self.event.unbind(self.target, self._find_target)

    def set_target(self, target):
        self.target = target

    def _find_target(self, focus=None, other=None, *args):
        targets = self.selector.get_targets(self.target, focus)
        for target in targets:
            self.action.act(self.target, target)

    def __to_json__(self):
        return {
            'event': self.event,
            'action': self.action,
            'selector': self.selector,
        }

    @staticmethod
    def from_json(game, action, event, selector):
            action = Action.from_json(**action)
            event = Event.from_json(**event)
            selector = Selector.from_json(**selector)
            return Effect(event, action, selector)


class Condition(JSONObject, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def evaluate(self, target, *args):
        pass

    @staticmethod
    def from_json(name, **kwargs):
        import hearthbreaker.tags.condition as action_mod

        cls_name = string.capwords(name, '_').replace("_", "")
        cls = getattr(action_mod, cls_name)
        obj = cls.__new__(cls)
        return obj.__from_json__(**kwargs)

    def __from_json__(self, **kwargs):
        self.__init__(**kwargs)
        return self

    @abc.abstractmethod
    def __to_json__(self):
        pass


class Deathrattle(JSONObject):
    def __init__(self, action, selector):
        self.action = action
        self.selector = selector

    def deathrattle(self, target):
        targets = self.selector.get_targets(target, target)
        for t in targets:
            self.action.act(target, t)

        target.player.game.check_delayed()

    def __to_json__(self):
        return {
            'action': self.action,
            'selector': self.selector
        }

    @staticmethod
    def from_json(action, selector):
        action = Action.from_json(**action)
        selector = Selector.from_json(**selector)
        return Deathrattle(action, selector)
