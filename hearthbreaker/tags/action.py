from hearthbreaker.tags.base import ReversibleAction, Action, MinionAction, Aura, Condition, AuraUntil, CardQuery, \
    CARD_SOURCE
import hearthbreaker.game_objects
from hearthbreaker.tags.condition import IsSecret
import hearthbreaker.tags.selector
import hearthbreaker.proxies


class Freeze(Action):
    def act(self, actor, target):
        target.freeze()

    def __to_json__(self):
        return {
            "name": "freeze"
        }


class Give(Action):
    def __init__(self, auras):
        if isinstance(auras, Action):
            self.auras = [Aura(auras, hearthbreaker.tags.selector.SelfSelector())]
        elif isinstance(auras, list):
            self.auras = auras
        else:
            self.auras = [auras]

    def act(self, actor, target):
        for aura in self.auras:
            target.add_aura(aura)

    def unact(self, actor, target):
        for aura in self.auras:
            aura.target = target
            target.remove_aura(aura)

    def __to_json__(self):
        return {
            'name': 'give',
            'auras': self.auras
        }

    def __from_json__(self, auras):
        self.auras = []
        for aura in auras:
            if "until" in aura:
                self.auras.append(AuraUntil.from_json(**aura))
            else:
                self.auras.append(Aura.from_json(**aura))
        return self


class Take(Action):
    def __init__(self, aura):
        if isinstance(aura, Action):
            self.aura = Aura(aura, hearthbreaker.tags.selector.SelfSelector())
        else:
            self.aura = aura

    def act(self, actor, target):
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

    def act(self, actor, target):
        target.attack_delta += self.amount

    def unact(self, actor, target):
        target.attack_delta -= self.amount

    def __to_json__(self):
        return {
            "name": "change_attack",
            "amount": self.amount
        }


# class IncreaseTempAttack(MinionAction):
#     def __init__(self, amount):
#         self.amount = amount
#
#     def act(self, actor, target):
#         target.temp_attack += self.amount
#
#     def unact(self, actor, target):
#         target.temp_attack -= self.amount
#
#     def __to_json__(self):
#         return {
#             "name": "increase_temp_attack",
#             "amount": self.amount
#         }


class ChangeHealth(MinionAction):
    def __init__(self, amount):
        self.amount = amount

    def act(self, actor, target):
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
            "amount": self.amount
        }


class MinimumHealth(MinionAction):
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

    def __to_json__(self):
        return {
            'name': 'minimun_health',
            'min_health': self.min_health
        }


class ManaChange(ReversibleAction):
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
        self.card_selector = hearthbreaker.tags.selector.Selector.from_json(**card_selector)
        self.filters = {}
        return self


class Summon(Action):
    def __init__(self, card, count=1):
        if isinstance(card, hearthbreaker.game_objects.Card):
            self.card = CardQuery(card.name)
        else:
            self.card = card
        self.count = count

    def act(self, actor, target):
        if isinstance(actor, hearthbreaker.game_objects.Minion):
            if actor.removed:
                index = actor.index
            else:
                index = actor.index + 1
        else:
            for summon in range(self.count):
                index = len(target.minions)
        card = self.card.get_card(target)
        for summon in range(self.count):
            card.summon(target, target.game, index)

    def __to_json__(self):
        if self.count > 1:
            return {
                'name': 'summon',
                'card': self.card,
                'count': self.count
            }
        return {
            'name': 'summon',
            'card': self.card
        }

    def __from_json__(self, card, count=1):
        self.card = CardQuery.from_json(**card)
        self.count = count
        return self


class Transform(Action):
    def __init__(self, card):
        if isinstance(card, hearthbreaker.game_objects.Card):
            self.card = CardQuery(card.name)
        else:
            self.card = card

    def act(self, actor, target):
        card = self.card.get_card(target)
        minion = card.create_minion(target.player)
        minion.card = card
        target.replace(minion)

    def __to_json__(self):
        return {
            'name': 'transform',
            'card': self.card
        }

    def __from_json__(self, card):
        self.card = CardQuery.from_json(**card)
        return self


class Kill(Action):
    def act(self, actor, target):
        target.die(None)

    def __to_json__(self):
        return {
            'name': 'kill'
        }


class Heal(Action):
    def __init__(self, amount):
        super().__init__()
        self.amount = amount

    def act(self, actor, target):
        target.heal(actor.player.effective_heal_power(self.amount), actor)

    def __to_json__(self):
        return {
            'name': 'heal',
            'amount': self.amount
        }


