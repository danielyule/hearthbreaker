import copy
from hearthbreaker.constants import MINION_TYPE
import hearthbreaker.game_objects


def draw_card(minion):
    minion.player.draw()


def opponent_draw_two(minion):
    minion.player.opponent.draw()
    minion.player.opponent.draw()


def silence(minion):
    if minion.card.target is not None:
        minion.card.target.silence()


def heal_two(minion):
    if minion.card.target is not None:
        minion.card.target.heal(minion.player.effective_heal_power(2), None)


def heal_three(minion):
    if minion.card.target is not None:
        minion.card.target.heal(minion.player.effective_heal_power(3), None)


def deal_one_damage(minion):
    if minion.card.target is not None:
        minion.card.target.damage(1, None)


def deal_two_damage(minion):
    if minion.card.target is not None:
        minion.card.target.damage(2, None)


def deal_three_damage(minion):
    if minion.card.target is not None:
        minion.card.target.damage(3, None)


def flame_imp(minion):
    minion.player.hero.damage(3, None)


def nightblade(minion):
    minion.player.game.other_player.hero.damage(3, None)


def pit_lord(minion):
    minion.player.hero.damage(5, None)


def priestess_of_elune(minion):
    minion.player.hero.heal(minion.player.effective_heal_power(4), None)


def guardian_of_kings(minion):
    minion.player.hero.heal(minion.player.effective_heal_power(6), None)


def change_attack_to_one(minion):
    if minion.card.target is not None:
        # This will increase/decrease a minions attack to 1
        minion.card.target.change_attack(1 - minion.card.target.calculate_attack())


def give_divine_shield(minion):
    if minion.card.target is not None:
        minion.card.target.divine_shield = True


def give_stealth(minion):
    if minion.card.target is not None:
        minion.card.target.stealth = True


def gain_one_health_for_each_card_in_hand(minion):
    minion.increase_health(len(minion.player.hand))


def take_control_of_minion(minion):
    if minion.card.target is not None:
        new_minion = minion.card.target.copy(minion.player)
        new_minion.add_to_board(len(minion.player.minions))
        minion.card.target.remove_from_board()


def give_three_health(minion):
    if minion.card.target is not None:
        minion.card.target.increase_health(3)


def deal_one_damage_all_characters(minion):
    targets = copy.copy(minion.player.game.current_player.minions)
    targets.remove(minion)
    targets.extend(minion.player.game.other_player.minions)
    targets.append(minion.player.game.other_player.hero)
    targets.append(minion.player.game.current_player.hero)

    for target in targets:
        target.damage(1, None)


def destroy_own_crystal(minion):
    minion.player.max_mana -= 1


def give_enemy_crystal(minion):
    if minion.game.other_player.max_mana < 10:
        minion.game.other_player.max_mana += 1


def discard_one(minion):
    minion.player.discard()


def discard_two(minion):
    minion.player.discard()
    minion.player.discard()


def deathwing(minion):
    targets = copy.copy(minion.player.game.other_player.minions)
    targets.extend(minion.player.game.current_player.minions)
    for target in targets:
        if target is not minion:
            target.die(None)
    for i in range(len(minion.player.hand)):
        minion.player.game.current_player.discard()


def darkscale_healer(minion):
    targets = copy.copy(minion.player.game.current_player.minions)
    targets.append(minion.player.game.current_player.hero)
    for minion in targets:
        minion.heal(minion.player.effective_heal_power(2), None)


def ssc(minion):
    if minion.card.target is not None:
        minion.card.target.change_attack(1)
        minion.card.target.increase_health(1)


def destroy_target(minion):
    if minion.card.target is not None:
        minion.card.target.die(None)


def two_temp_attack(minion):
    if minion.card.target is not None:
        minion.card.target.change_temp_attack(2)


def give_windfury(minion):
    if minion.card.target is not None:
        minion.card.target.wind_fury = True


def return_to_hand(minion):
    if minion.card.target is not None:
        minion.card.target.bounce()


def put_friendly_minion_on_board_from_enemy_deck(minion):
    player = minion.player.opponent
    index_list = []
    index = 0
    for card in player.deck.cards:
        if not player.deck.used[index] and isinstance(card, hearthbreaker.game_objects.MinionCard):
            index_list.append(index)
        index += 1
    if len(index_list) > 0:
        chosen_index = player.game.random(0, len(index_list) - 1)
        player.deck.used[index_list[chosen_index]] = True
        player.deck.cards[index_list[chosen_index]].summon(player, player.game, len(player.minions))


def put_minion_on_board_from_hand(minion):
    player = minion.player
    index_list = []
    index = 0
    for card in player.hand:
        if isinstance(card, hearthbreaker.game_objects.MinionCard) and card.minion_type == MINION_TYPE.DEMON:
            index_list.append(index)
        index += 1
    if len(index_list) > 0:
        chosen_index = player.game.random(0, len(index_list) - 1)
        player.hand[index_list[chosen_index]].summon(player, player.game, len(player.minions))
        player.hand.remove(player.hand[index_list[chosen_index]])
