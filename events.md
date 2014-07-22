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
 * minion_placed(minion)
 * minion_played(minion)
 * minion_summoned(minion)
 * after_minion_added(minion)
 * turn_started
 * turn_ended
 * attacking(attacker)
 * secret_revealed (secret)
 * overloaded
 * attack(attacker, target)

##Game
 * minion_died(dead_minion, killer)
 * kept_cards(card_array)
 * minion_removed(minion, player)
 * minion_healed
 * minion_damaged(minion)
 
##Character
 * attack
 * attack_completed
 * attacked (attacker)
 * damaged(amount, attacker)
 * healed(amount)
 * damaged_by_spell(amount, card)
 * hero_damaged(amount, attacker)
 * physically_damaged(amount, attacker)
 * damaged_by_minion(amount, minion)
 * damaged_by_player(amount, player)
 * did_damage(amount, target)
 * died (attacker)
 * attack_changed(amount)
 * health_increased(amount)
 * health_decreased(amount)
 * health_changed
 * enraged
 * unenraged
 
##Minion (Character)
 * added_to_board(minion, index)
 * silenced
 * copied(new_minion, new_owner)

 
##Hero (Character)
 * armor_increased
 * used_power
 * found_power_target(target)
 * fatigue_damage(fatigue)
 
##Weapon
 * destroyed