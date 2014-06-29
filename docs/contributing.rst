============
Contributing
============

This document is designed as a quick start guide to get new contributors up and running as fast as possible.
Everything in this document can be gleaned from reading other card's implementations, but is collected here for
ease of reference.

Currently, the most straightforward way to contribute is to implement cards that have not yet been implemented, although
any contributions at all are welcome.  Other options include finding and filing issues, joining the
`developer mailing list <https://groups.google.com/forum/#!forum/hearthstone-simulator-dev>`_  and adding your voice to
the discussions or helping test edge cases or researching others' work in finding strange applications of Hearthstone's
logic.

All code should conform to the style dictated by `Python's PEP8 Style Guide <http://legacy.python.org/dev/peps/pep-0008/>`_
The only exception is that unit tests for cards are named ``test_CardName`` where ``CardName`` is the name of the class.
This is to match the CamelCase convention for card names, but it contradicts the convention for method names to be
written in lowercase with underscores separating the words.  PEP8 Validation can be done by the
`flake8 tool <https://pypi.python.org/pypi/flake8>`_.  It can be installed with

::

    pip install flake8

It can then be run on the whole project by running the following command in the root directory.

::

    flake8 .

Any new code should be accompanied with a unit test which runs through the new code at least once.  All tests can be invoked with

::

    python -m unittest discover -s tests -p *_tests.py

Adding new cards
````````````````
Every card added to the game is implemented as a subclass of :class:`Card <hsgame.game_objects.Card>` (for spells) or its
subclasses :class:`MinionCard <hsgame.game_objects.MinionCard>` (for minions),
:class:`SecretCard <hsgame.game_objects.SecretCard>` (for secrets) or
:class:`WeaponCard <hsgame.game_objects.WeaponCard>` (for Weapons).

Cards are organized first by type, then by class.  So, for example, ``Corruption`` would be found in
``hsgame/cards/spells/warlock.py``, whereas ``EaglehornBow`` would be found in ``hsgame/cards/weapons/hunter.py``.
All cards are imported by the ``__init__.py`` in their card type folder.  So, for example, ``GuardianOfKings`` is
imported in ``hsgame/cards/minions/__init__.py``.  These are then imported by ``hsgame/cards/__init__.py`` so that
simply writing ``from hsgame.cards import *`` will import all cards and nothing else.

So, when implementing a new card, follow these steps:
 1. Create a new class in the appropriate folder, using CamelCase for the class name (removing spaces and apostrophes)
 2. Create a constructor for that class which calls the super's constructor with the needed attributes
 3. Add the method which performs the action of the card (:meth:`use <hsgame.game_objects.Card.use>` for spells, :meth:`create_minion <hsgame.game_objects.MinionCard.create_minion>` for minions, :meth:`create_weapon <hsgame.game_objects.WeaponCard.create_weapon>` for
    weapons, and :meth:`activate <hsgame.game_objects.SecretCard.activate>`, :meth:`deactivate <hsgame.game_objects.SecretCard.deactivate>` and :meth:`_reveal <hsgame.game_objects.SecretCard._reveal>` for secrets -- see the section for each type of card)
 4. Add an entry to the appropriate ``__init__.py``
 5. Change the card's entry in ``cards.csv`` to 'yes' in the first column
 6. Write at least one test for the new card

