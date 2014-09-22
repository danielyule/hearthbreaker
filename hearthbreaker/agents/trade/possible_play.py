from hearthbreaker.agents.trade.util import Util
from functools import reduce


class PossiblePlay:
    def __init__(self, cards, available_mana):
        if len(cards) == 0:
            raise Exception("PossiblePlay cards is empty")

        self.cards = cards
        self.available_mana = available_mana

    def card_mana(self):
        return reduce(lambda s, c: s + c.mana, self.cards, 0)

    def sorted_mana(self):
        return Util.reverse_sorted(map(lambda c: c.mana, self.cards))

    def wasted(self):
        return self.available_mana - self.card_mana()

    def value(self):
        res = self.card_mana()
        wasted = self.wasted()
        if wasted < 0:
            raise Exception("Too Much Mana")

        res += wasted * -100000000000

        factor = 100000000
        for card_mana in self.sorted_mana():
            res += card_mana * factor
            factor = factor / 10

        if self.has_hero_power() and self.available_mana < 6:
            res -= 10000000000000000

        return res

    def has_hero_power(self):
        for card in self.cards:
            if card.name == 'Hero Power':
                return True
        return False

    def first_card(self):
        if self.has_hero_power():
            for card in self.cards:
                if card.name == 'Hero Power':
                    return card
            raise Exception("bad")
        else:
            return self.cards[0]

    def __str__(self):
        names = [c.name for c in self.cards]
        s = str(names)
        return "{} {}".format(s, self.value())


class CoinPlays:
    def coin(self):
        cards = [c for c in filter(lambda c: c.name == 'The Coin', self.cards)]
        return cards[0]

    def plays(self):
        if self.has_coin():
            coinPlays = self.after_coin().plays_inner()
            if len(coinPlays) > 0:
                best = coinPlays[0]
                if best.wasted() == 0:
                    res = []
                    for play in coinPlays:
                        cards = [self.coin()] + play.cards
                        new_play = PossiblePlay(cards, play.available_mana - 1)
                        res.append(new_play)
                    return res

            return self.without_coin().plays_inner()
        else:
            return self.plays_inner()

    def has_coin(self):
        for card in self.cards:
            if card.name == "The Coin":
                return True
        return False

    def after_coin(self):
        if not self.has_coin():
            raise Exception("No Coin")
        cards = [c for c in filter(lambda c: c.name != 'The Coin', self.cards)]
        if len(cards) != len(self.cards) - 1:
            raise Exception("bad")
        return PossiblePlays(cards, self.mana + 1)

    def without_coin(self):
        if not self.has_coin():
            raise Exception("No Coin")
        cards = [c for c in filter(lambda c: c.name != 'The Coin', self.cards)]
        if len(cards) != len(self.cards) - 1:
            raise Exception("bad")
        return PossiblePlays(cards, self.mana)


class HeroPowerCard:
    def __init__(self):
        self.mana = 2
        self.name = "Hero Power"

    def can_use(self, player, game):
        return True


class PossiblePlays(CoinPlays):
    def __init__(self, cards, mana, allow_hero_power=True):
        self.cards = cards
        self.mana = mana
        self.allow_hero_power = allow_hero_power

    def raw_plays(self):
        res = []

        possible = [card for card in
                    filter(lambda card: card.mana <= self.mana, self.cards)]
        if self.mana >= 2 and self.allow_hero_power and False:
            possible.append(HeroPowerCard())

        if len(possible) == 0:
            return [[]]

        for card in possible:
            rest = self.cards[0:99999]

            if card.name == 'Hero Power':
                f_plays = PossiblePlays(rest,
                                        self.mana - card.mana,
                                        allow_hero_power=False).raw_plays()
            else:
                rest.remove(card)
                f_plays = PossiblePlays(rest,
                                        self.mana - card.mana,
                                        allow_hero_power=self.allow_hero_power).raw_plays()

            for following_play in f_plays:
                combined = [card] + following_play
                res.append(combined)

        res = Util.uniq_by_sorted(res)

        return res

    def plays_inner(self):
        res = [PossiblePlay(raw, self.mana) for raw in self.raw_plays() if len(raw) > 0]
        res = sorted(res, key=PossiblePlay.value)
        res.reverse()

        return res


class PlayMixin:
    def play_cards(self, player):
        if len(player.minions) == 7:
            return
        if player.game.game_ended:
            return

        plays = PossiblePlays(player.hand, player.mana, allow_hero_power=(not player.hero.power.used)).plays()

        if len(plays) > 0:
            play = plays[0]
            if len(play.cards) == 0:
                raise Exception("play has no cards")

            card = play.first_card()

            if card.name == 'Hero Power':
                player.hero.power.use()
            else:
                player.game.play_card(card)

            self.play_cards(player)
