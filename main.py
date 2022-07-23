import random
from time import time

from aiogram import Bot, Dispatcher, executor, types

import TEXTS
import keyboard_text as kt
import markups
from QiwiApi import Wallet
from State import State
from config import TOKEN, len_code, chat_data_id, qiwi_token, qiwi_secret_key
from models import *

bot = Bot(TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
state = State()
wallet = Wallet(token=qiwi_token, secret_key=qiwi_secret_key)

c = wallet.get_info_about_me()

async def start_func(message: types.Message):
	t = kt.start
	txt = message.text
	if txt == t[0]:
		user = User.get_or_none(User.user_id == message.chat.id)
		if user.premium:
			films = Film.select()
			film = random.choice(films)
			mes_id = film.message_id
			await bot.copy_message(message.chat.id, chat_data_id, mes_id)  # добавить try так как могут снести канал или мессендж
			return
		if not await check_follow(message.chat.id):
			channels = Channel.select()
			await bot.send_message(message.chat.id, TEXTS.need_follow, reply_markup=markups.follow(channels))
			return
		one_week = Config.get().one_week
		if time() - user.random_last >= one_week:
			films = Film.select()
			film = random.choice(films)
			user.set_random_last(time())
			mes_id = film.message_id
			await bot.copy_message(message.chat.id, chat_data_id, mes_id)  # добавить try так как могут снести канал или мессендж
		else:
			await bot.send_message(message.chat.id, TEXTS.random_unlimited)

	elif txt == t[1]:
		if not await check_follow(message.chat.id):
			channels = Channel.select()
			await bot.send_message(message.chat.id, TEXTS.need_follow, reply_markup=markups.follow(channels))
			return
		await bot.send_message(message.chat.id, TEXTS.send_code_message, reply_markup=markups.only_back())
		state.set(message.chat.id, 'send_code')
	elif txt == t[2]:
		await bot.send_message(message.chat.id, TEXTS.premium_message, reply_markup=markups.premium())

async def send_code_func(message):
	code = message.text.upper()
	if len(code) != len_code:
		await bot.send_message(message.chat.id, TEXTS.incorect_code)
		return
	user = User.get_or_none(User.user_id == message.chat.id)

	if user.premium:
		film = Film.get_or_none(Film.code == code)
		if film is None:
			await bot.send_message(message.chat.id, TEXTS.unfind_film)
		else:
			mes_id = film.message_id
			await bot.copy_message(message.chat.id, chat_data_id, mes_id)  # добавить try так как могут снести канал или мессенд
	else:
		if user.limit == 0:
			now = time()
			one_day = Config.get().one_day
			start_limit = Config.get().start_limit
			if now - user.last >= one_day:
				user.up_limit(start_limit)
				film = Film.get_or_none(Film.code == code)
				if film is None:
					await bot.send_message(message.chat.id, TEXTS.unfind_film)
				else:
					user.down_limit()
					user.set_last(time())
					mes_id = film.message_id
					await bot.copy_message(message.chat.id, chat_data_id, mes_id)  # добавить try
			else:
				await bot.send_message(message.chat.id, TEXTS.unlimited)
				return

		film = Film.get_or_none(Film.code == code)
		if film is None:
			await bot.send_message(message.chat.id, TEXTS.unfind_film)
		else:
			user.down_limit()
			user.set_last(time())
			mes_id = film.message_id
			await bot.copy_message(message.chat.id, chat_data_id, mes_id)  # добавить try

async def mail_func(message: types.Message):
	state.clear(message.chat.id)
	users = User.select()
	suc = 0
	unsuc = 0
	for user in users:
		try:
			await message.send_copy(user.user_id)
			suc += 1
		except Exception:
			unsuc += 1
	await bot.send_message(message.chat.id, TEXTS.mail_form.format(suc=suc, unsuc=unsuc))
	await start_handler(message)


async def check_follow(user_id):
	channels = Channel.select()
	flag = True
	if len(channels) == 0:
		await bot.get_me()
	for channel in channels:
		if channel.active:
			user_channel_status = await bot.get_chat_member(chat_id=channel.chat_id, user_id=user_id)
			if user_channel_status["status"] == 'left':
				flag = False
	return flag

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
	user = User.get_or_none(User.user_id == message.chat.id)
	if user is None:
		start_limit = Config.get().start_limit
		user = User.create(user_id=message.chat.id, limit=start_limit)
		user.save()
	state.clear(message.chat.id)
	await bot.send_message(message.chat.id, TEXTS.start_message, reply_markup=markups.start())

@dp.message_handler(commands=['restart'])
async def restart_handler(message: types.Message):
	state.clear(message.chat.id)
	await bot.send_message(message.chat.id, TEXTS.start_message, reply_markup=markups.start())

@dp.message_handler(commands=['secret_c'])
async def mail_handler(message: types.Message):
	state.set(message.chat.id, 'mail')
	await bot.send_message(message.chat.id, TEXTS.mail_message, reply_markup=markups.only_back())

@dp.message_handler(content_types=['text'])
async def text_handler(message: types.Message):
	txt = message.text
	st = state.get(message.chat.id)
	if txt == kt.back:
		await restart_handler(message)
	elif st == 'mail':
		await mail_func(message)
	elif st == 'send_code':
		await send_code_func(message)
	elif txt in kt.start:
		await start_func(message)

@dp.message_handler(content_types=['photo', 'video'])
async def media_handler(message: types.Message):
	st = state.get(message.chat.id)
	if st == 'mail':
		await mail_func(message)

@dp.callback_query_handler(lambda c: c.data)
async def callback_handler(call: types.CallbackQuery):
	cll = call.data.split('$')
	c = cll[0]
	if c == 'premium':
		price = Config.get().price
		print('s')
		bill = wallet.new_bill(price)
		bill_id = bill['billId']
		bill_url = bill['payUrl']
		await call.message.edit_text(TEXTS.premium_buy_message.format(price=price), reply_markup=markups.premium_buy(
			bill_id, bill_url))
	elif c == 'check':
		bill_id = cll[1]
		if wallet.get_info_bill(bill_id)['status']['value'] == 'PAID':
			user = User.get_or_none(user_id=call.message.chat.id)
			if user is None:
				await bot.send_message(call.message.chat.id, TEXTS.premium_trouble)
			else:
				user.premium = True
				user.save()
				await bot.send_message(call.message.chat.id, TEXTS.premium_added)
				await call.message.delete()
		else:
			await bot.answer_callback_query(call.id, TEXTS.payment_not_found, show_alert=True)

	elif c == 'check_follow':
		if await check_follow(call.message.chat.id):
			await call.message.delete()
			await bot.send_message(call.message.chat.id, TEXTS.continue_use)
		else:
			await bot.answer_callback_query(call.id, TEXTS.no_follow, show_alert=False)


if __name__ == '__main__':
	executor.start_polling(dp)
