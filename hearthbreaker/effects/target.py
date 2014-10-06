__author__ = 'Daniel'

from hearthbreaker.effects.base import Targeting


class Target(Targeting):
    def select_target(self, this, focus, other):
        return focus

    def __to_json__(self):
        return {
            'name': 'target'
        }


class Self(Targeting):
    def select_target(self, this, focus, other):
        return this

    def __to_json__(self):
        return {
            'name': 'self'
        }


class Owner(Targeting):
    def select_target(self, this, focus, other):
        return this.player.hero

    def __to_json__(self):
        return {
            'name': 'self'
        }
