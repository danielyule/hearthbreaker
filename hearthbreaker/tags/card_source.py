import abc
from itertools import chain

from hearthbreaker.tags.base import CardQuery, Player, Condition, Selector
from hearthbreaker.tags.selector import FriendlyPlayer


class CardSource(CardQuery, metaclass=abc.ABCMeta):

    def __init__(self, conditions):
        self.conditions = conditions

    def get_card(self, target, player, owner):
        card_list = self.get_list(target, player, owner)

        def check_condition(condition):
            return lambda c: condition.evaluate(target, c)

        for condition in self.conditions:
            card_list = filter(check_condition(condition), card_list)

        card_list = [card for card in card_list]
        card_len = len(card_list)
        if card_len == 1:
            return card_list[0]
        elif card_len == 0:
            return None
        else:
            return player.game.random_choice(card_list)

    @abc.abstractmethod
    def get_list(self, target, player, owner):
        pass


class HandSource(CardSource):

    def __init__(self, player=FriendlyPlayer(), conditions=[]):
        super().__init__(conditions)
        self.player = player

    def get_list(self, target, player, owner):
        players = self.player.get_players(target)
        cards = []
        for player in players:
            cards.extend(player.hand)
        return cards

    def __to_json__(self):
        return {
            'name': 'hand',
            'conditions': self.conditions,
            'player': self.player
        }

    @staticmethod
    def __from_json__(name, player, conditions):
        return HandSource(
            Player.from_json(player),
            [Condition.from_json(**condition) for condition in conditions]
        )


class DeckSource(CardSource):
    def __init__(self, player=FriendlyPlayer(), conditions=[]):
        super().__init__(conditions)
        self.player = player

    def get_list(self, target, player, owner):
        players = self.player.get_players(target)
        if len(players) == 1:
            return filter(lambda c: not c.drawn, players[0].deck.cards)
        else:
            return filter(lambda c: not c.drawn, chain(players[0].deck.cards, players[1].deck.cards))

    def __to_json__(self):
        return {
            'name': 'deck',
            'conditions': self.conditions,
            'player': self.player
        }

    @staticmethod
    def __from_json__(name, player, conditions):
        return DeckSource(
            Player.from_json(player),
            [Condition.from_json(**condition) for condition in conditions]
        )


class ObjectSource(CardQuery):
    def __init__(self, selector):
        self.selector = selector

    def get_card(self, target, player, owner):
        objects = self.selector.choose_targets(owner, target)
        if len(objects) == 1:
            return objects[0].card
        elif len(objects) == 0:
            return None
        else:
            return player.game.random_choice(objects).card

    def __to_json__(self):
        return {
            'name': 'object',
            'selector': self.selector,
        }

    @staticmethod
    def __from_json__(name, selector):
        return ObjectSource(Selector.from_json(**selector))


class SpecificCard(CardQuery):
    def __init__(self, card):
        self.card = card

    def get_card(self, target, player, owner):
        from hearthbreaker.engine import card_lookup
        return card_lookup(self.card)

    def __to_json__(self):
        return self.card

    @staticmethod
    def __from_json__(card):

        return SpecificCard(card)


class CardList(CardQuery):
    def __init__(self, list):
        self.list = list

    def get_card(self, target, player, owner):
        return player.game.random_choice(self.list)

    def __to_json__(self):
        return [card.name for card in self.list]

    @staticmethod
    def __from_json__(cards):
        from hearthbreaker.engine import card_lookup
        return CardList([card_lookup(card) for card in cards])


class CollectionSource(CardSource):
    def __init__(self, conditions):
        self.conditions = conditions

    def get_list(self, target, player, owner):
        from hearthbreaker.engine import get_cards
        return get_cards()

    def __to_json__(self):
        return {
            'name': 'collection',
            'conditions': self.conditions,
        }

    @staticmethod
    def __from_json__(name, conditions):
        return CollectionSource([Condition.from_json(**condition) for condition in conditions])


class LastCard(CardQuery):
    def __init__(self, player=FriendlyPlayer(),):
        super().__init__()
        self.player = player

    def get_card(self, target, player, owner):
        players = self.player.get_players(target)
        return players[0].game.last_card

    def __to_json__(self):
        return {
            'name': 'last_card',
            'player': self.player
        }

    @staticmethod
    def __from_json__(name, player):
        return LastCard(
            Player.from_json(player),
        )


class Same(CardQuery):
    def __init__(self):
        super().__init__()

    def get_card(self, target, player, owner):
        return player.game.selected_card

    def __to_json__(self):
        return {
            'name': 'same',
        }

    @staticmethod
    def __from_json__(name):
        return Same()
