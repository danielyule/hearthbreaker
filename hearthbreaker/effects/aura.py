import hearthbreaker.effects.base
from hearthbreaker.effects.event import Either, MatchingCardPlayed, TurnEnded
from hearthbreaker.effects.action import ManaChange


class ManaAura(hearthbreaker.effects.base.PlayerAura):
    def __init__(self, amount, minimum, card_selector, until_played):
        if until_played:
            until = Either(MatchingCardPlayed(card_selector), TurnEnded())
        else:
            until = TurnEnded()
        super().__init__(ManaChange(amount, minimum, card_selector), until)
