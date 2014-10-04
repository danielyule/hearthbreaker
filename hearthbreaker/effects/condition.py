from hearthbreaker.effects.base import Condition, Selector


class HasSecret(Condition):
    def evaluate(self, target, *args):
        return len(target.player.secrets) > 0

    def __to_json__(self):
        return {
            'type': 'has_secret'
        }


class CardMatches(Condition):
    def __init__(self, selector):
        super().__init__()
        self.selector = selector

    def evaluate(self, target, card, index):
        return self.selector.match(card)

    def __to_json__(self):
        return {
            'type': 'card_matches',
            'selector': self.selector,
        }

    def __from_json__(self, selector):
        selector = Selector.from_json(**selector)
        self.__init__(selector)
        return self
