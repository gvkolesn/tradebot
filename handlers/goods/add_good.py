from io import BytesIO

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Command

from data.config import admins
from loader import dp, db


@dp.message_handler(Command("add"))
async def handle_add_command(message: types.Message, state: FSMContext):
    if message.from_user.id not in admins:
        await message.answer("Добавлять товары в базу могут только администраторы.")
        return
    if len(message.text) == 4:
        await message.answer("Название товара:")
        await state.set_state("add_good_name")
    else:
        good_name=message.text[4:].strip()
        await enter_good_name(good_name, message, state)


@dp.message_handler(state="add_good_name")
async def set_good_name(message: types.Message, state: FSMContext):
    await enter_good_name(message.text, message, state)


async def enter_good_name(name: str, message: types.Message, state: FSMContext):
    await state.update_data(good_name=name)
    await message.answer("Введите описание товара:")
    await state.set_state("add_descr")


@dp.message_handler(state="add_descr")
async def set_good_description(message: types.Message, state: FSMContext):
    await state.update_data(good_descr=message.text)
    await message.answer("Введите цену товара:")
    await state.set_state("add_price")


@dp.message_handler(state="add_price")
async def set_good_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)
    except:
        await message.answer("Цена товара должна быть вещественным числом.")
        return
    await state.update_data(good_price=price)
    await message.answer("Загрузите фотографию или введите URL")
    await state.set_state("add_photo")


@dp.message_handler(state="add_photo", content_types=['text','photo'])
async def set_photo(message: types.Message, state: FSMContext):
    photo_params = {}
    if message.photo:
        photo_buffer = BytesIO()
        await message.photo[-1].download(destination=photo_buffer)
        photo_params["file_id"] = message.photo[-1].file_id
        photo_params["photo"] = photo_buffer.getvalue()
    else:
        photo_params["photo_url"] = message.text

    data = await state.get_data()
    name = data.get("good_name")
    descr = data.get("good_descr")
    price = data.get("good_price")
    try:
        good_id = await db.add_good(name=name, price=price, descr=descr, **photo_params)
    except:
        good_id = 0
    if good_id > 0:
        await message.answer(f"Товар успешно добавлен!\nID товара в БД {good_id}")
    else:
        await message.answer("Ошибка записи данных")
    await state.finish()


@dp.message_handler(Command("del"))
async def handle_del_command(message: types.Message):
    param = message.get_args()
    if message.from_user.id in admins and param and param.isnumeric():
        await db.delete_good(int(param))
        await message.answer(f"Товар ID {param} удален из базы данных.")
