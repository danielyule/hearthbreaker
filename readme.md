Hearthbreaker
=============
A Hearthstone Simulator
-----------------------

Hearthbreaker is an open source Hearthstone simulator for the purposes of machine learning and
data mining of Blizzard's [Hearthstone: Heroes of WarCraft](http://battle.net/hearthstone).  It implements every 
card in the game.  Every attempts has been made to mimic Hearthstone precisely, including edge cases and bugs.
The results of playing simulated games can be used to determine cards which work well together and cards which do not.  
Hearthbreaker is not designed to allow player to play Hearthstone against each other, nor is it designed to play against
human opponents within Hearthstone itself.  It is designed to be used as a library for analysis.

 * Documentation (In Progress) [http://danielyule.github.io/hearthbreaker/](http://danielyule.github.io/hearthbreaker/)
 * Travis CI Build Status: [![Build Status](https://travis-ci.org/danielyule/hearthbreaker.svg?branch=master)](https://travis-ci.org/danielyule/hearthbreaker)
 * Coveralls Code Coverage: [![Coverage Status](https://coveralls.io/repos/danielyule/hearthbreaker/badge.png?branch=master)](https://coveralls.io/r/danielyule/hearthbreaker?branch=master)
 * Developer Mailing List: [Google Group](https://groups.google.com/forum/#!forum/hearthstone-simulator-dev)

Usage
-----

Hearthbreaker is compatible with [Python](https://www.python.org/) 3.2+ and [PyPy3](http://pypy.org/) 2.3+ on any
operating system that supports them.

### Console Application

![Console Screenshot](http://danielyule.github.io/hearthbreaker/_static/console_screenshot.png)

There is a basic console that you can use for playing against a bot.  There are two bots to choose from: a random bot
that plays completely randomly or a trading bot which tries to trade efficiently with your minions.

Start the console with ``python text_runner.py deck1.hsdeck deck2.hsdeck``.  The two deck files are
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

*Note:* Curses is not available for PyPy


### Unit Tests
The tests are located in the [`tests`](tests) package.

All tests can be run with the following command: `python -m unittest discover -s tests -p *_tests.py`

For Python 3.2 and PyPy3, the unit tests are dependent on the [mock package](https://pypi.python.org/pypi/mock).

Progress
--------

All collectible cards have been implemented.
The engine is complete, and can be used to simulate games.  The game state can be copied, or serialized to JSON.
Replay functionality is included as well.  Furthermore, minions and weapons can be expressed either in python or
via a JSON declaration.

For an overview of upcoming work, see [the wiki](https://github.com/danielyule/hearthbreaker/wiki/)

Structure
---------
Almost all of the game logic is found in [hearthbreaker.game_objects](hearthbreker/game_objects.py).  The game functions
largely on a tag based system.  See [the wiki](https://github.com/danielyule/hearthbreaker/wiki/Tag-Format) for more
details.

The game is made up of players, each of which has a hand of cards, a hero, secrets and minions.  Decisions are made
by agents, which can either by computer controlled or human controlled.  The system is callback based, in that
when it is time to make a decision, the game will request the decision from the agents, rather than the agents
dictating how the game is run.

The cards themselves are each a class, and can be found in the [hearthbreaker/cards](hearthbreaker/cards) directory, 
organized by type (spell/minion/secret/weapon) and by class.

The project defines a number of interesting formats, which are described 
[on the wiki](https://github.com/danielyule/hearthbreaker/wiki/Formats)

Contributing
------------

To contribute, simply fork the repository, make changes and submit a pull request.

All pull requests which implement new cards must also include a unit test for those cards.  In the case where the card
 has no side effects aside from playing the minion, tests should include another card's effects on it.

All pull requests will be automatically verified through 
[travis-ci.org](https://travis-ci.org/danielyule/hearthbreaker), and a coverage report generated through
 [coveralls.io](https://coveralls.io/r/danielyule/hearthbreaker)

New ideas, and upcoming features are described [on the wiki](https://github.com/danielyule/hearthbreaker/wiki/Roadmap).
Feel free to get involved with any or all of them.

Developers from this and other hearthstone simulation projectors can be found on IRC on freenode.net, channel #hearthsim.

For more specifics about contributing, see the 
[contributing page](http://danielyule.github.io/hearthbreaker/contributing.html), 
or join the [Developer Mailing List](https://groups.google.com/forum/#!forum/hearthstone-simulator-dev)

Related Projects
----------------

A collection of Hearthstone AI related projects can be found at [hs-ai.com](http://hs-ai.com)


### HearthSim
Hiroaki Oyaizu has created [HearthSim](https://github.com/oyachai/HearthSim), another Hearthstone simulator, written in Java
with a stronger focus on efficiency and AI modelling. It currently has fewer cards implemented, but has a much more
sophisticated AI.

### Focus
Raffy is working towards a Domain Specific Language (DSL) for Hearthstone Cards, written in JSON.  The cards are
completely defined, but the engine (called [Focus](http://fluiddruid.net/forum/viewtopic.php?f=24&t=4808)) is still in
progress.  These will allow for anyone to define new cards, by simply writing a JSON object to represent the card.

### Fireplace
Jerome Leclanche is attempting to reverse engineer the xml format for the cards associated with Hearthstone and build
an engine based on that.  It is planned to be a complete simulator, including all collectible and mission cards.
His work can be found on [Fireplace GitHub page](https://github.com/jleclanche/fireplace)

### Soot
[Soot](https://github.com/Mischanix/soot) is a slightly out of date Clojure implementation of all cards in Hearthstone.  It's not clear how well the 
implementations work.  It is interesting for its functional implementation of the cards.

### Hearthstone JSON

[Hearthstone JSON](http://hearthstonejson.com/) is a JSON file containing all cards in Hearthstone, extracted from the executable.  Hearthbreaker
uses this data to verify that its cards are implemented correctly

_Hearthstone: Heroes of WarCraft_ and _Blizzard_ are trademarks of Blizzard Entertainment.

