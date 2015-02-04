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

Contributions should follow the standard `GitHub workflow <https://guides.github.com/introduction/flow/index.html>`_:

 1. Fork the repository
 2. Clone from the forked repository
 3. Create a feature branch
 4. Make some changes
 5. As soon as you have completed anything (a card, a bug fix, a new feature, etc), submit a pull request
 6. Ensure the code is passing Travis CI's tests
 7. Make any changes requested in review
 8. Back to step 3

Adding new cards
````````````````
Every card added to the game is implemented as a subclass of :class:`Card <hearthbreaker.game_objects.Card>` (for spells) or its
subclasses :class:`MinionCard <hearthbreaker.game_objects.MinionCard>` (for minions),
:class:`SecretCard <hearthbreaker.game_objects.SecretCard>` (for secrets) or
:class:`WeaponCard <hearthbreaker.game_objects.WeaponCard>` (for Weapons).

Cards are organized first by type, then by class.  So, for example, ``Corruption`` would be found in
``hearthbreaker/cards/spells/warlock.py``, whereas ``EaglehornBow`` would be found in ``hearthbreaker/cards/weapons/hunter.py``.
All cards are imported by the ``__init__.py`` in their card type folder.  So, for example, ``GuardianOfKings`` is
imported in ``hearthbreaker/cards/minions/__init__.py``.  These are then imported by ``hearthbreaker/cards/__init__.py`` so that
simply writing ``from hearthbreaker.cards import *`` will import all cards and nothing else.

So, when implementing a new card, follow these steps:
 1. Write at least one test for the new card
 2. Create a new class in the appropriate folder, using CamelCase for the class name (removing spaces and apostrophes)
 3. Create a constructor for that class which calls the super's constructor with the needed attributes
 4. Add the method which performs the action of the card (:meth:`use <hearthbreaker.game_objects.Card.use>` for spells, :meth:`create_minion <hearthbreaker.game_objects.MinionCard.create_minion>` for minions, :meth:`create_weapon <hearthbreaker.game_objects.WeaponCard.create_weapon>` for
    weapons, and :meth:`activate <hearthbreaker.game_objects.SecretCard.activate>`, :meth:`deactivate <hearthbreaker.game_objects.SecretCard.deactivate>` and :meth:`_reveal <hearthbreaker.game_objects.SecretCard._reveal>` for secrets -- see the section for each type of card)
 5. Add an entry to the appropriate ``__init__.py``
 6. Run ``flake8`` in the project's root folder to ensure proper formatting.

