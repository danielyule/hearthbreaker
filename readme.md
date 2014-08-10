Hearthbreaker
=============
A Hearthstone Simulator
-----------------------

Hearthbreaker is an open source Hearthstone simulator for the purposes of machine learning and
data mining of Blizzard's [Hearthstone: Heroes of WarCraft](http://battle.net/hearthstone).  It implements every 
collectible card in the game.  Every attempts has been made to mimic Hearthstone precisely, including edge cases and bugs
The results of playing simulated games can be used to determine cards which work well together and cards which do not.  
Hearthbreaker is not designed to allow player to play Hearthstone against each other, nor is it designed to play against
human opponents within Hearthstone itself.

 * Documentation (In Progress) [http://danielyule.github.io/hearthbreaker/](http://danielyule.github.io/hearthbreaker/)
 * Travis CI Build Status: [![Build Status](https://travis-ci.org/danielyule/hearthbreaker.svg?branch=master)](https://travis-ci.org/danielyule/hearthbreaker)
 * Coveralls Code Coverage: [![Coverage Status](https://coveralls.io/repos/danielyule/hearthbreaker/badge.png?branch=master)](https://coveralls.io/r/danielyule/hearthbreaker?branch=master)
 * Developer Mailing List: [Google Group](https://groups.google.com/forum/#!forum/hearthstone-simulator-dev)

Usage
-----

Hearthbreaker is compatible with [Python](https://www.python.org/) 3.2+ and [PyPy3](http://pypy.org/) 2.3+

###Console Application
There is a basic console that you can use for playing against a bot.  The bot you are playing against chooses its moves
at random.

Start the console with ``python hearthbreaker/ui/text_runner.py deck1.hsdeck deck2.hsdeck``.  The two deck files are
in cockatrice format, with a card name in English on each line, preceded by a number to specify how many.  For example:

    2 Goldshire Footman
    2 Murloc Raider
    2 Bloodfen Raptor
    2 Frostwolf Grunt
    2 River Crocolisk
    2 Ironfur Grizzly
    2 Magma Rager
    2 Silverback Patriarch
    2 Chillwind Yeti
    2 Oasis Snapjaw
    2 Sen'jin Shieldmasta
    2 Booty Bay Bodyguard
    2 Fen Creeper
    2 Boulderfist Ogre
    2 War Golem
    
The character class is inferred from the cards present, or defaults to mage.

The console application requires ncurses, which should be included with python on *nix and mac systems, but if you are 
on windows, you must download it from 
[http://www.lfd.uci.edu/~gohlke/pythonlibs/#curses](http://www.lfd.uci.edu/~gohlke/pythonlibs/#curses)


###Unit Tests
The tests are located in the [`tests`](tests) package.

All tests can be run with the following command: `python -m unittest discover -s tests -p *_tests.py`

For Python 3.2 and PyPy3, the unit tests are dependent on the [mock package](https://pypi.python.org/pypi/mock).

Progress
--------

All cards currently released by Blizzard are implemented.  Curse of Naxxramas cards will be implemented as they are
released.  The engine is complete, and nearly ready for use in machine learning.  See the 
[developer mailing list](https://groups.google.com/forum/#!forum/hearthstone-simulator-dev)
for more details.

Structure
---------
Almost all of the game logic is found in [hearthbreaker.game_objects](hearthbreker/game_objects.py).  The game functions
largely on an event based system. The events use a bind/trigger mechanism.  For an overview of the events and the 
parameters they  receive, see [events.md](events.md).

The game is made up of players, each of which has a hand of cards, a hero, secrets and minions.  Decisions are made
by agents, which can either by computer controlled or human controlled.  The system is callback based, in that
when it is time to make a decision, the game will request the decision from the agents, rather than the agents
dictating how the game is run.

The cards themselves are each a class, and can be found in the [hearthbreaker/cards](hearthbreaker/cards) directory, 
organized by type (spell/minion/secret/weapon) and by class.

This project also includes a replay facility, which allows for games to be recorded and played back.  The format for
the replay syntax is documented in [replay_format.md](replay_format.md).

Contributing
------------

To contribute, simply fork the repository, make changes and submit a pull request.

All pull requests which implement new cards must also include a unit test for those cards.  In the case where the card
 has no side effects aside from playing the minion, tests should include another card's effects on it.

All pull requests will be automatically verified through 
[travis-ci.org](https://travis-ci.org/danielyule/hearthbreaker), and a coverage report generated through
 [coveralls.io](https://coveralls.io/r/danielyule/hearthbreaker)

For more specifics about contributing, see the 
[contributing page](http://danielyule.github.io/hearthbreaker/contributing.html), 
or join the [Developer Mailing List](https://groups.google.com/forum/#!forum/hearthstone-simulator-dev)

Related Projects
----------------

###HearthSim
Hiroaki Oyaizu has created [HearthSim](https://github.com/oyachai/HearthSim), another Hearthstone simulator, written in Java
with a stronger focus on efficiency and AI modelling. It currently has fewer cards implemented, but has a much more
sophisticated AI.

###Focus
Raffy is working towards a Domain Specific Language (DSL) for Hearthstone Cards, written in JSON.  The cards are
completely defined, but the engine (called [Focus](http://fluiddruid.net/forum/viewtopic.php?f=24&t=4808)) is still in
progress.  These will allow for anyone to define new cards, by simply writing a JSON object to represent the card.

_Hearthstone: Heroes of WarCraft_ and _Blizzard_ are trademarks of Blizzard Entertainment.
