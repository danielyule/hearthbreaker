import copy
import importlib
import random
import abc
import hearthbreaker.powers
from hearthbreaker.tags.base import Aura, AuraUntil, Deathrattle, Effect, Enrage, Buff, BuffUntil
from hearthbreaker.tags.event import TurnEnded
from hearthbreaker.tags.selector import CurrentPlayer
from hearthbreaker.tags.status import ChangeAttack, ChangeHealth, Charge, Taunt, Stealth, DivineShield, Windfury, \
    SpellDamage, NoSpellTarget
import hearthbreaker.targeting
import hearthbreaker.constants

card_table = {}


def __create_card_table():
    importlib.import_module("hearthbreaker.cards")

    def __card_lookup_rec(card_type):
        subclasses = card_type.__subclasses__()
        if len(subclasses) is 0:
            c = card_type()
            card_table[c.ref_name] = card_type
        for sub_type in subclasses:
            __card_lookup_rec(sub_type)

    for card_class in Card.__subclasses__()[::-1]:
        __card_lookup_rec(card_class)


def card_lookup(card_name):
    """
    Given a the name of a card as a string, return an object corresponding to that card

    :param str card_name: A string representing the name of the card in English
    :return: An instance of a subclass of Card corresponding to the given card name or None if no Card
             by that name exists.
    :rtype: hearthbreaker.game_objects.Card
    """

    card = card_table[card_name]
    if card is not None:
        return card()
    return None


def get_cards():
    card_list = filter(lambda c: c.rarity != hearthbreaker.constants.CARD_RARITY.SPECIAL,
                       [card() for card in card_table.values()])
    return card_list


class GameException(Exception):
    """
    An :class:`Exception` relating to the operation of the game
    """

    def __init__(self, message):
        super().__init__(message)


class Bindable:
    """
    A class which inherits from Bindable has an event structure added to it.

    This event structure follows the observer pattern.  It consists of two parts: binding and triggering.
    A function handler is bound to an event using the :meth:`bind` or :meth:`bind_once` methods.  When the event is
    triggered using the :meth:`trigger` method, then any function handlers which have been bound to that event are
    called.

    Arguments can be passed to a bound function when binding or when triggering, or both.  Arguments from triggering
    are passed first, followed by arguments from binding.

    Functions can be bound such that they are called each time an event is triggered, or so that they are only called
    the next time a function is triggered.  The former case is handled by :meth:`bind` and the latter by
    :meth:`bind_once`

    **Examples**:

    Simple Binding::

       class EventTarget(Bindable):
           def __init__(self):
               super().__init__()

       def handler(fangs, scales):
           print("fangs: {:d}, scales: {:d}".format(fangs, scales))

       target = EventTarget()
       target.bind("attack", handler, 1001)
       target.trigger("attack", 2)             # outputs "fangs: 2, scales: 1001"
       target.trigger("attack", 6)             # outputs "fangs: 6, scales: 1001"

    Binding Once::

       class EventTarget(Bindable):
           def __init__(self):
               super().__init__()

       def handler(joke):
            print("{:s}! HAHAHA".format(joke))

       target = EventTarget()
       target.bind_once("joke_told", handler)

       # outputs "Well, I'd better replace it then! HAHAHA"
       target.trigger("joke_told", "Well, I'd better replace it then")

       # outputs nothing
       target.trigger("joke_told", "What a senseless waste of human life")

    Any class which subclasses this class must be sure to call :meth:`__init__`
    """

    def __init__(self):
        """
        Set up a new :class:`Bindable`.  Must be called by any subclasses.
        """
        self.events = {}

    def bind(self, event, function):
        """
        Bind a function to an event.  Each time the event is triggered, the function will be called.

        :param string event: The event to bind a function to
        :param function function: The function to bind.  The parameters are not checked until it is called, so
                                  ensure its signature matches the parameters called from :meth:`trigger`
        :see: :class:`Bindable`
        """

        if event not in self.events:
            self.events[event] = []

        self.events[event].append((function, False))

    def bind_once(self, event, function):
        """
        Bind a function to an event.  This function will only be called the next time the event is triggered, and
        then ignored.

        :param string event: The event to bind a function to
        :param function function: The function to bind.  The parameters are not checked until it is called, so
                                  ensure its signature matches the parameters called from :meth:`trigger`
        :see: :class:`Bindable`
        """

        if event not in self.events:
            self.events[event] = []

        self.events[event].append((function, True))

    def trigger(self, event, *args):
        """
        Trigger an event.  Any functions which have been bound to that event will be called.

        The parameters passed to this function as `args` will be passed along to the bound functions.

        :param string event: The name of the event to trigger
        :param list args: The arguments to pass to the bound function
        :see: :class:`Bindable`
        """
        if event in self.events:
            for handler in copy.copy(self.events[event]):
                if event in self.events and handler in self.events[event]:
                    if handler[1]:
                        self.events[event].remove(handler)
                        # tidy up the events dict so we don't have entries for events with no handlers
                        if len(self.events[event]) is 0:
                            del(self.events[event])
                    handler[0](*args)

    def unbind(self, event, function):
        """
        Unbind a function from an event.  When this event is triggered, the function is no longer called.

        `function` must be the same function reference as was passed in to :meth:`bind` or :meth:`bind_once`

        :param string event: The event to unbind the function from
        :param function function: The function to unbind.
        """
        if event in self.events:
            self.events[event] = [handler for handler in self.events[event] if not handler[0] == function]
            if len(self.events[event]) is 0:
                del (self.events[event])


class GameObject:
    """
    Provides typing for the various game objects in the engine.  Allows for checking the type of an object without
    needing to know about and import the various objects in the game engine
    """
    def __init__(self, effects=None, auras=None, buffs=None):
        # A list of the effects that this player has
        if effects:
            self.effects = effects
        else:
            self.effects = []
        #: A list of auras originate with this character
        if auras:
            self.auras = auras
        else:
            self.auras = []
        #: A list of buffs applied to this character
        if buffs:
            self.buffs = buffs
        else:
            self.buffs = []
        #: The player associated with this Game Object
        self.player = None

    def attach(self, obj, player):
        for effect in self.effects:
            effect.set_owner(obj)
            effect.apply()
        for buff in self.buffs:
            buff.set_owner(obj)
            buff.apply()
        for aura in self.auras:
            aura.set_owner(obj)
            player.add_aura(aura)

    def __to_json__(self):
        jsn = {}
        if self.effects:
            jsn['effects'] = self.effects
        if self.auras:
            jsn['auras'] = self.auras
        if self.buffs:
            jsn['buffs'] = self.buffs
        return jsn

    @staticmethod
    def __from_json__(minion, effects=None, auras=None, buffs=None, **kwargs):
        if effects:
            minion.effects = [Effect.from_json(**effect) for effect in effects]
        else:
            minion.effects = []
        if auras:
            minion.auras = [AuraUntil.from_json(**aura) if 'until' in aura else Aura.from_json(**aura)
                            for aura in auras]
        else:
            minion.auras = []
        if buffs:
            minion.buffs = [BuffUntil.from_json(**buff) if 'until' in buff else Buff.from_json(**buff)
                            for buff in buffs]
        else:
            minion.buffs = []

    @staticmethod
    def is_spell():
        """
        Checks if this object is a spell card
        :rtype: bool
        :returns: True if this is a spell card, false otherwise
        """
        return False

    @staticmethod
    def is_secret():
        """
        Checks if this object is a secret
        :rtype: bool
        :returns: True if this is a secret, false otherwise
        """
        return False

    @staticmethod
    def is_minion():
        """
        Checks if this object is a minion (card or actual minion)
        :rtype: bool
        :returns: True if this is a minion, false otherwise
        """
        return False

    @staticmethod
    def is_weapon():
        """
        Checks if this object is a weapon (card or actual weapon)
        :rtype: bool
        :returns: True if this is a weapon, false otherwise
        """

    @staticmethod
    def is_card():
        """
        Checks if this object is a card of any kind
        :rtype: bool
        :returns: True if this is a card, false otherwise
        """
        return False

    @staticmethod
    def is_hero():
        """
        Checks if this object is a hero
        :rtype: bool
        :returns: True if this is a hero, false otherwise
        """
        return False

    def add_effect(self, effect):
        """
        Applies the the given effect to the :class:`GameObject`.  The effect will be unapplied in the case of silence,
        and will be applied to any copies that are made.

        :param MinionEffect effect: The effect to apply to this :class:`GameObject
        """
        effect.set_owner(self)
        effect.apply()
        self.effects.append(effect)

    def add_aura(self, aura):
        if not isinstance(aura, Aura):
            raise TypeError("Expected an aura to be added")
        self.auras.append(aura)
        aura.set_owner(self)
        self.player.add_aura(aura)

    def remove_aura(self, aura):
        self.auras.remove(aura)
        self.player.remove_aura(aura)

    def add_buff(self, buff):
        if not isinstance(buff, Buff):
            raise TypeError("Expected a buff to be added")
        self.buffs.append(buff)
        buff.set_owner(self)
        buff.apply()

    def remove_buff(self, buff):
        self.buffs.remove(buff)
        buff.unapply()

    def unattach(self):
        for effect in reversed(self.effects):
            effect.unapply()
        for aura in reversed(self.auras):
            self.player.remove_aura(aura)
        for buff in reversed(self.buffs):
            if isinstance(buff, BuffUntil):
                buff.until.unbind(buff.owner, buff.__until__)


