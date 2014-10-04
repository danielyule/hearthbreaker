__author__ = 'Daniel'

from hearthbreaker.effects.base import Targeting


class Target(Targeting):
    def select_target(self, this, focus, other):
        return focus


class Self(Targeting):
    def select_target(self, this, focus, other):
        return this
