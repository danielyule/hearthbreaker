class CARD_RARITY:
    FREE = 1
    COMMON = 2
    RARE = 3
    EPIC = 4
    LEGENDARY = 5

    __rarities = {
        "FREE": FREE,
        "COMMON": COMMON,
        "RARE": RARE,
        "EPIC": EPIC,
        "LEGENDARY": LEGENDARY,
    }

    @staticmethod
    def from_str(rarity_name):
        return CARD_RARITY.__rarities[rarity_name.upper()]

    @staticmethod
    def to_str(class_number):
        classes = dict(zip(CARD_RARITY.__rarities.values(), CARD_RARITY.__rarities.keys()))
        return classes[class_number].capitalize()


class CHARACTER_CLASS:
    ALL = 0
    MAGE = 1
    HUNTER = 2
    SHAMAN = 3
    WARRIOR = 4
    DRUID = 5
    PRIEST = 6
    PALADIN = 7
    ROGUE = 8
    WARLOCK = 9
    LORD_JARAXXUS = 10
    DREAM = 11

    __classes = {
        "MAGE": MAGE,
        "HUNTER": HUNTER,
        "SHAMAN": SHAMAN,
        "WARRIOR": WARRIOR,
        "DRUID": DRUID,
        "PRIEST": PRIEST,
        "PALADIN": PALADIN,
        "ROGUE": ROGUE,
        "WARLOCK": WARLOCK,
        "LORD_JARAXXUS": LORD_JARAXXUS,
        "DREAM": DREAM,
        "": ALL,
    }

    @staticmethod
    def from_str(class_name):
        return CHARACTER_CLASS.__classes[class_name.upper()]

    @staticmethod
    def to_str(class_number):
        classes = dict(zip(CHARACTER_CLASS.__classes.values(), CHARACTER_CLASS.__classes.keys()))
        return classes[class_number].capitalize()


class MINION_TYPE:
    ALL = -1
    NONE = 0
    BEAST = 1
    MURLOC = 2
    DRAGON = 3
    GIANT = 4
    DEMON = 5
    PIRATE = 6
    TOTEM = 7
    MECH = 8

    __types = {
        "": NONE,
        "BEAST": BEAST,
        "MURLOC": MURLOC,
        "DRAGON": DRAGON,
        "GIANT": GIANT,
        "DEMON": DEMON,
        "PIRATE": PIRATE,
        "TOTEM": TOTEM,
        "MECH": MECH,
    }

    @staticmethod
    def from_str(type_name):

        return MINION_TYPE.__types[type_name.upper()]

    @staticmethod
    def to_str(minion_number):
        types = dict(zip(MINION_TYPE.__types.values(), MINION_TYPE.__types.keys()))
        return types[minion_number].capitalize()
