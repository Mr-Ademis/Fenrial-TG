from dataclasses import dataclass
from random import randint


@dataclass
class EffectsMob:
    attack_boost_mob: int = 0
    value_attack_boost_mob: int = 0
    attack_reduction_mob: int = 0
    value_attack_reduction_mob: int = 0
    bleeding_mob: int = 0
    value_bleeding_mob: int = 0

    @property
    def attack_boost_mob(self):
        if self.attack_boost_mob > 0:
            return self.value_attack_boost_mob

    @property
    def attack_reduction_mob(self):
        return self.attack_reduction_mob > 0

    @property
    def bleeding_mob(self):
        if self.bleeding_mob > 0:
            return self.value_bleeding_mob
