import abc
import copy
import json
import string


class JSONObject(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __to_json__(self):
        pass

    @staticmethod
    @abc.abstractclassmethod
    def from_json(action, selector):
        pass

    def to_instance(self, target):
        return copy.copy(self)

    def __from_json__(self, **kwargs):
        self.__init__(**kwargs)
        return self

    def eq(self, other):
        return str(self) == str(other)

    def __str__(self):
        return json.dumps(self.__to_json__(), default=lambda o: o.__to_json__(), sort_keys=True)


class Tag(JSONObject):
    def __deepcopy__(self, memo):
        cls = self.__class__
        new = cls.__new__(cls)
        memo[id(self)] = new
        for attribute, value in self.__dict__.items():
            if attribute != "owner":
                setattr(new, attribute, copy.deepcopy(value, memo))
            else:
                setattr(new, attribute, None)
        return new


class Aura(Tag):
    def __init__(self, status, selector, condition=None, expires=False):
        self.owner = None
        self.status = status
        self.selector = selector
        self.condition = condition
        self.expires = expires

    def set_owner(self, owner):
        self.owner = owner

    def apply(self):
        if not self.condition or self.condition.evaluate(self.owner, self.owner):
            targets = self.selector.get_targets(self.owner)
            for target in targets:
                self.status.act(self.owner, target)

    def unapply(self):
        targets = self.selector.get_targets(self.owner)
        for target in targets:
            self.status.unact(self.owner, target)

    def match(self, obj):
        return (not self.condition or self.condition.evaluate(self.owner, self.owner)) and \
            self.selector.match(self.owner, obj)

    def __to_json__(self):
        if self.condition:
            return {
                'status': self.status,
                'selector': self.selector,
                'condition': self.condition,
                'expires': self.expires,
            }
        return {
            'status': self.status,
            'selector': self.selector,
            'expires': self.expires,
        }

    @staticmethod
    def from_json(status, selector, condition=None, expires=False):
        status = Status.from_json(**status)
        selector = Selector.from_json(**selector)
        if condition:
            condition = Condition.from_json(**condition)
        return Aura(status, selector, condition, expires)


class Buff(Tag):
    def __init__(self, status, condition=None):
        self.status = status
        self.condition = condition
        self.owner = None

    def set_owner(self, owner):
        self.owner = owner

    def apply(self):
        if not self.condition or self.condition.evaluate(self.owner, self.owner):
            self.status.act(self.owner, self.owner)

    def unapply(self):
        self.status.unact(self.owner, self.owner)

    def is_minion(self):
        return False

    def to_instance(self, target):
        new_instance = copy.copy(self)
        new_instance.status = self.status.to_instance(target)
        return new_instance

    def __to_json__(self):
        if self.condition:
            return {
                'status': self.status,
                'condition': self.condition
            }
        return {
            'status': self.status,
        }

    @staticmethod
    def from_json(status, condition=None):
        status = Status.from_json(**status)
        if condition:
            condition = Condition.from_json(**condition)
        return Buff(status, condition)


class BuffUntil(Buff):
    def __init__(self, status, until):
        super().__init__(status)
        self.until = until

    def apply(self):
        super().apply()
        self.until.bind(self.owner, self.__until__)

    def unapply(self):
        self.until.unbind(self.owner, self.__until__)
        super().unapply()

    def __until__(self, *args):
        self.owner.remove_buff(self)

    def __to_json__(self):
        return {
            'status': self.status,
            'until': self.until
        }

    @staticmethod
    def from_json(status, until):
        status = Status.from_json(**status)
        until = Event.from_json(**until)
        return BuffUntil(status, until)


class AuraUntil(Aura):
    def __init__(self, status, selector, until, expires=True):
        super().__init__(status, selector, None, expires)
        self.until = until

    def apply(self):
        super().apply()
        self.until.bind(self.owner, self.__until__)

    def unapply(self):
        self.until.unbind(self.owner, self.__until__)
        super().unapply()

    def __until__(self, *args):
        self.owner.player.remove_aura(self)

    def __to_json__(self):
        return {
            'status': self.status,
            'selector': self.selector,
            'until': self.until,
            'expires': self.expires
        }

    @staticmethod
    def from_json(status, selector, until, expires=True):
        status = Status.from_json(**status)
        selector = Selector.from_json(**selector)
        until = Event.from_json(**until)
        return AuraUntil(status, selector, until, expires)


class Player(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_players(self, target):
        pass

    @abc.abstractmethod
    def match(self, source, obj):
        pass

    @staticmethod
    def from_json(name):
        from hearthbreaker.tags.selector import FriendlyPlayer, EnemyPlayer, BothPlayer, PlayerOne, \
            PlayerTwo, CurrentPlayer, OtherPlayer
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
            return CurrentPlayer()
        elif name == "other_player":
            return OtherPlayer()


class Picker(JSONObject, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def pick(self, source, targets):
        pass

    @staticmethod
    def from_json(name, count=0):
        from hearthbreaker.tags.selector import UserPicker, AllPicker, RandomPicker
        if name == "user":
            return UserPicker()
        elif name == "all":
            return AllPicker()
        elif name == "random":
            return RandomPicker(count)
        else:
            raise TypeError("What are you even doing?")


class Selector(JSONObject, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_targets(self, source, target=None):
        pass

    def choose_targets(self, source, target=None):
        return self.get_targets(source, target)

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


class Action(JSONObject, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def act(self, actor, target, other=None):
        pass

    @staticmethod
    def from_json(name, **kwargs):
        import hearthbreaker.tags.action as action_mod

        cls_name = string.capwords(name, '_').replace("_", "")
        cls = getattr(action_mod, cls_name)
        obj = cls.__new__(cls)
        return obj.__from_json__(**kwargs)


class Status(JSONObject, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def act(self, actor, target):
        pass

    @abc.abstractmethod
    def unact(self, actor, target):
        pass

    @staticmethod
    def from_json(name, **kwargs):
        import hearthbreaker.tags.status as status_mod

        cls_name = string.capwords(name, '_').replace("_", "")
        cls = getattr(status_mod, cls_name)
        obj = cls.__new__(cls)
        return obj.__from_json__(**kwargs)


class Amount(abc.ABCMeta):
    def __init__(cls, name, bases, dct):
        super(Amount, cls).__init__(name, bases, dct)
        base_init = cls.__init__
        base_to_json = cls.__to_json__
        base_from_json = cls.__from_json__
        base_to_instance = cls.to_instance

        def init_with_amount(self, amount=1, multiplier=1, **kwargs):
            self.amount = amount
            self.multipler = multiplier
            return base_init(self, **kwargs)

        def to_json_with_amount(self):
            js = base_to_json(self)
            if self.amount:
                js['amount'] = self.amount
            if self.multipler != 1:
                js['multiplier'] = self.multipler
            return js

        def from_json_with_amount(self, amount=1, multiplier=1, **kwargs):
            if amount:
                if isinstance(amount, dict):
                    self.amount = Function.from_json(**amount)
                else:
                    self.amount = amount
            self.multipler = multiplier
            if base_from_json is JSONObject.__from_json__:
                base_init(self, **kwargs)
                return self
            return base_from_json(self, **kwargs)

        def get_amount(self, source, target, *args):
            if isinstance(self.amount, Function):
                return self.amount.do(source, *args) * self.multipler
            else:
                return self.amount

        def to_instance(self, target):
            new_instance = base_to_instance(self, target)
            new_instance.amount = new_instance.get_amount(target, target)
            return new_instance

        cls.__init__ = init_with_amount
        cls.__to_json__ = to_json_with_amount
        cls.__from_json__ = from_json_with_amount
        cls.get_amount = get_amount
        cls.to_instance = to_instance


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

    def __deepcopy__(self, memo):
        cls = type(self)
        new = cls.__new__(cls)
        memo[id(self)] = new
        if self.condition:
            new.condition = copy.deepcopy(self.condition, memo)
        else:
            new.condition = None
        new.event_name = self.event_name
        return new

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

    def __deepcopy__(self, memo):
        new = super().__deepcopy__(memo)
        new.player = copy.deepcopy(self.player, memo)
        return new

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


class Effect(Tag):
    def __init__(self, event, tags):
        self.event = event
        if isinstance(tags, list):
            self.tags = tags
        else:
            self.tags = [tags]
        self.owner = None
        self.other = None

    def apply(self):
        self.event.bind(self.owner, self._find_target)

    def unapply(self):
        self.event.unbind(self.owner, self._find_target)

    def set_owner(self, owner):
        self.owner = owner

    def _find_target(self, focus=None, other=None, *args):
        for tag in self.tags:
            if not tag.do(self.owner, focus, other):
                break

    def __to_json__(self):
        return {
            'event': self.event,
            'tags': self.tags,
        }

    @staticmethod
    def from_json(event, tags):
        tags = [ActionTag.from_json(**tag) for tag in tags]
        event = Event.from_json(**event)
        return Effect(event, tags)


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

    @abc.abstractmethod
    def __to_json__(self):
        pass


class ActionTag(Tag):
    def __init__(self, actions, selector, condition=None):
        if isinstance(actions, list):
            self.actions = actions
        else:
            self.actions = [actions]
        self.selector = selector
        self.condition = condition

    def do(self, owner, target=None, other=None):
        if self.condition:
            if not self.condition.evaluate(owner, target):
                return
        targets = self.selector.choose_targets(owner, target)
        found_target = False
        for t in targets:
            found_target = True
            if t is owner or t.is_valid():
                for action in self.actions:
                    action.act(owner, t, other)

        return found_target

    def __to_json__(self):
        if self.condition:
            return {
                'actions': self.actions,
                'selector': self.selector,
                'condition': self.condition,
            }
        return {
            'actions': self.actions,
            'selector': self.selector
        }

    @classmethod
    def from_json(cls, actions, selector, condition=None):
        action = [Action.from_json(**a) for a in actions]
        selector = Selector.from_json(**selector)
        if condition:
            condition = Condition.from_json(**condition)
        return cls(action, selector, condition)


class Deathrattle(ActionTag):
    def do(self, target):
        super().do(target)
        target.player.game.check_delayed()


class Spell(ActionTag):
    def __init__(self, actions, selector, condition=None):
        super().__init__(actions, selector, condition)


class CardQuery(JSONObject, metaclass=abc.ABCMeta):
    def __init__(self):
        pass

    @abc.abstractmethod
    def get_card(self, target, player, owner):
        pass

    @abc.abstractmethod
    def __to_json__(self):
        pass

    @staticmethod
    def from_json(query):
        from hearthbreaker.tags.card_source import SpecificCard, CardList, HandSource, \
            DeckSource, CollectionSource, ObjectSource, LastCard, Same
        if isinstance(query, str):
            return SpecificCard.__from_json__(query)
        elif isinstance(query, list):
            return CardList.__from_json__(query)
        elif query['name'] == 'object':
            return ObjectSource.__from_json__(**query)
        elif query['name'] == 'hand':
            return HandSource.__from_json__(**query)
        elif query['name'] == 'deck':
            return DeckSource.__from_json__(**query)
        elif query['name'] == 'collection':
            return CollectionSource.__from_json__(**query)
        elif query['name'] == 'last_card':
            return LastCard()
        elif query['name'] == 'same':
            return Same()
        else:
            raise Exception(query['name'])


class Battlecry(ActionTag):
    def __init__(self, actions, selector, condition=None):
        super().__init__(actions, selector, condition)


class Choice(ActionTag):
    def __init__(self, card, actions, selector, condition=None):
        self.card = card
        super().__init__(actions, selector, condition)

    def __to_json__(self):
        super_json = super().__to_json__()
        super_json['card'] = self.card.ref_name
        return super_json

    @staticmethod
    def from_json(card, actions, selector, condition=None):
        from hearthbreaker.engine import card_lookup
        actions = [Action.from_json(**action) for action in actions]
        selector = Selector.from_json(**selector)
        if condition:
            condition = Condition.from_json(**condition)
        card = card_lookup(card)
        return Choice(card, actions, selector, condition)


class Function(JSONObject, metaclass=abc.ABCMeta):

    def do(self, target, *args):
        pass

    @staticmethod
    def from_json(name, **kwargs):
        import hearthbreaker.tags.selector as selector_mod

        cls_name = string.capwords(name, '_').replace("_", "")
        cls = getattr(selector_mod, cls_name)
        obj = cls.__new__(cls)
        return obj.__from_json__(**kwargs)

    def __from_json__(self, **kwargs):
        self.__init__(**kwargs)
        return self


class Context(metaclass=abc.ABCMeta):
    """
    Handles computations for actions and statuses that change based on if they are part of a battlecry, hero power
    or spell.
    """

    def __init__(self, player):
        """
        Creates a context associated with a particular player
        :param player: The player that this context is associated with
        :type player: :class:`hearthbreaker.engine.Player`
        """
        self.player = player

    @abc.abstractmethod
    def filter_targets(self, targets):
        """
        Filter the targets that the user can choose.  Spells cannot target minions who are not spell_targetable,
        for example.

        :param targets: All the possible target characters
        :type targets: [:class:`hearthbreaker.game_objects.Character`]
        :return: A list of targets which has been filtered according to the context
        :rtype: [:class:`hearthbreaker.game_objects.Character`]
        """
        pass

    @abc.abstractmethod
    def damage(self, amount, target):
        """
        Damage the target according to the context.  Spells must include spell_damage, while battlecries and physical
        attacks do not
        :param amount: The amount to damage the target
        :type amount: :class:`hearthbreaker.game_objects.Character`
        :param target: The character getting damaged
        """
        pass

    @abc.abstractmethod
    def heal(self, amount, target):
        """
        Heals the target according to the context.  Spells and hero power include heal_multiplier, while battlecries
        do not
        :param amount: The amount to damage the target
        :type amount: :class:`hearthbreaker.game_objects.Character`
        :param target: The character getting damaged
        """
        pass