Creating a Constructor
''''''''''''''''''''''
All cards must have a constructor that takes zero arguments.  This constructor must invoke the super instructor
with information about the card.  Details can be found in the documentation for
:meth:`Card.__init__ <hsgame.game_objects.Card.__init__>`, but essentially the following properties must be set:

 - Card name in English
 - The card's basic mana cost
 - The character class associated with the card
 - The card's rarity
 - (optional) a function for finding targets for the card (e.g. only enemy minions).  This is typically taken from the
    targeting module
 - (optional) a function for filtering targets (e.g. minions with less than three attack).  This is typically a lambda
    function that takes a possible target as input and returns a boolean

For example, here is the implementation of Cabal Shadow Priest, with comments for clarity:

::

    class CabalShadowPriest(MinionCard):
        def __init__(self):
            super().__init__(
                             "Cabal Shadow Priest",                               # The name of the card in English
                             6,                                                   # The card's mana cost
                             CHARACTER_CLASS.PRIEST,                              # The card can only be included in a Priest deck
                             CARD_RARITY.EPIC,                                    # The card's rarity is epic (has a purple gem)
                             hsgame.targeting.find_enemy_minion_battlecry_target, # The card targets enemy minions only
                             lambda target: target.attack_power <= 2)             # Among enemy minions, only those with attack less than 2

        def create_minion(self, player):
            return Minion(4, 5, battlecry=take_control_of_minion)

Specific Instructions for Card Types
''''''''''''''''''''''''''''''''''''

Creating a new spell
....................
Spells are direct subclasses of :class:`hsgame.game_objects.Card`.  In addition to creating a constructor, you must also
override the :meth:`use <hsgame.game_objects.Card.use>` method.  This method takes two parameters, player and game.
The player is the player who played the card, and game is the game that the card was played in.  It is essential that
implementations include a call to super. This call reduces the players mana by the cost of the card, and uses the
targeting function to generate a list of targets.  This list of available as ``self.target``.  For example when
implementing `Barrel Toss <http://hearthstone.gamepedia.com/Barrel_Toss>`_ the code would look as follows:

::

    class BarrelToss(Card):
        def __init__(self):
            super().__init__("Barrel Toss",                             # The card's name in English
                             1,                                         # The card's mana cost
                             CHARACTER_CLASS.MUKLA,                     # Which character can use this card
                             CARD_RARITY.COMMON,                        # How rare the card is
                             hsgame.targeting.find_spell_target         # This spell can target any character
                             )

        def use(self, player, game):
            super().use(player, game)                                   # Must call super().use() first
            self.target.damage(player.effective_spell_damage(2), self)  # calculate spell damage and damage
                                                                        # the target


Creating a new secret
.....................

Secrets are more complicated than normal spells, because they are activated on the enemy player's term and deactivated
on the player's turn.  As such they make heavy use of the game's
:class:`event binding system<hsgame.game_objects.Bindable>`.  Secrets require three methods:

:meth:`activate <hsgame.game_objects.SecretCard.activate>`
    Fires at the beginning of the enemy player's turn.  Should be used to bind any event listeners needed for the secret.

:meth:`deactivate <hsgame.game_objects.SecretCard.deactivate>`
    Fires at the end of the enemy player's turn.  Should be used to unbind any event listeners that the secret set up in
    ``activate``.

:meth:`_reveal <hsgame.game_objects.SecretCard._reveal>`
    Should be called by the event listeners set up in ``activate``.  This method does whatever the action of the secret
    is.  Make sure to call super().reveal (no underscore) somewhere in the body of this method.

For example, suppose we were going to implement a Warlock secret which did one damage to all characters when a spell is
played.

::

    class UnstableMagicks(SecretCard):
        def __init__(self):
            super().__init__("Unstable Magicks", 3, CHARACTER_CLASS.WARLOCK, CARD_RARITY.LEGENDARY)

        def activate(self, player):
            player.bind_once("spell_cast", self._reveal)              # We shall want to perform the action
                                                                      # of the secret when a spell is played

        def deactivate(self, player):
            player.unbind("spell_cast", self._reveal)                 # On our own turn, we don't want the secret
                                                                      # to activate

        def _reveal(self, attacker):                                  # This method will be called when the
            targets = game.other_player.minions.copy()                # secret is revealed.  But only because
            targets.extend(game.current_player.minions)               # it's set up that way in activate()
            targets.append(game.other_player.hero)                    # _reveal() will not be called unless it's
            targets.append(game.current_player.hero)                  # bound in activate.
            for target in targets:
                target.damage(1, None)

            super().reveal()                                          # Always be sure to call super().reveal()


Creating a new minion
.....................

Creating a new weapon
.....................


Unit Testing Techniques
'''''''''''''''''''''''
