from hearthbreaker.tags.base import Status, Action, Aura, Condition, AuraUntil, CardQuery, \
    CARD_SOURCE, Effect
from hearthbreaker.tags.condition import IsSecret
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

        if isinstance(auras, Status):
            from hearthbreaker.tags.selector import SelfSelector
            self.auras = [Aura(auras, SelfSelector())]
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

    def __from_json__(self, auras=None, effects=None):
        if effects:  # To allow for give to work with effects as well, we check at load time
            effects = [Effect.from_json(**effect) for effect in effects]
            return GiveEffect(effects)

        self.auras = []
        for aura in auras:
            if "until" in aura:
                self.auras.append(AuraUntil.from_json(**aura))
            else:
                self.auras.append(Aura.from_json(**aura))
        return self


class GiveEffect(Action):
    def __init__(self, effects):

        if isinstance(effects, Effect):
            self.effects = [effects]
        else:
            self.effects = effects

    def act(self, actor, target):
        for effect in self.effects:
            target.add_effect(effect)

    def __to_json__(self):
        return {
            'name': 'give',
            'effects': self.effects
        }


class Take(Action):
    def __init__(self, aura):
        if isinstance(aura, Action):
            from hearthbreaker.tags.selector import SelfSelector
            self.aura = Aura(aura, SelfSelector())
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


class Summon(Action):
    def __init__(self, card, count=1):
        if isinstance(card, CardQuery):
            self.card = card
        else:
            self.card = CardQuery(card.ref_name)
        self.count = count

    def act(self, actor, target):
        if actor.is_minion() and actor.player is target:
            if actor.removed:
                index = actor.index
            else:
                index = actor.index + 1
        else:
            for summon in range(self.count):
                index = len(target.minions)
        card = self.card.get_card(target)
        if card is None:
            return

        # TODO add explicit patters for multi minion summoning (if there is ever more than two)
        for summon in range(self.count):
            card.summon(target, target.game, index)
            if actor.is_minion():
                index = actor.index  # Move the later minions to the left of their originator

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
        if isinstance(card, CardQuery):
            self.card = card
        else:
            self.card = CardQuery(card.ref_name)

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


class Discard(Action):
    def __init__(self, amount=1):
        self.amount = amount

    def act(self, actor, target):
        for index in range(0, self.amount):
            target.discard()

    def __to_json__(self):
        return {
            'name': 'discard',
            'amount': self.amount
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
    def __init__(self, card, count=1):
        if isinstance(card, CardQuery):
            self.card = card
        else:
            self.card = CardQuery(card.ref_name)
        self.count = count

    def act(self, actor, target):
        for i in range(self.count):
            if len(target.hand) < 10:
                target.hand.append(self.card.get_card(target))

    def __to_json__(self):
        return {
            'name': 'add_card',
            'card': self.card,
            'count': self.count
        }

    def __from_json__(self, card, count=1):
        self.card = CardQuery.from_json(**card)
        self.count = count
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


class Bounce(Action):
    def act(self, actor, target):
        target.bounce()

    def __to_json__(self):
        return {
            'name': 'bounce'
        }


class SwapWithHand(Action):
    def __init__(self, condition=None):
        self.condition = condition

    def act(self, actor, target):
        if self.condition:
            chosen_card = target.game.random_draw(target.hand, lambda c: self.condition.evaluate(c) and c.is_minion())
        else:
            chosen_card = target.game.random_draw(target.hand, lambda c: c.is_minion())
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
        self._query = CardQuery(conditions=[IsSecret()], source=source)

    def act(self, actor, target):
        secret = self._query.get_card(target)
        if secret:
            target.secrets.append(secret)
            secret.player = target
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
        self._query = CardQuery(conditions=[IsSecret()], source=self.source)
        return self


class Equip(Action):
    def __init__(self, weapon):
        if isinstance(weapon, CardQuery):
            self.weapon = weapon
        else:
            self.weapon = CardQuery(weapon.ref_name)

    def act(self, actor, target):
        card = self.weapon.get_card(target)
        weapon = card.create_weapon(target)
        weapon.equip(target)

    def __to_json__(self):
        return {
            'name': 'equip',
            'weapon': self.weapon
        }

    def __from_json__(self, weapon):
        self.weapon = CardQuery.from_json(**weapon)
        return self


class Steal(Action):
    def act(self, actor, target):
        new_minion = target.copy(actor.player)
        target._remove_auras_and_effects()
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


class Silence(Action):
    def act(self, actor, target):
        target.silence()

    def __to_json__(self):
        return {
            'name': 'silence'
        }


class DestroyManaCrystal(Action):
    def act(self, actor, target):
        target.max_mana -= 1
        if target.mana > 0:
            target.mana -= 1

    def __to_json__(self):
        return {
            'name': 'destroy_mana_crystal'
        }


class GiveManaCrystal(Action):
    def __init__(self, count=1, empty=False):
        self.count = count
        self.empty = empty

    def act(self, actor, target):
        target.max_mana = min(self.count + target.max_mana, 10)
        if not self.empty:
            target.mana += self.count

    def __to_json__(self):
        return {
            'name': 'give_mana_crystal',
            'count': self.count,
            'empty': self.empty,
        }
