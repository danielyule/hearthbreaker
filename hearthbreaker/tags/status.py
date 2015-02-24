from hearthbreaker.tags.base import Status, Amount


class ChangeAttack(Status, metaclass=Amount):
    def __init__(self):
        super().__init__()

    def act(self, actor, target):
        pass

    def unact(self, actor, target):
        pass

    def update(self, owner, prev_atk):
        return prev_atk + self.get_amount(owner, owner)

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

    def act(self, actor, target):
        pass

    def unact(self, actor, target):
        pass

    def update(self, owner, prev_health):
        return self.min_health

    def __to_json__(self):
        return {
            'name': 'minimun_health',
            'min_health': self.min_health
        }


class SetAttack(ChangeAttack, metaclass=Amount):
    def __init__(self):
        self._diff = 0

    def act(self, actor, target):
        pass

    def unact(self, actor, target):
        pass

    def update(self, owner, prev_atk):
        return self.get_amount(owner, owner)

    def __to_json__(self):
        return {
            'name': 'set_attack',
        }


class DoubleAttack(ChangeAttack):

    def act(self, actor, target):
        pass

    def unact(self, actor, target):
        pass

    def update(self, owner, prev_atk):
        return prev_atk * 2

    def __to_json__(self):
        return {
            'name': 'double_attack',
        }


class ManaChange(Status, metaclass=Amount):
    def __init__(self, minimum=0):
        super().__init__()
        self.minimum = minimum

    def act(self, actor, target):
        pass

    def unact(self, actor, target):
        pass

    def update(self, owner, prev_mana):
        minimum = min(prev_mana, self.minimum)
        return max(minimum, prev_mana + self.get_amount(owner, owner))

    def __to_json__(self):
        if self.minimum:
            return {
                "name": "mana_change",
                "minimum": self.minimum
            }
        return {
            'name': 'mana_change',
        }


class Charge(Status):
    def act(self, actor, target):
        pass

    def unact(self, actor, target):
        pass

    def update(self, owner, prev_charge):
        return True

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


class Frozen(Status):
    def act(self, actor, target):
        target.frozen += 1

    def unact(self, actor, target):
        target.frozen -= 1

    def __to_json__(self):
        return {
            "name": "frozen"
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
        pass

    def unact(self, actor, target):
        pass

    def update(self, owner, prev_charge):
        return prev_charge if prev_charge > 2 else 2

    def __to_json__(self):
        return {
            'name': 'windfury'
        }


class MegaWindfury(Windfury):
    def act(self, actor, target):
        pass

    def unact(self, actor, target):
        pass

    def update(self, owner, prev_charge):
        return prev_charge if prev_charge > 4 else 4

    def __to_json__(self):
        return {
            'name': 'mega_windfury'
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


class PowerTargetsMinions(Status):
    def act(self, actor, target):
        target.power_targets_minions += 1

    def unact(self, actor, target):
        target.power_targets_minions -= 1

    def __to_json__(self):
        return {
            'name': 'power_targets_minions'
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
        if not target.removed:
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


class IncreaseWeaponBonus(Status):
    def __init__(self, amount):
        self.amount = amount

    def act(self, actor, target):
        target.bonus_attack += self.amount

    def unact(self, actor, target):
        target.bonus_attack -= self.amount

    def __to_json__(self):
        return {
            'name': 'increase_weapon_bonus',
            'amount': self.amount
        }