class Character(Bindable, GameObject, metaclass=abc.ABCMeta):
    """
    A Character in Hearthstone is something that can attack, i.e. a :class:`Hero` or :class:`Minion`.

     This common superclass handles all of the status tags and calculations involved in attacking or being attacked.
    """

    def __init__(self, attack_power, health, enrage=None, effects=None, auras=None, buffs=None):
        """
        Create a new Character with the given attack power and health

        :param int attack_power: the amount of attack this character has at creation
        :param int health: the maximum health of this character
        :param List[Action]: (optional) A list of :class:`hearthbreaker.tags.base.ReversibleActions` that describe
                             what will happen when this character is enraged
        """
        Bindable.__init__(self)
        GameObject.__init__(self, effects, auras, buffs)
        # : The current health of this character
        self.health = health
        # : The maximum health of this character
        self.base_health = health
        #: The amount of attack this character has
        self.base_attack = attack_power
        #: Whether or not this character can attack this turn
        self.active = False
        #: Whether or not this character has died
        self.dead = False
        #: If this character has windfury
        self.windfury = 0
        #: If this character has used their first windfury attack
        self.used_windfury = False
        #: If this character is currently frozen
        self.frozen = False
        #: If the character was frozen this turn (and so won't be unfrozen before the next turn)
        self.frozen_this_turn = False
        #: The :class:`Player` that owns this character
        self.player = None
        #: Whether or not this character is immune to damage (but not other tags)
        self.immune = 0
        #: The list of delayed events
        self.delayed = []
        #: Non zero if this character has stealth
        self.stealth = 0
        #: If this character is enraged
        self.enraged = False
        #: If this character has been removed from the board
        self.removed = False
        #: An integer describing when this character was created.  The lower, the earlier it was created
        self.born = -1
        #: An integer describing how much the attack of this character has been adjusted
        self.attack_delta = 0
        #: An integer describing how much the health of this character has been adjusted
        self.health_delta = 0
        #: A list of actions that describe what will happen when this character is enraged
        self.enrage = enrage
        #: The character that this minion is attacking, while it is carrying out its attack
        self.current_target = None

    def _remove_stealth(self):
        if self.stealth:
            for buff in self.buffs:
                if isinstance(buff.status, Stealth):
                    buff.unapply()
            self.buffs = [buff for buff in self.buffs if not isinstance(buff.status, Stealth)]

    def attack(self):
        """
        Causes this :class:`Character` to attack.

        The Character will assemble a list of possible targets and then ask the agent associated with this Character to
        select which target from the list it would like to attack.

        This method will not succeed if the Character can't attack, either because it is not active, or it is frozen,
        or some other factor.  All of the damage and death triggers will be processed at the end of this method, so that
        the order or evaluation doesn't affect the calculations.  For example, if Amani Berserker is damaged in the
        attack, its attack power shouldn't go up before the damage to its attacker is calculated.

        The attack will not take place if the Character dies or is otherwise removed as a result of attacking
        (e.g. various secrets)
        """
        if not self.can_attack():
            raise GameException("That minion cannot attack")

        found_taunt = False
        targets = []
        for enemy in self.player.game.other_player.minions:
            if enemy.taunt and enemy.can_be_attacked():
                found_taunt = True
            if enemy.can_be_attacked():
                targets.append(enemy)

        if found_taunt:
            targets = [target for target in targets if target.taunt]
        else:
            targets.append(self.player.game.other_player.hero)

        target = self.choose_target(targets)
        self._remove_stealth()
        self.current_target = target
        self.player.trigger("character_attack", self, target)
        self.trigger("attack", target)
        if self.removed or self.dead:  # removed won't be set yet if the Character died during this attack
            return
        target = self.current_target
        my_attack = self.calculate_attack()  # In case the damage causes my attack to grow
        target_attack = target.calculate_attack()
        if target_attack > 0:
            self.damage(target_attack, target)
        target.damage(my_attack, self)
        self.player.game.check_delayed()
        self.trigger("attack_completed")
        if self.windfury and not self.used_windfury:
            self.used_windfury = True
        else:
            self.active = False
        self.stealth = False
        self.current_target = None

    def choose_target(self, targets):
        """
        Consults the associated player to select a target from a list of targets

        :param list[Character] targets: the targets to choose a target from
        """
        return self.player.choose_target(targets)

    def calculate_attack(self):
        """
        Calculates the amount of attack this :class:`Character` has, including the base attack, any temporary attack
        bonuses for this turn
        """
        return max(0, self.base_attack + self.attack_delta)

    def calculate_max_health(self):
        """
        Calculates the maximum amount of health this :class:`Character` has, including the base health, and any aura
        tags
        """
        return self.base_health + self.health_delta

    def delayed_trigger(self, event, *args):
        """
        Set up a delayed trigger for an event.  Any events triggered with this method will not be called until
        :meth:`activate_delayed` is called.

        The purpose of this method is to allow for simultaneous events.  For example, if a minion is attacked
        then any damage events should be triggered after the attack, and at the same time as each other.

        :param string event: The event to set up a delayed trigger for
        :param list args: The arguments to pass to the handler when it is called.
        :see: :class:`Bindable`
        """
        self.delayed.append({'event': event, 'args': args})
        self.player.game.delayed_minions.add(self)

    def activate_delayed(self):
        """
        Activate any events that were delayed.

        :see: :meth:`delayed_trigger`
        """
        for delayed in self.delayed:
            self.trigger(delayed['event'], *delayed['args'])

        self.delayed = []

    def damage(self, amount, attacker):
        """
        Deal damage to this :class:`Character`.  This method uses the ``attacker`` parameter to determine the nature
        of the damage taken.  If the attacker is a :class:`Character`, then it is assumed to be a physical attack.
        If attacker is a :class:`SpellCard`, then it assumes a spell attack.  If ``None``, then something else
        (hero ability or battlecry).  This method will also trigger the various events associated with taking damage
        or dying.

        If the character has a divine shield, it will be removed, and the character will take no damage.  If the
        character's health is below the max_health, then the character is considered enraged.

        :param int amount: The amount of damage done (should be positive)
        :param Object attacker: The :class:`Character`or :class:`SpellCard that did the damage or ``None``.
        """
        if self.dead:
            return
        self.player.trigger("pre_damage", self, attacker, amount)
        if not self.immune:
            self.trigger("damaged", amount, attacker)
            self.player.trigger("character_damaged", self, attacker, amount)
            self.health -= amount
            if issubclass(type(attacker), Character):
                attacker.trigger("did_damage", self, amount)
                attacker._remove_stealth()
            self.trigger("health_changed")
            if not self.enraged and self.health != self.calculate_max_health():
                self.enraged = True
                self.trigger("enraged")
                self._do_enrage()
            if self.health <= 0:
                self.die(attacker)

    def change_attack(self, amount):
        """
        Change the amount of attack this :class:`Character` has.  The amount can be either positive or negative.
        This method will automatically undo its effect when silenced, and re-apply its effect when copied

        :param int amount: The amount to change the attack by
        """
        self.add_buff(Buff(ChangeAttack(amount)))

    def change_temp_attack(self, amount):
        """
        Change the amount of attack this :class:`Character` has on this turn only.  The amount can be either positive
        or negative. This method will automatically undo its effect when silenced, and re-apply its effect when copied

        :param int amount: The amount to change the temporary attack by
        """
        self.add_buff(BuffUntil(ChangeAttack(amount), TurnEnded(player=CurrentPlayer())))
        self.trigger("attack_changed", amount)

    def increase_health(self, amount):
        """
        Increase the amount of  total health this :class:`Character` has.  This is a permanent effect (unless the
        Character is silenced).  This effect will increase both the player's current health and maximum health

        :param int amount: the amount to increase health by
        """

        self.trigger("health_increased", amount)
        self.add_buff(Buff(ChangeHealth(amount)))
        self.trigger("health_changed")

    def decrease_health(self, amount):
        """
        Decrease the amount of  total health this :class:`Character` has.  This is a permanent effect (unless the
        Character is silenced).  This effect will decrease the player's maximum health, but will only decrease
        the player's health if it is above the new value for maximum health

        :param int amount: the amount to decrease health by
        """
        if self.enraged and self.health == self.calculate_max_health():
            self.enraged = False
            self.trigger("unenraged")
            self._do_unenrage()
        self.add_buff(Buff(ChangeHealth(-amount)))
        self.trigger("health_changed")
        self.trigger("health_decreased", amount)

    def set_attack_to(self, new_attack):
        """
        Sets the amount of total attack this :class:`Character` has.
        :param new_attack: An integer specifying what this character's new attack should be
        """
        diff = new_attack - (self.base_attack + self.attack_delta)
        for player in self.game.players:
            for aura in player.minion_auras:
                if aura.match(self) and isinstance(aura.status, ChangeAttack):
                    diff += aura.status.amount
        self.change_attack(diff)

    def set_health_to(self, new_health):
        """
        Sets the amount of total health this :class:`Character` has.  This will adjust its actual health if necessary
        :param new_health: An integer specifying what this character's new health should be
        """
        was_enraged = self.health < self.calculate_max_health()
        diff = new_health - (self.base_health + self.health_delta)

        for player in self.game.players:
            for aura in player.minion_auras:
                if aura.match(self) and isinstance(aura.status, ChangeHealth):
                    diff += aura.status.amount
        if diff > 0:
            self.increase_health(diff)
        elif diff < 0:
            self.decrease_health(-diff)
        self.health = self.calculate_max_health()
        if was_enraged:
            self._do_unenrage()
            self.trigger('unenraged')

    def freeze(self):
        """
        Causes this :class:`Character` to be frozen.  If this character is frozen on its opponent's turn, it
        will not be able to attack on the next turn.  If frozen on its owner's turn, it will not be able
        to attack this turn or its owner's next turn.
        """
        self.frozen_this_turn = True
        self.frozen = True

    def heal(self, amount, source):
        """
        Heals the :class:`Character`.  The health cannot exceed the character's max health.  If the amount
        being healed is less than 0, then the character is damaged instead.

        If the character's health is brought back to its maximum, then it is no longer enraged.

        :param int amount: The amount this character is being healed by.  Can be negative
        :param source: The source of this healing.  Could be a :class:`Minion`, a :class:`spell card <Card>` or None
        """
        if amount < 0:
            self.damage(-amount, source)
        if amount > 0:
            self.trigger("healed", amount)
            self.player.trigger("character_healed", self, amount)
            self.health += amount
            if self.health > self.calculate_max_health():
                self.health = self.calculate_max_health()
            if self.enraged and self.health == self.calculate_max_health():
                self.enraged = False
                self.trigger("unenraged")
                self._do_unenrage()
            self.trigger("health_changed")

    def silence(self):
        """
        Silence this :class:`Character`.  This will trigger the silence event, and undo any status tags that have
        affected this character (immune, attack & health increases, frozen, windfury)
        """
        self.frozen = False
        self.frozen_this_turn = False
        health_full = self.health == self.calculate_max_health()
        for effect in reversed(self.effects):
            effect.unapply()
        for aura in reversed(self.auras):
            self.player.remove_aura(aura)
        for buff in reversed(self.buffs):
            if isinstance(buff, BuffUntil):
                buff.until.unbind(buff.owner, buff.__until__)
            buff.unapply()

        self.effects = []
        self.auras = []
        self.buffs = []
        if self.enraged:
            self._do_unenrage()
        self.enrage = []
        if self.calculate_max_health() < self.health or health_full:
            self.health = self.calculate_max_health()
        self.trigger("silenced")

    def die(self, by):
        """
        Kills this :class:`Character`.  The death event will not be processed until :meth:`activate_delayed` is called.

        :param by: The object that killed this character.  Could be a :class:`Character`, a :class:`spell card <Card>`
                   or None
        """
        self.delayed_trigger("died", by)
        self.dead = True

    def can_attack(self):
        """
        Checks if this :class:`Character` can attack.  Evaluates whether or not is has already attacked, if its frozen
        and if it has an attack value

        :rtype boolean:
        """
        return self.calculate_attack() > 0 and self.active and not self.frozen and not (self.dead or self.removed)

    def spell_targetable(self):
        """
        Checks if a :class:`Character` can be targeted by a spell.  Minions with stealth or whose text say they can't be
        targeted by spells cannot be targeted, but any other character can.
        """
        return True

    def is_valid(self):
        return not self.dead and not self.removed

    def _do_enrage(self):
        if self.enrage:
            self.enrage.enrage(self)

    def _do_unenrage(self):
        if self.enrage:
            self.enrage.unenrage(self)


