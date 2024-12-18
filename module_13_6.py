from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio


api =""
bot = Bot(token = api)
dp = Dispatcher(bot, storage = MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
calc = KeyboardButton(text = 'Рассчитать')
info = KeyboardButton(text = 'Информация')
kb.add(calc, info)


kb_calc = InlineKeyboardMarkup(row_width=2)
calc_w = InlineKeyboardButton(text = 'Расчет для женщин', callback_data = 'calc_w')
calc_m = InlineKeyboardButton(text = 'Расчет для мужчин', callback_data = 'calc_m')
kb_calc.add(calc_w, calc_m)

kb_calculate = InlineKeyboardMarkup(row_width=2)
calc_women = InlineKeyboardButton(text = 'Расчет для женщин', callback_data = 'calc_women')
calc_men = InlineKeyboardButton(text = 'Расчет для мужчин', callback_data = 'calc_men')
kb_calculate.add(calc_women, calc_men)




kb_1 = InlineKeyboardMarkup()
b1 = InlineKeyboardButton(text = 'Рассчитать норму калорий', callback_data = 'calories')
b2 = InlineKeyboardButton(text = 'Формулы расчёта', callback_data = 'formulas')
kb_1.add(b1, b2)


@dp.message_handler(text = 'Рассчитать')
async def main_menu(message):
    await message.answer("Выберите опцию:", reply_markup = kb_1)


@dp.message_handler(commands = ['start'])
async def start(message):
    await message.answer("Привет! Я бот помогающий твоему здоровью.", reply_markup = kb)

@dp.callback_query_handler(text = 'formulas')
async def get_formulas(call):
    await call.message.answer("Формулы расчёта:", reply_markup = kb_calc)
    # await call.message.answer("10 x вес (кг) + 6,25 х рост (см) - 5 x возраст (г) - 161") # Обобщенная формула
    await call.answer()

@dp.callback_query_handler(text = 'calc_w')
async def get_formulas_w(call):
    await call.message.answer("для женщин: 10 x вес (кг) + 6,25 х рост (см) - 5 x возраст (г) - 161")
    await call.answer()

@dp.callback_query_handler(text = 'calc_m')
async def get_formulas_m(call):
    await call.message.answer("для мужчин: 10 x вес (кг) + 6,25 х рост (см) - 5 x возраст (г) + 5")
    await call.answer()



class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    calories = State()

@dp.callback_query_handler(text = 'calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст')
    await UserState.age.set()
    await call.answer()



@dp.message_handler(state = UserState.age)
async def set_growth(message,state):
    await state.update_data(age=message.text)
    data = await state.get_data()
    await message.answer('Введите свой рост')
    await UserState.growth.set()

@dp.message_handler(state = UserState.growth)
async def set_weigth(message,state):
    await state.update_data(growth=message.text)
    data = await state.get_data()
    await message.answer('Введите свой вес')
    await UserState.weight.set()

@dp.message_handler(state = UserState.weight)
async def send_calories(message,state):
    await state.update_data(weigth=message.text)
    data = await state.get_data(['age', 'growth', 'weigth'])
    await message.answer('Выполнить расчет для мужчин или для женщин?', reply_markup = kb_calculate)
    await UserState.calories.set()

    # """Обобщенная формула"""
    # calc = (10 * int(data['weigth'])) + (6.25 * int(data['growth'])) - (5 * int(data['age'])) - 161
    # await message.answer(f'Ваша норма калорий: {calc}')
    # await state.finish()  # завершаем состояние


@dp.callback_query_handler(text = 'calc_women', state = UserState.calories)
async def calc_W(call, state):
    data = await state.get_data(['age', 'growth', 'weigth'])
    calc_W = (10 * int(data['weigth'])) + (6.25 * int(data['growth'])) - (5 * int(data['age'])) -161
    await call.message.answer(f'Норма калорий для женщин: {calc_W}')
    await state.finish()  # завершаем состояние

#
@dp.callback_query_handler(text = 'calc_men', state = UserState.calories)
async def calc_M(call, state):
    data = await state.get_data(['age', 'growth', 'weigth'])
    calc_M = (10 * int(data['weigth'])) + (6.25 * int(data['growth'])) - (5 * int(data['age'])) + 5
    await call.message.answer(f'Норма калорий для мужчин: {calc_M}')
    await state.finish()  # завершаем состояние



@dp.message_handler()         # перехватываем все сообщения
async def all_messages(message):
    await message.answer("Введите команду /start, чтобы начать общение.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)