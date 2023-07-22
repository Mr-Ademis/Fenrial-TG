from dataclasses import dataclass
from random import randint


@dataclass
class MobCombat:
    name: str = ""
    vid: str = ""
    lvl: int = 0
    attack: int = 0
    picture_attack = ""
    nhp: int = 0
    hp: int = 0
    physical_protection_mob: int = 0
    magical_protection_mob: int = 0
    defense_player: int = 0

    @property
    def damage(self):
        return randint(
            int(self.attack * (100 - self.defense_player) / 100),
            int(self.attack * (100 - self.defense_player) / 100),
        )
