from hearthbreaker.effects.base import ReversibleAction, Selector


class Freeze(ReversibleAction):
    def act(self, target):
        target.freeze()

    def unact(self, target):
        target.unfreeze()

    def __to_json__(self):
        return {
            "type": "freeze"
        }


class ChangeAttack(ReversibleAction):
    def __init__(self, amount):
        self.amount = amount

    def act(self, target):
        target.change_attack(self.amount)

    def unact(self, target):
        target.change_attack(-self.amount)

    def __to_json__(self):
        return {
            "type": "change_attack",
            "amount": self.amount
        }


class ManaChange(ReversibleAction):
    def __init__(self, amount, minimum, card_selector):
        self.amount = amount
        self.minimum = minimum
        self.card_selector = card_selector
        self.filter = None

    def act(self, target):
        class Filter:
            def __init__(self, amount, minimum, filter):
                self.amount = amount
                self.min = minimum
                self.filter = filter

        self.filter = Filter(self.amount, self.minimum, self.card_selector.match)
        target.mana_filters.append(self.filter)

    def unact(self, target):
        target.mana_filters.remove(self.filter)

    def __to_json__(self):
        return {
            'type': 'mana_change',
            'amount': self.amount,
            'minimum': self.minimum,
            'card_selector': self.card_selector,
        }

    def __from_json__(self, amount, minimum, card_selector):
        self.amount = amount
        self.minimum = minimum
        self.card_selector = Selector.from_json(**card_selector)
        return self