class Damage(Action):
    def __init__(self, amount):
        super().__init__()
        self.amount = amount

    def act(self, actor, target):
        target.damage(self.amount, actor)

    def __to_json__(self):
        return {
            'name': 'damage',
            'amount': self.amount
        }


class Draw(Action):
    def __init__(self, amount=1):
        self.amount = amount

    def act(self, actor, target):
        for draw in range(0, self.amount):
            target.draw()

    def __to_json__(self):
        return {
            'name': 'draw',
            'amount': self.amount
        }


class Charge(MinionAction):
    def act(self, actor, target):
        target.charge += 1

    def unact(self, actor, target):
        target.charge -= 1

    def __to_json__(self):
        return {
            'name': 'charge'
        }


class Taunt(MinionAction):
    def act(self, actor, target):
        target.taunt += 1

    def unact(self, actor, target):
        target.taunt -= 1

    def __to_json__(self):
        return {
            'name': 'taunt'
        }


class Stealth(MinionAction):
    def act(self, actor, target):
        target.stealth += 1

    def unact(self, actor, target):
        target.stealth -= 1

    def __to_json__(self):
        return {
            'name': 'stealth'
        }


class Immune(MinionAction):
    def act(self, actor, target):
        target.immune += 1

    def unact(self, actor, target):
        target.immune -= 1

    def __to_json__(self):
        return {
            'name': 'immune'
        }


class Windfury(MinionAction):
    def act(self, actor, target):
        target.windfury += 1

    def unact(self, actor, target):
        target.windfury -= 1

    def __to_json__(self):
        return {
            'name': 'windfury'
        }


class CantAttack(MinionAction):
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


class IncreaseArmor(Action):
    def __init__(self, amount=1):
        super().__init__()
        self.amount = amount

    def act(self, actor, target):
        target.armor += self.amount

    def __to_json__(self):
        return {
            'name': 'increase_armor'
        }


class NoSpellTarget(MinionAction):
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


class Chance(Action):
    def __init__(self, action, one_in=2):
        self.action = action
        self.one_in = one_in

    def act(self, actor, target):
        if 1 == target.game.random_amount(1, self.one_in):
            self.action.act(actor, target)

    def __to_json__(self):
        return {
            'name': 'chance',
            'action': self.action,
            'one_in': self.one_in
        }

    def __from_json__(self, action, one_in):
        self.action = Action.from_json(**action)
        self.one_in = one_in
        return self


class AddCard(Action):
    def __init__(self, card):
        if isinstance(card, hearthbreaker.game_objects.Card):
            self.card = CardQuery(card.name)
        else:
            self.card = card

    def act(self, actor, target):
        if len(target.hand) < 10:
            target.hand.append(self.card.get_card(target))

    def __to_json__(self):
        return {
            'name': 'add_card',
            'card': self.card
        }

    def __from_json__(self, card, count=1):
        self.card = CardQuery.from_json(**card)
        return self


class ResurrectFriendly(Action):
    def __to_json__(self):
        return {
            'name': 'resurrect_friendly'
        }

    def act(self, actor, target):
        # Will be called once per Kel'Thuzad on the board
        # http://www.hearthhead.com/card=1794/kelthuzad#comments
        for minion in sorted(target.dead_this_turn, key=lambda m: m.born):
            minion.card.summon(target, target.game, len(target.minions))


class DoubleDeathrattle(ReversibleAction):
    def act(self, actor, target):
        target.double_deathrattle += 1

    def unact(self, actor, target):
        target.double_deathrattle -= 1

    def __to_json__(self):
        return {
            'name': 'double_deathrattle'
        }


class HealAsDamage(ReversibleAction):
    def act(self, actor, target):
        target.heal_does_damage += 1

    def unact(self, actor, target):
        target.heal_does_damage -= 1

    def __to_json__(self):
        return {
            'name': 'heal_as_damage'
        }


class Bounce(Action):
    def act(self, actor, target):
        target.bounce()

    def __to_json__(self):
        return {
            'name': 'bounce'
        }


