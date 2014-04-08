Events Triggered in hssim
=========================

##Player
 * damaged (amount)
 * died
 * card_drawn (card)
 * card_put_back(card)
 * turn_started
 * turn_ended
 * attack_minion
 * attack_player
 * fatigue_damage(amount)
 * damaged(amount, what)
 * spell_damaged(amount, card)
 * minion_damaged(amount, minion)
 * player_damaged(amount, player)
 * attack increased(amount)
 * attack_decreased(amount)
 * armour_increased(amount)
 * heal(amount)
 * used_power
 * found_power_target(target)

##Game


 * card_played
 * minion_on_minion_attack(minion, target)
 * minion_on_player_attack(minion, target)
 * player_on_minion_attack(player, target)
 * player_on_player_attack(player, target)
 * minion_added(new_minion)
 * minion_died(dead_minion)
 * kept_cards(card_array)
 * minion_removed

##Minion
 * added_to_board
 * attack_minion
 * attack_player
 * damaged(amount, attacker)
 * spell_damaged(amount, card)
 * minion_damaged(amount, minion)
 * player_damaged(amount, player)
 * died (attacker)
 * attack increased(amount)
 * attack_decreased(amount)
 * health_increased(amount)
 * silenced