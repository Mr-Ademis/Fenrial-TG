from combat_clas.player import Player
from combat_clas.mob import MobCombat
from combat_clas.effects import EffectsPlayer
from combat_clas.effects_mob import EffectsMob
from spells.combat_skill import *
from sql.bd import Database

bd = Database()


def user(uid):
    """Выгрузка данных игрока из БД"""
    for item in bd.user_combat(uid):
        user = Player(**item)
    return user


def effects_player(uid):
    """Выгрузка эффектов игрока из БД"""
    for item in bd.effects_player(uid):
        effect = EffectsPlayer(**item)
    return effect


def mob(uid, enemies):
    """Выгрузка данных моба"""
    for item in bd.enemies(uid, enemies):
        mob = MobCombat(**item)
    return mob


def enemies_effects(uid, enemies):
    """Выгрузка эффектов моба из БД"""
    for item in bd.effects_enemies(uid, enemies):
        effect = EffectsMob(**item)
    return effect


def combat_move(call):
    """Боевой лог, который тратит ход"""
    uid = call.from_user.id
    player = user(uid)
    player_effects = effects_player(uid)
    hp_player = player.nhp
    skil = skill_mapping.get(call.data, False)
    damage_player = player.damage(skil)
    if player_effects.attack_boost_player():
        damage_player *= player_effects.value_attack_boost_player
    if player_effects.attack_reduction_player():
        damage_player *= player_effects.value_attack_reduction_player
    enemies_1 = mob(uid, 1)
    enemies_1_effects = enemies_effects(uid, 1)
    hp_mob_1 = enemies_1.nhp
    damage_mob_1 = enemies_1.damage
    if enemies_1_effects.attack_boost_mob():
        damage_mob_1 *= enemies_1_effects.value_attack_boost_mob
    if enemies_1_effects.attack_reduction_mob():
        damage_mob_1 *= enemies_1_effects.value_attack_reduction_mob
    if enemies_1_effects.bleeding_mob():
        hp_mob_1 -= enemies_1_effects.value_bleeding_mob
    if player_effects.shield():
        damage_mob_1 = round(damage_mob_1 * 0.75)
    enemies_2 = {}
    if player.number_enemies == 2:
        enemies_2 = mob(uid, 2)
        hp_mob_2 = enemies_2.nhp
        damage_mob_2 = enemies_2.damage
        enemies_2_effects = enemies_effects(uid, 2)
        if enemies_2_effects.attack_boost_mob():
            damage_mob_2 *= enemies_2_effects.value_attack_boost_mob
        if enemies_2_effects.attack_reduction_mob():
            damage_mob_2 *= enemies_2_effects.value_attack_reduction_mob
        if enemies_2_effects.bleeding_mob():
            hp_mob_2 -= enemies_2_effects.value_bleeding_mob
        if player_effects.shield():
            damage_mob_2 = round(damage_mob_2 * 0.75)

    if skil.target == 1 or player.number_enemies == 1:
        if player.target == 1:
            if skil.damage_type == "physical":
                hp_mob_1 -= damage_player * (
                    (100 - enemies_1.physical_protection_mob) / 100
                )
            else:
                hp_mob_1 -= damage_player * (
                    (100 - enemies_1.magical_protection_mob) / 100
                )
        else:
            if skil.damage_type == "physical":
                hp_mob_2 -= damage_player * (
                    (100 - enemies_2.physical_protection_mob) / 100
                )
            else:
                hp_mob_2 -= damage_player * (
                    (100 - enemies_2.magical_protection_mob) / 100
                )
    else:
        if skil.damage_type == "physical":
            hp_mob_1 -= damage_player * (
                (100 - enemies_1.physical_protection_mob) / 100
            )
            hp_mob_2 -= damage_player * (
                (100 - enemies_2.physical_protection_mob) / 100
            )
        else:
            hp_mob_1 -= damage_player * ((100 - enemies_1.magical_protection_mob) / 100)
            hp_mob_2 -= damage_player * ((100 - enemies_2.magical_protection_mob) / 100)

    if player.number_enemies == 1:
        hp_player -= damage_mob_1
    else:
        hp_player -= damage_mob_1 + damage_mob_2

    if player.number_enemies == 1 and hp_mob_1 <=0:
        return функция победы
    else:
        if hp_player <=0:
            return функция смерти
        else:
            проверка на навык и его вид у моба
            изменение параметров игрока(урон...), моба (лечение)
            функция обновления данных в БД
            функция отрисовки картинки боя
            функция наполнения новой клавиатуры с проверкой условий для навыков
            log_combat = f''
            ### Наполнение текстового лога фразами из словарей и параметров функций ###
            функция отправки сообщения с новой картинкой и клавиатурой
