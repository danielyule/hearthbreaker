import abc
import string


class Aura(metaclass=abc.ABCMeta):
    def __init__(self):
        self.target = None

    def set_target(self, target):
        self.target = target

    @abc.abstractmethod
    def apply(self):
        pass

    @abc.abstractmethod
    def unapply(self):
        pass


class MinionAura(Aura):
    def __init__(self, effect, players, selector):
        super().__init__()
        self.effect = effect
        self.players = players
        self.selector = selector

    def apply(self):
        targets = self.players.get_player_minions(self.target)
        targets = self.selector.select(targets)
        for target in targets:
            self.effect.act(target)

    def unapply(self):
        targets = self.players.get_player_minions(self.target)
        targets = self.selector.select(targets)
        for target in targets:
            self.effect.unact(target)


class PlayerAura(Aura):
    def __init__(self, action, until):
        super().__init__()
        self.action = action
        self.until = until
        self.target = None

    def apply(self):
        self.action.act(self.target)
        self.until.bind(self.target.hero, self.__until__)

    def __until__(self, *args):
        self.target.remove_aura(self)

    def unapply(self):
        self.action.unact(self.target)
        self.until.unbind(self.target.hero, self.__until__)

    def __to_json__(self):
        return {
            'action': self.action,
            'until': self.until,
        }

    @staticmethod
    def from_json(**json):
        action = Action.from_json(**json['action'])
        until = Event.from_json(**json['until'])
        return PlayerAura(action, until)


class Action(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def act(self, target):
        pass

    @staticmethod
    def from_json(type, **kwargs):
        import hearthbreaker.effects.action as action_mod

        cls_name = string.capwords(type, '_').replace("_", "")
        cls = getattr(action_mod, cls_name)
        obj = cls.__new__(cls)
        return obj.__from_json__(**kwargs)

    def __from_json__(self, **kwargs):
        self.__init__(**kwargs)
        return self

    @abc.abstractmethod
    def __to_json__(self):
        pass


class ReversibleAction(Action, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def unact(self, target):
        pass


class Event(metaclass=abc.ABCMeta):
    def __init__(self, event_name):
        self.event_name = event_name

    @abc.abstractmethod
    def bind(self, target, func):
        pass

    @abc.abstractmethod
    def unbind(self, target, func):
        pass

    @staticmethod
    def from_json(event_name, **kwargs):
        import hearthbreaker.effects.event as event_mod

        cls_name = string.capwords(event_name, '_').replace("_", "")
        cls = getattr(event_mod, cls_name)
        obj = cls.__new__(cls)
        return obj.__from_json__(**kwargs)

    def __from_json__(self, **kwargs):
        self.__init__(**kwargs)
        return self

    def __to_json__(self):
        return {
            'event_name': self.event_name
        }


class MinionEvent(Event):
    def bind(self, target, func):
        target.bind(self.event_name, func)

    def unbind(self, target, func):
        target.unbind(self.event_name, func)


class PlayerEvent(Event):
    def bind(self, target, func):
        target.player.bind(self.event_name, func)

    def unbind(self, target, func):
        target.player.unbind(self.event_name, func)


class Selector(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def match(self, obj):
        pass

    @abc.abstractmethod
    def __to_json__(self):
        pass

    @staticmethod
    def from_json(type, **kwargs):
        import hearthbreaker.effects.selector as selector_mod

        cls_name = string.capwords(type, '_').replace("_", "") + "Selector"
        cls = getattr(selector_mod, cls_name)
        obj = cls.__new__(cls)
        return obj.__from_json__(**kwargs)

    def __from_json__(self, **kwargs):
        self.__init__(**kwargs)
        return self


class NewEffect:
    def __init__(self, event, action, targeting):
        self.event = event
        self.action = action
        self.targeting = targeting
        self.target = None

    def apply(self):
        self.event.bind(self.target, self._find_target)

    def unapply(self):
        self.event.unbind(self.target, self._find_target)

    def set_target(self, target):
        self.target = target

    def _find_target(self, focus, other=None):
        target = self.targeting.select_target(self.target, focus, other)
        self.action.act(target)


class Targeting(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def select_target(self, this, focus, other):
        pass
