import unittest
import csv
import re

from hearthbreaker.agents.basic_agents import DoNothingBot
from hearthbreaker.constants import CHARACTER_CLASS, MINION_TYPE, CARD_RARITY
from hearthbreaker.game_objects import card_lookup
from tests.agents.testing_agents import PredictableAgentWithoutHeroPower
from tests.testing_utils import generate_game_for
from hearthbreaker.cards import *


class CardTest(unittest.TestCase):
    # Make sure that the cards have been initialized correctly based on the data in cards.csv
    def test_all_cards(self):
        fake_game = generate_game_for(StonetuskBoar, StonetuskBoar, DoNothingBot, DoNothingBot)
        overload_re = re.compile("Overload: \((\\d)\)")
        spell_damage_re = re.compile("Spell Damage \\+(\\d)")
        battlecry_re = re.compile("Battlecry: .*")
        deathrattle_re = re.compile("Deathrattle: .*")
        split_re = re.compile("\\s*\\.\\s*")
        file = open("cards.csv", "r")
        reader = csv.DictReader(file)
        for row in reader:
            if row['Implemented?'] == "yes":
                card = card_lookup(row["Name"])
                self.assertEqual(int(row["Cost"]), card.mana, row["Name"])
                self.assertEqual(CHARACTER_CLASS.from_str(row["Class"]), card.character_class, row["Name"])
                self.assertEqual(CARD_RARITY.from_str(row["Rarity"]), card.rarity,
                                 "Expected card '{0}' to have rarity {1}".format(row["Name"], row["Rarity"]))
                if row["Type"] == "Minion":
                    minion = card.create_minion(fake_game.current_player)
                    minion.player = fake_game.current_player
                    minion.game = fake_game
                    for effect in split_re.split(row["Text"]):
                        if effect == "Taunt":
                            self.assertTrue(minion.taunt, "Expected {:s} to have taunt".format(row["Name"]))
                        elif effect == "Divine Shield":
                            self.assertTrue(minion.divine_shield,
                                            "Expected {:s} to have divine shield".format(row["Name"]))
                        elif effect == "Stealth":
                            self.assertTrue(minion.stealth, "Expected {:s} to have stealth".format(row["Name"]))
                        elif effect == "Windfury":
                            self.assertTrue(minion.windfury, "Expected {:s} to have windfury".format(row["Name"]))
                        elif effect == "Charge":
                            self.assertTrue(minion.charge, "Expected {:s} to have charge".format(row["Name"]))
                        elif battlecry_re.match(effect):
                            self.assertTrue(minion.battlecry is not None, "Expected {:s} to have a battlecry".format
                                            (row["Name"]))
                        elif deathrattle_re.match(effect):
                            self.assertTrue(minion.deathrattle is not None, "Expected {:s} to have a deathrattle".format
                                            (row["Name"]))
                        elif overload_re.match(effect) is not None:
                            self.assertEqual(int(overload_re.match(effect).group(1)), card.overload,
                                             ("Expected {:s} to have overload of" +
                                             " {:s}, but had {:d}").format(row["Name"],
                                                                           overload_re.match(effect).group(1),
                                             card.overload))
                        elif spell_damage_re.match(effect) is not None:
                            self.assertEqual(int(spell_damage_re.match(effect).group(1)), minion.spell_damage,
                                             ("Expected {:s} to have spell damage of" +
                                             " {:s}, but had {:d}").format(row["Name"],
                                                                           spell_damage_re.match(effect).group(1),
                                             minion.spell_damage))
                    minion.silence()
                    self.assertEqual(int(row["Attack"]), minion.calculate_attack(), row["Name"])
                    self.assertEqual(int(row["Health"]), minion.health, row["Name"])
                    self.assertEqual(MINION_TYPE.from_str(row["Race"]), card.minion_type, row["Name"])
                elif row["Type"] == "Weapon":
                    weapon = card.create_weapon(fake_game.current_player)
                    self.assertEqual(int(row["Attack"]), weapon.base_attack, row["Name"])
                    self.assertEqual(int(row["Health"]), weapon.durability, row["Name"])

        file.close()

    def test_play_with_one_card(self):
            file = open("cards.csv", "r")
            reader = csv.DictReader(file)
            for row in reader:
                if row["Implemented?"] == "yes":
                    card = card_lookup(row["Name"])
                    game = generate_game_for(type(card), StonetuskBoar, PredictableAgentWithoutHeroPower, DoNothingBot)

                    while not game.game_ended:
                        game.play_single_turn()
            file.close()
