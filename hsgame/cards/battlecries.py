__author__ = 'Daniel'

import hsgame.targetting

def draw_card(minion):
    minion.player.draw()

def silence(minion):
    targets = hsgame.targetting.find_minion_spell_target(minion.game)
    target = minion.player.agent.choose_target(targets)
    target.silence()