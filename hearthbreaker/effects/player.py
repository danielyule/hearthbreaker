import abc
from hearthbreaker.game_objects import MinionCard, SecretCard
import hearthbreaker.replay


class PlayerEffect(metaclass=abc.ABCMeta):
    """
    Represents effects that affect the player.  All player effects have an `action` attribute that specifies what the
    action is.  Each type of action has a set of parameters that determine how it applies.  Each action type has a
    specific subclass to represent it.
    """
    def __new__(cls, action, *args, **kwargs):

        if action == "mana_change":
            return ManaChangeEffect(*args, **kwargs)
        else:
            return super(PlayerEffect, cls).__new__(cls)

    @abc.abstractmethod
    def apply(self, player):
        pass

    def __init__(self, *args):
        pass


class ManaChangeEffect(PlayerEffect):

    def __init__(self, amount, card_filter, until, only_first=False):
        """
        Adds a mana filter to the cards that this player has.  Unlike the
        :class:`ManaFilter effect <hearthbreaker.effects.ManaFilter`, this filter is not tied to any minion, but
        instead will remain until an event occurs or, if `only_first` is True a card which matches the filter is played,
        whichever comes first.

        :param int amount: The amount to decrease the mana cost of effected cards
        :param string card_filter: The type of cards to affect.  Possible values are "minion", "spell", "secret" and
                                   "card"
        :param string until: The event to remove this mana filter.  Suggestions are "turn_started" for the start of the
                             next turn, "turn_ended" for the end of the current turn and "forever" if the filter should
                             never be removed.  The filter will be removed regardless of the `only_first` parameter.
        :param boolean only_first: True if this card filter should be removed the first time a player plays a card which
                                   matches the filter
        """
        super().__init__()
        self.amount = amount
        self.until = until
        self.card_filter = card_filter
        self.only_first = only_first

    def apply(self, player):
        this = self
        if self.card_filter == "minion":
            my_filter = lambda c: isinstance(c, MinionCard)
        elif self.card_filter == "spell":
            my_filter = lambda c: c.is_spell()
        elif self.card_filter == "secret":
            my_filter = lambda c: isinstance(c, SecretCard)
        else:
            my_filter = lambda c: True

        class Filter:
            def __init__(self):
                self.amount = this.amount
                self.min = 0
                self.filter = my_filter

        mana_filter = Filter()
        player.mana_filters.append(mana_filter)

        def remove():
            player.effects.remove(self)
            player.mana_filters.remove(mana_filter)
            if self.only_first:
                player.unbind("card_played", card_played)

        def card_played(card):
            if my_filter(card):
                remove()
                player.unbind(self.until, remove)
        if self.until != "forever":
            player.bind_once(self.until, remove)
        if self.only_first:
            player.bind("card_played", card_played)


class DuplicateMinion(PlayerEffect):
    def __init__(self, minion_to_duplicate, when):
        super().__init__()
        self.minion = hearthbreaker.replay.TrackingProxyCharacter(minion_to_duplicate, minion_to_duplicate.game)
        self.when = when

    def apply(self, player):

        def duplicate():
            minion = self.minion.resolve(player.game)
            if minion:
                dup = minion.copy(minion.player)
                dup.add_to_board(minion.index + 1)
            player.effects.remove(self)

        player.bind_once(self.when, duplicate)


class RemoveStealth(PlayerEffect):
    def __init__(self, stealthed_minions, when):
        super().__init__()
        self.minions = [hearthbreaker.replay.TrackingProxyCharacter(m, m.game) for m in stealthed_minions]
        self.when = when

    def apply(self, player):

        def duplicate():
            for ref in self.minions:
                minion = ref.resolve(player.game)
                if minion:
                    minion.stealth = False
            player.effects.remove(self)

        player.bind_once(self.when, duplicate)


class ReturnCard(PlayerEffect):
    def __init__(self, card, when):
        super().__init__()
        self.card = card
        self.when = when

    def apply(self, player):

        def return_card():
            if len(player.hand) < 10:
                player.hand.append(self.card)
            else:
                player.trigger("card_destroyed", self.card)
            player.effects.remove(self)

        player.bind_once(self.when, return_card)