def _is_spell_targetable(target):
    return target.spell_targetable()


class Card(Bindable, GameObject):
    """
    Represents a card in Heathstone.  Every card is implemented as a subclass, either directly or through
    :class:`MinionCard`, :class:`SecretCard` or :class:`WeaponCard`.  If it is a direct subclass of this
    class then it is a standard spell, whereas if it is a subclass of one of :class:`MinionCard`, :class:`SecretCard`
    or :class:`WeaponCard`., then it is a minion, secret or weapon respectively.

    In order to play a card, it should be passed to :meth:`Game.play_card`.  Simply calling :meth:`use` will
    cause its effect, but not update the game state.
    """

    def __init__(self, name, mana, character_class, rarity, target_func=None,
                 filter_func=_is_spell_targetable, overload=0, ref_name=None):
        """
            Creates a new :class:`Card`.

            ``target_func`` and ``filter_func`` have very specific behavior.  In use, the target function is called with
             the filter function as a parameter to generate the list of possible targets for the card, then ask the
             agent to choose the appropriate target.  The selected target will be available as the :attr:`target`
             attribute of :class:`Card`. As such, it is critical to call :meth:`use` in any overriding implementations.

            :param string name: The name of the card in English
            :param int mana: The base amount of mana this card costs
            :param int character_class: A constant from :class:`hearthbreaker.constants.CHARACTER_CLASS` denoting
                                        which character this card belongs to or
                                        :const:`hearthbreaker.constants.CHARACTER_CLASS.ALL` if neutral
            :param int rarity: A constant from :class:`hearthbreaker.constants.CARD_RARITY` denoting the rarity of the
                               card.
            :param function target_func: A function which takes a game, and returns a list of targets.  If None, then
                                         the card is assumed not to require a target.  If `target_func` returns
                                         an empty list, then the card cannot be played.  If it returns None, then the
                                         card is played, but with no target (i.e. a battlecry which has no valid target
                                         will not stop the minion from being played).

                                         See :mod:`hearthbreaker.targeting` for more details.
            :param function filter_func: A boolean function which can be used to filter the list of targets. An example
                                         for :class:`hearthbreaker.cards.spells.priest.ShadowMadness` might be a
                                         function which returns true if the target's attack is less than 3.
            :param int overload: The amount of overload on the card
        """
        super().__init__()
        self.name = name
        if ref_name:
            self.ref_name = ref_name
        else:
            self.ref_name = name
        self.mana = mana
        self.character_class = character_class
        self.rarity = rarity
        self.cancel = False
        self.targetable = target_func is not None
        if self.targetable:
            self.targets = []
            self.target = None
            self.get_targets = target_func
            self.filter_func = filter_func
        self.overload = overload
        self.drawn = True

    def can_use(self, player, game):
        """
        Verifies if the card can be used with the game state as it is.

        Checks that the player has enough mana to play the card, and that the card has a valid
        target if it requires one.

        :return: True if the card can be played, false otherwise.
        :rtype: bool
        """
        if game.game_ended:
            return False
        if self.targetable:
            self.targets = self.get_targets(game, self.filter_func)
            if self.targets is not None and len(self.targets) is 0:
                return False

        return player.mana >= self.mana_cost(player)

    def mana_cost(self, player):
        """
        Calculates the mana cost for this card.

        This cost is the base cost for the card, modified by any tags from the card itself, or
        from other cards (such as :class:`hearthbreaker.cards.minions.neutral.VentureCoMercenary`)

        :param hearthbreaker.game_objects.Player player: The player who is trying to use the card.

        :return: representing the actual mana cost of this card.
        :rtype: int
        """
        calc_mana = self.mana
        for mana_filter in player.mana_filters:
            if mana_filter.filter(self):
                temp_mana = calc_mana
                calc_mana -= mana_filter.amount
                if temp_mana < mana_filter.min:  # Extra logic to handle 0 cost creatures with Summoning portal
                    return temp_mana
                if calc_mana < mana_filter.min:
                    return mana_filter.min
        return calc_mana

    def use(self, player, game):
        """
        Use the card.

        This method will cause the card's effect, but will not update the game state or trigger any events.
        To play a card correctly, use :meth:`Game.play_card`.

        Implementations of new cards should override this method, but be sure to call ``super().use(player, game)``

        :param hearthbreaker.game_objects.Player player: The player who is using the card.
        :param hearthbreaker.game_objects.Game game: The game this card is being used in.
        """
        pass

    @staticmethod
    def is_spell():
        return True

    @staticmethod
    def is_card():
        return True

    def __str__(self):  # pragma: no cover
        """
        Outputs a description of the card for debugging purposes.
        """
        return self.name + " (" + str(self.mana) + " mana)"


