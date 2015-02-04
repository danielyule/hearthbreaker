import copy
from hearthbreaker.tags.base import Status, Amount


class ChangeAttack(Status, metaclass=Amount):
    def __init__(self):
        super().__init__()

    def act(self, actor, target):
        self.amount = self.get_amount(actor, target)
        target.attack_delta += self.amount

    def unact(self, actor, target):
        target.attack_delta -= self.amount

    def __to_json__(self):
        return {
            "name": "change_attack",
        }


class ChangeHealth(Status, metaclass=Amount):
    def __init__(self):
        super().__init__()

    def act(self, actor, target):
        self.amount = self.get_amount(actor, target)
        if self.amount > 0:
            target.health_delta += self.amount
            target.health += self.amount
        else:
            target.health_delta += self.amount
            if target.health > target.calculate_max_health():
                target.health = target.calculate_max_health()

    def unact(self, actor, target):
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
        }


class MinimumHealth(Status):
    def __init__(self, min_health):
        self.min_health = min_health
        self.__keep_funcs = {}

    def act(self, actor, target):
        def keep_above_one():
            if target.health < self.min_health:
                target.health = self.min_health

        target.bind("health_changed", keep_above_one)
        self.__keep_funcs[target] = keep_above_one

    def unact(self, actor, target):
        target.unbind("health_changed", self.__keep_funcs[target])

    def __deep_copy__(self, memo):
        return MinimumHealth(self.min_health)

    def __copy__(self):
        return MinimumHealth(self.min_health)

    def __to_json__(self):
        return {
            'name': 'minimun_health',
            'min_health': self.min_health
        }


class SetAttack(Status):
    def __init__(self, attack):
        self.attack = attack
        self._diff = 0

    def act(self, actor, target):
        self._diff = self.attack - target.calculate_attack()
        target.attack_delta += self._diff

    def unact(self, actor, target):
        target.attack_delta -= self._diff

    def __to_json__(self):
        return {
            'name': 'set_attack',
            'attack': self.attack
        }


class ManaChange(Status):
    def __init__(self, amount, minimum, card_selector):
        self.amount = amount
        self.minimum = minimum
        self.card_selector = card_selector
        self.filters = {}

    def act(self, actor, target):
        class Filter:
            def __init__(self, amount, minimum, filter):
                self.amount = amount
                self.min = minimum
                self.filter = filter

        self.card_selector.track_cards(target)
        self.filters[target] = Filter(self.amount, self.minimum, lambda c: self.card_selector.match(target, c))
        target.mana_filters.append(self.filters[target])

    def unact(self, actor, target):
        target.mana_filters.remove(self.filters[target])
        self.card_selector.untrack_cards(target)

    def __deep_copy__(self, memo):
        return ManaChange(self.amount, self.minimum, copy.deepcopy(self.card_selector, memo))

    def __copy__(self):
        return ManaChange(self.amount, self.minimum, self.card_selector)

    def __to_json__(self):
        return {
            'name': 'mana_change',
            'amount': self.amount,
            'minimum': self.minimum,
            'card_selector': self.card_selector,
        }

    def __from_json__(self, amount, minimum, card_selector):
        from hearthbreaker.tags.base import Selector
        self.amount = amount
        self.minimum = minimum
        self.card_selector = Selector.from_json(**card_selector)
        self.filters = {}
        return self


class Charge(Status):
    def act(self, actor, target):
        target.charge += 1

    def unact(self, actor, target):
        target.charge -= 1

    def __to_json__(self):
        return {
            'name': 'charge'
        }


class Taunt(Status):
    def act(self, actor, target):
        target.taunt += 1

    def unact(self, actor, target):
        target.taunt -= 1

    def __to_json__(self):
        return {
            'name': 'taunt'
        }


class Stealth(Status):
    def act(self, actor, target):
        target.stealth += 1

    def unact(self, actor, target):
        target.stealth -= 1

    def __to_json__(self):
        return {
            'name': 'stealth'
        }


class DivineShield(Status):
    def act(self, actor, target):
        target.divine_shield += 1

    def unact(self, actor, target):
        target.divine_shield -= 1

    def __to_json__(self):
        return {
            'name': 'divine_shield'
        }


