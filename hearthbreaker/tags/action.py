import copy
from hearthbreaker.tags.base import Status, Action, Aura, Condition, AuraUntil, CardQuery, \
    CARD_SOURCE, Effect, Buff, BuffUntil, Amount, Picker, Selector
from hearthbreaker.tags.condition import IsSecret
from hearthbreaker.tags.selector import AllPicker, ConstantSelector


class Give(Action):
    def __init__(self, buffs, picker=AllPicker()):

        if isinstance(buffs, Status):
            self.buffs = [Buff(buffs)]
        elif isinstance(buffs, list):
            self.buffs = buffs
            if isinstance(buffs[0], Aura):
                raise TypeError("Aura passed where buff was expected")
        elif isinstance(buffs, Aura):
            raise TypeError("Aura passed where buff was expected")
        else:
            self.buffs = [buffs]
        self.picker = picker

    def act(self, actor, target, other=None):
        buffs = self.picker.pick(actor, self.buffs)
        for buff in buffs:
            target.add_buff(buff.to_instance(target))

    def __to_json__(self):
        if isinstance(self.picker, AllPicker):
            return {
                'name': 'give',
                'buffs': self.buffs
            }
        return {
            'name': 'give',
            'buffs': self.buffs,
            'picker': self.picker,
        }

    def __from_json__(self, buffs=None, effects=None, auras=None, picker=None):
        if effects:  # To allow for give to work with effects as well, we check at load time
            return GiveEffect.__new__(GiveEffect).__from_json__(effects)

        if auras:  # To allow for give to work with auras as well, we check at load time
            return GiveAura.__new__(GiveAura).__from_json__(auras)

        self.buffs = []
        for buff in buffs:
            if "until" in buff:
                self.buffs.append(BuffUntil.from_json(**buff))
            else:
                self.buffs.append(Buff.from_json(**buff))

        if not picker:
            self.picker = AllPicker()
        else:
            self.picker = Picker.from_json(**picker)
        return self


class GiveAura(Action):
    def __init__(self, auras):
        if isinstance(auras, list):
            self.auras = auras
        else:
            self.auras = [auras]

    def act(self, actor, target, other=None):
        for aura in self.auras:
            target.add_aura(aura)

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


class GiveEffect(Action):
    def __init__(self, effects):

        if isinstance(effects, Effect):
            self.effects = [effects]
        else:
            self.effects = effects

    def act(self, actor, target, other=None):
        for effect in self.effects:
            for tag in effect.tags:
                for action in tag.actions:
                    if hasattr(action, "selector"):
                        action.selector = ConstantSelector([obj.born for obj in
                                                            action.selector.choose_targets(actor, target)])
            target.add_effect(effect)

    def __to_json__(self):
        return {
            'name': 'give',
            'effects': self.effects
        }

    def __from_json__(self, effects):
        self.effects = [Effect.from_json(**effect) for effect in effects]
        return self


class Summon(Action):
    def __init__(self, card, count=1):
        if isinstance(card, CardQuery):
            self.card = card
        else:
            self.card = CardQuery(card.ref_name)
        self.count = count

    def act(self, actor, target, other=None):
        card = self.card.get_card(target, target, actor)
        if card is None:
            return

        if actor.is_minion() and actor.player is target:
            # When a minion is summoned around another minion, they alternate between left and right,
            # starting on the right
            if actor.removed:
                c = 0
            else:
                c = 1
            for summon in range(self.count):
                index = actor.index + (c % 2)
                card.summon(target, target.game, index)
                if not actor.removed:
                    c += 1
        else:
            for summon in range(self.count):
                card.summon(target, target.game, len(target.minions))

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

    def act(self, actor, target, other=None):
        card = self.card.get_card(target, target.player, actor)
        if target.is_card():
            target.replace(card)
        elif target.is_minion():
            minion = card.create_minion(target.player)
            minion.card = card
            target.replace(minion)
        elif target.is_hero():
            hero = card.create_hero(target.player)
            hero.card = card
            target.player.trigger("minion_played", actor)
            hero.buffs = copy.deepcopy(actor.buffs)
            hero.health = actor.health
            target.replace(hero)
            if hero.health <= 0:
                hero.die(None)

    def __to_json__(self):
        return {
            'name': 'transform',
            'card': self.card
        }

    def __from_json__(self, card):
        self.card = CardQuery.from_json(**card)
        return self


