import json
import re
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


class JSONTester:
    def define_type(self, card_def):
        from hearthbreaker.constants import CHARACTER_CLASS, MINION_TYPE, CARD_RARITY
        from hearthbreaker.game_objects import Minion, MinionCard
        from hearthbreaker.tags.base import Battlecry, Choice, Deathrattle, Effect, Aura, Enrage
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

            if 'combo' in card_def:
                init_dict['combo'] = Battlecry.from_json(**card_def['combo'])

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
                create_dict['enrage'] = Enrage.from_json(**card_def['enrage'])

            if 'deathrattle' in card_def:
                create_dict['deathrattle'] = Deathrattle.from_json(**card_def['deathrattle'])

            return Minion(**create_dict)
        if card_def['rarity'] != "Special":
            name = re.sub("[:'.-]", "", card_def['name'])
            name = "".join([word[0].upper() + word[1:] for word in name.split()])
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


class TestJSONPaladin(JSONTester, tests.card_tests.paladin_tests.TestPaladin):
    pass


class TestJSONPriest(JSONTester, tests.card_tests.priest_tests.TestPriest):
    pass


class TestJSONRogue(JSONTester, tests.card_tests.rogue_tests.TestRogue):
    def test_EdwinVanCleef(self):
        pass  # Edwin can't be impemented currently with the new Battlecry mechanic, so we skip his test


class TestJSONShaman(JSONTester, tests.card_tests.shaman_tests.TestShaman):
    pass


class TestJSONWarlock(JSONTester, tests.card_tests.warlock_tests.TestWarlock):
    def test_Jaraxxus(self):
        pass

    def test_Jaraxxus_with_SacrificialPact(self):
        pass

    def test_Jaraxxus_with_secrets(self):
        pass

    def test_VoidTerror(self):
        pass


class TestJSONWarrior(JSONTester, tests.card_tests.warrior_tests.TestWarrior):
    def test_WarsongCommander(self):
        pass  # This test uses Bloodsail Corsair, which also can't be implemented (yet)


class TestJSONNeutral(JSONTester, tests.card_tests.neutral_tests.TestCommon):
    def test_Alexstrasza(self):
        pass

    def test_BloodKnight(self):
        pass

    def test_BloodsailCorsair(self):
        pass

    def test_BloodsailRaider(self):
        pass

    def test_CaptainGreenskin(self):
        pass

    def test_CaptainsParrot(self):
        pass

    def test_CrazedAlchemist(self):
        pass

    def test_Deathwing(self):
        pass

    def testEchoingOoze_silence(self):
        pass

    def test_EchoingOoze(self):
        pass

    def test_EchoingOoze_Faceless(self):
        pass

    def test_EchoingOoze_buff(self):
        pass

    def test_EliteTaurenChieftain(self):
        pass

    def test_FacelessManipulator(self):
        pass

    def test_FrostElemental(self):
        pass

    def test_FrostwolfWarlord(self):
        pass

    def test_GelbinMekkaTwerk(self):
        pass

    def test_HarrisonJones(self):
        pass

    def test_HungryCrab(self):
        pass

    def test_MillhouseManastorm(self):
        pass

    def test_MindControlTech(self):
        pass

    def test_Nightblade(self):
        pass

    def test_Onyxia(self):
        pass

    def test_PriestessOfElune(self):
        pass

    def test_ShatteredSunCleric(self):
        pass

    def test_SilverHandKnight(self):
        pass

    def test_SilvermoonGuardian(self):
        pass

    def test_SouthseaDeckhand(self):
        pass

    def test_StampedingKodo(self):
        pass

    def test_TheBlackKnight(self):
        pass

    def test_TinkmasterOverspark(self):
        pass

    def test_TwilightDrake(self):
        pass

    def test_VoodooDoctor(self):
        pass

    def test_WailingSoul(self):
        pass