class Immune(Status):
    def act(self, actor, target):
        target.immune += 1

    def unact(self, actor, target):
        target.immune -= 1

    def __to_json__(self):
        return {
            'name': 'immune'
        }


class Windfury(Status):
    def act(self, actor, target):
        target.windfury += 1

    def unact(self, actor, target):
        target.windfury -= 1

    def __to_json__(self):
        return {
            'name': 'windfury'
        }


class CantAttack(Status):
    def __init__(self):
        super().__init__()
        self._old_attack = None

    def act(self, actor, target):
        self._old_attack = target.can_attack
        target.can_attack = lambda: False

    def unact(self, actor, target):
        target.can_attack = self._old_attack

    def __to_json__(self):
        return {
            "name": "cant_attack"
        }


class SpellDamage(Status):
    def __init__(self, damage):
        super().__init__()
        self.damage = damage

    def act(self, actor, target):
        target.player.spell_damage += self.damage

    def unact(self, actor, target):
        target.player.spell_damage -= self.damage

    def __to_json__(self):
        return {
            'name': 'spell_damage',
            'damage': self.damage
        }


class NoSpellTarget(Status):
    """
    Keeps a minion from being targeted by spells (can still be targeted by battlecries)
    """

    def act(self, actor, target):
        target.can_be_targeted_by_spells = False

    def unact(self, actor, target):
        target.can_be_targeted_by_spells = True

    def __to_json__(self):
        return {
            "name": "no_spell_target"
        }


class DoubleDeathrattle(Status):
    def act(self, actor, target):
        target.double_deathrattle += 1

    def unact(self, actor, target):
        target.double_deathrattle -= 1

    def __to_json__(self):
        return {
            'name': 'double_deathrattle'
        }


class HealAsDamage(Status):
    def act(self, actor, target):
        target.heal_does_damage += 1

    def unact(self, actor, target):
        target.heal_does_damage -= 1

    def __to_json__(self):
        return {
            'name': 'heal_as_damage'
        }


class AttackEqualsHealth(Status):
    def __init__(self):
        super().__init__()
        self._calculate_attack = {}

    def act(self, actor, target):
        def attack_equal_to_health():
            return target.health

        self._calculate_attack[target] = target.calculate_attack
        target.calculate_attack = attack_equal_to_health

    def unact(self, actor, target):
        target.calculate_attack = self._calculate_attack[target]

    def __deep_copy__(self, memo):
        return AttackEqualsHealth()

    def __copy__(self):
        return AttackEqualsHealth()

    def __to_json__(self):
        return {
            'name': 'attack_equals_health'
        }


class Stolen(Status):
    def act(self, actor, target):
        pass

    def unact(self, actor, target):
        minion = target.copy(target.player.opponent)
        target.remove_from_board()
        minion.add_to_board(len(target.player.opponent.minions))

    def __to_json__(self):
        return {
            'name': 'stolen'
        }


class MultiplySpellDamage(Status):
    def __init__(self, amount=2):
        self.amount = amount

    def act(self, actor, target):
        target.spell_multiplier *= self.amount

    def unact(self, actor, target):
        target.spell_multiplier //= self.amount

    def __to_json__(self):
        return {
            'name': 'multiply_spell_damage',
            'amount': self.amount
        }


class MultiplyHealAmount(Status):
    def __init__(self, amount=2):
        self.amount = amount

    def act(self, actor, target):
        target.heal_multiplier *= self.amount

    def unact(self, actor, target):
        target.heal_multiplier //= self.amount

    def __to_json__(self):
        return {
            'name': 'multiply_heal_amount',
            'amount': self.amount
        }


class IncreaseWeaponAttack(Status):
    def __init__(self, amount):
        self.amount = amount

    def act(self, actor, target):
        target.bonus_attack += self.amount

    def unact(self, actor, target):
        target.bonus_attack -= self.amount

    def __to_json__(self):
        return {
            'name': 'increase_weapon_attack',
            'amount': self.amount
        }