# class SummonFromDeck(Action):
#     def act(self, actor, target):
#         chosen_card = target.game.random_draw(target.deck.cards,
#                                               lambda c: not c.drawn and
#                                               isinstance(c, hearthbreaker.game_objects.MinionCard))
#         if chosen_card:
#             chosen_card.drawn = True
#             target.deck.left -= 1
#             chosen_card.summon(target, target.game, len(target.minions))
#
#     def __to_json__(self):
#         return {
#             'name': 'summon_from_deck'
#         }
#
#
# class SummonFromHand(Action):
#     def __init__(self, condition=None):
#         self.condition = condition
#
#     def act(self, actor, target):
#         if self.condition:
#             chosen_card = target.game.random_draw(target.hand,
#                                                   lambda c: self.condition.evaluate(c) and
#                                                   isinstance(c, hearthbreaker.game_objects.MinionCard))
#         else:
#             chosen_card = target.game.random_draw(target.hand,
#                                                   lambda c: isinstance(c, hearthbreaker.game_objects.MinionCard))
#         if chosen_card:
#             chosen_card.summon(target, target.game, len(target.minions))
#             target.hand.remove(chosen_card)
#
#     def __to_json__(self):
#         if self.condition:
#             return {
#                 'name': 'summon_from_hand',
#                 'condition': self.condition
#             }
#         return {
#             'name': 'summon_from_hand'
#         }
#
#     def __from_json__(self, condition=None):
#         if condition:
#             self.condition = Condition.from_json(**condition)
#         else:
#             self.condition = None
#         return self


class SwapWithHand(Action):
    def __init__(self, condition=None):
        self.condition = condition

    def act(self, actor, target):
        if self.condition:
            chosen_card = target.game.random_draw(target.hand,
                                                  lambda c: self.condition.evaluate(c) and
                                                  isinstance(c, hearthbreaker.game_objects.MinionCard))
        else:
            chosen_card = target.game.random_draw(target.hand,
                                                  lambda c: isinstance(c, hearthbreaker.game_objects.MinionCard))
        if chosen_card:
            chosen_card.summon(target, target.game, len(target.minions))
            target.hand.remove(chosen_card)
            actor.bounce()

    def __to_json__(self):
        if self.condition:
            return {
                'name': 'swap_with_hand',
                'condition': self.condition
            }
        return {
            'name': 'swap_with_hand'
        }

    def __from_json__(self, condition=None):
        if condition:
            self.condition = Condition.from_json(**condition)
        else:
            self.condition = None
        return self


class ApplySecret(Action):

    def __init__(self, source):
        self.source = source
        self._query = CardQuery(condition=IsSecret(), source=source)

    def act(self, actor, target):
        secret = self._query.get_card(target)
        if secret:
            target.secrets.append(secret)
            if target is target.game.other_player:
                secret.player = target
                secret.activate(target)

    def __to_json__(self):
        return {
            'name': 'apply_secret',
            'source': CARD_SOURCE.to_str(self.source)
        }

    def __from_json__(self, source):
        self.source = CARD_SOURCE.from_str(source)
        self._query = CardQuery(condition=IsSecret(), source=source)


class Equip(Action):
    def __init__(self, weapon):
        self.weapon = weapon

    def act(self, actor, target):
        weapon = self.weapon.create_weapon(target)
        weapon.equip(target)

    def __to_json__(self):
        return {
            'name': 'equip',
            'weapon': self.weapon.name
        }

    def __from_json__(self, weapon):
        self.weapon = hearthbreaker.game_objects.card_lookup(weapon)
        return self


class Steal(Action):
    def act(self, actor, target):
        new_minion = target.copy(actor.player)
        target.remove_from_board()
        new_minion.add_to_board(len(actor.player.minions))

    def __to_json__(self):
        return {
            'name': 'steal'
        }


class Duplicate(Action):
    def __init__(self, minion):
        super().__init__()
        self.minion = hearthbreaker.proxies.TrackingProxyCharacter(minion, minion.game)
        self.__min_ref = None

    def track_changes(self, player):
        if not self.minion:
            self.minion = hearthbreaker.proxies.TrackingProxyCharacter(self.__min_ref, player.game)

    def act(self, actor, target):
        minion = self.minion.resolve(target.game)
        if minion:
            dup = minion.copy(minion.player)
            dup.add_to_board(minion.index + 1)

    def __to_json__(self):
        return {
            "name": "duplicate",
            "minion": str(self.minion)
        }

    def __from_json__(self, minion):
        self.__min_ref = minion
        self.minion = None
        return self


class AttackEqualsHealth(ReversibleAction):
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

    def __to_json__(self):
        return {
            'name': 'attack_equals_health'
        }


class Stolen(ReversibleAction):
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


class MultiplySpellDamage(ReversibleAction):
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


class MultiplyHealAmount(ReversibleAction):
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


class IncreaseWeaponAttack(ReversibleAction):
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
