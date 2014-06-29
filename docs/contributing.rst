Contributing
============

Currently, the most straightforward way to contribute is to implement cards that have not yet been implemented, although
any contributions at all are welcome.  Other options include finding and filing issues, joining the
`developer mailing list <https://groups.google.com/forum/#!forum/hearthstone-simulator-dev>`_  and adding your voice to
the discussions or helping test edge cases or researching others' work in finding strange applications of Hearthstone's
logic.

All code should conform to the style dictated by `Python's PEP8 Style Guide <http://legacy.python.org/dev/peps/pep-0008/>`_
The only exception is that unit tests for cards are named ``test_CardName`` where ``CardName`` is the name of the class.
This is to match the CamelCase convention for card names, but it contradicts the convention for method names to be
written in lowercase with underscores separating the words.  PEP8 Validation can be done by the
`pep8 tool <https://pypi.python.org/pypi/pep8>`_.  It can be installed with
::
    pip install pep8

It can then be run on the whole project by running the following command in the root directory.
    pep8 --first .

Any new code should be accompanied with a unit test which runs through the new code at least once.

Adding new cards
----------------
