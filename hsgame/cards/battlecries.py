import copy


__author__ = 'Daniel'


def draw_card(minion):
    minion.player.draw()

def silence(minion):
    if minion.card.target is not None:
        minion.card.target.silence()

def heal_two(minion):
    if minion.card.target is not None:
        minion.card.target.heal(2, None)
        
def heal_three(minion):
    if minion.card.target is not None:
        minion.card.target.heal(3, None)

def deal_one_damage(minion):
    if minion.card.target is not None:
        minion.card.target.damage(1, None)

def deal_two_damage(minion):
    if minion.card.target is not None:
        minion.card.target.damage(2, None)

def flame_imp(minion):
    minion.player.hero.damage(3, None)
    
def nightblade(minion):
    minion.other_player.hero.damage(3, None)
        
def pit_lord(minion):
    minion.player.hero.damage(5, None)
    
def priestess_of_elune(minion):
    minion.player.hero.heal(4, None)
    
def guardian_of_kings(minion):
    minion.player.hero.heal(6, None)
    
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
        
def deal_one_damage_all_characters(minion):
    targets = game.other_player.minions.copy()
    targets.extend(game.current_player.minions)
    targets.append(game.other_player.hero)
    targets.append(game.current_player.hero)
    for minion in targets:
        minion.damage(1, None)
        
def destroy_own_crystal(minion):
    player.max_mana -= 1
    
def give_enemy_crystal(minion):
    if other_player.max_mana < 10:
        other_player.max_mana += 1
        
def discard_one(minion):
    player.discard()
    
def discard_two(minion):
    player.discard()
    player.discard()

def discard_all(minion):
    for i in range(len(player.hand)):
        player.discard()

def darkscale_healer(minion):        
    targets = game.current_player.minions.copy()
    targets.append(game.current_player.hero)
    for minion in targets:
        minion.heal(2)

def ssc(minion):
    if minion.card.target is not None:
        minion.card.target.increase_attack(1)
        minion.card.target.increase_health(1)
    
def destroy_target(minion):
    if minion.card.target is not None:
        minion.card.target.die()
    
def two_temp_attack(minion):
    if minion.card.target is not None:
        minion.card.target.increase_temp_attack(2)