def _battlecry_targetable(target):
    return target.player is target.player.game.current_player or not target.stealth


class MinionCard(Card, metaclass=abc.ABCMeta):
    """
    Describes a :class:`Card` for summoning a minion.  This is distinct from the :class:`Minion` that represents the
    minion after it has been played.  This class represents the card aspects (mana cost, character class and rarity)
    as well as being responsible for creating the minion that will be added to the table.

    :see: :class:`Card`
    :see: :meth:`create_minion`
    """
    def __init__(self, name, mana, character_class, rarity, minion_type=hearthbreaker.constants.MINION_TYPE.NONE,
                 targeting_func=None, filter_func=_battlecry_targetable, ref_name=None, battlecry=None,
                 choices=None, combo=None, overload=0):
        """
        All parameters are passed directly to the :meth:`superclass's __init__ method <Card.__init__>`.

        :param string name: The name of this card in English
        :param int mana: The base mana cost of this card
        :param int character_class: The character class that this card belongs to.  Should be a member of
                                    :class:`hearthbreaker.constants.CHARACTER_CLASS`
        :param int rarity: How rare the card is.  Should be a member of :class:`hearthbreaker.constants.CARD_RARITY`
        :param int minion_type: The type that the summoned minion will have.  Should be a member of
                                :class:`hearthbreaker.constants.MINION_TYPE`
        :param function targeting_func: The function used to select a list of targets for this minion's battlecry, if it
                                        has one.  If it does not, then None.  This function should be taken from
                                        :mod:`hearthbreaker.targeting`, and should return `None` if there are no
                                        feasible targets.
        :param function filter_func: Used to filter targets returned from the targeting function for appropriateness.
                                     Typically used for ensuring that stealthed minions aren't targeted
        :param string ref_name: The name used for reference for this card.  If None (the default), the reference name
                                will be the same as its name.  Otherwise, this name must be unique across all cards.
        :param battlecry: Describes the battlecry this minion will use when it enters the field, or None for no
                          battlecry
        :type battlecry: :class:`hearthbreaker.tags.base.Battlecry`
        :param choices: Gives a list of :class:`hearthbreaker.tags.base.Choice` s for the user to pick between
        :type choices: [:class:`hearthbreaker.tags.base.Choice`]
        :param combo: Describes the battlecry this minion will have if played after another card.  Note that this
                      does not count as a battlecry for cards such as Nerub'ar Weblord.
        :type combo: :class:`hearthbreaker.tags.base.Battlecry`
        """
        super().__init__(name, mana, character_class, rarity, targeting_func, filter_func, overload, ref_name)
        self.minion_type = minion_type
        self.battlecry = battlecry
        self.choices = choices
        self.combo = combo

    def can_use(self, player, game):
        """
        Checks if this minion can be played.  The card must be able to play AND the board must not be full.

        :param hearthbreaker.game_objects.Player player: The player who wants to play this card
        :param hearthbreaker.game_objects.Game game: The game this card might be played in.
        """
        return len(player.minions) < 7 and super().can_use(player, game)

    def use(self, player, game):
        """
        Adds this minion to the board for the given player, if the card is able to be played.  The agent for the
        given player will be consulted about the location on the board of the played minion, about the target
        for the battlecry if necessary, and to choose an option for cards with choose.

        This method operates in the following order:

         1. Battlecry target chosen (if needed)
         2. Board placement chosen
         3. Minion is placed on the board
         4. minion_placed event
         5. Battlecry activated (if needed)
         6. minion_played event
         7. minion_summoned_event
         8. after_added event

        The precise ordering of events is necessary so that various tags (Sword of Justice, Knife Juggler, etc)
        trigger in the correct order, and to distinguish from :meth:`summon`, which is called when a minion is
        played as a side effect of of card (e.g. Feral Spirit)

        :param hearthbreaker.game_objects.Player player: The player who wants to play this card
        :param hearthbreaker.game_objects.Game game: The game this card will be played in.
        """
        if len(player.minions) >= 7:
            raise GameException("Only 7 minions allowed on the field at a time")
        super().use(player, game)
        minion = self.create_minion(player)
        minion.card = self
        minion.player = player
        minion.game = game
        minion.index = player.agent.choose_index(self, player)
        minion.add_to_board(minion.index)
        player.trigger("minion_placed", minion)
        if self.choices:
            choice = player.agent.choose_option(*self.choices)
            choice.battlecry(minion)
        if self.combo and player.cards_played > 0:
            self.combo.battlecry(minion)
        else:
            if self.battlecry:  # There are currently two battlecry systems, hence the weirdness
                self.battlecry.battlecry(minion)
            elif minion.battlecry is not None:
                minion.battlecry(minion)
        if not minion.removed:
            # In case the minion has been replaced by its battlecry (e.g. Faceless Manipulator)
            minion = player.minions[minion.index]
            player.trigger("minion_played", minion)
            player.trigger("minion_summoned", minion)
            player.trigger("after_added", minion)

    def summon(self, player, game, index):
        """
        Summons the minion associated with this card onto the board.  This is to be used when a spell
        created a minion, instead of being played from the hand.

        If the player already has 7 minions on the board, this method does nothing.

        This method operates in the following order:

         1. Minion is placed on the board
         2. minion_placed event
         3. minion_summoned_event
         4. after_added event

        The ordering is important so that efects trigger in the correct order.

        :see: :meth:`use`

        :param hearthbreaker.game_objects.Player player: The player the summoned minion will belong to
        :param hearthbreaker.game_objects.Player player: The player the summoned minion will belong to
        :param hearthbreaker.game_objects.Game game: The game the minion is being summoned to
        :param int index: The index where the new minion will be added
        """
        if len(player.minions) < 7:
            minion = self.create_minion(player)
            minion.card = self
            minion.player = player
            minion.game = game
            minion.index = index
            minion.add_to_board(index)
            player.trigger("minion_placed", minion)
            player.trigger("minion_summoned", minion)
            player.trigger("after_added", minion)
            return minion

    @abc.abstractmethod
    def create_minion(self, player):
        """
        Creates the minion associated with this card.  This method is responsible for creating the :class:`Minion`
        object and adding any necessary tags.  This method must be overridden by a subclass's implementation.  For
        more details, see :doc:`contributing`.

        This method is only responsible for creating the minion and attaching events.  It is not responsible for setting
        the minion's player or game attributes, or correctly setting its index.  That is handled within :meth:`play`
        and :meth:`summon`

        :param hearthbreaker.game_objects.Player player: The player who the newly created minion will belong to.

        :rtype: hearthbreaker.game_objects.Minion
        """
        pass

    @staticmethod
    def is_spell():
        return False

    @staticmethod
    def is_minion():
        return True


