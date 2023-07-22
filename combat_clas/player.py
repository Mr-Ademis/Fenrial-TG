from dataclasses import dataclass
from random import randint


@dataclass
class Player:
    clas: int = 0
    nhp: int = 0
    hp: int = 0
    mp: int = 0
    status: int = 0
    number_enemies: int = 1
    target: int = 1
    move_index: int = 0
    cooldown_potion: int = 0
    evasion: int = 0
    intellect: int = 0
    attack_player: int = 0
    attack_player_stack: int = 0
    skill_1: int = 0
    skill_1_stack: int = 0
    skill_2: int = 0
    skill_2_stack: int = 0
    skill_3: int = 0
    skill_3_stack: int = 0
    skill_4: int = 0
    skill_4_stack: int = 0
    skill_5: int = 0
    skill_5_stack: int = 0

    def skill_number(self, skill) -> bool:
        skill_mapping = {
            1: self.skill_1,
            2: self.skill_2,
            3: self.skill_3,
            4: self.skill_4,
            5: self.skill_5,
        }
        return skill_mapping.get(skill.number, False)

    def addiction_number(self, skill) -> bool:
        addiction_mapping = {
            1: self.skill_1_stack,
            2: self.skill_2_stack,
            3: self.skill_3_stack,
            4: self.skill_4_stack,
            5: self.skill_5_stack,
            10: self.attack_player_stack,
        }
        return addiction_mapping.get(skill.addiction, False)

    def is_ready_skill(self, skill) -> bool:
        if (
            self.move_index >= self.skill_number(skill) + skill.cooldown_skill
            and self.mp >= skill.skill_cost
            and (skill.addiction == 0 or self.addiction_number(skill) > 1)
        ):
            return skill.as_button()
        return False

    def damage(self, skill) -> bool:
        if skill.damage_type == "physical":
            attack_modifier = self.attack_player * skill.coefficient
        else:
            attack_modifier = self.intellect * skill.coefficient

        self.dmg = randint(int(attack_modifier * 0.9), int(attack_modifier * 1.1))

        if skill.addiction == 10:
            self.dmg *= self.addiction_number(skill)

        return self.dmg

    def is_critical_hit(self):
        return randint(1, 100) <= 3

    def is_evasion(self):
        return randint(1, 100) <= self.evasion

    @property
    def hp_percent(self):
        if self.nhp != 0:
            return (
                1
                if int(self.nhp / self.hp * 100) // 10 == 0
                else int(self.nhp / self.hp * 100) // 10
            )
        else:
            return 0

    @property
    def mp_percent(self):
        if self.mp != 0:
            return 1 if self.mp // 10 == 0 else self.mp // 10
        else:
            return 0