class Kill(Action):
    def act(self, actor, target, other=None):
        target.die(None)

    def __to_json__(self):
        return {
            'name': 'kill'
        }


class Heal(Action, metaclass=Amount):
    def __init__(self):
        super().__init__()

    def act(self, actor, target, other=None):
        target.heal(actor.player.effective_heal_power(self.get_amount(actor, target, other)), actor)

    def __to_json__(self):
        return {
            'name': 'heal',
        }


class SetHealth(Action, metaclass=Amount):
    def __init__(self):
        super().__init__()

    def act(self, actor, target, other=None):
        target.health = self.get_amount(actor, target, other)

    def __to_json__(self):
        return {
            'name': 'set_health'
        }


class Damage(Action, metaclass=Amount):
    def __init__(self):
        super().__init__()

    def act(self, actor, target, other=None):
        target.damage(self.get_amount(actor, target, other), actor)

    def __to_json__(self):
        return {
            'name': 'damage',
        }


class Draw(Action, metaclass=Amount):
    def __init__(self):
        super().__init__()

    def act(self, actor, target, other=None):
        for draw in range(0, self.get_amount(actor, target, other)):
            target.draw()

    def __to_json__(self):
        return {
            'name': 'draw',
        }


class Discard(Action, metaclass=Amount):
    def __init__(self, query=CardQuery(source=CARD_SOURCE.MY_HAND)):
        super().__init__()
        self.query = query

    def act(self, actor, target, other=None):
        for index in range(0, self.get_amount(actor, target, other)):
            card = self.query.get_card(target, actor.player, actor)
            if card:
                actor.player.trigger("discard", card)

    def __to_json__(self):
        return {
            'name': 'discard',
            'query': self.query,
        }

    def __from_json__(self, query):
        self.query = CardQuery.from_json(**query)
        return self


class IncreaseArmor(Action, metaclass=Amount):
    def __init__(self):
        super().__init__()

    def act(self, actor, target, other=None):
        target.armor += self.get_amount(actor, target, other)

    def __to_json__(self):
        return {
            'name': 'increase_armor'
        }


class ChangeTarget(Action):
    def __init__(self, selector):
        self.selector = selector

    def act(self, actor, target, other=None):
        possible_targets = [t for t in self.selector.choose_targets(target, target.current_target)]
        if len(possible_targets) > 0:
            target.current_target = possible_targets[0]

    def __to_json__(self):
        return {
            'name': 'change_target',
            'selector': self.selector,
        }

    def __from_json__(self, selector):
        from hearthbreaker.tags.base import Selector
        self.selector = Selector.from_json(**selector)
        return self


class AddCard(Action):
    def __init__(self, card, count=1, add_to_deck=False):
        if isinstance(card, CardQuery):
            self.card = card
        else:
            self.card = CardQuery(card.ref_name)
        self.add_to_deck = add_to_deck
        self.count = count

    def act(self, actor, target, other=None):
        if self.add_to_deck:
            for i in range(self.count):
                target.deck.put_back(self.card.get_card(target, target, actor))
        else:
            for i in range(self.count):
                if len(target.hand) < 10:
                    card = self.card.get_card(target, target, actor)
                    if card:
                        target.hand.append(card)

    def __to_json__(self):
        if self.add_to_deck:
            return {
                'name': 'add_card',
                'card': self.card,
                'count': self.count,
                'add_to_deck': self.add_to_deck,
            }
        return {
            'name': 'add_card',
            'card': self.card,
            'count': self.count
        }

    def __from_json__(self, card, count=1, add_to_deck=False):
        self.card = CardQuery.from_json(**card)
        self.count = count
        self.add_to_deck = add_to_deck
        return self


