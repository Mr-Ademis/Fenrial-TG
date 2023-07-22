from dataclasses import dataclass


@dataclass
class CombatSkill:
    icon: str = ""
    button_text: str = ""
    payload: str = ""
    picture: str = ""
    cost: int = 0
    target: int = 1
    coefficient: int = 1
    cooldown: int = 0
    damage_type: str = ""
    number: int = 0
    addiction: int = 0

    def as_button(self) -> str:
        return f"{self.icon}{self.button_text}({self.cost})"


insidious_blow = CombatSkill(
    icon="🗡",
    button_text="КУ",
    payload="insidious_blow",
    picture="Fenrial_TG/spells/img/jJ-SsZhfOqU.jpg",
    cost=7,
    coefficient=3,
    cooldown=0,
    damage_type="physical",
    number=1,
    addiction=0,
)

gutting = CombatSkill(
    icon="⚔️",
    button_text="Птр",
    payload="gutting",
    picture="Fenrial_TG/spells/img/jJ-SsZhfOqU.jpg",
    cost=12,
    coefficient=5,
    cooldown=0,
    damage_type="physical",
    number=2,
    addiction=1,
)


skill_mapping = {"insidious_blow": insidious_blow, "gutting": gutting}

skill_mapping_clas_1 = {"insidious_blow": insidious_blow, "gutting": gutting}
