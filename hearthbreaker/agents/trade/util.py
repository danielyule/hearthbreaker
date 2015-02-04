import random
import collections
import functools
from hearthbreaker.game_objects import Hero


class memoized(object):
    '''Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    '''
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        '''Return the function's docstring.'''
        return self.func.__doc__

    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        return functools.partial(self.__call__, obj)


class Util:
    @staticmethod
    def reverse_sorted(list):
        res = sorted(list)
        res.reverse()
        return res

    @staticmethod
    def uniq_by_sorted(list):
        res = {}
        for obj in list:
            a = [c.name for c in obj]
            k = str.join("", sorted(a))
            if not res.get(k):
                res[k] = obj

        return res.values()

    @staticmethod
    def rand_el(list):
        i = random.randint(0, len(list) - 1)
        return list[i]

    @staticmethod
    def rand_prefer_minion(targets):
        minions = [card for card in filter(lambda c: not isinstance(c, Hero), targets)]
        if len(minions) > 0:
            targets = minions
        return Util.rand_el(targets)

    @staticmethod
    def filter_out_one(arr, f):
        res = [obj for obj in filter(lambda x: not f(x), arr)]
        if len(res) + 1 != len(arr):
            s = "bad remove, list has {} elements, removed {}, {}"
            raise Exception(s.format(len(arr), len(arr) - len(res), arr))
        return res

    @staticmethod
    def names(arr):
        res = []
        for obj in arr:
            if hasattr(obj, "name"):
                res.append(obj.name)
            else:
                res.append("UNK")
        return res
