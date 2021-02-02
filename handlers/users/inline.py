from io import BytesIO

from aiogram import types
from aiogram.dispatcher.filters import Command, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from data.config import allowed_users
from loader import dp, db, bot

from .start import *


async def check_user_from_query(query: types.InlineQuery):
    user_info = await db.get_user_info(query.from_user.id)
    if user_info is None:
        await query.answer(results=[],
            switch_pm_text=INVALID_REF_KEY_MSG,
            )
    return not (user_info is None)


@dp.inline_handler(text="")
async def empty_query(query: types.InlineQuery):
    if await check_user_from_query(query):
        await query.answer(
            results=[
                types.InlineQueryResultArticle(
                    id=str(s["id"]),
                    title=s["name"],
                    description="Цена: " + str(s["price"]),
                    input_message_content=types.InputTextMessageContent(
                        message_text="/start " + str(s["id"]),
#                        message_text= s["name"] + "\nЦена: " + str(s["price"]),
                    )
                ) for s in await db.get_all_goods()
            ],
            cache_time=30
        )


@dp.inline_handler()
async def non_empty_query(query: types.InlineQuery):
    if await check_user_from_query(query):
        goods_list = await db.get_goods_like(query.query.upper())
        if goods_list:
            await query.answer(
                results=[
                        types.InlineQueryResultArticle(
                        id=str(s["id"]+1),
                        title=s["name"],
                        description="Цена: " + str(s["price"]),
                        thumb_url=s['photo_url'],
                        input_message_content=types.InputTextMessageContent(
                            message_text="/start " + str(s["id"]),
                        )
                    ) for s in goods_list
                ],
                cache_time=30,
                switch_pm_text="Показать товар",
                switch_pm_parameter=goods_list[0]['id']
            )


@dp.callback_query_handler(lambda c: c.data.startswith("show"))
async def interrupt_button_handler(call: CallbackQuery, state: FSMContext):
    await call.answer()
    try:
        good_id = int(call.data[5:])
        await show_good_by_id(call.message, good_id, state)
    except:
        pass