Creating a Constructor
''''''''''''''''''''''
All cards must have a constructor that takes zero arguments.  This constructor must invoke the super instructor
with information about the card.  Details can be found in the documentation for
:meth:`Card.__init__ <hearthbreaker.game_objects.Card.__init__>`, but essentially the following properties must be set:

 - Card name in English
 - The card's basic mana cost
 - The character class associated with the card
 - The card's rarity
 - (optional) a function for finding targets for the card (e.g. only enemy minions).  This is typically taken from the targeting module
 - (optional) a function for filtering targets (e.g. minions with less than three attack).  This is typically a lambda function that takes a possible target as input and returns a boolean
 - (optional) The card's minion type, from the :class:`MINION_TYPE <hearthbreaker.constants.MINION_TYPE>` class (i.e. Beast, Mech, Totem, etc.)

For example, here is the implementation of Cabal Shadow Priest, with comments for clarity:

::

    class CabalShadowPriest(MinionCard):
        def __init__(self):
            super().__init__(
                             "Cabal Shadow Priest",                               # The name of the card in English
                             6,                                                   # The card's mana cost
                             CHARACTER_CLASS.PRIEST,                              # The card can only be included in a Priest deck
                             CARD_RARITY.EPIC,                                    # The card's rarity is epic (has a purple gem)
                             hearthbreaker.targeting.find_enemy_minion_battlecry_target, # The card targets enemy minions only
                             lambda target: target.attack_power <= 2)             # Among enemy minions, only those with 2 or less attack

        def create_minion(self, player):
            return Minion(4, 5, battlecry=take_control_of_minion)

Specific Instructions for Card Types
''''''''''''''''''''''''''''''''''''

Creating a new spell
....................
Spells are direct subclasses of :class:`hearthbreaker.game_objects.Card`.  In addition to creating a constructor, you must also
override the :meth:`use <hearthbreaker.game_objects.Card.use>` method.  This method takes two parameters, player and game.
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
                             hearthbreaker.targeting.find_spell_target  # This spell can target any character
                             )

        def use(self, player, game):
            super().use(player, game)                                   # Must call super().use() first
            self.target.damage(player.effective_spell_damage(2), self)  # calculate spell damage and damage
                                                                        # the target


Creating a new secret
.....................

Secrets are more complicated than normal spells, because they are activated on the enemy player's term and deactivated
on the player's turn.  As such they make heavy use of the game's
:class:`event binding system<hearthbreaker.game_objects.Bindable>`.  Secrets require three methods:

:meth:`activate <hearthbreaker.game_objects.SecretCard.activate>`
    Fires at the beginning of the enemy player's turn.  Should be used to bind any event listeners needed for the secret.

:meth:`deactivate <hearthbreaker.game_objects.SecretCard.deactivate>`
    Fires at the end of the enemy player's turn.  Should be used to unbind any event listeners that the secret set up in
    ``activate``.

:meth:`_reveal <hearthbreaker.game_objects.SecretCard._reveal>`
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

Minions are created through the :meth:`create_minion <hearthbreaker.game_objects.MinionCard.create_minion>` method of
:class:`MinionCard <hearthbreaker.game_objects.MinionCard>`.  This method should create the
:class:`Minion <hearthbreaker.game_objects.Minion>` object, state any effects and auras that are needed and return the created minion.

The Minion object only requires two parameters in its constructor: ``attack`` and ``health``, but can optionally include
the various minion attributes, such as taunt or stealth, as well as its battlecry or deathrattle if necessary.

If the battlecry requires targeting, then the function used for selecting targets should be included in the call
to ``super().__init__()``.  A Battlecry is a function with one parameter: minion, meaning the minion performing the battlecry.

For example, if we were creating a card for `Crazy Monkey <http://hearthstone.gamepedia.com/Crazy_Monkey>`_ we might
implement it as follows:

::

    class CrazyMonkey(MinionCard):
        def __init__(self):
            super().__init__("Crazy Monkey", 1, CHARACTER_CLASS.MUKLA, CARD_RARITY.COMMON)

        def create_minion(self, player):
            return Minion(                          # Create a new Minion
                          1,                        # The minion has 1 attack
                          2,                        # The minion has 2 health
                          battlecry=throw_bananas)  # The battlecry is to throw bananas. This
                                                    # assumes that throw_bananas is defined
                                                    #  in hearthbreaker/cards/battlecries.py



In ``hearthbreaker/cards/battlecries.py`` meanwhile, ``throw_bananas`` might be defined like

::

    def throw_bananas(minion):
        for banana in range(0, 2):                  # We need to give the other player two bananas
            (minion.player                          # Get the player associated with this minion
                 .game                              # Get the game the player is a part of
                 .other_player                      # other_player always refers to the non-active player
                 .hand                              # Player.hand is a list of cards
                 .append(Banana()))                 # Add a new instance of the banana card


When creating the minion, its behaviour can be determined by its tags: :class:`effects <hearthbreaker.tags.base.Effect>`,
:class:`auras <hearthbreaker.tags.base.Aura>`, enrage and :class:`deathrattle <hearthbreaker.tags.base.Deathrattle>`.
There is some documentation on these tags `on the wiki <https://github.com/danielyule/hearthbreaker/wiki/Tag-Format>`_,
but essentially, an aura is an object which causes an ongoing change to the board, while an effect is an action that is
triggered at by a certain event.  Deathrattle and enrage are clear.  Minion creation should all be handled in a single constructor call.

So, the implementation for Young Priestess looks like

::

    class YoungPriestess(MinionCard):
        def __init__(self):
            super().__init__("Young Priestess", 1, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

        def create_minion(self, player):
            return Minion(                       # Create a new Minion
                2,                               # The minion has 2 attack
                1,                               # The minion has 1 health
                effects=[                        # Could have multiple effects, so use an array
                    Effect(                      # Create a new Effect object to describe what happens
                        TurnEnded(),             # The first parameter is when the effect should happen
                        ChangeHealth(1),         # The second parameter is what should happen
                        RandomSelector(          # The final parameter specifies who it should happen to
                            MinionSelector()     # What should the random selector select from?
                            ))])

Creating a new weapon
.....................

Weapons are created in a similar manner to minions, although they use a
:meth:`create_weapon <hearthbreaker.game_objects.MinionCard.create_weapon>` method rather than a
:meth:`create_minion <hearthbreaker.game_objects.MinionCard.create_minion>` method.  Just like minions, weapons can have
battlecries and deathrattles, although their basic attributes are attack and durability rather than attack and health.

For example, implementing the `Warglaive of Azzinoth <http://hearthstone.gamepedia.com/Warglaive_of_Azzinoth>`_ might
look like this:

::

    class WarglaiveOfAzzinoth(WeaponCard):
        def __init__(self):
            super().__init__("Warglaive of Azzinoth", 2, CHARACTER_CLASS.STORMRAGE, CARD_RARITY.COMMON)

        def create_weapon(self, player):
            return Weapon(2, 2)

Unit Testing Techniques
'''''''''''''''''''''''
All unit tests are built using the `python unit test library <https://docs.python.org/3/library/unittest.html>`_.  There
must be at minimum one test for each card, or possibly more if the card is especially complex, or has finicky
interactions with other cards.