class SecretCard(Card, metaclass=abc.ABCMeta):
    def __init__(self, name, mana, character_class, rarity):
        super().__init__(name, mana, character_class, rarity, None)
        self.player = None

    def can_use(self, player, game):
        return super().can_use(player, game) and self.name not in [secret.name for secret in player.secrets]

    def use(self, player, game):
        super().use(player, game)
        player.secrets.append(self)
        self.player = player

    def reveal(self):
        self.player.trigger("secret_revealed", self)
        self.player.secrets.remove(self)
        self.deactivate(self.player)

    @abc.abstractmethod
    def _reveal(self, *args):
        pass

    @abc.abstractmethod
    def activate(self, player):
        pass

    @abc.abstractmethod
    def deactivate(self, player):
        pass

    @staticmethod
    def is_secret():
        return True


class Minion(Character):
    def __init__(self, attack, health, battlecry=None,
                 deathrattle=None, taunt=False, charge=False, spell_damage=0, divine_shield=False, stealth=False,
                 windfury=False, spell_targetable=True, effects=None, auras=None, buffs=None,
                 enrage=None):
        super().__init__(attack, health, enrage, effects, auras, buffs)
        self.game = None
        self.card = None
        self.index = -1
        self.charge = 0
        self.taunt = 0
        self.divine_shield = 0
        self.can_be_targeted_by_spells = True
        self.battlecry = battlecry
        if deathrattle:
            if isinstance(deathrattle, Deathrattle):
                self.deathrattle = [deathrattle]
            else:
                self.deathrattle = deathrattle
        else:
            self.deathrattle = []
        self.aura_attack = 0
        self.aura_health = 0
        self.exhausted = True
        self.removed = False
        if charge:
            self.buffs.append(Buff(Charge()))
        if taunt:
            self.buffs.append(Buff(Taunt()))
        if stealth:
            self.buffs.append(Buff(Stealth()))
        if divine_shield:
            self.buffs.append(Buff(DivineShield()))
        if windfury:
            self.buffs.append(Buff(Windfury()))
        if not spell_targetable:
            self.buffs.append(Buff(NoSpellTarget()))
        if spell_damage:
            self.buffs.append(Buff(SpellDamage(spell_damage)))

    def add_to_board(self, index):
        aura_affects = {}
        for player in self.game.players:
            for aura in player.minion_auras:
                aura_affects[aura] = set()
                for minion in self.player.minions:
                    if aura.match(minion):
                        aura_affects[aura].add(minion)
        self.game.minion_counter += 1
        self.player.minions.insert(index, self)
        self.born = self.game.minion_counter
        count = 0
        for minion in self.player.minions:
            minion.index = count
            count += 1
        self.index = index
        self.active = True
        self.health += self.calculate_max_health() - self.base_health - self.health_delta
        self.attach(self, self.player)
        for player in self.game.players:
            for aura in player.minion_auras:
                for minion in self.player.minions:
                    if aura in aura_affects:
                        is_in = minion in aura_affects[aura]
                        if not is_in and aura.match(minion):
                            aura.status.act(aura.owner, minion)
                        elif is_in and not aura.match(minion):
                            aura.status.unact(aura.owner, minion)
        self.trigger("added_to_board", self, index)

    def calculate_attack(self):
        """
        Calculates the amount of attack this :class:`Minion` has, including the base attack, any temporary attack
        bonuses for this turn and any aura tags
        """
        return super().calculate_attack() + self.aura_attack

    def calculate_max_health(self):
        """
        Calculates the maximum amount of health this :class:`Character` has, including the base health, and any aura
        tags
        """

        return super().calculate_max_health() + self.aura_health

    def remove_from_board(self):
        if not self.removed:
            aura_affects = {}
            for aura in self.player.minion_auras:
                aura_affects[aura] = set()
                for minion in self.player.minions:
                    if aura.match(minion):
                        aura_affects[aura].add(minion)
            for minion in self.player.minions:
                if minion.index > self.index:
                    minion.index -= 1
            self.player.minions.remove(self)
            self.player.trigger("minion_removed", self)
            self.removed = True
            for aura in self.player.minion_auras:
                for minion in self.player.minions:
                    is_in = minion in aura_affects[aura]
                    if not is_in and aura.match(minion):
                        aura.status.act(aura.owner, minion)
                    elif is_in and not aura.match(minion):
                        aura.status.unact(aura.owner, minion)

    def replace(self, new_minion):
        """
        Replaces this minion with another one

        :param hearthbreaker.game_objects.Minion new_minion: The minion to replace this minion with
        """
        self.unattach()
        new_minion.index = self.index
        new_minion.player = self.player
        new_minion.game = self.game
        new_minion.active = True
        new_minion.exhausted = True
        self.game.minion_counter += 1
        new_minion.born = self.game.minion_counter
        if self.index >= len(self.player.minions):
            raise ValueError("Attempting to replace minion with invalid index")
        self.player.minions[self.index] = new_minion
        new_minion.attach(new_minion, self.player)
        for aura in self.player.minion_auras:
            if aura.match(new_minion):
                aura.status.act(self, new_minion)
        new_minion.health += new_minion.calculate_max_health() - new_minion.base_health

    def attack(self):
        super().attack()

    def damage(self, amount, attacker):
        if self.divine_shield:
            self.buffs = [buff for buff in self.buffs if not isinstance(buff.status, DivineShield)]
            self.divine_shield = 0
        else:
            super().damage(amount, attacker)

    def heal(self, amount, source):
        super().heal(amount, source)

    def die(self, by):
        # Since deathrattle gets removed by silence, save it
        if not self.dead and not self.removed:
            deathrattle = self.deathrattle

            def delayed_death(c):

                if deathrattle is not None:
                    for rattle in deathrattle:
                        rattle.deathrattle(self)
                        if self.player.double_deathrattle:
                            rattle.deathrattle(self)
                self.unattach()
                self.player.trigger("minion_died", self, by)
                self.player.graveyard.add(self.card.name)
            self.bind_once("died", delayed_death)
            super().die(by)
            self.player.dead_this_turn.append(self)
            self.remove_from_board()

    def silence(self):
        super().silence()
        self.battlecry = None
        self.deathrattle = []

    def can_attack(self):
        return (self.charge or not self.exhausted) and super().can_attack()

    def can_be_attacked(self):
        return not self.stealth

    def spell_targetable(self):
        return (not self.stealth or self.player is self.player.game.current_player) and self.can_be_targeted_by_spells

    @staticmethod
    def is_minion():
        return True

    def __str__(self):  # pragma: no cover
        return "({0}) ({1}) {2} at index {3}".format(self.calculate_attack(), self.health, self.card.name, self.index)

    def copy(self, new_owner, new_game=None):
        new_minion = Minion(self.base_attack, self.base_health, self.battlecry,
                            effects=copy.deepcopy(self.effects),
                            auras=copy.deepcopy(self.auras),
                            buffs=copy.deepcopy(self.buffs),
                            deathrattle=copy.deepcopy(self.deathrattle),
                            enrage=copy.deepcopy(self.enrage))
        new_minion.health = self.base_health - (self.calculate_max_health() - self.health)
        new_minion.enraged = self.enraged
        new_minion.immune = self.immune
        new_minion.index = self.index
        new_minion.active = self.active
        new_minion.exhausted = self.exhausted
        new_minion.born = self.born
        card_type = type(self.card)
        new_minion.card = card_type()
        new_minion.player = new_owner
        if new_game:
            new_minion.game = new_game
        else:
            new_minion.game = new_owner.game
        return new_minion

    @staticmethod
    def __from_json__(md, player, game):
        minion = Minion(md['attack'], md['max_health'])
        GameObject.__from_json__(minion, **md)
        minion.health = md['max_health'] - md['damage']
        minion.exhausted = md['exhausted']
        minion.active = not md['already_attacked']
        minion.born = md['sequence_id']
        if 'enrage' in md:
            minion.enrage = Enrage.from_json(**md['enrage'])
        minion.deathrattle = []
        for rattle in md['deathrattles']:
            minion.deathrattle.append(Deathrattle.from_json(**rattle))
        minion.card = card_lookup(md["name"])
        minion.game = game
        minion.player = player
        return minion

    def bounce(self):
        if len(self.player.hand) < 10:
            self.unattach()
            self.remove_from_board()
            self.player.hand.append(self.card)
        else:
            self.die(None)
            self.game.check_delayed()

    def __to_json__(self):
        if self.frozen_this_turn and self.player is self.player.game.current_player:
            frozen_for = 3
        elif self.frozen_this_turn:
            frozen_for = 2
        elif self.frozen:
            frozen_for = 1
        else:
            frozen_for = 0
        r_val = super().__to_json__()
        r_val.update({
            'name': self.card.name,
            'sequence_id': self.born,
            'position': self.index,
            'damage': self.calculate_max_health() - self.health,
            'max_health': self.base_health,
            'attack': self.base_attack,
            "exhausted": self.exhausted,
            "already_attacked": not self.active,
            'deathrattles': self.deathrattle,
            'frozen_for': frozen_for,
        })
        if self.enrage:
            r_val['enrage'] = self.enrage
        return r_val


