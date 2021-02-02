from random import choice
from string import ascii_letters
from re import compile

from data.config import admins

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import bot, dp, db

INVALID_REF_KEY_MSG = "Чтобы использовать этого бота, введи код приглашения либо пройди по реферальной ссылке"
WELCOME_MSG = "Привет, {}!\n"
RETURN_MSG = "С возвращением, {}\n"
USER_INFO_MSG = "Твой баланс {} монет.\nТвоя реферальная ссылка: {}"

REFERRAL_REWARD = 10.0

def generate_random_string(length: int = 16):
    return ''.join(choice(ascii_letters) for i in range(length))


async def ref_link(ref_key: str):
    return f"https://t.me/{(await bot.me).username}?start={ref_key}"


async def add_admin_to_db(message: types.Message):
    ref_key = generate_random_string()
    await db.add_user(id=message.from_user.id, username=message.from_user.first_name, ref_key=ref_key)
    await message.answer(WELCOME_MSG.format(message.from_user.first_name) +
                         USER_INFO_MSG.format(0, await ref_link(ref_key))
                        )



@dp.message_handler(CommandStart(deep_link=compile(r"\d+$")))
async def bot_start_with_good_id(message: types.Message, state: FSMContext):
    user_info = await db.get_user_info(message.from_user.id)
    if user_info is None:
        if message.from_user.id in admins:
            await add_admin_to_db(message)
        else:
            await message.answer(INVALID_REF_KEY_MSG)
            await state.set_state("start_ref_key")
            return
    param = message.get_args()
    await show_good_by_id(message, int(param), state)


@dp.message_handler(CommandStart(deep_link=''))
async def bot_start_wo_params(message: types.Message, state: FSMContext):
    user_info = await db.get_user_info(message.from_user.id)
    if user_info is None:
        if message.from_user.id in admins:
            await add_admin_to_db(message)
        else:
            await message.answer(INVALID_REF_KEY_MSG)
            await state.set_state("start_ref_key")
    else:
        await message.answer(RETURN_MSG.format(user_info['name']) +
                             USER_INFO_MSG.format(user_info['balance'],
                                                  await ref_link(user_info['refkey'])
                                                  )
                             )


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message, state: FSMContext):
    user_info = await db.get_user_info(message.from_user.id)
    param = message.get_args()
    if user_info is None:
        await check_ref_key(message, state, param)
    else:
        await message.answer(RETURN_MSG.format(user_info['name']) +
                             USER_INFO_MSG.format(user_info['balance'],
                                                  await ref_link(user_info['refkey'])
                                                 )
                            )


async def show_good_by_id(message: types.Message, good_id: int, state: FSMContext):
    s = await db.get_good(good_id)
    if s:
        await state.update_data(good_id=good_id, name=s["name"], price=s["price"],
                                descr=s["descr"], photo_url=s['photo_url'])
        text = s["name"] + "\nЦена: " + str(s["price"]) + "\n" + s["descr"]
        reply_kbd = InlineKeyboardMarkup(inline_keyboard=[
                                                 [InlineKeyboardButton(text="Купить", callback_data=f"buy:{good_id}"),]
                                            ]
                                        )
        if s['file_id'] or s['photo_url']:
            await message.answer_photo(photo=s['file_id'] if s['file_id'] else s['photo_url'],
                                       caption=text, reply_markup=reply_kbd
                                      )
        else:
            await message.answer(text=text, reply_markup=reply_kbd)
    else:
        await message.answer(text=f'Товар с ID {good_id} не найден в базе данных')


async def check_ref_key(message: types.Message, state: FSMContext, ref_key: str):
    referee = await db.get_referee(ref_key)
    if referee is None:
        await message.answer(INVALID_REF_KEY_MSG)
        await state.set_state("start_ref_key")
        return
    await state.update_data(referee=referee)
    await message.answer("Введи свой e-mail")
    await state.set_state("start_email")


@dp.message_handler(state="start_ref_key")
async def enter_ref_key(message: types.Message, state: FSMContext):
    await check_ref_key(message, state, message.text)


@dp.message_handler(state="start_email")
async def enter_email(message: types.Message, state: FSMContext):
    name=message.from_user.first_name
    ref_key=generate_random_string()
    data = await state.get_data()
    referee = data.get("referee")
    await db.add_user(id=message.from_user.id,
                      username=name,
                      ref_key=ref_key,
                      referee=referee,
                      email=message.text)
    if referee:
        await db.add_money(referee, REFERRAL_REWARD)
    await message.answer(WELCOME_MSG.format(name) + USER_INFO_MSG.format(0, await ref_link(ref_key)))
    await state.finish()
