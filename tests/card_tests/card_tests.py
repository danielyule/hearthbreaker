import json
import unittest
import re

from hearthbreaker.agents.basic_agents import DoNothingAgent
from hearthbreaker.constants import CHARACTER_CLASS, MINION_TYPE, CARD_RARITY
from hearthbreaker.game_objects import card_lookup
from tests.agents.testing_agents import PlayAndAttackAgent
from tests.testing_utils import generate_game_for
from hearthbreaker.cards import *


class CardTest(unittest.TestCase):
    # Make sure that the cards have been initialized correctly based on the data from Hearthstone JSON
    def test_all_cards(self):
        fake_game = generate_game_for(StonetuskBoar, StonetuskBoar, DoNothingAgent, DoNothingAgent)
        overload_re = re.compile("Overload: \\((\\d)\\)")
        spell_damage_re = re.compile("Spell Damage \\+(\\d)")
        battlecry_re = re.compile("Battlecry: .*")
        deathrattle_re = re.compile("Deathrattle: .*")
        split_re = re.compile("\\s*\\.\\s*")
        bold_tag_re = re.compile("</?b>")
        file = open("AllSets.enUS.json", "r", encoding="UTF-8")
        card_dict = json.load(file)
        not_implemented = []
        for card_set in ['Expert', "Basic", "Curse of Naxxramas", "Goblins vs Gnomes"]:
            for card_info in card_dict[card_set]:
                if 'collectible' in card_info and card_info['collectible'] and card_info["type"] != "Hero":
                    try:
                        card = card_lookup(card_info["name"])
                    except KeyError:
                        not_implemented.append(card_info["name"])
                        continue
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
                    self.assertEqual(CARD_RARITY.from_str(card_info["rarity"]), card.rarity,
                                     "Expected card {} to have rarity {}.  Got {}".format(
                                         card_info["name"], card_info["rarity"], CARD_RARITY.to_str(card.rarity)))
                    if card_info["type"] == "Minion":
                        minion = card.create_minion(fake_game.current_player)
                        minion.player = fake_game.current_player
                        minion.game = fake_game
                        minion.card = card
                        minion.add_to_board(0)
                        if "text" in card_info:
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
                                    self.assertTrue(minion.windfury,
                                                    "Expected {:s} to have windfury".format(card_info["name"]))
                                elif effect == "Charge":
                                    self.assertTrue(minion.charge,
                                                    "Expected {:s} to have charge".format(card_info["name"]))
                                elif battlecry_re.match(effect):
                                    self.assertTrue(minion.battlecry is not None,
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
                                    self.assertEqual(int(spell_damage_re.match(effect).group(1)), minion.spell_damage,
                                                     ("Expected {:s} to have spell damage of" +
                                                     " {}, but had {}").format(card_info["name"],
                                                                               spell_damage_re.match(effect).group(1),
                                                     minion.spell_damage))
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
            print("Cards not implemented: {}".format(str(not_implemented)))

    def test_play_with_one_card(self):
        file = open("AllSets.enUS.json", "r", encoding="UTF-8")
        card_dict = json.load(file)
        for card_set in ['Expert', "Basic", "Curse of Naxxramas", "Goblins vs Gnomes"]:

            for card_info in card_dict[card_set]:
                if 'collectible' in card_info and card_info['collectible'] and card_info["type"] != "Hero":
                    try:
                        card = card_lookup(card_info["name"])
                    except KeyError:
                        continue
                    game = generate_game_for(type(card), StonetuskBoar, PlayAndAttackAgent, DoNothingAgent)

                    while not game.game_ended:
                        game.play_single_turn()
            file.close()
