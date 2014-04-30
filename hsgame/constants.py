__author__ = 'Daniel'

class CARD_STATUS:
    BASIC = 1
    EXPERT = 2
    RARE = 3
    EPIC = 4
    LEGENDARY = 5
    SPECIAL = -1


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

    @staticmethod
    def from_str(class_name):
        classes = {
            "MAGE": CHARACTER_CLASS.MAGE,
            "HUNTER": CHARACTER_CLASS.HUNTER,
            "SHAMAN": CHARACTER_CLASS.SHAMAN,
            "WARRIOR": CHARACTER_CLASS.WARRIOR,
            "DRUID": CHARACTER_CLASS.DRUID,
            "PRIEST": CHARACTER_CLASS.PRIEST,
            "PALADIN": CHARACTER_CLASS.PALADIN,
            "ROGUE": CHARACTER_CLASS.ROGUE,
            "WARLOCK": CHARACTER_CLASS.WARLOCK,
        }

        return classes[class_name.upper()]
    
    @staticmethod
    def to_str(class_number):
        classes = {
            CHARACTER_CLASS.MAGE: "Mage",
            CHARACTER_CLASS.HUNTER: "Hunter",
            CHARACTER_CLASS.SHAMAN: "Shaman",
            CHARACTER_CLASS.WARRIOR: "Warrior",
            CHARACTER_CLASS.DRUID: "Druid",
            CHARACTER_CLASS.PRIEST: "Priest",
            CHARACTER_CLASS.PALADIN: "Paladin",
            CHARACTER_CLASS.ROGUE: "Rogue",
            CHARACTER_CLASS.WARLOCK: "Warlock",
        }
        return classes[class_number]


class MINION_TYPE:
    NONE = 0
    BEAST = 1
    MURLOC = 2