class WeaponCard(Card, metaclass=abc.ABCMeta):
    """
    Represents a :class:`Card` for creating a :class:`Weapon`
    """

    def __init__(self, name, mana, character_class, rarity, target_func=None, filter_func=lambda t: not t.stealth,
                 overload=0, battlecry=None, combo=None):
        """
        Create a new :class:`WeaponCard`

        :param string name: The name of the weapon in English
        :param int mana: The base amount of mana this card costs
        :param int character_class: A constant from :class:`hearthbreaker.constants.CHARACTER_CLASS` denoting
                                    which character this card belongs to or
                                    :const:`hearthbreaker.constants.CHARACTER_CLASS.ALL` if neutral
        :param int rarity: A constant from :class:`hearthbreaker.constants.CARD_RARITY` denoting the rarity of the card.
        :param function target_func: A function which takes a game, and returns a list of targets.  If None, then
                                     the weapon is assumed not to require a target for its battlecry.
                                     If `target_func` returns None, then the card is played, but with no target (i.e. a
                                     battlecry which has no valid target will not stop the weapon from being played).
                                     See :mod:`hearthbreaker.targeting` for more details.
        :param function filter_func: A boolean function which can be used to filter the list of targets. An example
                                     for :class:`hearthbreaker.cards.spells.priest.ShadowMadness` might be a function
                                     which returns true if the target's attack is less than 3.  Currently no weapons
                                     require anything but the default
        :param int overload: The amount of overload on the card
        :param battlecry: A battlecry that will activate when this weapon is equipped
        :type battlecry: :class:`hearthbreaker.tags.base.Battlecry`
        :param combo: A battlecry that will activate when this weapon is equipped and at least one other card has
                      been played.  If combo activates, battlecry will not
        :type combo: :class:`hearthbreaker.tags.base.Battlecry`
        """
        super().__init__(name, mana, character_class, rarity, target_func, filter_func, overload)
        self.battlecry = battlecry
        self.combo = combo

    def use(self, player, game):
        """
        Create a new weapon and attach it to the player's hero

        :param Player player: The player who will use this weapon
        :param Game game: The game this weapon will be used in
        """
        super().use(player, game)
        weapon = self.create_weapon(player)
        weapon.card = self
        weapon.player = player
        weapon.game = game
        if self.combo and player.cards_played > 0:
            self.combo.battlecry(weapon)
        else:
            if self.battlecry:
                self.battlecry.battlecry(weapon)
            elif weapon.battlecry is not None:
                weapon.battlecry(weapon)
        weapon.equip(player)

    @abc.abstractmethod
    def create_weapon(self, player):
        """
        Create a new weapon.  Any new weapon cards which are created must override this method.
        """
        pass

    @staticmethod
    def is_spell():
        return False

    @staticmethod
    def is_weapon():
        return True


class Weapon(Bindable, GameObject):
    """
    Represents a Hearthstone weapon.  All weapons have attack power and durability.  The logic for handling the
    attacks is handled by :class:`Hero`, but it can be modified through the use of events.
    """

    def __init__(self, attack_power, durability, battlecry=None, deathrattle=None,
                 effects=None, auras=None, buffs=None):
        """
        Creates a new weapon with the given attack power and durability.  A battlecry and deathrattle can also
        optionally be set.
        :param int attack_power: The amount of attack this weapon gives the hero
        :param int durability: The number of times this weapon can be used to attack before being discarded
        :param function battlecry: Called when this weapon is equipped
        :param function deathrattle: Called when the weapon is destroyed
        """
        Bindable.__init__(self)
        GameObject.__init__(self, effects, auras, buffs)
        # : The amount of attack this weapon gives the hero
        self.base_attack = attack_power
        # : The number of times this weapon can be used to attack before being discarded
        self.durability = durability
        #: Called when this weapon is equipped
        self.battlecry = battlecry
        #: Called when the weapon is destroyed
        self.deathrattle = deathrattle
        #: The :class:`Player` associated with this weapon
        self.player = None
        #: The :class:`WeaponCard` that created this weapon
        self.card = None

    def copy(self, new_owner):
        new_weapon = Weapon(self.base_attack, self.durability, self.battlecry, copy.deepcopy(self.deathrattle),
                            copy.deepcopy(self.effects), copy.deepcopy(self.auras), copy.deepcopy(self.buffs))
        new_weapon.player = new_owner
        return new_weapon

    def destroy(self):
        self.trigger("destroyed")
        # Deathrattle is triggered no matter how the weapon is destroyed, see
        # http://www.hearthhead.com/card=1805/deaths-bite#comments:id=1983510
        if self.deathrattle is not None:
            self.deathrattle.deathrattle(self.player.hero)
        self.player.hero.weapon = None
        self.player.hero.trigger("weapon_destroyed")
        self.unattach()

    def equip(self, player):
        self.player = player
        if self.player.hero.weapon is not None:
            self.player.hero.weapon.destroy()
        self.player.hero.weapon = self
        self.attach(self.player.hero, player)
        self.player.hero.trigger("weapon_equipped")

    def __to_json__(self):
        parent_json = super().__to_json__()
        parent_json.update({
            'name': self.card.name,
            'attack': self.base_attack,
            'durability': self.durability,
        })
        return parent_json

    @staticmethod
    def is_weapon():
        return True

    @staticmethod
    def __from_json__(wd, player):
        weapon_card = card_lookup(wd['name'])
        weapon = weapon_card.create_weapon(player)
        weapon.base_attack = wd['attack']
        weapon.durability = wd['durability']
        weapon.card = weapon_card
        GameObject.__from_json__(weapon, **wd)
        return weapon


class Deck:
    def __init__(self, cards, character_class):
        if len(cards) != 30:
            raise GameException("Deck must have exactly 30 cards in it")
        self.cards = cards
        self.character_class = character_class
        for card in cards:
            card.drawn = False
        self.left = 30

    def copy(self):
        def copy_card(card):
            new_card = type(card)()
            new_card.drawn = card.drawn
            return new_card
        new_deck = Deck.__new__(Deck)
        new_deck.cards = [copy_card(card) for card in self.cards]
        new_deck.character_class = self.character_class
        new_deck.left = self.left
        return new_deck

    def can_draw(self):
        return self.left > 0

    def draw(self, game):
        if not self.can_draw():
            raise GameException("Cannot draw more than 30 cards")
        card = game.random_draw(self.cards, lambda c: not c.drawn)
        card.drawn = True
        self.left -= 1
        return card

    def put_back(self, card):
        for index in range(0, 30):
            if self.cards[index] == card:
                if not card.drawn:
                    raise GameException("Tried to put back a card that hadn't been used yet")
                self.cards[index].drawn = False
                self.left += 1
                return
        raise GameException("Tried to put back a card that didn't come from this deck")

    def __to_json__(self):
        card_list = []
        for index in range(0, 30):
            card_list.append({
                'name': self.cards[index].name,
                'used': self.cards[index].drawn
            })
        return card_list

    @classmethod
    def __from__to_json__(cls, dd, character_class):
        cards = []
        used = []
        left = 30
        for entry in dd:
            card = card_lookup(entry["name"])
            card.drawn = entry["used"]
            cards.append(card)
            used.append(entry["used"])
            if entry["used"]:
                left -= 1
        deck = Deck.__new__(Deck)
        deck.cards = cards
        deck.used = used
        deck.left = left
        deck.character_class = character_class
        return deck


