Events Triggered in hssim
=========================

##Player

 * card_drawn (card)
 * card_put_back(card)
 * card_destroyed(card)
 * card_discarded(card)
 * card_played(card)
 * card_used(card)
 * spell_cast (card)
 * minion_summoned(minion)
 * minion_played(minion)
 * turn_started
 * turn_ended
 * attacking(attacker)
 * secret_revealed (secret)
 * overloaded

##Game
 * minion_added(new_minion)
 * minion_died(dead_minion)
 * kept_cards(card_array)
 * minion_removed(minion, player)
 * minion_healed
 
##Character
 * attack
 * attack_minion (target)
 * attack_player (target)
 * attack_completed
 * attacked (attacker)
 * damaged(amount, attacker)
 * healed(amount)
 * spell_damaged(amount, card)
 * secret_damaged(amount, attacker)
 * physically_damaged(amount, attacker)
 * minion_damaged(amount, minion)
 * player_damaged(amount, player)
 * did_damage(amount, target)
 * died (attacker)
 * attack_changed(amount)
 * health_increased(amount)
 * health_decreased(amount)
 * health_changed
 * enraged
 * unenraged
 
##Minion (Character)
 * added_to_board(minion)
 * silenced
 * copied(new_minion, new_owner)

 
##Hero (Character)
 * armour_increased
 * used_power
 * found_power_target(target)
 * fatigue_damage(fatigue)
 
##Weapon
 * destroyed