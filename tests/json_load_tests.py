import json
import re
import tests.card_tests.druid_tests
import tests.card_tests.mage_tests
import tests.card_tests.hunter_tests


class JSONTester:
    def define_type(self, card_def):
        from hearthbreaker.constants import CHARACTER_CLASS, MINION_TYPE, CARD_RARITY
        from hearthbreaker.game_objects import Minion, MinionCard
        from hearthbreaker.tags.base import Battlecry, Choice, Action, Deathrattle, Effect, Aura
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
                init_dict['battlecry'] = Battlecry.from_json(**card_def['battlecry'])

            if 'choices' in card_def:
                init_dict['choices'] = [Choice.from_json(**choice) for choice in card_def['choices']]

            if 'overload' in card_def:
                init_dict['overload'] = card_def['overload']

            MinionCard.__init__(self, **init_dict)

        def create_minion(self, player):
            create_dict = {
                'attack': card_def['attack'],
                'health': card_def['health']
            }
            if 'effects' in card_def:
                create_dict['effects'] = [Effect.from_json(player.game, **effect) for effect in card_def['effects']]

            if 'auras' in card_def:
                create_dict['auras'] = [Aura.from_json(**aura) for aura in card_def['auras']]

            if 'enrage' in card_def:
                create_dict['enrage'] = Action.from_json(**card_def['enrage'])

            if 'deathrattle' in card_def:
                create_dict['deathrattle'] = Deathrattle.from_json(**card_def['deathrattle'])

            if 'spell_damage' in card_def:
                create_dict['spell_damage'] = card_def['spell_damage']

            return Minion(**create_dict)
        if card_def['rarity'] != "Special":
            name = re.sub("[:'.-]", "", card_def['name'])
            name = "".join([word.title() for word in name.split()])
            cls_def = getattr(hearthbreaker.cards, name, None)
            if cls_def:
                self.old_attrs[name] = {
                    'init': cls_def.__init__,
                    'create_minion': cls_def.create_minion
                }
                cls_def.__init__ = __init__
                cls_def.create_minion = create_minion

    def setUp(self):
        super().setUp()
        with open("card_defs.json", "r") as file:
            cards = json.load(file)
            self.old_attrs = {}
            for card in cards:
                self.define_type(card)

    def tearDown(self):
        super().tearDown()
        import hearthbreaker.cards
        for name, defn in self.old_attrs.items():
            cls_def = getattr(hearthbreaker.cards, name)
            cls_def.__init__ = defn['init']
            cls_def.create_minion = defn['create_minion']


class TestJSONDruid(JSONTester, tests.card_tests.druid_tests.TestDruid):
    pass


class TestJSONMage(JSONTester, tests.card_tests.mage_tests.TestMage):
    pass


class TestJSONHunter(JSONTester, tests.card_tests.hunter_tests.TestHunter):
    pass
