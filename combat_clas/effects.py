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

    @property неправильно 
    def attack_boost_player(self): неправильно
        if self.attack_boost_player > 0:
            return self.value_attack_boost_player

    @property неправильно
    def attack_reduction_player(self): неправильно
        if self.attack_reduction_player > 0:
            return self.value_attack_reduction_player

    @property
    def bleeding_player(self): неправильно
        if self.bleeding_player > 0:
            return self.value_bleeding_player

    @property
    def shield(self): неправильно
        return self.shield > 0
