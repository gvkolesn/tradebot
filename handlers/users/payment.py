from aiogram import types
from loader import dp, db, bot

from .start import *

from dataclasses import dataclass
from typing import List

from aiogram.types import LabeledPrice, ContentTypes

from data import config


@dataclass
class Item:
    title: str
    description: str
    start_parameter: str
    currency: str
    prices: List[LabeledPrice]
    provider_data: dict = None
    photo_url: str = None
    photo_size: int = None
    photo_width: int = None
    photo_height: int = None
    need_name: bool = False
    need_phone_number: bool = False
    need_email: bool = False
    need_shipping_address: bool = True
    send_phone_number_to_provider: bool = False
    send_email_to_provider: bool = False
    is_flexible: bool = False

    provider_token: str = config.PROVIDER_TOKEN

    def generate_invoice(self):
        return self.__dict__


POST_REGULAR_SHIPPING = types.ShippingOption(
    id='post_reg',
    title='Почтой',
    prices=[
        types.LabeledPrice(
            'Почтой обычной', 10_00),
    ]
)

ONLINE_SHIPPING = types.ShippingOption(
    id='online',
    title='Онлайн',
    prices=[
        types.LabeledPrice(
            'Онлайн', 0),
    ]
)

PAY_WITH_BALANCE_MSG = """У вас есть {} реферальных баллов, которыми можно оплатить часть покупки. 
                       Для оплаты баллами введите их количество (0 - если не хотите оплачивать баллами).
"""

@dp.callback_query_handler(lambda c: c.data.startswith("buy"))
async def buy_button_handler(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
#    good_id = int(call.data[4:])
#    s = await db.get_good(good_id)
#    await state.update_data(good_id=good_id)
#    await state.update_data(good_info=s)
    await call.message.answer("Введите количество")
    await state.set_state("get_qty")


@dp.message_handler(state="get_qty")
async def handle_qty(message: types.Message, state: FSMContext):
    qty = int(message.text)
    if qty <= 0:
        await message.answer("Количество товара должно быть положительным. Процесс покупки прерван.")
        await state.finish()
        return
    await state.update_data(qty=qty)
    balance = await db.get_balance(message.chat.id)
    if balance:
        await message.answer(text=PAY_WITH_BALANCE_MSG.format(balance))
        await state.update_data(balance=balance)
        await state.set_state("bal_payment")
    else:
        await state.update_data(balance=0)
        await make_invoice(message, state)


@dp.message_handler(state="bal_payment")
async def handle_balance_payment(message: types.Message, state: FSMContext):
    payment = int(message.text)
    data = await state.get_data()
    limit = data.get("balance")
    qty = data.get("qty")
    price = data.get("price")
    if payment < 0:
        await message.answer("Количество баллов не может быть отрицательным.\n" +
                             PAY_WITH_BALANCE_MSG.format(limit)
                            )
        return
    elif payment > limit:
        await message.answer("На Вашем балансе недостаточно баллов.\n" +
                             PAY_WITH_BALANCE_MSG.format(limit)
                            )
        return
    elif payment > qty*price:
        await message.answer("Количество баллов не должно превышать цену покупки.\n" +
                             PAY_WITH_BALANCE_MSG.format(limit)
                            )
        return
    else:
        await state.update_data(balance=payment)
        await make_invoice(message, state)


async def make_invoice(message: types.Message, state: FSMContext):
    data = await state.get_data()
    bal_pay = data.get("balance")
    qty = data.get("qty")
    price = data.get("price")
    name = data.get("name")
    descr = data.get("descr")
    photo_url = data.get("photo_url")
    prices = [LabeledPrice(label="Цена", amount=int(qty*price*100)),]
    if bal_pay:
        prices.append(LabeledPrice(label="Оплачено баллами", amount=-bal_pay * 100))
    good = Item(title=f"{qty} x " + name, description=descr,
                currency="RUB",
                prices=prices,
                start_parameter="create_invoice",
                photo_url=photo_url
    )
    await bot.send_invoice(chat_id=message.chat.id,
                           **good.generate_invoice(),
                           payload="123456")
    await state.reset_state(with_data=False)


@dp.shipping_query_handler()
async def choose_shipping(query: types.ShippingQuery):
    await bot.answer_shipping_query(shipping_query_id=query.id,
                                    shipping_options=[POST_REGULAR_SHIPPING],
                                    ok=True)


@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_query.id,
                                        ok=True)


@dp.message_handler(content_types=ContentTypes.SUCCESSFUL_PAYMENT)
async def got_payment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    bal_pay = data.get("balance")
    if bal_pay:
        await db.add_money(message.chat.id, -bal_pay)
    await bot.send_message(chat_id=message.chat.id,
                           text="Спасибо за покупку! Ожидайте отправку"
                          )
    await state.finish()
