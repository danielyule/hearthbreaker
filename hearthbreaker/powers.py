from copy import copy


class Power:
    def __init__(self):
        self.hero = None
        self.used = False

    def can_use(self):
        return not self.used and self.hero.player.mana >= 2

    def use(self):
        if self.can_use():
            self.hero.player.trigger("used_power")
            self.hero.player.mana -= 2
            self.used = True


class DruidPower(Power):
    def use(self):
        super().use()
        self.hero.change_temp_attack(1)
        self.hero.increase_armor(1)


class HunterPower(Power):
    def use(self):
        if self.hero.power_targets_minions:
            target = self.hero.find_power_target()
            super().use()
            target.damage(2 * self.hero.player.spell_multiplier, None)
            self.hero.player.game.check_delayed()
        else:
            super().use()
            self.hero.player.game.other_player.hero.damage(2 * self.hero.player.spell_multiplier, None)


class MagePower(Power):
    def use(self):
        target = self.hero.find_power_target()
        super().use()
        target.damage(1 * self.hero.player.spell_multiplier, None)
        self.hero.player.game.check_delayed()


class PriestPower(Power):
    def use(self):
        target = self.hero.find_power_target()
        super().use()
        if self.hero.player.heal_does_damage:
            target.damage(2 * self.hero.player.spell_multiplier, None)
        else:
            target.heal(2 * self.hero.player.heal_multiplier, None)

    def __str__(self):
        return "Lesser Heal"


# Special power the priest can obtain via the card Shadowform
class MindSpike(Power):
    def use(self):
        super().use()
        target = self.hero.find_power_target()
        target.damage(2 * self.hero.player.spell_multiplier, None)

    def __str__(self):
        return "Mind Spike"


# Special power the priest can obtain via the card Shadowform
class MindShatter(Power):
    def use(self):
        super().use()
        target = self.hero.find_power_target()
        target.damage(3 * self.hero.player.spell_multiplier, None)

    def __str__(self):
        return "Mind Shatter"


class PaladinPower(Power):
    def use(self):
        super().use()
        from hearthbreaker.cards.minions.paladin import SilverHandRecruit

        recruit_card = SilverHandRecruit()
        recruit_card.summon(self.hero.player, self.hero.player.game, len(self.hero.player.minions))


class RoguePower(Power):
    def use(self):
        super().use()
        from hearthbreaker.cards.weapons.rogue import WickedKnife
        wicked_knife = WickedKnife()
        knife = wicked_knife.create_weapon(self.hero.player)
        knife.card = wicked_knife
        knife.equip(self.hero.player)


class ShamanPower(Power):
    def __init__(self):
        self.healing_totem = False
        self.searing_totem = False
        self.stoneclaw_totem = False
        self.wrath_of_air_totem = False

        super().__init__()

    def can_use(self):
        self.healing_totem = False
        self.searing_totem = False
        self.stoneclaw_totem = False
        self.wrath_of_air_totem = False

        for minion in self.hero.player.minions:
            if minion.card.name == "Healing Totem":
                self.healing_totem = True
            elif minion.card.name == "Searing Totem":
                self.searing_totem = True
            elif minion.card.name == "Stoneclaw Totem":
                self.stoneclaw_totem = True
            elif minion.card.name == "Wrath of Air Totem":
                self.wrath_of_air_totem = True

        if self.healing_totem and self.searing_totem and self.stoneclaw_totem and self.wrath_of_air_totem:
            return False

        return super().can_use()

    def use(self):
        super().use()
        from hearthbreaker.cards.minions.shaman import HealingTotem, SearingTotem, StoneclawTotem, WrathOfAirTotem

        totems = []
        if not self.healing_totem:
            totems.append(HealingTotem())
        if not self.searing_totem:
            totems.append(SearingTotem())
        if not self.stoneclaw_totem:
            totems.append(StoneclawTotem())
        if not self.wrath_of_air_totem:
            totems.append(WrathOfAirTotem())

        random_totem = self.hero.player.game.random_choice(totems)
        random_totem.summon(self.hero.player, self.hero.player.game, len(self.hero.player.minions))


class WarlockPower(Power):
    def use(self):
        super().use()
        self.hero.player.game.current_player.hero.damage(2 * self.hero.player.spell_multiplier, None)
        self.hero.player.game.current_player.draw()


class JaraxxusPower(Power):
    def use(self):
        super().use()
        from hearthbreaker.cards.minions.warlock import Infernal

        infernal_card = Infernal()
        infernal_card.summon(self.hero.player, self.hero.player.game, len(self.hero.player.minions))


class DieInsect(Power):
    def use(self):
        super().use()
        targets = copy(self.hero.player.opponent.minions)
        targets.append(self.hero.player.opponent.hero)
        target = self.hero.player.game.random_choice(targets)
        target.damage(2 * self.hero.player.spell_multiplier, None)


class WarriorPower(Power):
    def use(self):
        super().use()
        self.hero.increase_armor(2)
