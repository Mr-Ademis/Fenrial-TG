import telebot
from telebot import types

from random import randint, choice
from datetime import datetime, timedelta
import time
import os
import re
import time
import threading

from PIL import Image, ImageFont, ImageDraw

import engine
import tok
import non_combat
from text import text
from sql import bd

bd = bd.Database()


bot = telebot.TeleBot(tok.tok)

### Словари
clas = {0: "Без класса", 1: "Воин", 2: "Ассасин", 3: "Маг"}
bag = {0: 14, 1: 21}

__QUERY_BATTLE_ADD_ = (
    "INSERT INTO battle VALUES("
    "default, %(vkid)s, default, 1, %(nhp)s, %(hp)s, %(mp)s, default, "
    " %(name_mob)s, %(vid_mob)s, %(lvl_mob)s, %(attack_mob)s, %(physical_protection_mob)s,"
    "%(magical_protection_mob)s, %(nhp_mob)s, %(hp_mob)s, default,"
    " default, default, default, default, default, default, default, default, default, %(def_player)s, %(evasion)s, %(attack_player)s, %(intellect)s)"
)


__QUERY_DELETE_BATTLE = "DELETE FROM battle WHERE vkid = %(vkid)s"

user = {}


def user_battle(uid):
    """Выгрузка таблицы бой из БД для удобства"""
    for item in bd.battle(uid):
        user = {
            "nhp": item["nhp"],
            "status": item["status"],
            "hp": item["hp"],
            "mp": item["mp"],
            "cooldown_potion": item["cooldown_potion"],
            "name_mob": item["name_mob"],
            "vid_mob": item["vid_mob"],
            "lvl_mob": item["lvl_mob"],
            "attack_mob": item["attack_mob"],
            "physical_protection_mob": item["physical_protection_mob"],
            "magical_protection_mob": item["magical_protection_mob"],
            "nhp_mob": item["nhp_mob"],
            "hp_mob": item["hp_mob"],
            "def_player": item["def_player"],
            "evasion": item["evasion"],
            "attack_player": item["attack_player"],
            "intellect": item["intellect"],
            "status_skill_10": item["status_skill_10"],
            "status_skill_1": item["status_skill_1"],
            "status_skill_2": item["status_skill_2"],
            "status_skill_3": item["status_skill_3"],
            "status_skill_4": item["status_skill_4"],
            "status_skill_5": item["status_skill_5"],
            "status_skill_6": item["status_skill_6"],
        }
        return user

def nhp_update(uid, nhp):
    """Обновляем хп игрока на указанное"""
    bd.exec(f"UPDATE battle SET nhp = {nhp} where vkid = {uid}", None)
    engine.unloading_players()


def nmp_update(uid, nmp):
    """Обновляем мп игрока на указанное"""
    bd.exec(f"UPDATE battle SET mp = {nmp} where vkid = {uid}", None)
    engine.unloading_players()


def hp_mp_update(uid, nhp, nmp):
    """Обновляем хп, мп игрока на указанное"""
    bd.exec(f"UPDATE players SET nhp = {nhp}, nmp = {nmp} where vkid = {uid}", None)
    engine.unloading_players()


