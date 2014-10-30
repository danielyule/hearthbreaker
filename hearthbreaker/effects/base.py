import abc
import string
import hearthbreaker.effects.minion


class Aura:
    def __init__(self, action, selector):
        self.target = None
        self.action = action
        self.selector = selector

    def set_target(self, target):
        self.target = target

    def apply(self):
        targets = self.selector.get_targets(self.target, self.target.player)
        for target in targets:
            self.action.act(target)

    def unapply(self):
        targets = self.selector.get_targets(self.target, self.target.player)
        for target in targets:
            self.action.unact(target)

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


class Selector(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_targets(self, source, player):
        pass

    @abc.abstractmethod
    def match(self, source, obj):
        pass

    @abc.abstractmethod
    def __to_json__(self):
        pass

    @staticmethod
    def from_json(name, **kwargs):
        import hearthbreaker.effects.selector as selector_mod

        cls_name = string.capwords(name, '_').replace("_", "") + "Selector"
        cls = getattr(selector_mod, cls_name)
        obj = cls.__new__(cls)
        return obj.__from_json__(**kwargs)

    def __from_json__(self, **kwargs):
        self.__init__(**kwargs)
        return self


class Action(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def act(self, target):
        pass

    @staticmethod
    def from_json(name, **kwargs):
        import hearthbreaker.effects.action as action_mod

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


class ReversibleAction(Action, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def unact(self, target):
        pass


class MinionAction(ReversibleAction, metaclass=abc.ABCMeta):
    pass


class Event(metaclass=abc.ABCMeta):
    def __init__(self, event_name, condition):
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
        import hearthbreaker.effects.event as event_mod

        cls_name = string.capwords(event_name, '_').replace("_", "")
        cls = getattr(event_mod, cls_name)
        obj = cls.__new__(cls)
        return obj.__from_json__(**kwargs)

    def __from_json__(self, condition=None):
        if condition:
            condition = Condition.from_json(**condition)
        self.__init__(condition)
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


class NewEffect:
    def __init__(self, event, action, targeting):
        self.event = event
        if isinstance(action, MinionAction):
            from hearthbreaker.effects.action import Give
            self.action = Give(action)
        else:
            self.action = action
        self.targeting = targeting
        self.target = None

    def apply(self):
        self.event.bind(self.target, self._find_target)

    def unapply(self):
        self.event.unbind(self.target, self._find_target)

    def set_target(self, target):
        self.target = target

    def _find_target(self, focus=None, other=None):
        target = self.targeting.select_target(self.target, focus, other)
        if target:
            self.action.act(target)

    def __to_json__(self):
        return {
            'event': self.event,
            'action': self.action,
            'targeting': self.targeting,
        }

    @staticmethod
    def from_json(game, **kwargs):
        if 'action' not in kwargs or type(kwargs['action']) is str:
            return hearthbreaker.effects.minion.MinionEffect.from_json(game, **kwargs)
        else:
            action = Action.from_json(**kwargs['action'])
            event = Event.from_json(**kwargs['event'])
            targeting = Targeting.from_json(**kwargs['targeting'])
            return NewEffect(event, action, targeting)


class Targeting(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def select_target(self, this, focus, other):
        pass

    @abc.abstractmethod
    def __to_json__(self):
        pass

    @staticmethod
    def from_json(name, **kwargs):
        import hearthbreaker.effects.target as action_mod

        cls_name = string.capwords(name, '_').replace("_", "")
        cls = getattr(action_mod, cls_name)
        obj = cls.__new__(cls)
        return obj.__from_json__(**kwargs)

    def __from_json__(self, **kwargs):
        self.__init__(**kwargs)
        return self


class Condition(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def evaluate(self, target, *args):
        pass

    @staticmethod
    def from_json(name, **kwargs):
        import hearthbreaker.effects.condition as action_mod

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
