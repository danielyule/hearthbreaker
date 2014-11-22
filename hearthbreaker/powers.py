import hearthbreaker.constants
import hearthbreaker.game_objects
import hearthbreaker.tags.action
import hearthbreaker.tags.base
import hearthbreaker.tags.selector
import hearthbreaker.tags.event


def powers(character_class):
    if character_class == hearthbreaker.constants.CHARACTER_CLASS.DRUID:
        return DruidPower
    elif character_class == hearthbreaker.constants.CHARACTER_CLASS.HUNTER:
        return HunterPower
    elif character_class == hearthbreaker.constants.CHARACTER_CLASS.MAGE:
        return MagePower
    elif character_class == hearthbreaker.constants.CHARACTER_CLASS.PRIEST:
        return PriestPower
    elif character_class == hearthbreaker.constants.CHARACTER_CLASS.PALADIN:
        return PaladinPower
    elif character_class == hearthbreaker.constants.CHARACTER_CLASS.ROGUE:
        return RoguePower
    elif character_class == hearthbreaker.constants.CHARACTER_CLASS.SHAMAN:
        return ShamanPower
    elif character_class == hearthbreaker.constants.CHARACTER_CLASS.WARLOCK:
        return WarlockPower
    elif character_class == hearthbreaker.constants.CHARACTER_CLASS.WARRIOR:
        return WarriorPower


class Power:
    def __init__(self, hero):
        self.hero = hero
        self.used = False

    def can_use(self):
        return not self.used and self.hero.player.mana >= 2

    def use(self):
        if self.can_use():
            self.hero.player.trigger("used_power")
            self.hero.player.mana -= 2
            self.used = True


class DruidPower(Power):
    def __init__(self, hero):
        super().__init__(hero)

    def use(self):
        super().use()
        self.hero.change_temp_attack(1)
        self.hero.increase_armor(1)


class HunterPower(Power):
    def __init__(self, hero):
        super().__init__(hero)

    def use(self):
        super().use()
        self.hero.player.game.other_player.hero.damage(2, None)


class MagePower(Power):
    def __init__(self, hero):
        super().__init__(hero)

    def use(self):
        target = self.hero.find_power_target()
        super().use()
        target.damage(1 * self.hero.player.spell_multiplier, None)
        self.hero.player.game.check_delayed()


class PriestPower(Power):
    def __init__(self, hero):
        super().__init__(hero)

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
    def __init__(self, hero):
        super().__init__(hero)

    def use(self):
        super().use()
        target = self.hero.find_power_target()
        target.damage(2, None)

    def __str__(self):
        return "Mind Spike"


# Special power the priest can obtain via the card Shadowform
class MindShatter(Power):
    def __init__(self, hero):
        super().__init__(hero)

    def use(self):
        super().use()
        target = self.hero.find_power_target()
        target.damage(3, None)

    def __str__(self):
        return "Mind Shatter"


class PaladinPower(Power):
    def __init__(self, hero):
        super().__init__(hero)

    def use(self):
        class SilverHandRecruit(hearthbreaker.game_objects.MinionCard):
            def __init__(self):
                super().__init__("Silver Hand Recruit", 1, hearthbreaker.constants.CHARACTER_CLASS.PALADIN,
                                 hearthbreaker.constants.CARD_RARITY.SPECIAL)

            def create_minion(self, player):
                return hearthbreaker.game_objects.Minion(1, 1)

        super().use()

        recruit_card = SilverHandRecruit()
        recruit_card.summon(self.hero.player, self.hero.player.game, len(self.hero.player.minions))


class RoguePower(Power):
    def __init__(self, hero):
        super().__init__(hero)

    def use(self):
        class WickedKnife(hearthbreaker.game_objects.WeaponCard):
            def __init__(self):
                super().__init__("Wicked Knife", 1, hearthbreaker.constants.CHARACTER_CLASS.ROGUE,
                                 hearthbreaker.constants.CARD_RARITY.SPECIAL)

            def create_weapon(self, player):
                weapon = hearthbreaker.game_objects.Weapon(1, 2)
                return weapon

        super().use()

        knife = WickedKnife().create_weapon(self.hero.player)
        knife.equip(self.hero.player)


class ShamanPower(Power):
    def __init__(self, hero):
        self.healing_totem = False
        self.searing_totem = False
        self.stoneclaw_totem = False
        self.wrath_of_air_totem = False

        super().__init__(hero)

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
        class HealingTotem(hearthbreaker.game_objects.MinionCard):
            def __init__(self):
                super().__init__("Healing Totem", 1, hearthbreaker.constants.CHARACTER_CLASS.SHAMAN,
                                 hearthbreaker.constants.CARD_RARITY.SPECIAL, hearthbreaker.constants.MINION_TYPE.TOTEM)

            def create_minion(self, player):
                return hearthbreaker.game_objects.Minion(0, 2, effects=[hearthbreaker.tags.base.Effect(
                    hearthbreaker.tags.event.TurnEnded(),
                    hearthbreaker.tags.action.Heal(1),
                    hearthbreaker.tags.selector.MinionSelector(condition=None)
                )])

        class SearingTotem(hearthbreaker.game_objects.MinionCard):
            def __init__(self):
                super().__init__("Searing Totem", 1, hearthbreaker.constants.CHARACTER_CLASS.SHAMAN,
                                 hearthbreaker.constants.CARD_RARITY.SPECIAL, hearthbreaker.constants.MINION_TYPE.TOTEM)

            def create_minion(self, player):
                return hearthbreaker.game_objects.Minion(1, 1)

        class StoneclawTotem(hearthbreaker.game_objects.MinionCard):
            def __init__(self):
                super().__init__("Stoneclaw Totem", 1, hearthbreaker.constants.CHARACTER_CLASS.SHAMAN,
                                 hearthbreaker.constants.CARD_RARITY.SPECIAL, hearthbreaker.constants.MINION_TYPE.TOTEM)

            def create_minion(self, player):
                return hearthbreaker.game_objects.Minion(0, 2, taunt=True)

        class WrathOfAirTotem(hearthbreaker.game_objects.MinionCard):
            def __init__(self):
                super().__init__("Wrath of Air Totem", 1, hearthbreaker.constants.CHARACTER_CLASS.SHAMAN,
                                 hearthbreaker.constants.CARD_RARITY.SPECIAL, hearthbreaker.constants.MINION_TYPE.TOTEM)

            def create_minion(self, player):
                return hearthbreaker.game_objects.Minion(0, 2, spell_damage=1)

        super().use()

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
    def __init__(self, hero):
        super().__init__(hero)

    def use(self):
        super().use()
        self.hero.player.game.current_player.hero.damage(2, None)
        self.hero.player.game.current_player.draw()


class JaraxxusPower(Power):
    def __init__(self, hero):
        super().__init__(hero)

    def use(self):
        class Infernal(hearthbreaker.game_objects.MinionCard):
            def __init__(self):
                super().__init__("Infernal", 6, hearthbreaker.constants.CHARACTER_CLASS.LORD_JARAXXUS,
                                 hearthbreaker.constants.CARD_RARITY.SPECIAL)

            def create_minion(self, player):
                return hearthbreaker.game_objects.Minion(6, 6, hearthbreaker.constants.MINION_TYPE.DEMON)

        super().use()

        infernal_card = Infernal()
        infernal_card.summon(self.hero.player, self.hero.player.game, len(self.hero.player.minions))


class WarriorPower(Power):
    def __init__(self, hero):
        super().__init__(hero)

    def use(self):
        super().use()
        self.hero.increase_armor(2)