def image_combat(
    uid, substrate, player, user, spell_player, spell_mob, course_of_battle
):
    im = Image.open(substrate)
    pointsize = 32
    font = "Fenrial_TG/days2.ttf"
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(font, pointsize)

    portr = Image.open(f"Fenrial_TG/moobs/f_{player['clas']}.jpg")
    im.paste(portr, (0, 0))

    ### Бары хп, мп ###
    hp_p_b = str(int((((user["nhp"] * 100) / user["hp"]) // 10) * 10))
    if hp_p_b == "0" and user["nhp"] != 0:
        hp_p_b = "10"

    hp_p = Image.open(f"Fenrial_TG/bar_mp_hp/f_hp_{hp_p_b}.jpg")
    im.paste(hp_p, (205, 40))

    mp_p_b = str(int((user["mp"] // 10) * 10))
    if user["mp"] != 0 and mp_p_b == "0":
        mp_p_b = "10"

    if user["mp"] != 0:
        mp_p = Image.open(f"Fenrial_TG/bar_mp_hp/f_mp_{mp_p_b}.jpg")
        im.paste(mp_p, (205, 95))

    hp_m_b = str((int(((user["nhp_mob"] * 100) / user["hp_mob"]) // 10) * 10))
    if user["nhp_mob"] != 0 and hp_m_b == "0":
        hp_m_b = "10"

    hp_b = Image.open(f"Fenrial_TG/bar_mp_hp/f_mob_{hp_m_b}.jpg")
    im.paste(hp_b, (88, 796))

    ### Навыки ###

    player_skil = Image.open(spell_player)
    im.paste(player_skil, (211, 167))
    mob_skil = Image.open(spell_mob)
    im.paste(mob_skil, (85, 642))

    if 0 < user["status_skill_4"] <= 4 and player["clas"] == 2:
        krv_img = Image.open(f"Fenrial_TG/spells/krv.jpg")
        im.paste(krv_img, (225, 715))

    if 0 < user["status_skill_6"] == 1 and player["clas"] == 1:
        krv_img = Image.open(f"Fenrial_TG/spells/IePQ234E7o.jpg")
        im.paste(krv_img, (225, 715))

    if user["status_skill_4"] > 3 and player["clas"] == 1:
        krv_img = Image.open(f"Fenrial_TG/spells/ertqwe.jpg")
        im.paste(krv_img, (300, 715))

    if user["status_skill_5"] > 3 and player["clas"] == 1:
        krv_img = Image.open(f"Fenrial_TG/spells/retwertw.jpg")
        im.paste(krv_img, (360, 160))

    if user["status_skill_1"] != 0 and player["clas"] == 3:
        krv_img = Image.open(f"Fenrial_TG/spells/sh.jpg")
        im.paste(krv_img, (360, 160))

    ### Текст ###
    regen_hp = ""
    regen_mp = ""

    regen_player_hp = 0
    regen_player_mp = 0

    match player["clas"]:
        case 0:
            regen_player_hp = 1
            regen_player_mp = 1
        case 1:
            regen_player_hp = int(player["stamina"] / 2.5)
            regen_player_mp = int(player["intellect"] / 2.5)
        case 2:
            regen_player_hp = int(player["stamina"] / 2.5)
            regen_player_mp = int(player["intellect"] / 2.5)
        case 3:
            regen_player_hp = int(player["stamina"] / 2.5)
            regen_player_mp = int(player["intellect"] / 2.5)

    if course_of_battle != 0:
        regen_hp = f"(+{regen_player_hp})"
        regen_mp = f"(+{regen_player_mp})"
    hp = f'{user["nhp"]}/{user["hp"]} {regen_hp}'
    hp = f"{(17 - len(hp))*' '}{hp}"
    mp = f'{user["mp"]}/100 {regen_mp}'
    mp = f"{(18 - len(mp))*' '}{mp}"

    name_m = f'{user["name_mob"]}'
    name_m = f"{(18 - len(name_m))*' '}{name_m}"

    hp_m = f'{user["nhp_mob"]}/{user["hp_mob"]}'
    hp_m = f"{(9 - len(hp_m))*' '}{hp_m}"

    if user["cooldown_potion"] == 0:
        potion = ""
    else:
        potion = f'{user["cooldown_potion"]}'

    coordinates = {
        "зелья хп": [120, 200, potion],
        "хп": [210, 40, hp],
        "мп": [210, 95, mp],
        "хп моба": [555, 792, hp_m],
        "название моба": [445, 752, name_m],
    }

    def draw_text(x_cor: int, y_cor: int, text: str) -> None:
        """Функция отрисовки текста"""
        for i in ((-5, -5), (5, -5), (-5, 5), (5, 5), (0, 0)):
            draw.text((x_cor + i[0], y_cor + i[1]), text, font=font, fill="black")
        draw.text((x_cor + i[0], y_cor + i[1]), text, font=font, fill="white")

    # Переберем словарь пареметров и вызовим функцию отрисовки для каждого
    for item in coordinates.values():
        draw_text(item[0], item[1], item[2])

    im.save(f"Fenrial_TG/fights/fights{uid}.jpg")
    return f"Fenrial_TG/fights/fights{uid}.jpg"


class keyboard_download(object):
    def __init__(self):
        """Конструктор клавиатуры"""
        self.bt1_0 = self.bt2_0 = self.bt1_2 = self.bt2_2 = self.bt3_2 = None
        self.bt4_2 = self.bt6 = self.bt7 = self.bt8 = self.bt9 = None
        self.create_keyboard()

    def create_button(self, label: str, callback: str):
        return telebot.types.InlineKeyboardButton(text=label, callback_data=callback)

    def create_keyboard(self):
        self.bt1_0 = self.create_button("💢Вып (10)", "💢Выпад")
        self.bt2_0 = self.create_button("💥ОВ (15)", "💥Опасный выпад")

        self.bt1_2 = self.create_button("🗡КУ (7)", "🗡Коварный удар")
        self.bt2_2 = self.create_button("💥УВ (12)", "💥Удар в спину")
        self.bt3_2 = self.create_button("⚔Птр (12)", "⚔Потрошение")
        self.bt4_2 = self.create_button("👁О (12)", "👁Ослепление")
        self.bt5_2 = self.create_button("💔Рас (7)", "💔Рассечение")

        self.bt1_3 = self.create_button("💫ЧС (7)", "💫Чародейские стрелы")
        self.bt2_3 = self.create_button("💎МЩ (12)", "💎Морозный щит")
        self.bt3_3 = self.create_button("🔥ОШ (17)", "🔥Огненный шар")
        self.bt4_3 = self.create_button("✨Скч(12)", "✨Скачок")
        self.bt5_3 = self.create_button("❄КЛ (20)", "❄Кольцо льда")

        self.bt1_1 = self.create_button("✊🏻МУ(20)", "✊🏻Мощный удар")
        self.bt2_1 = self.create_button("🔥УГ(12)", "🔥Удар героя")
        self.bt3_1 = self.create_button("💥Р(12)", "💥Раскол брони")
        self.bt4_1 = self.create_button("👹ДК(12)", "👹Деморализующий крик")
        self.bt5_1 = self.create_button("♨БК(12)", "♨Боевой крик")

        self.bt6 = self.create_button("🗡Атака", "🗡Атака")
        self.bt7 = self.create_button("🧪", "🧪Зелья")
        self.bt8 = self.create_button("📖", "spell_book_battle")
        self.bt9 = self.create_button("👞", "👞Сбежать запрос")


keyb = keyboard_download()


def keyboard(player, user, inventor):
    buut = telebot.types.InlineKeyboardMarkup(row_width=3)
    kbb = []
    kba = []
    match player["clas"]:
        case 0:
            if user["mp"] >= 15 and user["status_skill_3"] == 0:
                kbb = kbb + [keyb.bt1_0, keyb.bt2_0]
            elif user["mp"] >= 10:
                kbb.append(keyb.bt1_0)
        case 1:
            if user["mp"] >= 20 and user["status_skill_1"] >= 2:
                kbb.append(keyb.bt1_1)
            if user["mp"] >= 12 and user["status_skill_2"] == 0:
                kbb.append(keyb.bt2_1)
            if user["mp"] >= 12 and user["status_skill_3"] == 0:
                kbb.append(keyb.bt3_1)
            if user["mp"] >= 12 and user["status_skill_4"] == 0:
                kbb.append(keyb.bt4_1)
            if user["mp"] >= 12 and user["status_skill_5"] == 0:
                kbb.append(keyb.bt5_1)
        case 2:
            if user["mp"] >= 7:
                kbb.append(keyb.bt1_2)
            if user["mp"] >= 12 and user["status_skill_1"] == 0 and user["status"] < 2:
                kbb.append(keyb.bt2_2)
            if user["mp"] >= 12 and user["status_skill_2"] >= 2:
                kbb.append(keyb.bt3_2)
            if user["status"] > 1 and user["mp"] >= 12 and user["status_skill_3"] == 0:
                kbb.append(keyb.bt4_2)
            if user["mp"] >= 7 and user["status_skill_4"] == 0:
                kbb.append(keyb.bt5_2)
        case 3:
            if user["mp"] >= 7:
                kbb.append(keyb.bt1_3)
            if user["mp"] >= 12 and user["status_skill_1"] == 0:
                kbb.append(keyb.bt2_3)
            if user["mp"] >= 17 and user["status_skill_2"] == 0:
                kbb.append(keyb.bt3_3)
            if user["status"] > 1 and user["mp"] >= 12 and user["status_skill_3"] == 0:
                kbb.append(keyb.bt4_3)
            if user["mp"] >= 22 and user["status_skill_4"] == 0:
                kbb.append(keyb.bt5_3)

    buut.add(*kbb)
    potion_hp = 0
    potion_mp = 0
    for i in inventor.keys():
        if inventor[i] == 103:
            item_quantity = "quantity_"
            item_quantity = item_quantity + re.search(r"\d+", i)[0]
            potion_hp = f"{inventor[item_quantity]}"
            break
    for i in inventor.keys():
        if inventor[i] == 104:
            item_quantity = "quantity_"
            item_quantity = item_quantity + re.search(r"\d+", i)[0]
            potion_mp = f"{inventor[item_quantity]}"
            break
    if user["cooldown_potion"] == 0 and (potion_hp != 0 or potion_mp != 0):
        kba.append(keyb.bt7)
    kba = [keyb.bt6] + kba + [keyb.bt8, keyb.bt9]
    buut.add(*kba)
    return buut


@bot.message_handler()
def send(uid, text, markup=None):
    """Отправка сообщения"""
    if markup:
        bot.send_message(uid, text, reply_markup=markup, parse_mode="html")
    else:
        bot.send_message(uid, text, parse_mode="html")


def photo(uid, text, caption, markup=None):
    """Отправка картинки"""
    if markup:
        bot.send_photo(
            uid, text, caption=caption, reply_markup=markup, parse_mode="html"
        )
    else:
        bot.send_photo(uid, text, caption=caption, parse_mode="html")


def tran_1(uid, player, inventor):
    """Отрисовка начала боя"""
    if player["level"] == 1:
        mob = {
            "животное": (
                "t5cc_QEdE5c",
                str(randint(6, 7)),
                str(randint(2, 4)),
                str(randint(1, 4)),
                "1",
                "🦇",
                str(randint(65, 70)),
                "БЕСХВОСТЫЙ ГРЫЗУН",
            ),
            "орк": (
                "TfD0aaRQ5fI",
                str(randint(6, 8)),
                str(randint(6, 9)),
                str(randint(2, 7)),
                "1",
                "🧟‍♂️",
                str(randint(70, 80)),
                "ГРУБЫЙ КОСТОЛОМ",
            ),
            "нежить": (
                "VDTh1K2lQ7E",
                str(randint(6, 7)),
                str(randint(2, 6)),
                str(randint(10, 19)),
                "1",
                "💀",
                str(randint(70, 75)),
                "РАЗЪЯРЕННЫЙ КУЛЬТИСТ",
            ),
        }
    else:
        hpm1 = randint(
            (player["level"] - 1) * 200 * 0.7, (player["level"] - 1) * 200 * 1
        )
        hpm2 = randint(
            (player["level"] - 1) * 200 * 0.7, (player["level"] - 1) * 200 * 1.2
        )
        hpm3 = randint(
            (player["level"] - 1) * 200 * 0.7, (player["level"] - 1) * 200 * 1
        )

        a121 = randint(
            round(((player["level"] - 1) * 10 + (player["level"] - 1) * 2)),
            round(((player["level"] - 1) * 10 + (player["level"] - 1) * 2) * 1.2),
        )
        a122 = randint(
            round(((player["level"] - 1) * 10 + (player["level"] - 1) * 2)),
            round(((player["level"] - 1) * 10 + (player["level"] - 1) * 2) * 1.4),
        )
        a123 = randint(
            round(((player["level"] - 1) * 10 + (player["level"] - 1) * 2)),
            round(((player["level"] - 1) * 10 + (player["level"] - 1) * 2) * 1.2),
        )

        mob = {
            "животное": (
                "t5cc_QEdE5c",
                str(a121),
                str(randint(1, 30)),
                str(randint(1, 4)),
                "1",
                "🦇",
                str(hpm1),
                "БЕСХВОСТЫЙ ГРЫЗУН",
            ),
            "орк": (
                "TfD0aaRQ5fI",
                str(a122),
                str(randint(1, 30)),
                str(randint(1, 15)),
                "1",
                "🧟‍♂️",
                str(hpm2),
                "ГРУБЫЙ КОСТОЛОМ",
            ),
            "нежить": (
                "VDTh1K2lQ7E",
                str(a123),
                str(randint(1, 20)),
                str(randint(1, 30)),
                "1",
                "💀",
                str(hpm3),
                "РАЗЪЯРЕННЫЙ КУЛЬТИСТ",
            ),
        }

    vid_mob = choice(["животное", "орк", "нежить"])

    im = Image.open(f"Fenrial_TG/moobs/{mob[vid_mob][0]}.jpg")
    pointsize = 32
    font = "Fenrial_TG/days2.ttf"
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(font, pointsize)

    portr = Image.open(f"Fenrial_TG/moobs/f_{player['clas']}.jpg")
    im.paste(portr, (0, 0))

    ### Бары хп, мп ###
    hp_p_b = str(
        int((((int(player["nhp"]) * 100) / (int(player["stamina"]) * 10)) // 10) * 10)
    )

    if hp_p_b != "10" and hp_p_b != "0":
        hp_p = Image.open(f"Fenrial_TG/bar_mp_hp/f_hp_{hp_p_b}.jpg")
        im.paste(hp_p, (195, 43))

    mp_p_b = str(int((int(player["nmp"]) // 10) * 10))
    if int(player["nmp"]) != 0 and mp_p_b == "0":
        mp_p_b = "10"
    if int(player["nmp"]) != 0:
        mp_p = Image.open(f"Fenrial_TG/bar_mp_hp/f_mp_{mp_p_b}.jpg")
        im.paste(mp_p, (195, 101))

    ### Все надписи ###

    hp = f"{player['nhp']} / {int(player['stamina'])*10}"
    hp = f"{(17 - len(hp))*' '}{hp}"
    mp = f"{player['nmp']} / 100"
    mp = f"{(18 - len(mp))*' '}{mp}"

    name_m = f"{mob[vid_mob][-1]}"
    name_m = f"{(18 - len(name_m))*' '}{name_m}"

    hp_m = f"{mob[vid_mob][-2]}/{mob[vid_mob][-2]}"
    hp_m = f"{(9 - len(hp_m))*' '}{hp_m}"

    z_hp = "0"
    z_mp = "0"
    for i in inventor.keys():
        if inventor[i] == 103:
            item_quantity = "quantity_"
            item_quantity = item_quantity + re.search(r"\d+", i)[0]
            z_hp = f"{inventor[item_quantity]}"
            break
    for i in inventor.keys():
        if inventor[i] == 104:
            item_quantity = "quantity_"
            item_quantity = item_quantity + re.search(r"\d+", i)[0]
            z_mp = f"{inventor[item_quantity]}"
            break

    def_player = 0
    evasion = 0

    match player["clas"]:
        case 0:
            def_player = 9
            evasion = 5
        case 1:
            def_player = int(
                (player["defens"] * 60)
                / ((8 * player["level"] + player["stamina"] / 3) * 2)
            )
            evasion = int(int(player["agility"] * 10 / (player["level"] * 3)))
        case 2:
            def_player = int(
                10
                + (player["defens"] * 30)
                / ((8 * player["level"] + player["stamina"] / 3) * 2)
            )
            evasion = int(player["agility"] * 20 / (player["level"] * 4))
        case 3:
            def_player = int(
                5
                + (player["defens"] * 20)
                / ((8 * player["level"] + player["stamina"] / 3) * 2)
            )
            evasion = int(player["agility"] * 5 / (player["level"] * 2))

    coordinates = {
        "защита игрока": [253, 170, f"{def_player} %"],
        "уворот игрока": [253, 240, f"{evasion} %"],
        "зелья хп": [400, 170, z_hp],
        "зелья мп": [400, 240, z_mp],
        "хп": [210, 40, hp],
        "мп": [210, 95, mp],
        "атака моба": [160, 490, f"{mob[vid_mob][1]}"],
        "ф сопр моба": [160, 570, f"{mob[vid_mob][2]} %"],
        "м сопр моба": [160, 650, f"{mob[vid_mob][3]} %"],
        "лвл моба": [160, 720, f"{mob[vid_mob][4]}"],
        "хп моба": [555, 792, hp_m],
        "название моба": [445, 752, name_m],
    }

    def draw_text(x_cor: int, y_cor: int, text: str) -> None:
        """Функция отрисовки текста"""
        for i in ((-5, -5), (5, -5), (-5, 5), (5, 5), (0, 0)):
            draw.text((x_cor + i[0], y_cor + i[1]), text, font=font, fill="black")
        draw.text((x_cor + i[0], y_cor + i[1]), text, font=font, fill="white")

    # Переберем словарь пареметров и вызовим функцию отрисовки для каждого
    for item in coordinates.values():
        draw_text(item[0], item[1], item[2])

    im.save(f"Fenrial_TG/fights/start{uid}.jpg")

    butt = telebot.types.InlineKeyboardMarkup(row_width=2)
    bt1 = telebot.types.InlineKeyboardButton(text="🗡Напасть", callback_data="🗡Напасть")
    bt2 = telebot.types.InlineKeyboardButton(
        text="👞Идти дальше", callback_data="👞Идти дальше"
    )
    bt3 = telebot.types.InlineKeyboardButton(
        text="⛺Разбить лагерь", callback_data="⛺Разбить лагерь"
    )
    bt4 = telebot.types.InlineKeyboardButton(
        text="🏰в Хайдамар", callback_data="🏰в Хайдамар"
    )
    if player["nhp"] != 40 or player["nmp"] != 100:
        butt.add(bt1, bt2, bt3, bt4)
    else:
        butt.add(bt1, bt2, bt4)
    attach = open(f"Fenrial_TG/fights/start{uid}.jpg", "rb")

    bd.exec(
        __QUERY_BATTLE_ADD_,
        {
            "vkid": uid,
            "nhp": int(player["nhp"]),
            "hp": int(player["stamina"]) * 10,
            "mp": int(player["nmp"]),
            "name_mob": str(mob[vid_mob][-1]),
            "vid_mob": str(mob[vid_mob][-3]),
            "lvl_mob": int(mob[vid_mob][4]),
            "attack_mob": int(mob[vid_mob][1]),
            "physical_protection_mob": int(mob[vid_mob][2]),
            "magical_protection_mob": int(mob[vid_mob][3]),
            "nhp_mob": int(mob[vid_mob][-2]),
            "hp_mob": int(mob[vid_mob][-2]),
            "def_player": def_player,
            "evasion": evasion,
            "attack_player": int(player["atack"]),
            "intellect": int(player["intellect"]),
        },
    )
    photo(uid, attach, None, butt)


def attack(uid, player, call, inventor):
    """Функция вызова клавиатуры в начале боя"""
    text = ""
    if player["clas"] == 2:
        text = "\n\n👣Вам удалось подкрасться противнику за спину!"
    elif player["clas"] == 3:
        text = "\n\n👣Противник на достаточном удалении.\n🔮Есть возможность совершить действие, пока он сближается с Вами!"
    elif player["clas"] == 1:
        bd.exec(f"UPDATE battle SET status = 2 where vkid = {uid}", None)
    user = user_battle(uid)
    attachment = open(f"Fenrial_TG/fights/start{uid}.jpg", "rb")
    bot.edit_message_media(
        media=telebot.types.InputMedia(
            type="photo", media=attachment, caption="", parse_mode="html"
        ),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=None,
    )
    buut = keyboard(player, user, inventor)
    attachment = open(f"Fenrial_TG/player_img/avatar_{player['clas']}.jpg", "rb")
    if player["experience"] == 0 and player["clas"] == 0:
        photo(
            uid,
            attachment,
            f"<b>⚠️Ваши действия:</b>{text}\n\n⚠️Кнопки во время боя отображают лишь обозначения заклинаний и количество маны, необходимое для их использования.\nС их описанием и значениями можно ознакомиться в любой момент в профиле или во время боя, нажав  📖",
            buut,
        )
    else:
        photo(uid, attachment, f"<b>⚠️Ваши действия:</b>{text}", buut)


def request_escape(uid, call, player):
    """Подтверждение побега"""
    user = user_battle(uid)
    buut = telebot.types.InlineKeyboardMarkup()
    bt1 = telebot.types.InlineKeyboardButton(text="✅", callback_data="accept_escape")
    bt2 = telebot.types.InlineKeyboardButton(text="❌", callback_data="close_escape")
    buut.add(bt1, bt2)
    spell_player = spell_mob = "Fenrial_TG/spells/rpg03_013.jpg"
    dop_text_user_attack = ""
    match user["vid_mob"]:
        case "🦇":
            substrate = "Fenrial_TG/moobs/t5cc_QEdE5c_f.jpg"
        case "🧟‍♂️":
            substrate = "Fenrial_TG/moobs/TfD0aaRQ5fI_f.jpg"
        case "💀":
            substrate = "Fenrial_TG/moobs/VDTh1K2lQ7E_f.jpg"
    attachment = open(
        image_combat(
            uid, substrate, player, user, spell_player, spell_mob, course_of_battle=0
        ),
        "rb",
    )
    bot.edit_message_media(
        media=telebot.types.InputMedia(
            type="photo",
            media=attachment,
            caption=f"⚠️Вы действительно хотите сбежать?",
            parse_mode="html",
        ),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=buut,
    )


def run_away_accept(uid, inventor, call, player):
    """Функция побега"""
    user = user_battle(uid)
    engine.status_update(uid, 100)
    uron = randint(int(user["attack_mob"] * 1.2), int(user["attack_mob"] * 1.5))
    if player["clas"] > 1 and 0 <= user["status"] < 2:
        uron = 0
    if user["nhp"] - uron > 0:
        attachment = open(f"Fenrial_TG/sys_img/pobeg.jpg", "rb")
        if uron != 0:
            hp_mp_update(uid, user["nhp"] - uron, user["mp"])
            player["nhp"] = user["nhp"] - uron
            player["nmp"] = user["mp"]
            bot.edit_message_media(
                media=telebot.types.InputMedia(
                    type="photo",
                    media=attachment,
                    caption=f"👣Вам удалось сбежать от противника\n💥Получено {uron} урона в спину",
                    parse_mode="html",
                ),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=None,
            )
        else:
            bot.edit_message_media(
                media=telebot.types.InputMedia(
                    type="photo",
                    media=attachment,
                    caption=f"👣Вам удалось сбежать от противника, не получив урона в спину",
                    parse_mode="html",
                ),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=None,
            )
        butt = telebot.types.InlineKeyboardMarkup(row_width=2)
        bt2 = telebot.types.InlineKeyboardButton(
            text="👞Идти дальше", callback_data="👞Идти дальше"
        )
        bt3 = telebot.types.InlineKeyboardButton(
            text="⛺Разбить лагерь", callback_data="⛺Разбить лагерь"
        )
        bt4 = telebot.types.InlineKeyboardButton(
            text="🏰в Хайдамар", callback_data="🏰в Хайдамар"
        )
        butt.add(bt2, bt3, bt4)
        attachment = open(non_combat.image_research(uid, player, inventor), "rb")
        photo(uid, attachment, "<b>🏞 Равнины Хайдамара</b> (1-5 ур.)", butt)
    else:
        send(
            uid, f"☠Получено {uron} урона в спину", telebot.types.ReplyKeyboardRemove()
        )
        dead(uid, call, inventor, player)


def close_escape(uid, call, inventor, player):
    user = user_battle(uid)
    buut = keyboard(player, user, inventor)
    spell_player = spell_mob = "Fenrial_TG/spells/rpg03_013.jpg"
    dop_text_user_attack = ""
    match user["vid_mob"]:
        case "🦇":
            substrate = "Fenrial_TG/moobs/t5cc_QEdE5c_f.jpg"
        case "🧟‍♂️":
            substrate = "Fenrial_TG/moobs/TfD0aaRQ5fI_f.jpg"
        case "💀":
            substrate = "Fenrial_TG/moobs/VDTh1K2lQ7E_f.jpg"
    attachment = open(
        image_combat(
            uid, substrate, player, user, spell_player, spell_mob, course_of_battle=0
        ),
        "rb",
    )
    match player["clas"]:
        case 1:
            dop_text_user_attack = f'\n\n✊🏻Ярость: {user["status_skill_1"]}'
        case 2:
            dop_text_user_attack = f'\n\n🗡Серия ударов: {user["status_skill_2"]}'
        case 3:
            if user["status_skill_1"] > 0:
                dop_text_user_attack = f'\n\n💎Морозный щит: {user["status_skill_1"]}'
    bot.edit_message_media(
        media=telebot.types.InputMedia(
            type="photo",
            media=attachment,
            caption=f"<b>⚠️Ваши действия:</b>{dop_text_user_attack}",
            parse_mode="html",
        ),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=buut,
    )


def combat_training_log(uid, call, inventor, player):
    """Ведение логики боя, бой, отрисовка боя"""

    user = user_battle(uid)

    msg = call.data
    vid_mob = user["vid_mob"]
    choce_spell = randint(1, 100)
    match player["clas"]:
        case 0:
            spell_player = "Fenrial_TG/spells/PlR5HBrrYFw.jpg"
        case 1:
            spell_player = "Fenrial_TG/spells/pYCtxNnpePw.jpg"
        case 2:
            spell_player = "Fenrial_TG/spells/tHQYzUTALKA.jpg"
        case 3:
            spell_player = "Fenrial_TG/spells/JsGTK1YDLFI.jpg"
    user_attack = randint(
        int(user["attack_player"] * 0.8), int(user["attack_player"] * 1.2)
    )
    user_attack = int(user_attack * ((100 - user["physical_protection_mob"]) / 100))
    text_user_attack = f"🔪Вы нанесли {user_attack} урона"
    dop_text_user_attack = ""
    krv = randint(int(user["attack_player"] * 1), int(user["attack_player"] * 1.5))
    mob_attack_rate = 1

    if player["clas"] == 2:
        dop_text_user_attack = f'\n\n🗡Серия ударов: {user["status_skill_2"]}'
    if player["clas"] == 1:
        dop_text_user_attack = f'\n\n✊🏻Ярость: {user["status_skill_1"]}'
    hp_reg_mob = 0

    hp_m = user["nhp_mob"]
    hp_player = user["nhp"]

    regen_player_hp = 0
    regen_player_mp = 0

    if player["clas"] == 0:
        regen_player_hp = 1
        regen_player_mp = 1
    else:
        regen_player_hp = int(player["stamina"] / 2.5)
        regen_player_mp = int(player["intellect"] / 2.5)

    match msg:
        case "💢Выпад":
            nmp_update(uid, (user["mp"] - 10))
            spell_player = "Fenrial_TG/spells/iiORuGQ0rtA.jpg"
            user_attack = randint(
                int(user["attack_player"] * 1.5), int(user["attack_player"] * 2.5)
            )
            user_attack = int(
                user_attack * ((100 - user["physical_protection_mob"]) / 100)
            )
            text_user_attack = f"💢Вы нанесли {user_attack} урона"
        case "💥Опасный выпад":
            nmp_update(uid, (user["mp"] - 15))
            spell_player = "Fenrial_TG/spells/sts_082.jpg"
            user_attack = randint(
                int(user["attack_player"] * 3), int(user["attack_player"] * 4)
            )
            user_attack = int(
                user_attack * ((100 - user["physical_protection_mob"]) / 100)
            )
            text_user_attack = f"💥Вы нанесли {user_attack} урона"
            bd.exec(f"UPDATE battle SET status_skill_3 = 3 where vkid = {uid}", None)

        case "🗡Коварный удар":
            nmp_update(uid, (user["mp"] - 7))
            spell_player = "Fenrial_TG/spells/jJ-SsZhfOqU.jpg"
            user_attack = randint(
                int(user["attack_player"] * 2.5), int(user["attack_player"] * 3)
            )
            user_attack = int(
                user_attack * ((100 - user["physical_protection_mob"]) / 100)
            )
            text_user_attack = f"🗡Вы нанесли {user_attack} урона"
            bd.exec(
                f"UPDATE battle SET status_skill_2 = status_skill_2 + 1 where vkid = {uid}",
                None,
            )
        case "💥Удар в спину":
            nmp_update(uid, (user["mp"] - 12))
            spell_player = "Fenrial_TG/spells/Bj61TyrCJpo.jpg"
            if user["status"] < 2 or user["status_skill_3"] == 3:
                user_attack = randint(
                    int(user["attack_player"] * 4), int(user["attack_player"] * 4.5)
                )
            else:
                user_attack = randint(
                    int(user["attack_player"] * 1.5), int(user["attack_player"] * 2)
                )
            user_attack = int(
                user_attack * ((100 - user["physical_protection_mob"]) / 100)
            )
            text_user_attack = f"💥Вы нанесли {user_attack} урона"
            bd.exec(f"UPDATE battle SET status_skill_1 = 3 where vkid = {uid}", None)
        case "⚔Потрошение":
            nmp_update(uid, (user["mp"] - 12))
            spell_player = "Fenrial_TG/spells/yMIuh1cvH-8.jpg"
            user_attack = randint(
                int(user["attack_player"] * 5.2), int(user["attack_player"] * 5.5)
            )
            user_attack = int(
                user_attack * ((100 - user["physical_protection_mob"]) / 100)
            )
            text_user_attack = f"⚔Вы нанесли {user_attack} урона"
            bd.exec(f"UPDATE battle SET status_skill_2 = 0 where vkid = {uid}", None)
        case "👁Ослепление":
            nmp_update(uid, (user["mp"] - 12))
            spell_player = "Fenrial_TG/spells/f-Omf3Dh7XU.jpg"
            user_attack = 0
            text_user_attack = f"👁Вы ослепили противника"
            spell_mob = "Fenrial_TG/spells/rpg03_013.jpg"
            attack_mob = 0
            bd.exec(f"UPDATE battle SET status = 0 where vkid = {uid}", None)
            bd.exec(f"UPDATE battle SET status_skill_3 = 4 where vkid = {uid}", None)
        case "💔Рассечение":
            nmp_update(uid, (user["mp"] - 7))
            spell_player = "Fenrial_TG/spells/sts_099.jpg"
            user_attack = randint(
                int(user["attack_player"] * 1), int(user["attack_player"] * 1.5)
            )
            user_attack = int(
                user_attack * ((100 - user["physical_protection_mob"]) / 100)
            )
            text_user_attack = (
                f"💔Вы нанесли {user_attack} урона и оставили противнику открытую рану"
            )
            bd.exec(f"UPDATE battle SET status_skill_4 = 5 where vkid = {uid}", None)

        case "💫Чародейские стрелы":
            nmp_update(uid, (user["mp"] - 7))
            spell_player = "Fenrial_TG/spells/srXE0oyETn0.jpg"
            user_attack = randint(
                int(user["intellect"] * 4), int(user["intellect"] * 6)
            )
            user_attack = int(
                user_attack * ((100 - user["magical_protection_mob"]) / 100)
            )
            text_user_attack = f"💫Вы нанесли {user_attack} урона"
        case "💎Морозный щит":
            nmp_update(uid, (user["mp"] - 12))
            spell_player = "Fenrial_TG/spells/HtacL5QRlio.jpg"
            user_attack = 0
            spell_mob = "Fenrial_TG/spells/rpg03_013.jpg"
            attack_mob = 0
            text_user_attack = f"💎Вы сотворили Морозный щит, поглощающий часть урона"
            if user["status"] < 2:
                text_user_attack = f"💎Вы сотворили Морозный щит, поглощающий часть урона\n\n❗️Пока Вы творили заклинание, противник подошел ближе!"
            bd.exec(f"UPDATE battle SET status_skill_1 = 3 where vkid = {uid}", None)
            bd.exec(f"UPDATE battle SET status = 1 where vkid = {uid}", None)
        case "🔥Огненный шар":
            nmp_update(uid, (user["mp"] - 17))
            spell_player = "Fenrial_TG/spells/Jyv-lHRyEy0.jpg"
            user_attack = randint(
                int(user["intellect"] * 8), int(user["intellect"] * 10)
            )
            user_attack = int(
                user_attack * ((100 - user["magical_protection_mob"]) / 100)
            )
            text_user_attack = f"🔥Вы нанесли {user_attack} урона"
            bd.exec(f"UPDATE battle SET status_skill_2 = 4 where vkid = {uid}", None)
        case "✨Скачок":
            nmp_update(uid, (user["mp"] - 12))
            spell_player = "Fenrial_TG/spells/VRliOnB1N50.jpg"
            user_attack = 0
            text_user_attack = f"✨Вам удалось телепортироваться на небольшое расстояние"
            spell_mob = "Fenrial_TG/spells/rpg03_013.jpg"
            attack_mob = 0
            bd.exec(f"UPDATE battle SET status = 0 where vkid = {uid}", None)
            bd.exec(f"UPDATE battle SET status_skill_3 = 3 where vkid = {uid}", None)
        case "❄Кольцо льда":
            nmp_update(uid, (user["mp"] - 20))
            spell_player = "Fenrial_TG/spells/hwjVwpePUc0.jpg"
            user_attack = randint(
                int(user["intellect"] * 8), int(user["intellect"] * 10)
            )
            user_attack = int(
                user_attack * ((100 - user["magical_protection_mob"]) / 100)
            )
            text_user_attack = f"❄Вы нанесли {user_attack} урона"
            bd.exec(f"UPDATE battle SET status_skill_4 = 4 where vkid = {uid}", None)

        case "🗡Атака":
            if player["clas"] == 1:
                bd.exec(
                    f"UPDATE battle SET status_skill_1 = status_skill_1 + 1 where vkid = {uid}",
                    None,
                )
                if 1 < user["status_skill_5"] - 2 < 5:
                    user_attack = randint(
                        int(user["attack_player"] * 1.5), int(user["attack_player"] * 2)
                    )
                    user_attack = int(
                        user_attack * ((100 - user["physical_protection_mob"]) / 100)
                    )
                    text_user_attack = f"🔪Вы нанесли {user_attack} урона(♨)"
        case "✊🏻Мощный удар":
            nmp_update(uid, (user["mp"] - 20))
            spell_player = "Fenrial_TG/spells/8oXVpm3NzwI.jpg"
            user_attack = randint(
                int(user["attack_player"] * 2 * user["status_skill_1"]),
                int(user["attack_player"] * 3 * user["status_skill_1"]),
            )
            user_attack = int(
                user_attack * ((100 - user["physical_protection_mob"]) / 100)
            )
            text_user_attack = f"✊🏻Вы нанесли {user_attack} урона"
            bd.exec(f"UPDATE battle SET status_skill_1 = 0 where vkid = {uid}", None)
        case "🔥Удар героя":
            nmp_update(uid, (user["mp"] - 12))
            spell_player = "Fenrial_TG/spells/54WTwwTA8Mk.jpg"
            user_attack = randint(
                int(user["attack_player"] * 3), int(user["attack_player"] * 4)
            )
            user_attack = int(
                user_attack * ((100 - user["physical_protection_mob"]) / 100)
            )
            text_user_attack = f"🔥Вы нанесли {user_attack} урона"
            bd.exec(f"UPDATE battle SET status_skill_2 = 5 where vkid = {uid}", None)
        case "💥Раскол брони":
            nmp_update(uid, (user["mp"] - 12))
            spell_player = "Fenrial_TG/spells/IePQ22dJE7o.jpg"
            bd.exec(
                f"UPDATE battle SET physical_protection_mob = round(physical_protection_mob / 2) where vkid = {uid}",
                None,
            )
            user["physical_protection_mob"] = round(user["physical_protection_mob"] / 2)
            user_attack = randint(
                int(user["attack_player"] * 1), int(user["attack_player"] * 1.5)
            )
            user_attack = int(
                user_attack * ((100 - user["physical_protection_mob"]) / 100)
            )
            text_user_attack = f'💥Вы нанесли {user_attack} урона и уменьшили броню противника на 50% (снижена до {user["physical_protection_mob"]}%)'
            bd.exec(f"UPDATE battle SET status_skill_3 = 4 where vkid = {uid}", None)
            bd.exec(f"UPDATE battle SET status_skill_6 = 1 where vkid = {uid}", None)
        case "👹Деморализующий крик":
            nmp_update(uid, (user["mp"] - 12))
            spell_player = "Fenrial_TG/spells/FKOuMhNFhEs.jpg"
            user_attack = 0
            spell_mob = "Fenrial_TG/spells/rpg03_013.jpg"
            attack_mob = 0
            text_user_attack = f"👹Сила противника снижена на 25% на 3 хода"
            mob_attack_rate = 0.5
            bd.exec(f"UPDATE battle SET status_skill_4 = 6 where vkid = {uid}", None)
            bd.exec(f"UPDATE battle SET status = 1 where vkid = {uid}", None)
        case "♨Боевой крик":
            nmp_update(uid, (user["mp"] - 12))
            spell_player = "Fenrial_TG/spells/xPY_6TVL1Hw.jpg"
            user_attack = 0
            spell_mob = "Fenrial_TG/spells/rpg03_013.jpg"
            attack_mob = 0
            text_user_attack = f"♨Сила обычных ударов повышена на 50%"
            bd.exec(f"UPDATE battle SET status_skill_5 = 6 where vkid = {uid}", None)
            bd.exec(f"UPDATE battle SET status = 1 where vkid = {uid}", None)

    user = user_battle(uid)
    if player["clas"] > 1 and user["status"] > 0:
        choce_spell = 100
    if player["clas"] == 1 and user["status"] == 1:
        choce_spell = 100

    match vid_mob:
        case "🦇":
            substrate = "Fenrial_TG/moobs/t5cc_QEdE5c_f.jpg"
            spell_mob = "Fenrial_TG/spells/sts_073.jpg"
            attack_mob = randint(
                int(user["attack_mob"] * 0.8), int(user["attack_mob"] * 1.2)
            )
            attack_mob = int(
                attack_mob * mob_attack_rate * ((100 - user["def_player"]) / 100)
            )
            text_attack_mob = f"\n🗡Противник нанес {attack_mob} урона"
            if 0 < choce_spell < 11:
                spell_mob = "Fenrial_TG/spells/0o1ls5KmWTo.jpg"
                attack_mob = 0
                hp_reg_mob = int(user["hp_mob"] * 0.15)
                text_attack_mob = f"\n💖Противник восстановил {hp_reg_mob} здоровья!"
            elif 11 < choce_spell < 20:
                spell_mob = "Fenrial_TG/spells/rpg03_014.jpg"
                attack_mob = 0
                new_attack_mob = int(user["attack_mob"] * 1.35)
                text_attack_mob = f"\n🔥Противник повысил атаку до {new_attack_mob}!"
                bd.exec(
                    f"UPDATE battle SET attack_mob = {new_attack_mob} where vkid = {uid}",
                    None,
                )
        case "🧟‍♂️":
            substrate = "Fenrial_TG/moobs/TfD0aaRQ5fI_f.jpg"
            spell_mob = "Fenrial_TG/spells/pYCtxNnpePw.jpg"
            attack_mob = randint(
                int(user["attack_mob"] * 0.8), int(user["attack_mob"] * 1.2)
            )
            attack_mob = int(
                attack_mob * mob_attack_rate * ((100 - user["def_player"]) / 100)
            )
            text_attack_mob = f"\n🗡Противник нанес {attack_mob} урона"
            if 0 < choce_spell < 11:
                spell_mob = "Fenrial_TG/spells/Pm98fDKoY4A.jpg"
                attack_mob = randint(int(attack_mob * 1.5), int(attack_mob * 2))
                attack_mob = int(
                    attack_mob * mob_attack_rate * ((100 - user["def_player"]) / 100)
                )
                text_attack_mob = f"\n💣Бомба противника взорвалась прямо перед Вами, нанеся {attack_mob} урона!"
            elif 11 < choce_spell < 20 and player["clas"] != 3:
                spell_mob = "Fenrial_TG/spells/psk_055.jpg"
                attack_mob = 0
                text_attack_mob = f"\n⚡Противник смог парировать Вашу атаку!"
                user_attack = 0
                text_user_attack = ""
        case "💀":
            substrate = "Fenrial_TG/moobs/VDTh1K2lQ7E_f.jpg"
            spell_mob = "Fenrial_TG/spells/JsGTK1YDLFI.jpg"
            attack_mob = randint(
                int(user["attack_mob"] * 0.8), int(user["attack_mob"] * 1.2)
            )
            attack_mob = int(attack_mob * ((100 - user["def_player"]) / 100))
            text_attack_mob = f"\n🗡Противник нанес {attack_mob} урона"
            if 0 < choce_spell < 11:
                spell_mob = "Fenrial_TG/spells/XKU2x6of9V4.jpg"
                attack_mob = 0
                mana = randint(15, 25)
                text_attack_mob = f"\n💀Противник сжег Вам {mana} маны"
                if user["mp"] - mana < 0:
                    nmp_update(uid, 0)
                else:
                    nmp_update(uid, user["mp"] - mana)
            elif 11 < choce_spell < 20:
                spell_mob = "Fenrial_TG/spells/12a-5xsKm8s.jpg"
                attack_mob = randint(int(attack_mob * 1.5), int(attack_mob * 2))
                attack_mob = int(attack_mob * ((100 - user["def_player"]) / 100))
                text_attack_mob = f"\n💥Стрела темной энергии обожгла Вам запястье, нанеся {attack_mob} урона!"
            elif (
                20 < choce_spell < 30
                and player["clas"] == 3
                and user_attack > int(user["attack_player"] * 1.3)
            ):
                spell_mob = "Fenrial_TG/spells/DfwS996bjEg.jpg"
                user_attack = 0
                attack_mob = 0
                text_user_attack = ""
                text_attack_mob = f"\n🌀Противник отразил Ваше заклинание!"

    user = user_battle(uid)
    hp_m = hp_m - user_attack + hp_reg_mob
    if 1 < user["status_skill_4"] < 4 and player["clas"] == 2:
        hp_m = hp_m - krv

    if hp_m > user["hp_mob"]:
        hp_m = user["hp_mob"]

    if user["status"] < 2 and player["clas"] > 0:
        attack_mob = 0
        spell_mob = "Fenrial_TG/spells/rpg03_013.jpg"
        text_attack_mob = ""

    else:
        if randint(1, 100) <= user["evasion"] and attack_mob != 0:
            attack_mob = 0
            text_attack_mob = "\n✋Вам удалось увернуться от атаки противника"

        if 0 < user["status_skill_1"] < 4 and player["clas"] == 3 and attack_mob > 0:
            attack_mob = round(attack_mob * 0.5)
            bd.exec(
                f"UPDATE battle SET status_skill_1 = status_skill_1 - 1 where vkid = {uid}",
                None,
            )
            user["status_skill_1"] = user["status_skill_1"] - 1
            if user["status_skill_1"] != 0:
                dop_text_user_attack = f'\n\n💎{attack_mob} урона поглощено щитом\n💎Морозный щит {user["status_skill_1"]}'
            else:
                dop_text_user_attack = (
                    f"\n\n💎{attack_mob } урона поглощено щитом\n💎Морозный щит разрушен!"
                )
        hp_player = hp_player - attack_mob + regen_player_hp

    mp_player = user["mp"] + regen_player_mp
    if mp_player > 100:
        mp_player = 100
    if hp_player > user["hp"]:
        hp_player = user["hp"]

    if hp_m <= 0:
        # Победа #
        bd.exec(f"UPDATE battle SET nhp_mob = 0 where vkid = {uid}", None)
        user = user_battle(uid)
        text_attack_mob = "\n\n☠️Cмертельный урон!"
        dop_text_user_attack = ""
        if 0 < user["status_skill_4"] < 4 and player["clas"] == 2:
            dop_text_user_attack = f"\n💔Противник теряет {krv} здоровья от кровотечения"
        spell_mob = "Fenrial_TG/spells/sts_033.jpg"
        attachment = open(
            image_combat(
                uid,
                substrate,
                player,
                user,
                spell_player,
                spell_mob,
                course_of_battle=0,
            ),
            "rb",
        )
        bot.edit_message_media(
            media=telebot.types.InputMedia(
                type="photo",
                media=attachment,
                caption=f"{text_user_attack}{dop_text_user_attack}{text_attack_mob}",
                parse_mode="html",
            ),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None,
        )

        im = Image.open("Fenrial_TG/sys_img/pobeda_1.jpg")
        pointsize = 32
        font = "Fenrial_TG/days2.ttf"
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype(font, pointsize)

        if player["clas"] != 0:
            new_exp = round(player["level"] * 4.5)
        else:
            new_exp = 30

        if player["level"] != 1:
            exp = f"Опыт:  {player['experience']+new_exp} / {player['level_limit']} ( +{new_exp} )"
            exp = f"{(31 - len(exp))*' '}{exp}"
        else:
            exp = f"Опыт:  {player['experience']+30} / 180 ( +30 )"
            exp = f"{(31 - len(exp))*' '}{exp}"

        moneta = Image.open(f"Fenrial_TG/sys_img/8ytVa5V8lEo.jpg")
        im.paste(moneta, (146, 327))

        exp_text_bar = f"{int((((player['experience']+new_exp)*100/player['level_limit'])//10)*10)}"
        if exp_text_bar != "10" and exp_text_bar != "0":
            exp_bar = Image.open(f"Fenrial_TG/bar_mp_hp/e_n_{exp_text_bar}.jpg")
            im.paste(exp_bar, (89, 767))

        nagrada = randint(player["level"], player["level"] * 2)
        if len(f"{nagrada}") == 1:
            nagrada = f"{(8 - len(f'{nagrada}'))*' '}{nagrada}"
        else:
            nagrada = f"{(7 - len(f'{nagrada}'))*' '}{nagrada}"
        coordinates = {"кол награды": [240, 485, str(nagrada)], "опыт": [400, 719, exp]}

        def draw_text(x_cor: int, y_cor: int, text: str) -> None:
            """Функция отрисовки текста"""
            for i in ((-5, -5), (5, -5), (-5, 5), (5, 5), (0, 0)):
                draw.text((x_cor + i[0], y_cor + i[1]), text, font=font, fill="black")
            draw.text((x_cor + i[0], y_cor + i[1]), text, font=font, fill="white")

        # Переберем словарь пареметров и вызовим функцию отрисовки для каждого
        for item in coordinates.values():
            draw_text(item[0], item[1], item[2])

        im.save(f"Fenrial_TG/fights/pobeda_{uid}.jpg")

        # Обновление статов (опыт, награда) #

        bd.exec(
            f"UPDATE players SET experience = experience + {new_exp}, balance = balance + {nagrada} where vkid = {uid}",
            None,
        )
        bd.exec(
            f"UPDATE statistics SET mobs_killed = mobs_killed + 1 where vkid = {uid}",
            None,
        )
        hp_mp_update(uid, user["nhp"], user["mp"])
        engine.unloading_players()
        engine.unloading_statistics()
        player["nhp"] = user["nhp"]
        player["nmp"] = user["mp"]
        player["experience"] = player["experience"] + new_exp
        bd.exec(__QUERY_DELETE_BATTLE, {"vkid": uid})
        butt = telebot.types.InlineKeyboardMarkup(row_width=2)
        bt2 = telebot.types.InlineKeyboardButton(
            text="👞Идти дальше", callback_data="👞Идти дальше"
        )
        bt3 = telebot.types.InlineKeyboardButton(
            text="⛺Разбить лагерь", callback_data="⛺Разбить лагерь"
        )
        bt4 = telebot.types.InlineKeyboardButton(
            text="🏰в Хайдамар", callback_data="🏰в Хайдамар"
        )
        if user["nhp"] != 40 or user["mp"] != 100:
            butt.add(bt2, bt3, bt4)
        else:
            butt.add(bt2, bt4)
        attachment = open(f"Fenrial_TG/fights/pobeda_{uid}.jpg", "rb")
        photo(uid, attachment, "", None)

        if player["experience"] >= player["level_limit"]:
            ### Новый ЛВЛ ###
            attachment = open(f"Fenrial_TG/sys_img/yIKPoQPbSZA.jpg", "rb")
            if player["level"] > 1:
                photo(
                    uid,
                    attachment,
                    f'🎉Получен {player["level"]+1} уровень!!!\n💖Здоровье и мана полностью восстановлены!',
                    None,
                )
            else:
                photo(
                    uid,
                    attachment,
                    f'<b>🎉Получен {player["level"]+1} уровень!!!</b>\n💖Здоровье и мана полностью восстановлены!\n\n🔔Вам доступен выбор класса в Ратуше',
                    None,
                )
            player["nhp"] = player["stamina"] * 10
            player["nmp"] = 100
            player["experience"] = 0
            player["level"] = player["level"] + 1
            player["level_limit"] = int(
                (player["level"]) * 6 * (15 + 15 * int(player["level"]))
            )
            bd.exec(
                f"UPDATE players SET nhp = {player['stamina']*10},\
                    nmp = 100, experience = 0, level = level + 1\
                    where vkid = {uid}",
                None,
            )
            engine.unloading_players()

        attachment = open(non_combat.image_research(uid, player, inventor), "rb")
        photo(uid, attachment, "<b>🏞 Равнины Хайдамара</b> (1-5 ур.)", butt)

    elif hp_m > 0 and hp_player <= 0:
        nhp_update(uid, 0)
        nmp_update(uid, mp_player)
        bd.exec(f"UPDATE battle SET nhp_mob = {hp_m} where vkid = {uid}", None)
        user = user_battle(uid)
        attachment = open(
            image_combat(
                uid,
                substrate,
                player,
                user,
                spell_player,
                spell_mob,
                course_of_battle=0,
            ),
            "rb",
        )
        bot.edit_message_media(
            media=telebot.types.InputMedia(
                type="photo",
                media=attachment,
                caption=f"{text_user_attack}{text_attack_mob}{dop_text_user_attack}",
                parse_mode="html",
            ),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None,
        )
        dead(uid, call, inventor, player)

    else:
        nhp_update(uid, hp_player)
        nmp_update(uid, mp_player)
        bd.exec(f"UPDATE battle SET nhp_mob = {hp_m} where vkid = {uid}", None)

        if player["clas"] == 3 or player["clas"] == 1:
            if user["status_skill_2"] > 0:
                bd.exec(
                    f"UPDATE battle SET status_skill_2 = status_skill_2 - 1 where vkid = {uid}",
                    None,
                )

        if user["status_skill_1"] > 0 and player["clas"] == 2:
            bd.exec(
                f"UPDATE battle SET status_skill_1 = status_skill_1 - 1 where vkid = {uid}",
                None,
            )
        if user["status_skill_3"] > 0 and user["status"] > 1:
            bd.exec(
                f"UPDATE battle SET status_skill_3 = status_skill_3 - 1 where vkid = {uid}",
                None,
            )
        if user["status_skill_4"] > 0 and user["status"] > 1 and player["clas"] != 2:
            bd.exec(
                f"UPDATE battle SET status_skill_4 = status_skill_4 - 1 where vkid = {uid}",
                None,
            )
        if user["status_skill_4"] > 0 and player["clas"] == 2:
            bd.exec(
                f"UPDATE battle SET status_skill_4 = status_skill_4 - 1 where vkid = {uid}",
                None,
            )
        if user["status_skill_5"] > 0 and user["status"] > 1:
            bd.exec(
                f"UPDATE battle SET status_skill_5 = status_skill_5 - 1 where vkid = {uid}",
                None,
            )

        if user["cooldown_potion"] > 0:
            bd.exec(
                f"UPDATE battle SET cooldown_potion = cooldown_potion - 1 where vkid = {uid}",
                None,
            )
        bd.exec(f"UPDATE battle SET status = status + 1 where vkid = {uid}", None)

        user = user_battle(uid)

        match player["clas"]:
            case 1:
                buff = ""
                debuff = ""
                if user["status_skill_4"] > 3:
                    debuff = f'👹Уменьшение атаки противника: {-1*(3 - user["status_skill_4"])}\n'
                if user["status_skill_4"] == 3:
                    debuff = f"👹Уменьшение атаки противника развеяно\n"
                if user["status_skill_5"] > 3:
                    buff = f'♨Усиление атаки: {-1*(3 - user["status_skill_5"])}\n'
                if user["status_skill_5"] == 3:
                    buff = f"♨Усиление Вашей атаки развеяно\n"
                dop_text_user_attack = (
                    f'\n\n{debuff}{buff}✊🏻Ярость: {user["status_skill_1"]}'
                )
            case 2:
                dop_text_user_attack = f'\n\n🗡Серия ударов: {user["status_skill_2"]}'
            case 3:
                if user["status_skill_1"] > 0 and attack_mob == 0:
                    dop_text_user_attack = (
                        f'\n\n💎Морозный щит: {user["status_skill_1"]}'
                    )

        buut = keyboard(player, user, inventor)
        attachment = open(
            image_combat(
                uid,
                substrate,
                player,
                user,
                spell_player,
                spell_mob,
                course_of_battle=1,
            ),
            "rb",
        )

        if 0 < user["status_skill_4"] < 4 and player["clas"] == 2:
            dop_text_user_attack = f'\n\n💔Противник теряет {krv} здоровья от кровотечения\n🗡Серия ударов: {user["status_skill_2"]}'

        bot.edit_message_media(
            media=telebot.types.InputMedia(
                type="photo",
                media=attachment,
                caption=f"{text_user_attack}{text_attack_mob}{dop_text_user_attack}",
                parse_mode="html",
            ),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=buut,
        )


def dead(uid, call, inventor, player):
    """Смерть"""
    engine.status_update(uid, 50)
    bd.exec(f"UPDATE statistics SET died = died + 1 where vkid = {uid}", None)
    player["nhp"] = 1
    player["nmp"] = 1
    if player["level"] == 1:
        time_study = 60
        start_study = datetime.today()
        end_study = start_study + timedelta(seconds=time_study)
        engine.timers_update(uid, start_study, end_study, 50)
        attachment = open(f"Fenrial_TG/sys_img/xYsLHoNWfrk.jpg", "rb")
        photo(
            uid,
            attachment,
            f'<b>☠Последний вдох, перед глазами тьма...</b>\n⚠На 1 уровне штрафов за смерть нет.\n⚡Продолжить путешествие сможете через минуту.{text.training["Смерть"]}',
        )
        bd.exec(__QUERY_DELETE_BATTLE, {"vkid": uid})
        return threading.Thread(
            target=non_combat.revival, args=[uid, player, inventor, time_study]
        ).start()
    else:
        time_study = 60 * player["level"]
        start_study = datetime.today()
        end_study = start_study + timedelta(seconds=time_study)
        engine.timers_update(uid, start_study, end_study, 50)
        attachment = open(f"Fenrial_TG/sys_img/xYsLHoNWfrk.jpg", "rb")
        player["experience"] = round(player["experience"] * 0.9)
        bd.exec(
            f"UPDATE players SET balance = round(balance*0.75), experience = round(experience*0.9) where vkid = {uid}",
            None,
        )
        engine.unloading_players()
        photo(
            uid,
            attachment,
            f"<b>☠Последний вдох, перед глазами тьма...</b>\n\n⚠Вы потеряли:\n📗10% опыта и 💰25% накопленных монет.\n⚡Продолжить путешествие сможете через {player['level']} мин",
        )
        bd.exec(__QUERY_DELETE_BATTLE, {"vkid": uid})
        return threading.Thread(
            target=non_combat.revival, args=[uid, player, inventor, time_study]
        ).start()


def potion(uid, call, inventor, player):
    user = user_battle(uid)
    potion_hp_text = ""
    potion_mp_text = ""
    potion_hp = 0
    potion_mp = 0
    for i in inventor.keys():
        if inventor[i] == 103:
            item_quantity = "quantity_"
            item_quantity = item_quantity + re.search(r"\d+", i)[0]
            potion_hp = f"{inventor[item_quantity]}"
            potion_hp_text = (
                f'🔴Флакон жизни (+{int(player["stamina"]*3)}💚): {potion_hp} шт.'
            )
            break
    for i in inventor.keys():
        if inventor[i] == 104:
            item_quantity = "quantity_"
            item_quantity = item_quantity + re.search(r"\d+", i)[0]
            potion_mp = f"{inventor[item_quantity]}"
            potion_mp_text = f"\n🔵Флакон маны (+{30}⛎): {potion_mp} шт."
            break
    spell_player = spell_mob = "Fenrial_TG/spells/rpg03_013.jpg"
    match user["vid_mob"]:
        case "🦇":
            substrate = "Fenrial_TG/moobs/t5cc_QEdE5c_f.jpg"
        case "🧟‍♂️":
            substrate = "Fenrial_TG/moobs/TfD0aaRQ5fI_f.jpg"
        case "💀":
            substrate = "Fenrial_TG/moobs/VDTh1K2lQ7E_f.jpg"
    attachment = open(
        image_combat(
            uid, substrate, player, user, spell_player, spell_mob, course_of_battle=0
        ),
        "rb",
    )
    buut = telebot.types.InlineKeyboardMarkup(row_width=2)
    bt1 = telebot.types.InlineKeyboardButton(
        text="🔴Флакон жизни", callback_data="🔴Флакон жизни"
    )
    bt2 = telebot.types.InlineKeyboardButton(
        text="🔵Флакон маны", callback_data="🔵Флакон маны"
    )
    if potion_mp != 0 and potion_hp != 0:
        buut.add(bt1, bt2)
    elif potion_mp != 0 and potion_hp == 0:
        buut.add(bt2)
    elif potion_mp == 0 and potion_hp != 0:
        buut.add(bt1)
    bt3 = telebot.types.InlineKeyboardButton(
        text="❌Закрыть", callback_data="убрать зелья"
    )
    buut.add(bt3)
    bot.edit_message_media(
        media=telebot.types.InputMedia(
            type="photo",
            media=attachment,
            caption=f"{potion_hp_text}{potion_mp_text}",
            parse_mode="html",
        ),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=buut,
    )


def del_potion(uid, call, inventor, player):
    user = user_battle(uid)
    buut = keyboard(player, user, inventor)
    spell_player = spell_mob = "Fenrial_TG/spells/rpg03_013.jpg"
    dop_text_user_attack = ""
    match user["vid_mob"]:
        case "🦇":
            substrate = "Fenrial_TG/moobs/t5cc_QEdE5c_f.jpg"
        case "🧟‍♂️":
            substrate = "Fenrial_TG/moobs/TfD0aaRQ5fI_f.jpg"
        case "💀":
            substrate = "Fenrial_TG/moobs/VDTh1K2lQ7E_f.jpg"
    attachment = open(
        image_combat(
            uid, substrate, player, user, spell_player, spell_mob, course_of_battle=0
        ),
        "rb",
    )
    match player["clas"]:
        case 1:
            dop_text_user_attack = f'\n\n✊🏻Ярость: {user["status_skill_1"]}'
        case 2:
            dop_text_user_attack = f'\n\n🗡Серия ударов: {user["status_skill_2"]}'
        case 3:
            if user["status_skill_1"] > 0:
                dop_text_user_attack = f'\n\n💎Морозный щит: {user["status_skill_1"]}'
    bot.edit_message_media(
        media=telebot.types.InputMedia(
            type="photo",
            media=attachment,
            caption=f"<b>⚠️Ваши действия:</b>{dop_text_user_attack}",
            parse_mode="html",
        ),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=buut,
    )


def application_potion(uid, call, inventor, player, item):
    user = user_battle(uid)
    dop_text_user_attack = ""
    bd.exec(
        f"UPDATE statistics SET potions_drunk = potions_drunk + 1 where vkid = {uid}",
        None,
    )
    if item == "🔴Флакон жизни":
        text = f'💚Восстановлено {int(player["stamina"]*3)} HP\n\n'
        hp_player = user["nhp"] + int(player["stamina"] * 3)
        if hp_player > user["hp"]:
            hp_player = user["hp"]
        nhp_update(uid, hp_player)
        engine.decrease_minus(uid, 103, 1)
        spell_player = "Fenrial_TG/spells/id_103.jpg"
    else:
        text = "⛎Восстановлено 30 MP\n\n"
        mp_player = user["mp"] + 30
        if mp_player > 100:
            mp_player = 100
        nmp_update(uid, mp_player)
        engine.decrease_minus(uid, 104, 1)
        spell_player = "Fenrial_TG/spells/id_104.jpg"
    bd.exec(f"UPDATE battle SET cooldown_potion = 5 where vkid = {uid}", None)
    user = user_battle(uid)
    ### Навыки ###
    spell_mob = "Fenrial_TG/spells/rpg03_013.jpg"
    match user["vid_mob"]:
        case "🦇":
            substrate = "Fenrial_TG/moobs/t5cc_QEdE5c_f.jpg"
        case "🧟‍♂️":
            substrate = "Fenrial_TG/moobs/TfD0aaRQ5fI_f.jpg"
        case "💀":
            substrate = "Fenrial_TG/moobs/VDTh1K2lQ7E_f.jpg"
    attachment = open(
        image_combat(
            uid, substrate, player, user, spell_player, spell_mob, course_of_battle=0
        ),
        "rb",
    )
    buut = keyboard(player, user, inventor)
    match player["clas"]:
        case 1:
            dop_text_user_attack = f'\n\n✊🏻Ярость: {user["status_skill_1"]}'
        case 2:
            dop_text_user_attack = f'\n\n🗡Серия ударов: {user["status_skill_2"]}'
        case 3:
            if user["status_skill_1"] > 0:
                dop_text_user_attack = f'\n\n💎Морозный щит: {user["status_skill_1"]}'
    bot.edit_message_media(
        media=telebot.types.InputMedia(
            type="photo",
            media=attachment,
            caption=f"{text}<b>⚠️Ваши действия:</b>{dop_text_user_attack}",
            parse_mode="html",
        ),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=buut,
    )


from dataclasses import dataclass


@dataclass
class PlayerCombat:
    class_player: int = 0
    nhp: int = 0
    status: int = 0
    move_index: int = 0
    hp: int = 0
    mp: int = 0
    cooldown_potion: int = 0
    evasion: int = 0
    attack_player: int = 0
    intellect: int = 0
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

    physical_protection_mob: int = 0
    magical_protection_mob: int = 0

    def skill_number(self, skill) -> bool:
        match skill.skill_number:
            case 1:
                return self.skill_1
            case 2:
                return self.skill_2
            case 3:
                return self.skill_3
            case 4:
                return self.skill_4
            case 5:
                return self.skill_5

    def addiction_number(self, skill) -> bool:
        match skill.addiction:
            case 1:
                return self.skill_1_stack
            case 2:
                return self.skill_2_stack
            case 3:
                return self.skill_3_stack
            case 4:
                return self.skill_4_stack
            case 5:
                return self.skill_5_stack
            case 10:
                return self.attack_player_stack

    def is_ready_skill(self, skill) -> bool:
        if skill.addiction == 0:
            if (
                self.move_index >= self.skill_number(skill) + skill.cooldown_skill
                and self.mp >= skill.skill_cost
            ):
                return skill.as_button()
        else:
            if (
                self.move_index >= self.skill_number(skill) + skill.cooldown_skill
                and self.addiction_number(skill) > 1
                and self.mp >= skill.skill_cost
            ):
                return skill.as_button()

    def damage(self, skill) -> bool:
        if skill.skill_damage_type == 0:
            self.dmg = randint(
                int(
                    self.attack_player
                    * 0.8
                    * skill.skill_coefficient
                    * ((100 - self.physical_protection_mob) / 100)
                ),
                int(
                    self.attack_player
                    * 1.2
                    * skill.skill_coefficient
                    * ((100 - self.physical_protection_mob) / 100)
                ),
            )
            if skill.addiction == 10:
                self.dmg * self.addiction_number(skill)
        else:
            self.dmg = randint(
                int(
                    self.intellect
                    * 0.8
                    * skill.skill_coefficient
                    * ((100 - self.magical_protection_mob) / 100)
                ),
                int(
                    self.intellect
                    * 1.2
                    * skill.skill_coefficient
                    * ((100 - self.magical_protection_mob) / 100)
                ),
            )
        return self.dmg

    @property
    def critical(self):
        """Проверка на срабатывание крита"""
        return randint(1, 100) <= 5

    @property
    def chance_evasion(self):
        """Проверка на уклонение"""
        tmp_miss = randint(1, 100)
        return tmp_miss <= self.evasion

    @property
    def hp_percent(self):
        """Процент хп для отрисовки бара хп"""
        if int(self.nhp / self.hp * 100) // 10 == 0 and self.nhp > 0:
            return 1
        else:
            return int(self.nhp / self.hp * 100) // 10

    @property
    def mp_percent(self):
        """Процент мп для отрисовки бара хп"""
        if self.mp // 10 == 0 and self.mp > 0:
            return 1
        else:
            return self.mp // 10


def user_battle(uid):
    """Выгрузка таблицы бой из БД для удобства"""
    for item in bd.battle(uid):
        user = PlayerCombat(
            class_player=item.get("vkid", 0),
            nhp=item.get("nhp", 0),
            status=item.get("status", 0),
            move_index=item.get("move_index", 0),
            hp=item.get("hp", 0),
            mp=item.get("mp", 0),
            cooldown_potion=item.get("cooldown_potion", 0),
            evasion=item.get("evasion", 0),
            attack_player=item.get("attack_player", 0),
            intellect=item.get("intellect", 0),
            attack_player_stack=item.get("attack_player_stack", 0),
            skill_1=item.get("skill_1", 0),
            skill_1_stack=item.get("skill_1_stack", 0),
            skill_2=item.get("skill_2", 0),
            skill_2_stack=item.get("skill_2_stack", 0),
            skill_3=item.get("skill_3", 0),
            skill_3_stack=item.get("skill_3_stack", 0),
            skill_4=item.get("skill_4", 0),
            skill_4_stack=item.get("skill_4_stack", 0),
            skill_5=item.get("skill_5", 0),
            skill_5_stack=item.get("skill_5_stack", 0),
            physical_protection_mob=item.get("physical_protection_mob", 1),
            magical_protection_mob=item.get("magical_protection_mob", 1),
        )
        return user


@dataclass
class MobCombat:
    id: int = 0
    name_mob: str = ""
    vid_mob: str = ""
    lvl_mob: int = 0
    attack_mob: int = 0
    nhp_mob: int = 0
    hp_mob: int = 0
    def_player: int = 0

    @property
    def damage(self):
        self.dmg = randint(
            int(self.attack_mob * 0.8 * ((100 - self.def_player) / 100)),
            int(self.attack_mob * 1.2 * ((100 - self.def_player) / 100)),
        )
        return f"🗡Противник нанес {self.dmg} урона"


def mob_battle(uid):
    """Выгрузка таблицы бой из БД для удобства"""
    for item in bd.battle(uid):
        mob = MobCombat(
            name_mob=item.get("name_mob", "Моб"),
            vid_mob=item.get("vid_mob", "Вид Моба"),
            lvl_mob=item.get("lvl_mob", 1),
            attack_mob=item.get("attack_mob", 1),
            nhp_mob=item.get("nhp_mob", 1),
            hp_mob=item.get("hp_mob", 1),
            def_player=item.get("def_player", 1),
        )
        return mob


@dataclass
class CombatSkill:
    skill_icon: str = ""
    skill_name: str = ""
    skill_picture: str = ""
    skill_cost: int = 0
    skill_coefficient: int = 1
    cooldown_skill: int = 0
    skill_damage_type: int = 0
    button_text: str = ""
    skill_number: int = 0
    addiction: int = 0

    def as_button(self) -> str:
        return f"{self.skill_icon}{self.button_text}({self.skill_cost})"


insidious_blow = CombatSkill(
    skill_icon="🗡",
    skill_name="Коварный удар",
    skill_picture="Fenrial_TG/spells/jJ-SsZhfOqU.jpg",
    skill_cost=7,
    skill_coefficient=3,
    cooldown_skill=0,
    skill_damage_type=0,
    button_text="КУ",
    skill_number=1,
    addiction=0,
)

gutting = CombatSkill(
    skill_icon="⚔️",
    skill_name="Потрошение",
    skill_picture="Fenrial_TG/spells/jJ-SsZhfOqU.jpg",
    skill_cost=12,
    skill_coefficient=5,
    cooldown_skill=0,
    skill_damage_type=0,
    button_text="Птр",
    skill_number=2,
    addiction=1,
)

strong_beat = CombatSkill(
    skill_icon="✊🏻",
    skill_name="Мощный удар",
    skill_picture="Fenrial_TG/spells/jJ-SsZhfOqU.jpg",
    skill_cost=20,
    skill_coefficient=2,
    cooldown_skill=0,
    skill_damage_type=0,
    button_text="МУ",
    skill_number=2,
    addiction=10,
)

ademis = user_battle(5499224283)
mob = mob_battle(5499224283)



skill_player = insidious_blow
print(ademis.damage(skill_player))
print(skill_player.skill_icon,skill_player.skill_name)
print(skill_player.skill_picture)


@dataclass
class Effects:
    skill_icon: str = ""
    skill_name: str = ""
    skill_picture: str = ""
    skill_cost: int = 0
    skill_coefficient: int = 1
    cooldown_skill: int = 0
    effects_type: int = 0
    ###1-кровотечение, 2-снижение атаки, 3-снижение брони, 4-щит с частичным поглощением, 5-исключение получения урона(скачок, ослепление...), 6-повышение атаки###
    button_text: str = ""
    skill_number: int = 0
    lasting: int = 0
    ###Продолжительность ходов###

    def as_button(self) -> str:
        return f"{self.skill_icon}{self.button_text}({self.skill_cost})"

    def action_check(self, player):
        player.move_index


#            id
#            class_player
#            nhp
#            status
#            move_index

#            hp
#            mp

#            def_player
#            evasion
#            attack_player
#            intellect

#            cooldown_potion

#            attack_player_stack
#            skill_1
#            skill_1_stack
#            skill_2
#            skill_2_stack
#            skill_3
#            skill_3_stack
#            skill_4
#            skill_4_stack
#            skill_5
#            skill_5_stack

#            name_mob
#            vid_mob
#            lvl_mob
#            attack_mob
#            nhp_mob
#            hp_mob
#            physical_protection_mob
#            magical_protection_mob


#            bleeding
#            attack_reduction
#            attack_boost