The basic attributes for each card (mana cost, rarity, health if it's a minion, etc) are tested automatically against
the data in `AllSets.enUs.json <https://github.com/danielyule/hearthstone-simulator/blob/master/AllSets.enUS.json>`_, so you do not need
to test these things yourself.

Each card unit tests consists of a game played with that card and some others.  The decks used in unit testing are not
constrained by the two copies of any card limitation, so any number can be used.

Most unit tests utilize the :meth:`generate_game_for <tests.testing_utils.generate_game_for>` method.  This method takes
four parameters, all of which are classes, rather than instances of those classes.  The first two are the cards used to
compose the decks of the two players.  If a list is passed into either parameter, then the cards in that list are
repeated until a deck of thirty is made up.  If only a single card is passed in then the entire deck is made up of
copies of that card.  The method will choose a character class based on the makeup of the cards passed in, or default to
Mage if none of the cards are class specific.

The second two parameters are the computerized agents to use for testing the cards.  There are five most commonly used
agents:

:class:`DoNothingAgent <hearthbreaker.agents.basic_agents.DoNothingAgent>`

    As its name implies, this bot does nothing.  It does not play a card, or use its hero power.  This bot is used if
    the enemy player doesn't need to do anything.

:class:`CardTestingAgent <tests.testing_agents.testing_agents.CardTestingAgent>`

    This agent will play as many cards on its turn as it has the mana for, in the order they are presented in the deck.
    This agent will not play cards out of sequence, so if there is an Oasis Snapjaw card on the top of the deck, no cards
    will be played until turn four, when the Snapjaw is, even if the player has other, lower cost cards in hand.
    For targeting this agents will select the first elements in the list of targets presented to it, which means an
    enemy minion if one is down, then a friendly minion if one is present, or if there are no minions, the enemy hero.
    There are variations on this agent, which will target specific groups, such as EnemySpellTestingAgent, which will
    only ever target an enemy.  Aside from playing cards, this minion will not do anything (such as attack or use the
    hero power)


:class:`OneCardPlayingAgent <tests.testing_agents.testing_agents.OneCardPlayingAgent>`

    This agent is very similar to `CardTestingAgent` except that it only plays one card per turn, unless that card is
    The Coin, in which case it will play the coin and whichever card comes after it, so long as it has the mana


:class:`PlayAndAttackAgent <tests.testing_agents.testing_agents.PlayAndAttackAgent>`

    This agent tries to do everything it can in a very particular order:

     1. Play as many cards as it has mana for, in the order they are in the deck.  Unlike `CardTestingAgent`, this agent
     will look for any playable cards in the hand, rather than only the first.
     2. Attack with any active minions.


:class:`PredictableAgent <tests.agents.basic_agents.PredictableAgent>`

    PredictableAgent extends `PlayAndAttackAgent` with the ability to use the hero's power.  So it will:

     1. Use the hero ability
     2. Play as many cards as it has mana for, in the order they are in the deck.
     3. Attack with the hero if possible (The targeting works similar to spell testing agent above)
     4. Attack with any active minions.

With this in mind, let's create a unit test for `Hogger SMASH <http://hearthstone.gamepedia.com/Hogger_SMASH!>`_.  This
card is a spell that does four damage to its target.

::

    def test_HoggerSmash(self):
        game = generate_game_for(                         # We use generate_game_for to create a test game
                                 HoggerSmash,             # The first player will have 30 Hogger SMASH!es
                                 MogushanWarden,          # The second player will have 30 Wardens
                                 CardTestingAgent,        # The first player will try to play SMASH!
                                 DoNothingAgent)          # The second player needs only get hit with the smash
        for turn in range(0, 4):                          # Advance the game to the turn before smash is played
            game.play_single_turn()
        self.assertEqual(30, game.players[1].hero.health) # Ensure the second player's health hasn't been affected
        game.play_single_turn()                           # Play Hogger Smash
        self.assertEqual(26, game.players[1].hero.health) # Make sure it did the damage it should have
