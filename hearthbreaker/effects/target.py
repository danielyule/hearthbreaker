import copy

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


class RandomFriendlyMinion(Targeting):
    def select_target(self, this, focus, other):
        targets = copy.copy(this.player.minions)
        targets.remove(this)
        if len(targets) > 0:
            return this.player.game.random_choice(targets)
        return None

    def __to_json__(self):
        return {
            'name': 'random_friendly_minion'
        }
