from hearthbreaker.effects.base import MinionEvent, PlayerEvent


class DidDamage(MinionEvent):
    def __init__(self, condition=None):
        super().__init__("did_damage", condition)


class SpellCast(PlayerEvent):
    def __init__(self, condition=None):
        super().__init__("spell_cast", condition)


class Either(PlayerEvent):
    def __init__(self, event1, event2):
        super().__init__("either", None)
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


class CardPlayed(PlayerEvent):
    def __init__(self, condition):
        super().__init__("card_played", condition)


class TurnEnded(PlayerEvent):
    def __init__(self, condition=None):
        super().__init__("turn_ended", condition)


class MinionDied(PlayerEvent):
    def __init__(self, condition=None):
        super().__init__("minion_died", condition)


class MinionPlaced(PlayerEvent):
    def __init__(self, condition=None):
        super().__init__("minion_placed", condition)


class Overloaded(PlayerEvent):
    def __init__(self, condition=None):
        super().__init__("overloaded", condition)
