import copy


__author__ = 'Daniel'


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
        
        
def gain_one_health_for_each_card_in_hand(minion):
    minion.increase_health(len(minion.player.hand))
    

def take_control_of_minion(minion):
    if minion.card.target is not None:
        m = copy.copy(minion.card.target)
        minion.card.target.remove_from_board()
        m.add_to_board(m.card, minion.game, minion.player, 0)