class Hero(Character):
    def __init__(self, character_class, player):
        super().__init__(0, 30)

        self.armor = 0
        self.weapon = None
        self.bonus_attack = 0
        self.character_class = character_class
        self.player = player
        self.game = player.game
        self.power = hearthbreaker.powers.powers(self.character_class)(self)

    def calculate_attack(self):
        if self.player == self.player.game.current_player and self.weapon:
            return super().calculate_attack() + self.weapon.base_attack + self.bonus_attack
        else:
            return super().calculate_attack()

    def copy(self, new_owner, new_game):
        new_hero = Hero(self.character_class, new_owner)
        if self.weapon:
            new_hero.weapon = self.weapon.copy(new_owner)
        new_hero.health = self.health
        new_hero.armor = self.armor
        new_hero.bonus_attack = 0
        new_hero.used_windfury = False
        new_hero.frozen = False
        new_hero.frozen_this_turn = False
        new_hero.active = self.active
        new_hero.effects = copy.deepcopy(self.effects)
        new_hero.auras = copy.deepcopy(self.auras)
        new_hero.buffs = copy.deepcopy(self.buffs)

        return new_hero

    def attack(self):
        super().attack()
        if self.weapon is not None:
            self.weapon.durability -= 1
            if self.weapon.durability is 0:
                self.weapon.destroy()

    def damage(self, amount, attacker):
        self.armor -= amount
        if self.armor < 0:
            new_amount = -self.armor
            self.armor = 0
            super().damage(new_amount, attacker)
        elif issubclass(type(attacker), Character):
            attacker.trigger("did_damage", self, 0)

    def increase_armor(self, amount):
        self.player.trigger("armor_increased", amount)
        self.armor += amount

    def die(self, by):
        super().die(by)
        self.player.game.game_over()

    def find_power_target(self):
        targets = hearthbreaker.targeting.find_spell_target(self.player.game, lambda t: t.spell_targetable())
        target = self.choose_target(targets)
        self.trigger("found_power_target", target)
        return target

    @staticmethod
    def is_hero():
        return True

    def __to_json__(self):
        if self.frozen_this_turn and self.player is self.player.game.current_player:
            frozen_for = 3
        elif self.frozen_this_turn:
            frozen_for = 2
        elif self.frozen:
            frozen_for = 1
        else:
            frozen_for = 0
        r_val = super().__to_json__()
        r_val.update({
            'character': hearthbreaker.constants.CHARACTER_CLASS.to_str(self.character_class),
            'weapon': self.weapon,
            'health': self.health,
            'armor': self.armor,
            'attack': self.base_attack,
            'immune': self.immune,
            'frozen_for': frozen_for,
            'used_windfury': self.used_windfury,
            'already_attacked': not self.active,
        })
        return r_val

    @classmethod
    def __from_json__(cls, hd, player):
        hero = Hero(hearthbreaker.constants.CHARACTER_CLASS.from_str(hd["character"]), player)
        GameObject.__from_json__(hero, **hd)
        if hd["frozen_for"] == 3 or hd["frozen_for"] == 2:
            hero.frozen_this_turn = True
        elif hd["frozen_for"] > 0:
            hero.frozen = True
        hero.health = hd["health"]
        hero.base_attack = hd["attack"]
        hero.armor = hd["armor"]
        hero.immune = hd["immune"]
        hero.used_windfury = hd["used_windfury"]
        hero.active = not hd["already_attacked"]
        if hd['weapon']:
            hero.weapon = Weapon.__from_json__(hd["weapon"], player)
        return hero


class Player(Bindable):
    def __init__(self, name, deck, agent, game):
        super().__init__()
        self.game = game
        self.hero = Hero(deck.character_class, self)
        self.name = name
        self.mana = 0
        self.max_mana = 0
        self.deck = deck
        self.spell_damage = 0
        self.minions = []
        self.graveyard = set()
        self.hand = []
        self.minion_auras = []
        self.player_auras = []
        self.fatigue = 0
        self.agent = agent
        self.effects = []
        self.secrets = []
        self.spell_multiplier = 1
        self.heal_multiplier = 1
        self.heal_does_damage = 0
        self.double_deathrattle = 0
        self.mana_filters = []
        self.overload = 0
        self.opponent = None
        self.cards_played = 0
        self.dead_this_turn = []

    def __str__(self):  # pragma: no cover
        return "Player: " + self.name

    def copy(self, new_game):
        copied_player = Player(self.name, self.deck.copy(), self.agent, new_game)

        copied_player.hero = self.hero.copy(copied_player, new_game)
        copied_player.graveyard = copy.copy(self.graveyard)
        copied_player.minions = [minion.copy(copied_player, new_game) for minion in self.minions]
        copied_player.hand = [type(card)() for card in self.hand]
        copied_player.spell_damage = self.spell_damage
        copied_player.mana = self.mana
        copied_player.max_mana = self.max_mana
        copied_player.overload = self.overload
        copied_player.dead_this_turn = copy.copy(self.dead_this_turn)
        for effect in self.effects:
            effect = copy.copy(effect)
            copied_player.add_effect(effect)
        copied_player.secrets = []
        for secret in self.secrets:
            new_secret = type(secret)()
            new_secret.player = copied_player
            copied_player.secrets.append(new_secret)
        for aura in filter(lambda a: isinstance(a, AuraUntil), self.player_auras):
            aura = copy.deepcopy(aura)
            aura.owner = copied_player.hero
            copied_player.add_aura(aura)
        for aura in filter(lambda a: isinstance(a, AuraUntil), self.minion_auras):
            aura = copy.deepcopy(aura)
            aura.owner = copied_player.hero
            copied_player.add_aura(aura)
        copied_player.effect_count = dict()
        return copied_player

    def draw(self):
        if self.can_draw():
            card = self.deck.draw(self.game)
            self.trigger("card_drawn", card)
            if len(self.hand) < 10:
                self.hand.append(card)
            else:
                self.trigger("card_destroyed", card)
        else:
            self.fatigue += 1
            self.hero.trigger("fatigue_damage", self.fatigue)
            self.hero.damage(self.fatigue, None)
            self.hero.activate_delayed()

    def can_draw(self):
        return self.deck.can_draw()

    def effective_spell_damage(self, base_damage):
        return (base_damage + self.spell_damage) * self.spell_multiplier

    def effective_heal_power(self, base_heal):
        if self.heal_does_damage:
            return -(base_heal + self.spell_damage) * self.spell_multiplier
        else:
            return base_heal * self.heal_multiplier

    def put_back(self, card):
        self.hand.remove(card)
        self.deck.put_back(card)
        self.trigger("card_put_back", card)

    def discard(self):
        if len(self.hand) > 0:
            targets = self.hand
            target = self.game.random_choice(targets)
            self.hand.remove(target)
            self.trigger("card_discarded", target)

    def add_effect(self, effect):
        def remove_effect(*args):
            effect.unapply()
            self.effects.remove(effect)
            effect.event.unbind(self.hero, remove_effect)
        self.effects.append(effect)
        effect.set_owner(self.hero)
        effect.apply()
        effect.event.bind(self.hero, remove_effect)

    def add_aura(self, aura):
        if isinstance(aura.selector, hearthbreaker.tags.selector.MinionSelector):
            self.minion_auras.append(aura)
        else:
            self.player_auras.append(aura)
        if not aura.owner:
            aura.set_owner(self.hero)
        aura.apply()

    def remove_aura(self, aura):
        if isinstance(aura.selector, hearthbreaker.tags.selector.MinionSelector):
            self.minion_auras = [au for au in filter(lambda a: not a.eq(aura), self.minion_auras)]
        else:
            self.player_auras = [au for au in filter(lambda a: not a.eq(aura), self.player_auras)]
        aura.unapply()

    def choose_target(self, targets):
        return self.agent.choose_target(targets)

    def is_valid(self):
        return True

    def __to_json__(self):
        auras = copy.copy(self.player_auras)
        auras.extend(self.minion_auras)
        return {
            'hero': self.hero,
            'deck': self.deck,
            'graveyard': [card for card in self.graveyard],
            'hand': [card.name for card in self.hand],
            'secrets': [secret.name for secret in self.secrets],
            'effects': self.effects,
            'auras': [aura for aura in filter(lambda a: isinstance(a, AuraUntil), auras)],
            'minions': self.minions,
            'mana': self.mana,
            'max_mana': self.max_mana,
            'name': self.name,
        }

    @classmethod
    def __from_json__(cls, pd, game, agent):
        deck = Deck.__from__to_json__(pd["deck"],
                                      hearthbreaker.constants.CHARACTER_CLASS.from_str(pd["hero"]["character"]))
        player = Player("whatever", deck, agent, game)
        hero = Hero.__from_json__(pd["hero"], player)
        player.hero = hero
        hero.player = player
        if hero.weapon:
            hero.weapon.player = player
        player.mana = pd["mana"]
        player.max_mana = pd["max_mana"]
        player.name = pd['name']
        player.hand = [card_lookup(name) for name in pd["hand"]]
        player.graveyard = set()
        for card_name in pd["graveyard"]:
            player.graveyard.add(card_name)

        player.secrets = []
        for secret_name in pd["secrets"]:
            secret = card_lookup(secret_name)
            secret.player = player
            player.secrets.append(secret)
        i = 0
        player.minions = []
        for md in pd["minions"]:
            minion = Minion.__from_json__(md, player, game)
            minion.index = i
            player.minions.append(minion)
            i += 1
        return player


