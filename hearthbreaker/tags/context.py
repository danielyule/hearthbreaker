from hearthbreaker.tags.base import Context


class BattlecryContext(Context):
    def filter_targets(self, targets):
        return [target for target in targets if target.player is self.player or not target.stealth]

    def damage(self, amount, target):
        target.damage(amount)

    def heal(self, amount, target):
        if self.player.player.heal_does_damage:
            self.damage(amount, target)
        else:
            target.heal(amount)


class SpellContext(Context):
    def filter_targets(self, targets):
        return [target for target in targets if target.player is self.player or not target.stealth]

    def damage(self, amount, target):
        target.damage((amount + self.player.spell_damage) * self.player.spell_multiplier)

    def heal(self, amount, target):
        if self.player.heal_does_damage:
            self.damage(amount, target)
        else:
            return amount * self.player.heal_multiplier
