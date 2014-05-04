__author__ = 'Daniel'

import unittest
import csv

class CardTest(unittest.TestCase):

    def test_AllCards(self):
        file = open("cards.csv", "r")
        reader = csv.DictReader(file)
        for row in reader:
            if row['Implemented?'] == "yes":
                print(row[" Name"])

        file.close()