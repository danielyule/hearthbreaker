from hearthbreaker.effects.base import ReversibleAction, Action, MinionAction, Aura
import hearthbreaker.game_objects
import hearthbreaker.effects.selector


class Freeze(ReversibleAction):
    def act(self, target):
        target.freeze()

    def unact(self, target):
        target.unfreeze()

    def __to_json__(self):
        return {
            "name": "freeze"
        }


class Give(ReversibleAction):
    def __init__(self, aura):
        if isinstance(aura, Action):
            self.aura = Aura(aura, hearthbreaker.effects.selector.SelfSelector())
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


class Take(Action):
    def __init__(self, aura):
        if isinstance(aura, Action):
            self.aura = Aura(aura, hearthbreaker.effects.selector.SelfSelector())
        else:
            self.aura = aura

    def act(self, target):
        aura_json = str(self.aura)
        for aura in target.auras:
            if str(aura) == aura_json:
                target.remove_aura(aura)
                break

    def __to_json__(self):
        return {
            'name': 'take',
            'aura': self.aura
        }

    def __from_json__(self, aura):
        self.aura = Aura.from_json(**aura)
        return self


class ChangeAttack(MinionAction):
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


class ChangeHealth(MinionAction):
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
        self.filters = {}

    def act(self, target):
        class Filter:
            def __init__(self, amount, minimum, filter):
                self.amount = amount
                self.min = minimum
                self.filter = filter

        self.filters[target.player] = Filter(self.amount, self.minimum, lambda c: self.card_selector.match(target, c))
        target.player.mana_filters.append(self.filters[target.player])

    def unact(self, target):
        target.player.mana_filters.remove(self.filters[target.player])

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
        self.card_selector = hearthbreaker.effects.selector.Selector.from_json(**card_selector)
        self.filters = {}
        return self


class Summon(Action):
    def __init__(self, card):
        self.card = card

    def act(self, target):
        self.card.summon(target.player, target.player.game, len(target.player.minions))

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


class Heal(Action):
    def __init__(self, amount):
        super().__init__()
        self.amount = amount

    def act(self, target):
        target.heal(self.amount, None)

    def __to_json__(self):
        return {
            'name': 'heal',
            'amount': self.amount
        }


class Draw(Action):
    def act(self, target):
        target.player.draw()

    def __to_json__(self):
        return {
            'name': 'draw'
        }


class Charge(MinionAction):
    def act(self, target):
        target.charge += 1

    def unact(self, target):
        target.charge -= 1

    def __to_json__(self):
        return {
            'name': 'charge'
        }


class Taunt(MinionAction):
    def act(self, target):
        target.taunt += 1

    def unact(self, target):
        target.taunt -= 1

    def __to_json__(self):
        return {
            'name': 'taunt'
        }


class Stealth(MinionAction):
    def act(self, target):
        target.stealth += 1

    def unact(self, target):
        target.stealth -= 1

    def __to_json__(self):
        return {
            'name': 'stealth'
        }


class CantAttack(MinionAction):
    def __init__(self):
        super().__init__()
        self._old_attack = None

    def act(self, target):
        self._old_attack = target.can_attack
        target.can_attack = lambda: False

    def unact(self, target):
        target.can_attack = self._old_attack

    def __to_json__(self):
        return {
            "name": "cant_attack"
        }


class IncreaseArmor(Action):
    def __init__(self, amount=1):
        super().__init__()
        self.amount = amount

    def act(self, target):
        target.armor += self.amount

    def __to_json__(self):
        return {
            'name': 'increase_armor'
        }


class NoSpellTarget(ReversibleAction):
    """
    Keeps a minion from being targeted by spells (can still be targeted by battlecries)
    """

    def act(self, target):
        target.can_be_targeted_by_spells = False

    def unact(self, target):
        target.can_be_targeted_by_spells = True

    def __to_json__(self):
        return {
            "name": "no_spell_target"
        }


class Chance(Action):
    def __init__(self, action, one_in=2):
        self.action = action
        self.one_in = one_in

    def act(self, target):
        if 1 == target.player.game.random_amount(1, self.one_in):
            self.action.act(target)

    def __to_json__(self):
        return {
            'name': 'chance',
            'action': self.action,
            'one_in': self.one_in
        }

    def __from_json__(self, action, one_in):
        self.action = Action.from_json(**action)
        self.one_in = one_in


class AddCard(Action):
    def __init__(self, card):
        self.card = type(card)

    def act(self, target):
        if len(target.player.hand) < 10:
            target.player.hand.append(self.card())

    def __to_json__(self):
        return {
            'name': 'add_card',
            'card': self.card().name
        }

    def __from_json__(self, card):
        self.card = hearthbreaker.game_objects.card_lookup(card)
