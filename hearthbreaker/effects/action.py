from hearthbreaker.effects.base import ReversibleAction, Selector, Action, Aura
from hearthbreaker.effects.selector import SelfSelector
import hearthbreaker.game_objects


class Freeze(ReversibleAction):
    def act(self, target):
        target.freeze()

    def unact(self, target):
        target.unfreeze()

    def __to_json__(self):
        return {
            "name": "freeze"
        }


class ChangeAttack(ReversibleAction):
    def __init__(self, amount):
        self.amount = amount

    def act(self, target):
        target.attack_delta += self.amount

    def unact(self, target):
        target.attack_delta -= self.amount

    def __to_json__(self):
        return {
            "name": "change_attack",
            "amount": self.amount
        }


class ChangeHealth(ReversibleAction):
    def __init__(self, amount):
        self.amount = amount

    def act(self, target):
        if self.amount > 0:
            target.health_delta += self.amount
            target.health += self.amount
        else:
            target.health_delta += self.amount
            if target.health > target.calculate_max_health():
                target.health = target.calculate_max_health()

    def unact(self, target):
        if self.amount > 0:
            target.health_delta -= self.amount
            if target.health > target.calculate_max_health():
                target.health = target.calculate_max_health()
        else:
            if target.calculate_max_health() == target.health:
                target.health -= self.amount
            target.health_delta -= self.amount

    def __to_json__(self):
        return {
            "name": "change_health",
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

        self.filter = Filter(self.amount, self.minimum, lambda c: self.card_selector.match(target, c))
        target.player.mana_filters.append(self.filter)

    def unact(self, target):
        target.player.mana_filters.remove(self.filter)

    def __to_json__(self):
        return {
            'name': 'mana_change',
            'amount': self.amount,
            'minimum': self.minimum,
            'card_selector': self.card_selector,
        }

    def __from_json__(self, amount, minimum, card_selector):
        self.amount = amount
        self.minimum = minimum
        self.card_selector = Selector.from_json(**card_selector)
        return self


class Summon(Action):
    def __init__(self, card):
        self.card = card

    def act(self, target):
        self.card().summon(target.player, target.game, len(target.player.minions))

    def __to_json__(self):
        return {
            'name': 'summon',
            'card': self.card.name
        }

    def __from_json__(self, card):
        self.card = hearthbreaker.game_objects.card_lookup(card)
        return self


class Kill(Action):

    def act(self, target):
        target.die(None)

    def __to_json__(self):
        return {
            'name': 'kill'
        }


class Draw(Action):
    def act(self, target):
        target.player.draw()

    def __to_json__(self):
        return {
            'name': 'draw'
        }


class Give(ReversibleAction):
    def __init__(self, aura):
        if isinstance(aura, Action):
            self.aura = Aura(aura, SelfSelector())
        else:
            self.aura = aura

    def act(self, target):
        target.add_aura(self.aura)

    def unact(self, target):
        target.remove_aura(self.aura)

    def __to_json__(self):
        return {
            'name': 'give',
            'aura': self.aura
        }

    def __from_json__(self, aura):
        self.aura = Aura.from_json(**aura)
        return self


class Charge(ReversibleAction):
    def act(self, target):
        target.charge += 1

    def unact(self, target):
        target.charge -= 1

    def __to_json__(self):
        return {
            'name': 'charge'
        }
