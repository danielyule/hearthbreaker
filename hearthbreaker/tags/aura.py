import hearthbreaker.tags.base
from hearthbreaker.tags.condition import CardMatches
from hearthbreaker.tags.event import Either, TurnEnded, CardPlayed
from hearthbreaker.tags.action import ManaChange
from hearthbreaker.tags.selector import PlayerSelector


class ManaAura(hearthbreaker.tags.base.AuraUntil):

    def __init__(self, amount, minimum, card_selector, until_played, until_turn_ended=True):
        if until_turn_ended:
            if until_played:
                until = Either(CardPlayed(CardMatches(card_selector)), TurnEnded())
            else:
                until = TurnEnded()
        else:
            if until_played:
                until = CardPlayed(CardMatches(card_selector))
            else:
                until = None
        super().__init__(ManaChange(amount, minimum, card_selector), PlayerSelector(), until)
