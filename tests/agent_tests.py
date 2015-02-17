import random
import unittest
from hearthbreaker.agents.basic_agents import RandomAgent
from hearthbreaker.cards import GoldshireFootman, MurlocRaider, BloodfenRaptor, FrostwolfGrunt, RiverCrocolisk, \
    IronfurGrizzly, MagmaRager, SilverbackPatriarch, ChillwindYeti, SenjinShieldmasta, BootyBayBodyguard, \
    FenCreeper, BoulderfistOgre, WarGolem, Shieldbearer, FlameImp, YoungPriestess, DarkIronDwarf, DireWolfAlpha, \
    Voidwalker, HarvestGolem, KnifeJuggler, ShatteredSunCleric, ArgentSquire, Doomguard, Soulfire, DefenderOfArgus, \
    AbusiveSergeant, NerubianEgg, KeeperOfTheGrove
from hearthbreaker.cards.heroes import Guldan, Malfurion
from hearthbreaker.engine import Game, Deck


class TestAgents(unittest.TestCase):

    def setUp(self):
        random.seed(1857)

    def test_RandomAgent(self):
        deck1 = Deck([
            GoldshireFootman(),
            GoldshireFootman(),
            MurlocRaider(),
            MurlocRaider(),
            BloodfenRaptor(),
            BloodfenRaptor(),
            FrostwolfGrunt(),
            FrostwolfGrunt(),
            RiverCrocolisk(),
            RiverCrocolisk(),
            IronfurGrizzly(),
            IronfurGrizzly(),
            MagmaRager(),
            MagmaRager(),
            SilverbackPatriarch(),
            SilverbackPatriarch(),
            ChillwindYeti(),
            ChillwindYeti(),
            KeeperOfTheGrove(),
            KeeperOfTheGrove(),
            SenjinShieldmasta(),
            SenjinShieldmasta(),
            BootyBayBodyguard(),
            BootyBayBodyguard(),
            FenCreeper(),
            FenCreeper(),
            BoulderfistOgre(),
            BoulderfistOgre(),
            WarGolem(),
            WarGolem(),
        ], Malfurion())

        deck2 = Deck([
            Shieldbearer(),
            Shieldbearer(),
            FlameImp(),
            FlameImp(),
            YoungPriestess(),
            YoungPriestess(),
            DarkIronDwarf(),
            DarkIronDwarf(),
            DireWolfAlpha(),
            DireWolfAlpha(),
            Voidwalker(),
            Voidwalker(),
            HarvestGolem(),
            HarvestGolem(),
            KnifeJuggler(),
            KnifeJuggler(),
            ShatteredSunCleric(),
            ShatteredSunCleric(),
            ArgentSquire(),
            ArgentSquire(),
            Doomguard(),
            Doomguard(),
            Soulfire(),
            Soulfire(),
            DefenderOfArgus(),
            DefenderOfArgus(),
            AbusiveSergeant(),
            AbusiveSergeant(),
            NerubianEgg(),
            NerubianEgg(),
        ], Guldan())

        game = Game([deck1, deck2], [RandomAgent(), RandomAgent()])
        game.pre_game()
        game.current_player = game.players[1]

        game.play_single_turn()

        self.assertEqual(0, len(game.current_player.minions))

        game.play_single_turn()
        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(3, game.current_player.minions[1].health)
        self.assertEqual("Young Priestess", game.current_player.minions[0].card.name)

        game.play_single_turn()
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Frostwolf Grunt", game.current_player.minions[0].card.name)

        game.play_single_turn()
        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(28, game.other_player.hero.health)
        self.assertEqual(3, len(game.current_player.minions))
        self.assertEqual("Dire Wolf Alpha", game.current_player.minions[2].card.name)

        for turn in range(0, 13):
            game.play_single_turn()
            self.assertFalse(game.game_ended)

        game.play_single_turn()

        self.assertEqual(0, game.current_player.hero.health)
        self.assertEqual(21, game.other_player.hero.health)

        self.assertTrue(game.game_ended)
