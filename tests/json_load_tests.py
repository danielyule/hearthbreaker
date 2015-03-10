import json
import re
from hearthbreaker.cards.base import MinionCard, WeaponCard
from hearthbreaker.game_objects import Weapon, Minion
import tests.card_tests.druid_tests
import tests.card_tests.mage_tests
import tests.card_tests.hunter_tests
import tests.card_tests.paladin_tests
import tests.card_tests.priest_tests
import tests.card_tests.rogue_tests
import tests.card_tests.shaman_tests
import tests.card_tests.warlock_tests
import tests.card_tests.warrior_tests
import tests.card_tests.neutral_tests


with open("card_defs.json", "r") as file:
    cards = json.load(file)


class JSONTester:
    def define_type(self, card_def):
        from hearthbreaker.constants import CHARACTER_CLASS, MINION_TYPE, CARD_RARITY
        from hearthbreaker.tags.base import Battlecry, Choice, Deathrattle, Effect, Aura, Buff
        import hearthbreaker.cards

        def __init__(self):
            init_dict = {
                'name': card_def['name'],
                'mana': card_def['mana'],
                'rarity': CARD_RARITY.from_str(card_def['rarity'])
            }
            if 'character_class' in card_def:
                init_dict['character_class'] = CHARACTER_CLASS.from_str(card_def['character_class'])

            if 'minion_type' in card_def:
                init_dict['minion_type'] = MINION_TYPE.from_str(card_def['minion_type'])

            if 'battlecry' in card_def:
                init_dict['battlecry'] = tuple(Battlecry.from_json(**battlecry) for battlecry in card_def['battlecry'])

            if 'choices' in card_def:
                init_dict['choices'] = [Choice.from_json(**choice) for choice in card_def['choices']]

            if 'combo' in card_def:
                init_dict['combo'] = Battlecry.from_json(**card_def['combo'])

            if 'overload' in card_def:
                init_dict['overload'] = card_def['overload']

            if 'buffs' in card_def:
                init_dict['buffs'] = [Buff.from_json(**buff) for buff in card_def['buffs']]
            if 'auras' in card_def:
                init_dict['auras'] = [Aura.from_json(**aura) for aura in card_def['auras']]
            if 'effects' in card_def:
                init_dict['effects'] = [Effect.from_json(**effect) for effect in card_def['effects']]

            MinionCard.__init__(self, **init_dict)

        def __init_weapon__(self):
            init_dict = {
                'name': card_def['name'],
                'mana': card_def['mana'],
                'rarity': CARD_RARITY.from_str(card_def['rarity'])
            }
            if 'character_class' in card_def:
                init_dict['character_class'] = CHARACTER_CLASS.from_str(card_def['character_class'])

            if 'battlecry' in card_def:
                init_dict['battlecry'] = Battlecry.from_json(**card_def['battlecry'])

            if 'combo' in card_def:
                init_dict['combo'] = Battlecry.from_json(**card_def['combo'])

            if 'overload' in card_def:
                init_dict['overload'] = card_def['overload']

            if 'buffs' in card_def:
                init_dict['buffs'] = [Buff.from_json(**buff) for buff in card_def['buffs']]
            if 'auras' in card_def:
                init_dict['auras'] = [Aura.from_json(**aura) for aura in card_def['auras']]
            if 'effects' in card_def:
                init_dict['effects'] = [Effect.from_json(**effect) for effect in card_def['effects']]

            WeaponCard.__init__(self, **init_dict)

        def create_minion(self, player):
            create_dict = {
                'attack': card_def['attack'],
                'health': card_def['health']
            }
            if "impl" in card_def:
                impl = card_def['impl']
                if 'effects' in impl:
                    create_dict['effects'] = [Effect.from_json(**effect) for effect in impl['effects']]

                if 'auras' in impl:
                    create_dict['auras'] = [Aura.from_json(**aura) for aura in impl['auras']]

                if 'buffs' in impl:
                    create_dict['buffs'] = [Buff.from_json(**buff) for buff in impl['buffs']]

            if 'enrage' in card_def:
                create_dict['enrage'] = [Aura.from_json(**enrage) for enrage in card_def['enrage']]

            if 'deathrattle' in card_def:
                create_dict['deathrattle'] = [Deathrattle.from_json(**deathrattle)
                                              for deathrattle in card_def['deathrattle']]

            return Minion(**create_dict)

        def create_weapon(self, player):
            create_dict = {
                'attack_power': card_def['attack'],
                'durability': card_def['durability']
            }
            if "impl" in card_def:
                impl = card_def['impl']
                if 'effects' in impl:
                    create_dict['effects'] = [Effect.from_json(**effect) for effect in impl['effects']]

                if 'auras' in impl:
                    create_dict['auras'] = [Aura.from_json(**aura) for aura in impl['auras']]

                if 'buffs' in impl:
                    create_dict['buffs'] = [Buff.from_json(**buff) for buff in impl['buffs']]

            if 'deathrattle' in card_def:
                create_dict['deathrattle'] = Deathrattle.from_json(**card_def['deathrattle'])

            return Weapon(**create_dict)
        if card_def['rarity'] != "Special":
            if 'ref_name' in card_def:
                name = card_def['ref_name']
            else:
                name = card_def['name']
            name = re.sub("[:'. ()-]", "", name)
            name = "".join([word[0].upper() + word[1:] for word in name.split()])
            cls_def = getattr(hearthbreaker.cards, name, None)
            if cls_def:
                if card_def['type'] == 'minion':
                    self.old_attrs[name] = {
                        'init': cls_def.__init__,
                        'create_minion': cls_def.create_minion
                    }
                    cls_def.__init__ = __init__
                    cls_def.create_minion = create_minion
                elif card_def['type'] == 'weapon':
                    self.old_attrs[name] = {
                        'init': cls_def.__init__,
                        'create_weapon': cls_def.create_weapon
                    }
                    cls_def.__init__ = __init_weapon__
                    cls_def.create_weapon = create_weapon

    def setUp(self):
        super().setUp()
        self.old_attrs = {}
        for card in cards:
            self.define_type(card)

    def tearDown(self):
        super().tearDown()
        import hearthbreaker.cards
        for name, defn in self.old_attrs.items():
            cls_def = getattr(hearthbreaker.cards, name)
            if 'create_minion' in defn:
                cls_def.__init__ = defn['init']
                cls_def.create_minion = defn['create_minion']
            else:
                cls_def.__init__ = defn['init']
                cls_def.create_weapon = defn['create_weapon']


class TestJSONDruid(JSONTester, tests.card_tests.druid_tests.TestDruid):
    pass


class TestJSONMage(JSONTester, tests.card_tests.mage_tests.TestMage):
    pass


class TestJSONHunter(JSONTester, tests.card_tests.hunter_tests.TestHunter):
    pass


class TestJSONPaladin(JSONTester, tests.card_tests.paladin_tests.TestPaladin):
    pass


class TestJSONPriest(JSONTester, tests.card_tests.priest_tests.TestPriest):
    pass


class TestJSONRogue(JSONTester, tests.card_tests.rogue_tests.TestRogue):
    pass


class TestJSONShaman(JSONTester, tests.card_tests.shaman_tests.TestShaman):
    pass


class TestJSONWarlock(JSONTester, tests.card_tests.warlock_tests.TestWarlock):
    pass


class TestJSONWarrior(JSONTester, tests.card_tests.warrior_tests.TestWarrior):
    pass


class TestJSONNeutral(JSONTester, tests.card_tests.neutral_tests.TestCommon):
    pass