class ResurrectFriendly(Action):
    def __to_json__(self):
        return {
            'name': 'resurrect_friendly'
        }

    def act(self, actor, target, other=None):
        # Will be called once per Kel'Thuzad on the board
        # http://www.hearthhead.com/card=1794/kelthuzad#comments
        for minion in sorted(target.dead_this_turn, key=lambda m: m.born):
            minion.card.summon(target, target.game, len(target.minions))


class Bounce(Action):
    def __init__(self, bounce_to_deck=False):
        self.bounce_to_deck = bounce_to_deck

    def act(self, actor, target, other=None):
        target.bounce(self.bounce_to_deck)

    def __to_json__(self):
        if self.bounce_to_deck:
            return {
                'name': 'bounce',
                'bounce_to_deck': True,
            }
        return {
            'name': 'bounce'
        }


class SwapWithHand(Action):
    def __init__(self, condition=None):
        self.condition = condition

    def act(self, actor, target, other=None):
        if actor.is_valid():
            if self.condition:
                chosen_card = target.game.random_draw(target.hand,
                                                      lambda c: self.condition.evaluate(c) and c.is_minion())
            else:
                chosen_card = target.game.random_draw(target.hand, lambda c: c.is_minion())
            if chosen_card:
                chosen_card.summon(target, target.game, len(target.minions))
                chosen_card.unattach()
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

    def act(self, actor, target, other=None):
        secret = self._query.get_card(target, target, actor)
        if secret:
            target.secrets.append(secret)
            secret.player = target
            if target is target.game.other_player:
                secret.player = target
                # To allow for Mad Scientist not to be redeemed or duplicated as a result of its death,
                # but still allow other minions that die during the same cycle to be duplicated.
                # Based on testing for patch 2.1.0.7785
                if actor.dead:
                    target.bind_once("after_death", secret.activate)
                else:
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

    def act(self, actor, target, other=None):
        card = self.weapon.get_card(target, target, actor)
        weapon = card.create_weapon(target)
        weapon.card = card
        weapon.equip(target)

    def __to_json__(self):
        return {
            'name': 'equip',
            'weapon': self.weapon
        }

    def __from_json__(self, weapon):
        self.weapon = CardQuery.from_json(**weapon)
        return self


class Destroy(Action):
    def act(self, actor, target, other=None):
        target.destroy()

    def __to_json__(self):
        return {
            'name': 'destroy'
        }


class Steal(Action):
    def act(self, actor, target, other=None):
        new_minion = target.copy(actor.player)
        target.unattach()
        target.remove_from_board()
        new_minion.add_to_board(len(actor.player.minions))

    def __to_json__(self):
        return {
            'name': 'steal'
        }


class Duplicate(Action):
    def __init__(self, selector):
        super().__init__()
        self.selector = selector

    def act(self, actor, target, other=None):
        for minion in self.selector.choose_targets(actor, target):
            if len(minion.player.minions) < 7:
                dup = minion.copy(minion.player)
                dup.add_to_board(minion.index + 1)

    def __to_json__(self):
        return {
            "name": "duplicate",
            "selector": self.selector,
        }

    def __from_json__(self, selector):
        self.selector = Selector.from_json(**selector)
        return self


class Replace(Action):
    def act(self, actor, target, other=None):
        new_minion = target.copy(actor.player)
        actor.replace(new_minion)

    def __to_json__(self):
        return {
            'name': 'replace'
        }


class Silence(Action):
    def act(self, actor, target, other=None):
        target.silence()

    def __to_json__(self):
        return {
            'name': 'silence'
        }


