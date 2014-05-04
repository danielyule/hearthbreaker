__author__ = 'Daniel'

import hsgame.targetting


def draw_card(minion):
    minion.player.draw()


def silence(minion):
    if minion.card.target is not None:
        minion.card.target.silence()


def deal_one_damage(minion):
    if minion.card.target is not None:
        minion.card.target.damage(1, None)


def deal_two_damage(minion):
    if minion.card.target is not None:
        minion.card.target.damage(2, None)