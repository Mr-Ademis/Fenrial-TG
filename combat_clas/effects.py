from dataclasses import dataclass
from random import randint


@dataclass
class EffectsPlayer:
    attack_boost_player: int = 0
    value_attack_boost_player: int = 0
    attack_reduction_player: int = 0
    value_attack_reduction_player: int = 0
    bleeding_player: int = 0
    value_bleeding_player: int = 0
    shield: int = 0

    @property
    def attack_boost_player(self):
        if self.attack_boost_player > 0:
            return self.value_attack_boost_player

    @property
    def attack_reduction_player(self):
        if self.attack_reduction_player > 0:
            return self.value_attack_reduction_player

    @property
    def bleeding_player(self):
        if self.bleeding_player > 0:
            return self.value_bleeding_player

    @property
    def shield(self):
        return self.shield > 0
