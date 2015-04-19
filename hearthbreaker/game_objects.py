import abc
import copy
from functools import reduce
import hearthbreaker.constants

from hearthbreaker.tags.base import Aura, AuraUntil, Effect, Buff, BuffUntil, Deathrattle
from hearthbreaker.tags.event import TurnEnded
from hearthbreaker.tags.selector import CurrentPlayer
from hearthbreaker.tags.status import Stealth, ChangeAttack, ChangeHealth, SetAttack, Charge, Taunt, DivineShield, \
    Windfury, NoSpellTarget, SpellDamage, MinimumHealth
import hearthbreaker.targeting


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
        self._attached = False

    def attach(self, obj, player):
        if not self._attached:
            self.player = player
            for effect in self.effects:
                effect.set_owner(obj)
                effect.apply()
            for buff in self.buffs:
                buff.set_owner(obj)
                buff.apply()
            for aura in self.auras:
                aura.set_owner(obj)
                player.add_aura(aura)
            self._attached = True

    def calculate_stat(self, stat_class, starting_value=0):
        """
        Calculates the amount of a particular stat this :class:`GameObject` has at current time.
        """

        # Add together all the attack amounts from buffs
        stat = reduce(lambda a, b: b.update(self, a), [buff.status for buff in self.buffs
                                                       if isinstance(buff.status, stat_class) and
                                                       (not buff.condition or buff.condition.evaluate(self, self))],
                      starting_value)
        stat = reduce(lambda a, b: b.update(self, a), [aura.status
                                                       for player in self.player.game.players
                                                       for aura in player.object_auras
                                                       if aura.match(self) and isinstance(aura.status, stat_class)],
                      stat)

        return max(0, stat)

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

    def is_valid(self):
        """
        Checks if this object is a valid target for actions and statuses
        """
        return True

    def is_character(self):
        """
        Checks if this object is a character (minion or hero)
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
        for an_aura in self.auras:
            if an_aura.eq(aura):
                self.auras.remove(an_aura)
                break
        self.player.remove_aura(aura)

    def add_buff(self, buff):
        if not isinstance(buff, Buff):
            raise TypeError("Expected a buff to be added")
        self.buffs.append(buff)
        buff.set_owner(self)
        buff.apply()

    def remove_buff(self, buff):
        for a_buff in self.buffs:
            if a_buff.eq(buff):
                self.buffs.remove(a_buff)
                break
        buff.unapply()

    def unattach(self):
        if self._attached:
            for effect in reversed(self.effects):
                effect.unapply()
            self.effects = []
            for aura in reversed(self.auras):
                self.player.remove_aura(aura)
            self.auras = []
            for buff in reversed(self.buffs):
                buff.unapply()
            self.buffs = []
            self._attached = False


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
        #: How many attacks this character has performed this turn
        self.attacks_performed = 0
        #: Whether or not this character has died
        self.dead = False
        #: If this character has windfury
        self.used_windfury = False
        #: If this character is currently frozen
        self.frozen = 0
        #: The :class:`Player` that owns this character
        self.player = None
        #: Whether or not this character is immune to damage (but not other tags)
        self.immune = 0
        #: The list of delayed events
        self.delayed = []
        #: Non zero if this character has stealth
        self.stealth = 0
        #: Non zero if this character has divine shield
        self.divine_shield = 0
        #: If this character is enraged
        self.enraged = False
        #: If this character has been removed from the board
        self.removed = False
        #: An integer describing when this character was created.  The lower, the earlier it was created
        self.born = -1
        #: An integer describing how much the health of this character has been adjusted
        self.health_delta = 0
        #: A list of actions that describe what will happen when this character is enraged
        self.enrage = enrage if enrage else []
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
        self.player.trigger("character_attack", self, self.current_target)
        self.trigger("attack", self.current_target)
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
        self.attacks_performed += 1
        self.stealth = False
        self.current_target = None

    def choose_target(self, targets):
        """
        Consults the associated player to select a target from a list of targets

        :param list[Character] targets: the targets to choose a target from
        """
        return self.player.choose_target(targets)

    def calculate_stat(self, stat_class, starting_value=0):
        """
        Calculates the amount of attack this :class:`Character` has, including the base attack, any temporary attack
        bonuses for this turn
        """
        stat = starting_value

        return super().calculate_stat(stat_class, stat)

    def calculate_attack(self):
        """
        Calculates the amount of attack this :class:`Character` has, including the base attack, any temporary attack
        bonuses for this turn
        """
        return self.calculate_stat(ChangeAttack, self.base_attack)

    def calculate_max_health(self):
        """
        Calculates the maximum amount of health this :class:`Character` has, including the base health, and any aura
        tags
        """
        return self.base_health + self.health_delta

    def attacks_allowed(self):
        """
        Checks the number of attacks this character can make per turn.
        """
        return self.calculate_stat(Windfury, 1)

    def windfury(self):
        """
        Checks if this character has windfury attached
        """
        return self.calculate_stat(Windfury, 1) > 1

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
            # This is constructed to avoid infinite recursion when mistress of pain and auchenai soulpriest
            # are in use.  This will prevent the did_damage event from going off if the character being damaged is
            # already dead.
            # We could simply do the check for death before this, but then the Mistress of Pain can't bring a dead
            # hero back to life after damaging it via misdirection.
            if attacker and attacker.is_character() and self.health >= 0:
                self.health -= amount
                attacker.trigger("did_damage", self, amount)
                attacker._remove_stealth()
            else:
                self.health -= amount
            min_health = self.calculate_stat(MinimumHealth, 0)
            if self.health < min_health:
                self.health = min_health
            self.trigger("damaged", amount, attacker)
            self.player.trigger("character_damaged", self, attacker, amount)
            if self.health <= 0:
                self.die(attacker)
            self.trigger("health_changed")
            if not self.enraged and self.health != self.calculate_max_health():
                self.enraged = True
                self.trigger("enraged")
                self._do_enrage()

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
        self.buffs.append(Buff(SetAttack(new_attack)))

    def set_health_to(self, new_health):
        """
        Sets the amount of total health this :class:`Character` has.  This will adjust its actual health if necessary
        :param new_health: An integer specifying what this character's new health should be
        """
        was_enraged = self.health < self.calculate_max_health()
        diff = new_health - (self.base_health + self.health_delta)

        for player in self.game.players:
            for aura in player.object_auras:
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
        return self.calculate_attack() > 0 and self.attacks_performed < self.attacks_allowed() and \
            not self.frozen and not (self.dead or self.removed)

    def spell_targetable(self):
        """
        Checks if a :class:`Character` can be targeted by a spell.  Minions with stealth or whose text say they can't be
        targeted by spells cannot be targeted, but any other character can.
        """
        return True

    def is_valid(self):
        return not self.dead and not self.removed

    def is_character(self):
        return True

    def _do_enrage(self):
        for aura in self.enrage:
            self.add_aura(aura)

    def _do_unenrage(self):
        for aura in self.enrage:
            self.remove_aura(aura)


class Weapon(Bindable, GameObject):
    """
    Represents a Hearthstone weapon.  All weapons have attack power and durability.  The logic for handling the
    attacks is handled by :class:`Hero`, but it can be modified through the use of events.
    """

    def __init__(self, attack_power, durability, deathrattle=None,
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
        #: Called when the weapon is destroyed
        self.deathrattle = deathrattle
        #: The :class:`Player` associated with this weapon
        self.player = None
        #: The :class:`WeaponCard` that created this weapon
        self.card = None

    def copy(self, new_owner):
        new_weapon = Weapon(self.base_attack, self.durability, copy.deepcopy(self.deathrattle),
                            copy.deepcopy(self.effects), copy.deepcopy(self.auras), copy.deepcopy(self.buffs))
        new_weapon.player = new_owner
        return new_weapon

    def destroy(self):
        self.trigger("destroyed")
        # Deathrattle is triggered no matter how the weapon is destroyed, see
        # http://www.hearthhead.com/card=1805/deaths-bite#comments:id=1983510
        if self.deathrattle is not None:
            self.deathrattle.do(self.player.hero)
        self.player.hero.weapon = None
        self.player.hero.trigger("weapon_destroyed")
        self.unattach()

    def equip(self, player):
        self.player = player
        if self.player.hero.weapon is not None:
            self.player.hero.weapon.destroy()
        self.player.hero.weapon = self
        self.attach(self, player)
        self.player.hero.trigger("weapon_equipped")

    def calculate_attack(self):
        """
        Calculates the amount of attack this :class:`Wea[on` has, including the base attack, any temporary attack
        bonuses for this turn
        """
        return self.calculate_stat(ChangeAttack, self.base_attack)

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
        from hearthbreaker.engine import card_lookup
        weapon_card = card_lookup(wd['name'])
        weapon = weapon_card.create_weapon(player)
        weapon.base_attack = wd['attack']
        weapon.durability = wd['durability']
        weapon.card = weapon_card
        GameObject.__from_json__(weapon, **wd)
        return weapon


class Minion(Character):
    def __init__(self, attack, health,
                 deathrattle=None, taunt=False, charge=False, spell_damage=0, divine_shield=False, stealth=False,
                 windfury=False, spell_targetable=True, effects=None, auras=None, buffs=None,
                 enrage=None):
        super().__init__(attack, health, enrage, effects, auras, buffs)
        self.game = None
        self.card = None
        self.index = -1
        self.taunt = 0
        self.replaced_by = None
        self.can_be_targeted_by_spells = True
        if deathrattle:
            if isinstance(deathrattle, Deathrattle):
                self.deathrattle = [deathrattle]
            else:
                self.deathrattle = deathrattle
        else:
            self.deathrattle = []
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
            for aura in player.object_auras:
                aura_affects[aura] = set()
                for minion in self.player.minions:
                    if aura.match(minion):
                        aura_affects[aura].add(minion)
        self.game.minion_counter += 1
        self.player.minions.insert(index, self)
        self.born = self.game.minion_counter
        for minion in self.player.minions[index + 1:]:
            minion.index += 1
        self.index = index
        self.health += self.calculate_max_health() - self.base_health - self.health_delta
        self.attach(self, self.player)
        for player in self.game.players:
            for aura in player.object_auras:
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
        return super().calculate_attack()

    def calculate_max_health(self):
        """
        Calculates the maximum amount of health this :class:`Character` has, including the base health, and any aura
        tags
        """

        return super().calculate_max_health()

    def charge(self):
        return self.calculate_stat(Charge, False)

    def remove_from_board(self):
        if not self.removed:
            aura_affects = {}
            for aura in self.player.object_auras:
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
            for aura in self.player.object_auras:
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
        new_minion.exhausted = True
        self.game.minion_counter += 1
        new_minion.born = self.game.minion_counter
        if self.index >= len(self.player.minions):
            raise ValueError("Attempting to replace minion with invalid index")
        self.player.minions[self.index] = new_minion
        new_minion.attach(new_minion, self.player)
        for aura in self.player.object_auras:
            if aura.match(new_minion):
                aura.status.act(self, new_minion)
        new_minion.health += new_minion.calculate_max_health() - new_minion.base_health
        self.removed = True
        self.replaced_by = new_minion

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
                self.remove_from_board()
                self.unattach()
                if deathrattle is not None:
                    for rattle in deathrattle:
                        rattle.do(self)

                        if self.player.double_deathrattle:
                            rattle.do(self)
                self.player.trigger("minion_died", self, by)
                # Used to activate any secrets applied during the death phase
                self.player.trigger("after_death", self.player)

                self.player.graveyard.append(self.card.name)
            self.bind_once("died", delayed_death)
            super().die(by)
            self.player.dead_this_turn.append(self)

    def silence(self):
        super().silence()
        self.battlecry = None
        self.deathrattle = []

    def can_attack(self):
        return (self.charge() or not self.exhausted) and super().can_attack()

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
        new_minion = Minion(self.base_attack, self.base_health,
                            effects=copy.deepcopy(self.effects),
                            auras=copy.deepcopy(self.auras),
                            buffs=copy.deepcopy(self.buffs),
                            deathrattle=copy.deepcopy(self.deathrattle),
                            enrage=copy.deepcopy(self.enrage))
        new_minion.health = self.base_health - (self.calculate_max_health() - self.health)
        new_minion.enraged = self.enraged
        new_minion.immune = self.immune
        new_minion.index = self.index
        new_minion.attacks_performed = self.attacks_performed
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
        from hearthbreaker.engine import card_lookup
        minion = Minion(md['attack'], md['max_health'])
        GameObject.__from_json__(minion, **md)
        minion.health = md['max_health'] - md['damage']
        minion.exhausted = md['exhausted']
        minion.attacks_performed = not md['attacks_performed']
        minion.born = md['sequence_id']
        if 'enrage' in md:
            minion.enrage = [Aura.from_json(**enrage) for enrage in md['enrage']]
        minion.deathrattle = []
        for rattle in md['deathrattles']:
            minion.deathrattle.append(Deathrattle.from_json(**rattle))
        minion.card = card_lookup(md["name"])
        minion.game = game
        minion.player = player
        return minion

    def bounce(self, bounce_to_deck=False):
        if bounce_to_deck:
            self.unattach()
            self.remove_from_board()
            self.player.deck.put_back(self.card)
        else:
            if len(self.player.hand) < 10:
                self.unattach()
                self.remove_from_board()
                self.card.attach(self.card, self.player)
                self.player.hand.append(self.card)
            else:
                self.die(None)
                self.game.check_delayed()

    def __to_json__(self):

        r_val = super().__to_json__()
        r_val.update({
            'name': self.card.name,
            'sequence_id': self.born,
            'position': self.index,
            'damage': self.calculate_max_health() - self.health,
            'max_health': self.base_health,
            'attack': self.base_attack,
            "exhausted": self.exhausted,
            "attacks_performed": not self.attacks_performed,
            'deathrattles': self.deathrattle,
        })
        if self.enrage:
            r_val['enrage'] = self.enrage
        return r_val


class Hero(Character):
    def __init__(self, health, character_class, power, player):
        super().__init__(0, health)
        self.armor = 0
        self.weapon = None
        self.character_class = character_class
        self.player = player
        self.game = player.game
        self.power = power
        self.power.hero = self
        self.card = None
        self.power_targets_minions = False

    def calculate_attack(self):
        if self.player == self.player.game.current_player and self.weapon:
            base = self.base_attack + self.weapon.base_attack
        else:
            base = self.base_attack
        return self.calculate_stat(ChangeAttack, base)

    def calculate_stat(self, stat_class, starting_value=0):
        if self.player == self.player.game.current_player and self.weapon:
            starting_value = self.weapon.calculate_stat(stat_class, starting_value)

        return super().calculate_stat(stat_class, starting_value)

    def copy(self, new_owner):
        new_hero = Hero(self.base_health, self.character_class, self.power, new_owner)
        if self.weapon:
            new_hero.weapon = self.weapon.copy(new_owner)
        new_hero.health = self.health
        new_hero.armor = self.armor
        new_hero.used_windfury = False
        new_hero.attacks_performed = self.attacks_performed

        new_hero.effects = copy.deepcopy(self.effects)
        new_hero.auras = copy.deepcopy(self.auras)
        new_hero.buffs = copy.deepcopy(self.buffs)
        new_hero.card = type(self.card)()

        return new_hero

    def attack(self):
        super().attack()
        if self.weapon is not None:
            self.weapon.durability -= 1
            if self.weapon.durability == 0 or self.weapon.calculate_stat(ChangeAttack, self.weapon.base_attack) == 0:
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

    def replace(self, new_hero):
        """
        Replaces this hero with another one

        :param hearthbreaker.game_objects.Hero new_hero: The hero to replace this hero with
        """
        self.unattach()
        new_hero.player = self.player
        new_hero.game = self.game
        new_hero.exhausted = False
        self.game.minion_counter += 1
        new_hero.born = self.game.minion_counter

        self.player.hero = new_hero
        new_hero.power.hero = new_hero
        new_hero.attach(new_hero, self.player)
        for aura in self.player.object_auras:
            if aura.match(new_hero):
                aura.status.act(self, new_hero)

    @staticmethod
    def is_hero():
        return True

    def __to_json__(self):

        r_val = super().__to_json__()
        r_val.update({
            'character': hearthbreaker.constants.CHARACTER_CLASS.to_str(self.character_class),
            'weapon': self.weapon,
            'health': self.health,
            'armor': self.armor,
            'name': self.card.short_name,
            'attack': self.base_attack,
            'immune': self.immune,
            'used_windfury': self.used_windfury,
            'attacks_performed': self.attacks_performed,
        })
        return r_val

    @classmethod
    def __from_json__(cls, hd, player):
        hero = player.deck.hero.create_hero(player)
        hero.card = player.deck.hero
        GameObject.__from_json__(hero, **hd)
        hero.health = hd["health"]
        hero.base_attack = hd["attack"]
        hero.armor = hd["armor"]
        hero.immune = hd["immune"]
        hero.used_windfury = hd["used_windfury"]
        hero.attacks_performed = not hd["attacks_performed"]
        if hd['weapon']:
            hero.weapon = Weapon.__from_json__(hd["weapon"], player)
        return hero
