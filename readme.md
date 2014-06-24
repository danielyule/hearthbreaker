Hearthstone Simulator
=====================

The purpose of this project is to create an open source Hearthstone simulator for the purposes of machine learning and
data mining of Blizzard's [Hearthstone: Heroes of WarCraft](http://battle.net/hearthstone).  The end goal
is to create a system implementing every card in Hearthstone, then simulate games of bots against bots to train
them.  The results from these games can be used to determine cards which work well together and cards which do not.
The goal is not to create a clone of Hearthstone which players can use to replace the game itself with.

 * Documentation (In Progress) [http://danielyule.github.io/hearthstone-simulator/](http://danielyule.github.io/hearthstone-simulator/)
 * Travis CI Build Status: [![Build Status](https://travis-ci.org/danielyule/hearthstone-simulator.svg?branch=master)](https://travis-ci.org/danielyule/hearthstone-simulator)
 * Coveralls Code Coverage: [![Coverage Status](https://coveralls.io/repos/danielyule/hearthstone-simulator/badge.png?branch=master)](https://coveralls.io/r/danielyule/hearthstone-simulator?branch=master)
 * Developer Mailing List: [Google Group](https://groups.google.com/forum/#!forum/hearthstone-simulator-dev)

Usage
-----
The only way to use the system currently is through unit tests.  The tests are located in the [`tests`](tests) package.

All tests can be run with the following command: `python -m unittest discover -s tests -p *_tests.py`

The Hearthstone Simulator is compatible with Python 3.3+

Progress
--------

Currently, the main engine is mostly implemented, along with a few cards.  [cards.csv](cards.csv) is a listing of all cards in the
game along with information on which has been implemented.  Any card which has been implemented also has at least one
unit test to ensure that it works correctly

Structure
---------
Almost all of the game logic is found in [hsgame.game_objects](hsgame/game_objects.py).  The game functions largely on an event based system.
The events use a bind/trigger mechanism.  For example, a card which has a deathrattle will bind an event to its 'death'
event that takes the appropriate action.  Parameters can be passed to an event at the time it is bound, or the time it
is triggered, or both.  For an overview of the events and the parameters they receive, see [events.md](events.md).

The cards themselves are each a class, and can be found in the [hsgame/cards](hsgame/cards) directory, organized by type
(spell/minion/secret/weapon) and by class.  To see which cards have been implemented, simply search for "yes".

This project also includes a replay facility, which allows for games to be recorded and played back.  The format for
the replay syntax is documented in [replay_format.md](replay_format.md).

Contributing
------------

To contribute, simply fork the repository, make changes and submit a pull request.

All pull requests which implement new cards must also include a unit test for those cards.  In the case where the card
 has no side effects aside from playing the minion, tests should include another card's effects on it.

All pull requests will be automatically verified through [travis-ci.org](https://travis-ci.org/danielyule/hearthstone-simulator), and a coverage report generated through [coveralls.io](https://coveralls.io/r/danielyule/hearthstone-simulator)

_Hearthstone: Heroes of WarCraft_ and _Blizzard_ are trademarks of Blizzard Entertainment.
