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
        
        
def change_attack_to_one(minion):
    if minion.card.target is not None:
        # This will increase/decrease a minions attack to 1
        minion.card.target.increase_attack(1 - minion.card.target.attack_power)
        
        
def give_divine_shield(minion):
    if minion.card.target is not None:
        minion.card.target.divine_shield = True