class Game(Bindable):
    def __init__(self, decks, agents):
        super().__init__()
        self.delayed_minions = set()
        self.first_player = self._generate_random_between(0, 1)
        if self.first_player is 0:
            play_order = [0, 1]
        else:
            play_order = [1, 0]
        self.players = [Player("one", decks[play_order[0]], agents[play_order[0]], self),
                        Player("two", decks[play_order[1]], agents[play_order[1]], self)]
        self.current_player = self.players[0]
        self.other_player = self.players[1]
        self.current_player.opponent = self.other_player
        self.other_player.opponent = self.current_player
        self.game_ended = False
        self.minion_counter = 0
        self.__pre_game_run = False
        self.last_spell = None
        self._has_turn_ended = True
        self._all_cards_played = []

    def random_draw(self, cards, requirement):
        filtered_cards = [card for card in filter(requirement, cards)]
        if len(filtered_cards) > 0:
            return filtered_cards[self._generate_random_between(0, len(filtered_cards) - 1)]
        return None

    def random_choice(self, choice):
        return choice[self._generate_random_between(0, len(choice) - 1)]

    def random_amount(self, minimum, maximum):
        return self._generate_random_between(minimum, maximum)

    def _generate_random_between(self, lowest, highest):
        return random.randint(lowest, highest)

    def check_delayed(self):
        sorted_minions = sorted(self.delayed_minions, key=lambda m: m.born)
        self.delayed_minions = set()
        for minion in sorted_minions:
            minion.activate_delayed()

    def pre_game(self):
        if self.__pre_game_run:
            return
        self.__pre_game_run = True

        for i in range(0, 3):
            self.players[0].draw()

        for i in range(0, 4):
            self.players[1].draw()
        card_keep_index = self.players[0].agent.do_card_check(self.players[0].hand)
        self.trigger("kept_cards", self.players[0].hand, card_keep_index)
        put_back_cards = []
        for card_index in range(0, 3):
            if not card_keep_index[card_index]:
                self.players[0].draw()
                put_back_cards.append(self.players[0].hand[card_index])

        for card in put_back_cards:
            self.players[0].put_back(card)

        card_keep_index = self.players[1].agent.do_card_check(self.players[1].hand)
        self.trigger("kept_cards", self.players[1].hand, card_keep_index)
        put_back_cards = []
        for card_index in range(0, 4):
            if not card_keep_index[card_index]:
                self.players[1].draw()
                put_back_cards.append(self.players[1].hand[card_index])

        for card in put_back_cards:
            self.players[1].put_back(card)

        self.players[1].hand.append(card_lookup("The Coin"))

    def start(self):
        self.pre_game()
        self.current_player = self.players[1]
        while not self.game_ended:
            self.play_single_turn()

    def play_single_turn(self):
        self._start_turn()
        self.current_player.agent.do_turn(self.current_player)
        self._end_turn()

    def _start_turn(self):
        if not self._has_turn_ended:  # when a game is copied, the turn isn't ended before the next one starts
            self._end_turn()
        if self.current_player == self.players[0]:
            self.current_player = self.players[1]
            self.other_player = self.players[0]
        else:
            self.current_player = self.players[0]
            self.other_player = self.players[1]
        if self.current_player.max_mana < 10:
            self.current_player.max_mana += 1

        for secret in self.other_player.secrets:
            secret.activate(self.other_player)
        for minion in self.current_player.minions:
            minion.active = True
        self.current_player.mana = self.current_player.max_mana - self.current_player.overload
        self.current_player.overload = 0
        self.current_player.cards_played = 0
        self.current_player.dead_this_turn = []
        self.current_player.hero.power.used = False
        self.current_player.hero.active = True
        self.current_player.draw()
        self.current_player.trigger("turn_started", self.current_player)
        self._has_turn_ended = False

    def game_over(self):
        self.game_ended = True

    def _end_turn(self):
        self.current_player.trigger("turn_ended")
        if self.current_player.hero.frozen_this_turn:
            self.current_player.hero.frozen_this_turn = False
        else:
            self.current_player.hero.frozen = False

        self.other_player.hero.frozen_this_turn = False
        for minion in self.other_player.minions:
            minion.frozen_this_turn = False

        for minion in self.current_player.minions:
            minion.active = False
            minion.exhausted = False
            minion.used_windfury = False
            if minion.frozen_this_turn:
                minion.frozen_this_turn = False
            else:
                minion.frozen = False

        for secret in self.other_player.secrets:
            secret.deactivate(self.other_player)

        self.check_delayed()
        self._has_turn_ended = True

    def copy(self):
        copied_game = copy.copy(self)
        copied_game.events = {}
        copied_game._all_cards_played = []
        copied_game.players = [player.copy(copied_game) for player in self.players]
        if self.current_player is self.players[0]:
            copied_game.current_player = copied_game.players[0]
            copied_game.other_player = copied_game.players[1]
        else:
            copied_game.current_player = copied_game.players[1]
            copied_game.other_player = copied_game.players[0]

        copied_game.current_player.opponent = copied_game.other_player
        copied_game.other_player.opponent = copied_game.current_player
        copied_game._has_turn_ended = self._has_turn_ended

        for player in copied_game.players:
            player.hero.attach(player.hero, player)
            if player.hero.weapon:
                player.hero.weapon.attach(player.hero, player)
            for minion in player.minions:
                minion.attach(minion, player)
                if minion.enraged:
                    minion._do_enrage()

        for secret in copied_game.other_player.secrets:
            secret.activate(copied_game.other_player)
        return copied_game

    def play_card(self, card):
        if self.game_ended:
            raise GameException("The game has ended")
        if not card.can_use(self.current_player, self):
            raise GameException("That card cannot be used")
        card_index = self.current_player.hand.index(card)
        self.current_player.hand.pop(card_index)
        self.current_player.mana -= card.mana_cost(self.current_player)
        self.current_player.trigger("card_played", card, card_index)
        self._all_cards_played.append(card)
        card.target = None
        if card.targetable and card.targets:
            card.target = self.current_player.agent.choose_target(card.targets)

        if card.is_spell():
            self.last_spell = card
            self.current_player.trigger("spell_cast", card)

        if not card.cancel:
            card.use(self.current_player, self)
            self.current_player.trigger("card_used", card)
            self.current_player.cards_played += 1
            self.check_delayed()

        # overload is applied regardless of counterspell, but after the card is played
        self.current_player.overload += card.overload

    def __to_json__(self):
        if self.current_player == self.players[0]:
            active_player = 1
        else:
            active_player = 2
        return {
            'players': self.players,
            'active_player': active_player,
            'current_sequence_id': self.minion_counter,
        }

    @staticmethod
    def __from_json__(d, agents):
        new_game = Game.__new__(Game)
        new_game._all_cards_played = []
        new_game.minion_counter = d["current_sequence_id"]
        new_game.delayed_minions = set()
        new_game.game_ended = False
        new_game.random_func = random.randint
        new_game.events = {}
        new_game.players = [Player.__from_json__(pd, new_game, None) for pd in d["players"]]
        new_game._has_turn_ended = False
        if d["active_player"] == 1:
            new_game.current_player = new_game.players[0]
            new_game.other_player = new_game.players[1]
            new_game.current_player.opponent = new_game.players[1]
            new_game.other_player.opponent = new_game.players[0]
        else:
            new_game.current_player = new_game.players[1]
            new_game.other_player = new_game.players[0]
            new_game.current_player.opponent = new_game.players[0]
            new_game.other_player.opponent = new_game.players[1]

        index = 0
        for player in new_game.players:
            player.agent = agents[index]
            for effect_json in d['players'][index]['effects']:
                player.add_effect(Effect.from_json(**effect_json))
            player.player_auras = []
            for aura_json in d['players'][index]['auras']:
                player.add_aura(AuraUntil.from_json(**aura_json))
            player.hero.attach(player.hero, player)
            if player.hero.weapon:
                player.hero.weapon.attach(player.hero, player)

            for minion in player.minions:
                minion.attach(minion, player)
                if minion.health != minion.calculate_max_health():
                    minion.enraged = True
                    minion._do_enrage()
            index += 1
        return new_game

__create_card_table()
