__author__ = 'Daniel'

from hearthbreaker.effects.base import Targeting


class Target(Targeting):
    def select_target(self, this, focus, other):
        return focus

    def __to_json__(self):
        return {
            'type': 'target'
        }


class Self(Targeting):
    def select_target(self, this, focus, other):
        return this

    def __to_json__(self):
        return {
            'type': 'self'
        }