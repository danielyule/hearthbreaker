__author__ = 'Daniel'

import hsgame.targetting


def draw_card(minion):
    minion.player.draw()


def silence(minion):
    targets = hsgame.targetting.find_minion_spell_target(minion.game)
    target = minion.player.agent.choose_target(targets)
    target.silence()


def deal_one_damage(minion):
    targets = minion.game.other_player.minions.copy()
    targets.append(minion.game.other_player)
    targets.extend(minion.player.minions)
    targets.append(minion.player)
    target = minion.player.agent.choose_target(targets)
    target.damage(1, None)


def deal_two_damage(minion):
    targets = minion.game.other_player.minions.copy()
    targets.append(minion.game.other_player)
    targets.extend(minion.player.minions)
    targets.append(minion.player)
    target = minion.player.agent.choose_target(targets)
    target.damage(2, None)