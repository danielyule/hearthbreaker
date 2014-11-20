import hearthbreaker
from hearthbreaker.constants import MINION_TYPE
import hearthbreaker.game_objects
from hearthbreaker.tags.base import Condition


class HasSecret(Condition):
    def evaluate(self, target, *args):
        return len(target.player.secrets) > 0

    def __to_json__(self):
        return {
            'name': 'has_secret'
        }


class IsSecret(Condition):
    def evaluate(self, target, obj, *args):
        return isinstance(obj, hearthbreaker.game_objects.SecretCard)

    def __to_json__(self):
        return {
            'name': 'is_secret'
        }


class IsSpell(Condition):
    def evaluate(self, target, obj, *args):
        return isinstance(obj, hearthbreaker.game_objects.Card) and obj.is_spell()

    def __to_json__(self):
        return {
            'name': 'is_spell'
        }


class CardMatches(Condition):
    def __init__(self, selector):
        super().__init__()
        self.selector = selector

    def evaluate(self, target, card, *args):
        return self.selector.match(target, card)

    def __to_json__(self):
        return {
            'name': 'card_matches',
            'selector': self.selector,
        }

    def __from_json__(self, selector):
        selector = hearthbreaker.tags.selector.Selector.from_json(**selector)
        self.__init__(selector)
        return self


class HasOverload(Condition):

    def evaluate(self, target, card, args):
        return card.overload > 0

    def __to_json__(self):
        return {
            'name': 'has_overload'
        }


class IsMinion(Condition):
    def evaluate(self, target, minion, *args):
        return isinstance(minion, hearthbreaker.game_objects.Minion)

    def __to_json__(self):
        return {
            "name": 'is_minion'
        }


class MinionIsTarget(Condition):
    def evaluate(self, target, minion, *args):
        return minion is target

    def __to_json__(self):
        return {
            'name': 'minion_is_target'
        }


class MinionIsNotTarget(Condition):
    def evaluate(self, target, minion, *args):
        return minion is not target

    def __to_json__(self):
        return {
            'name': 'minion_is_not_target'
        }


class CardIsNotTarget(Condition):
    def evaluate(self, target, card, *args):
        return target.card is not card

    def __to_json__(self):
        return {
            'name': 'card_is_not_target'
        }


class MinionIsType(Condition):
    def __init__(self, minion_type, include_self=False):
        super().__init__()
        self.minion_type = minion_type
        self.include_self = include_self

    def evaluate(self, target, minion=None, *args):
        if isinstance(target, hearthbreaker.game_objects.Minion):
            if self.include_self or target is not minion:
                return minion.card.minion_type == self.minion_type
            return False
        else:
            return isinstance(target, hearthbreaker.game_objects.MinionCard) and target.minion_type == self.minion_type

    def __to_json__(self):
        return {
            'name': 'minion_is_type',
            'include_self': self.include_self,
            'minion_type': MINION_TYPE.to_str(self.minion_type)
        }

    def __from_json__(self, minion_type, include_self=False):
        self.minion_type = MINION_TYPE.from_str(minion_type)
        self.include_self = include_self
        return self


class MinionHasDeathrattle(Condition):
    def __to_json__(self):
        return {
            'name': 'minion_has_deathrattle'
        }

    def __init__(self):
        super().__init__()

    def evaluate(self, target, minion, *args):
        return len(minion.deathrattle) > 0


class Adjacent(Condition):
    def __to_json__(self):
        return {
            'name': 'adjacent'
        }

    def __init__(self):
        super().__init__()

    def evaluate(self, target, minion, *args):
        return minion.player is target.player and \
            (minion.index == target.index - 1) or (minion.index == target.index + 1)


class AttackLessThanOrEqualTo(Condition):
    def __init__(self, attack_max, include_self=False):
        super().__init__()
        self.attack_max = attack_max
        self.include_self = include_self

    def evaluate(self, target, minion, *args):
        return (self.include_self or target is not minion) and minion.calculate_attack() <= self.attack_max

    def __to_json__(self):
        return {
            'name': 'attack_less_than_or_equal_to',
            'include_self': self.include_self,
            'attack_max': self.attack_max
        }