class DestroyManaCrystal(Action):
    def act(self, actor, target, other=None):
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

    def act(self, actor, target, other=None):
        target.max_mana = min(self.count + target.max_mana, 10)
        if not self.empty:
            target.mana += self.count

    def __to_json__(self):
        return {
            'name': 'give_mana_crystal',
            'count': self.count,
            'empty': self.empty,
        }


class IncreaseDurability(Action):
    def act(self, actor, target, other=None):
        if target.weapon:
            target.weapon.durability += 1

    def __to_json__(self):
        return {
            'name': 'increase_durability',
        }


class DecreaseDurability(Action):
    def act(self, actor, target, other=None):
        if target.weapon:
            target.weapon.durability -= 1
            if target.weapon.durability <= 0:
                target.weapon.destroy()

    def __to_json__(self):
        return {
            'name': 'decrease_durability',
        }


class IncreaseWeaponAttack(Action, metaclass=Amount):
    def __init__(self):
        pass

    def act(self, actor, target, other=None):
        if target.weapon:
            target.weapon.base_attack += self.get_amount(actor, target, other)

    def __to_json__(self):
        return {
            'name': 'increase_weapon_attack'
        }


class RemoveDivineShields(Action):
    def act(self, actor, target, other=None):
        from hearthbreaker.tags.status import DivineShield
        if target.divine_shield:
            target.buffs = [buff for buff in target.buffs if not isinstance(buff.status, DivineShield)]
            target.divine_shield = 0

    def __to_json__(self):
        return {
            "name": "remove_divine_shields"
        }


# class SwapStats(Action):
#     def act(self, actor, target, other=None):
#         temp_attack = target.calculate_attack()
#         temp_health = target.health
#         if temp_attack == 0:
#             target.die(None)
#         else:
#             target.set_attack_to(temp_health)
#             target.set_health_to(temp_attack)
#
#     def __to_json__(self):
#         return {
#             'name': 'swap_stats',
#         }


class Remove(Action):
    def act(self, actor, target, other=None):
        target.unattach()
        target.remove_from_board()

    def __to_json__(self):
        return {
            'name': 'remove'
        }


class SwapStats(Action):
    def __init__(self, source_stat, dest_stat, swap_with_owner):
        self.source_stat = source_stat
        self.dest_stat = dest_stat
        self.swap_with_owner = swap_with_owner

    def act(self, actor, target, other=None):
        if self.swap_with_owner:
            source = actor
        else:
            source = target
        temp = self.get_attribute(source, self.source_stat)
        self.set_attribute(source, self.source_stat, self.get_attribute(target, self.dest_stat))
        self.set_attribute(target, self.dest_stat, temp)
        if source.health == 0:
            source.die(None)
        if target is not source and target.health == 0:
            target.die(None)
        actor.player.game.check_delayed()

    @staticmethod
    def get_attribute(obj, attribute):
        if attribute == "damage":
            return obj.calculate_max_health() - obj.health
        elif attribute == 'mana':
            return obj.card.mana
        elif attribute == "attack":
            return obj.calculate_attack()
        elif attribute == "health":
            return obj.health

    @staticmethod
    def set_attribute(obj, attribute, value):
        from hearthbreaker.tags.status import ManaChange, SetAttack
        if attribute == "damage":
            was_enraged = obj.enraged
            obj.health = max(0, obj.clculate_max_health() - value)
            if value > 0:
                obj.enraged = True
                if not was_enraged:
                    obj._do_enrage()
        elif attribute == 'mana':
            obj.add_buff(Buff(ManaChange(value - obj.mana_cost())))
        elif attribute == "attack":
            obj.add_buff(Buff(SetAttack(value)))
        elif attribute == "health":
            obj.set_health_to(value)

    def __to_json__(self):
        return {
            'name': 'swap_stats',
            'source_stat': self.source_stat,
            'dest_stat': self.dest_stat,
            'swap_with_owner': self.swap_with_owner,
        }
