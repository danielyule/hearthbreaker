Events Triggered in hssim
=========================

##Player
 * damaged (amount)
 * died (attacker)
 * card_drawn (card)
 * card_put_back(card)
 * card_destroyed(card)
 * card_played(card)
 * card_used(card)
 * spell_cast (card)
 * turn_started
 * turn_ended
 * attacking (attacker)
 * attack_minion
 * attack_player
 * attacked (attacker)
 * fatigue_damage(amount)
 * damaged(amount, what)
 * spell_damaged(amount, card)
 * physically_damaged(amount, attacker)
 * minion_damaged(amount, minion)
 * player_damaged(amount, player)
 * attack increased(amount)
 * attack_decreased(amount)
 * armour_increased(amount)
 * heal(amount)
 * secret_revealed (secret)
 * used_power
 * found_power_target(target)

##Game
 * minion_on_minion_attack(minion, target)
 * minion_on_player_attack(minion, target)
 * player_on_minion_attack(player, target)
 * player_on_player_attack(player, target)
 * minion_added(new_minion)
 * minion_died(dead_minion)
 * kept_cards(card_array)
 * minion_removed

##Minion
 * added_to_board(minion)
 * attacking (attacker)
 * attack_minion
 * attack_player
 * attacked(attacker)
 * damaged(amount, attacker)
 * healed(amount)
 * spell_damaged(amount, card)
 * physically_damaged(amount, attacker)
 * minion_damaged(amount, minion)
 * player_damaged(amount, player)
 * died (attacker)
 * attack increased(amount)
 * attack_decreased(amount)
 * health_increased(amount)
 * health_decreased(amount)
 * silenced