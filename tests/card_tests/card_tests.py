import json
import unittest
import re

from hearthbreaker.agents.basic_agents import DoNothingAgent
from hearthbreaker.constants import CHARACTER_CLASS, MINION_TYPE, CARD_RARITY
from hearthbreaker.engine import card_lookup
from tests.agents.testing_agents import PlayAndAttackAgent
from tests.card_tests.id_mapping import id_mappings
from tests.testing_utils import generate_game_for
from hearthbreaker.cards import *


class TestUtilities:
    def assertSparePart(self, card):
        self.assertIn(card.name, ["Finicky Cloakfield", "Emergency Coolant", "Rusty Horn", "Armor Plating",
                                  "Reversing Switch", "Time Rewinder", "Whirling Blades"],
                      "'{}' was not a spare part card".format(card.name))

    def assertNotSparePart(self, card):
        self.assertNotIn(card.name, ["Finicky Cloakfield", "Emergency Coolant", "Rusty Horn", "Armor Plating",
                                     "Reversing Switch", "Time Rewinder", "Whirling Blades"],
                         "'{}' was a spare part card".format(card.name))


class CardTest(unittest.TestCase):
    # Make sure that the cards have been initialized correctly based on the data from Hearthstone JSON
    def test_all_cards(self):
        fake_game = generate_game_for(StonetuskBoar, StonetuskBoar, DoNothingAgent, DoNothingAgent)
        overload_re = re.compile("Overload: \\((\\d)\\)")
        spell_damage_re = re.compile("Spell Damage \\+(\\d)")
        battlecry_re = re.compile("Battlecry: .*")
        deathrattle_re = re.compile("Deathrattle: .*")
        split_re = re.compile("\\s*\\.|\n\\s*")
        bold_tag_re = re.compile("</?b>")
        file = open("AllSets.enUS.json", "r", encoding="UTF-8")
        card_dict = json.load(file)
        not_implemented = []
        total_cards = 0
        for card_set in ['Classic', "Basic", "Curse of Naxxramas", "Goblins vs Gnomes", "Blackrock Mountain",
                         "The Grand Tournament", "Reward", "Promotion"]:
            for card_info in card_dict[card_set]:
                if card_info["type"] in ['Minion', 'Spell', 'Weapon', 'Secret']:
                    total_cards += 1
                    try:
                        card = card_lookup(id_mappings[card_info["id"]])
                    except KeyError:
                        if 'collectible' in card_info and card_info['collectible']:
                            not_implemented.append("{}: ({})".format(card_info["name"], card_info['id']))
                        continue
                    if "cost" in card_info:
                        self.assertEqual(int(card_info["cost"]), card.mana,
                                         "Expected {} to have cost {}.  Got {}".format(
                                         card_info["name"], card_info["cost"], card.mana))
                    if "playerClass" in card_info:
                        self.assertEqual(CHARACTER_CLASS.from_str(card_info["playerClass"]), card.character_class,
                                         "Expected {} to have class {}.  Got {}".format(
                                             card_info["name"], card_info["playerClass"],
                                             CHARACTER_CLASS.to_str(card.character_class)))
                    else:
                        self.assertEqual(CHARACTER_CLASS.ALL, card.character_class,
                                         "Expected {} to have no class.  Got {}".format(
                                             card_info["name"], CHARACTER_CLASS.to_str(card.character_class)))
                    if "rarity" in card_info:
                        self.assertEqual(CARD_RARITY.from_str(card_info["rarity"]), card.rarity,
                                         "Expected card {} to have rarity {}.  Got {}".format(
                                             card_info["name"], card_info["rarity"], CARD_RARITY.to_str(card.rarity)))
                    if "collectible" in card_info:
                        if card_info['collectible']:
                            self.assertTrue(card.collectible, "Expected card {} to be collectible".format(
                                card_info['name']))
                        else:
                            self.assertFalse(card.collectible, "Expected card {} not to be collectible".format(
                                card_info['name']))
                    if card_info["type"] == "Minion":
                        minion = card.create_minion(fake_game.current_player)
                        minion.player = fake_game.current_player
                        minion.game = fake_game
                        minion.card = card
                        minion.add_to_board(0)
                        if "text" in card_info:
                            if card_info['name'] == "Argent Horserider":
                                print(split_re.split(re.sub(bold_tag_re, "", card_info["text"])))
                            for effect in split_re.split(re.sub(bold_tag_re, "", card_info["text"])):
                                if effect == "Taunt":
                                    self.assertTrue(minion.taunt,
                                                    "Expected {:s} to have taunt".format(card_info["name"]))
                                elif effect == "Divine Shield":
                                    self.assertTrue(minion.divine_shield,
                                                    "Expected {:s} to have divine shield".format(card_info["name"]))
                                elif effect == "Stealth":
                                    self.assertTrue(minion.stealth,
                                                    "Expected {:s} to have stealth".format(card_info["name"]))
                                elif effect == "Windfury":
                                    self.assertTrue(minion.windfury(),
                                                    "Expected {:s} to have windfury".format(card_info["name"]))
                                elif effect == "Charge":
                                    self.assertTrue(minion.charge(),
                                                    "Expected {:s} to have charge".format(card_info["name"]))
                                elif battlecry_re.match(effect):
                                    self.assertTrue(card.battlecry is not None,
                                                    "Expected {:s} to have a battlecry".format
                                                    (card_info["name"]))
                                elif deathrattle_re.match(effect):
                                    self.assertTrue(minion.deathrattle is not None,
                                                    "Expected {:s} to have a deathrattle".format
                                                    (card_info["name"]))
                                elif overload_re.match(effect) is not None:
                                    self.assertEqual(int(overload_re.match(effect).group(1)), card.overload,
                                                     ("Expected {:s} to have overload of" +
                                                     " {:s}, but had {:d}").format(card_info["name"],
                                                                                   overload_re.match(effect).group(1),
                                                     card.overload))
                                elif spell_damage_re.match(effect) is not None:
                                    self.assertEqual(int(spell_damage_re.match(effect).group(1)),
                                                     minion.player.spell_damage,
                                                     ("Expected {:s} to have spell damage of" +
                                                     " {}, but had {}").format(card_info["name"],
                                                                               spell_damage_re.match(effect).group(1),
                                                     minion.player.spell_damage))
                        minion.silence()
                        self.assertEqual(int(card_info["attack"]), minion.calculate_attack(),
                                         "Expected {} to have attack of {}.  Got {}".format(
                                         card_info["name"], card_info["attack"], minion.calculate_attack()))
                        self.assertEqual(int(card_info["health"]), minion.health,
                                         "Expected {} to have health of {}.  Got {}".format(
                                         card_info["name"], card_info["health"], minion.health))
                        if "race" in card_info:
                            self.assertEqual(MINION_TYPE.from_str(card_info["race"]), card.minion_type,
                                             "Expected {} to have race {}.  Got {}".format(
                                             card_info["name"], card_info["race"],
                                             MINION_TYPE.to_str(card.minion_type)))
                        else:
                            self.assertEqual(MINION_TYPE.NONE, card.minion_type,
                                             "Expected {} to have no race.  Got {}".format(
                                                 card_info["name"], MINION_TYPE.to_str(card.minion_type)))
                    elif card_info["type"] == "Weapon":
                        weapon = card.create_weapon(fake_game.current_player)
                        self.assertEqual(int(card_info["attack"]), weapon.base_attack,
                                         "Expected {} to have attack of {}.  Got {}".format(
                                         card_info["name"], card_info["attack"], weapon.base_attack))
                        self.assertEqual(int(card_info["durability"]), weapon.durability,
                                         "Expected {} to have durability of {}.  Got {}".format(
                                         card_info["name"], card_info["durability"], weapon.durability))

        file.close()
        if len(not_implemented) > 0:
            print("{} of {} cards implemented".format(total_cards - len(not_implemented), total_cards))
            print("Cards not implemented:")
            for card in not_implemented:
                print("  - {}".format(card))

    def test_play_with_one_card(self):
        file = open("AllSets.enUS.json", "r", encoding="UTF-8")
        card_dict = json.load(file)
        for card_set in ['Classic', "Basic", "Curse of Naxxramas", "Goblins vs Gnomes", "Blackrock Mountain"]:

            for card_info in card_dict[card_set]:
                if 'collectible' in card_info and card_info['collectible'] and card_info["type"] != "Hero":
                    try:
                        card = card_lookup(card_info["name"])
                    except KeyError:
                        continue
                    game = generate_game_for(type(card), StonetuskBoar, PlayAndAttackAgent, DoNothingAgent)
                    try:
                        while not game.game_ended:
                            game.play_single_turn()
                    except Exception as e:
                        print(card)
                        raise e
            file.close()
