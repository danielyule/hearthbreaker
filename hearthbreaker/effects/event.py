from hearthbreaker.effects.base import MinionEvent, PlayerEvent


class DidDamage(MinionEvent):
    def __init__(self):
        super().__init__("did_damage")


class SpellCast(PlayerEvent):
    def __init__(self):
        super().__init__("spell_cast")


class Either(PlayerEvent):
    def __init__(self, event1, event2):
        super().__init__("either")
        self.event1 = event1
        self.event2 = event2

    def bind(self, target, func):
        self.event1.bind(target, func)
        self.event2.bind(target, func)

    def unbind(self, target, func):
        self.event1.unbind(target, func)
        self.event2.unbind(target, func)

    def __to_json__(self):
        return {
            'event_name': self.event_name,
            'event1': self.event1,
            'event2': self.event2,
        }

    def __from_json__(self, **kwargs):
        event1 = self.from_json(**kwargs['event1'])
        event2 = self.from_json(**kwargs['event2'])
        return Either(event1, event2)


class MatchingCardPlayed(PlayerEvent):
    def __init__(self, card_selector=None):
        super().__init__("card_played")
        self.selector = card_selector
        self.func = None

    def bind(self, target, func):
        self.func = func
        target.player.bind(self.event_name, self._check_selector)

    def unbind(self, target, func):
        self.func = func
        target.player.unbind(self.event_name, self._check_selector)

    def _check_selector(self, card, index):
        if self.selector and self.selector.match(card):
            self.func(card, index)

    def __to_json__(self):
        return {
            'event_name': 'matching_card_played',
            'card_selector': self.selector
        }


class TurnEnded(PlayerEvent):
    def __init__(self):
        super().__init__("turn_ended")
