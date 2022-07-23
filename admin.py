import random

from aiogram import Bot, Dispatcher, executor, types

import TEXTS
import keyboard_text as kt
import markups
from State import State
from config import TOKEN_ADMIN
from models import *

bot = Bot(TOKEN_ADMIN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
state = State()

chat_data_id = '-1001673276336'
len_code = 5

def get_random_code():
	sloves = 'qwertyuiopasdfghjklzxcvbnm12345678901234567890'
	resp = ''
	for i in range(5):
		resp += random.choice(sloves)
	return resp.upper()


async def start_func(message: types.Message):
	t = kt.admin_start
	txt = message.text
	if txt == t[0]:
		await bot.send_message(message.chat.id, TEXTS.admin_send_video, reply_markup=markups.only_back())
		state.set(message.chat.id, 'send_video')
	elif txt == t[1]:
		films = Film.select()
		txt = TEXTS.films_start
		for film in films:
			t = TEXTS.film_form.format(id=film.id, title=film.title, code=film.code)
			txt += t
		txt += TEXTS.film_end.format(l=len(films))
		state.set(message.chat.id, 'send_id')
		await bot.send_message(message.chat.id, txt, reply_markup=markups.only_back())

	elif txt == t[2]:
		await bot.send_message(message.chat.id, TEXTS.admin_settings, reply_markup=markups.admin_settings())

async def settings_func(message: types.Message):
	txt = message.text
	t = kt.admin_settings
	if txt == t[0]:
		limit = Config.get().start_limit
		state.set(message.chat.id, 'send_limit')
		await bot.send_message(message.chat.id, TEXTS.admin_limit_message.format(limit=limit), reply_markup=markups.admin_back_settings())

	elif txt == t[1]:
		price = Config.get().price
		state.set(message.chat.id, 'send_price')
		await bot.send_message(message.chat.id, TEXTS.admin_price_message.format(price=price), reply_markup=markups.admin_back_settings())

	elif txt == t[2]:
		channels = Channel.select()
		await bot.send_message(message.chat.id, TEXTS.admin_channels_message, reply_markup=markups.admin_channels(channels))


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
	state.clear(message.chat.id)
	await bot.send_message(message.chat.id, TEXTS.admin_start_message, reply_markup=markups.admin_start())

@dp.message_handler(content_types=['text'])
async def text_handler(message: types.Message):
	txt = message.text
	st = state.get(message.chat.id)
	if txt == kt.back:
		await start_handler(message)

	elif txt == kt.admin_back_settings:
		state.clear(message.chat.id)
		await bot.send_message(message.chat.id, TEXTS.admin_settings, reply_markup=markups.admin_settings())

	elif st == 'add_channel':
		try:
			chat_id = message.forward_from_chat.id
			members = await bot.get_chat_administrators(chat_id)
			flag = False
			for member in members:
				if member.user.id == 5305369632:
					flag = True
			if not flag:
				await bot.send_message(message.chat.id, TEXTS.add_first_bot)
				return
			chat = await bot.get_chat(chat_id)
			url = chat.invite_link
			channel = Channel.create(title=chat.title, chat_id=chat_id, url=url)
			channel.save()
			await bot.send_message(message.chat.id, TEXTS.channel_added, reply_markup=markups.admin_settings())
			state.clear(message.chat.id)
			channels = Channel.select()
			await bot.send_message(message.chat.id, TEXTS.admin_channels_message, reply_markup=markups.admin_channels(channels))

		except Exception as e:
			print(e)
			await bot.send_message(message.chat.id, TEXTS.no_admin)

		return

	elif st == 'send_limit':
		if not txt.isdigit():
			await bot.send_message(message.chat.id, TEXTS.is_not_int)
		else:
			config = Config.get()
			config.edit_start_limit(int(txt))
			await bot.send_message(message.chat.id, TEXTS.admin_limit_changed)
			state.clear(message.chat.id)
			await bot.send_message(message.chat.id, TEXTS.admin_settings, reply_markup=markups.admin_settings())

	elif st == 'send_price':
		if not txt.isdigit():
			await bot.send_message(message.chat.id, TEXTS.is_not_int)
		else:
			config = Config.get()
			config.edit_price(int(txt))
			await bot.send_message(message.chat.id, TEXTS.admin_price_changed)
			state.clear(message.chat.id)
			await bot.send_message(message.chat.id, TEXTS.admin_settings, reply_markup=markups.admin_settings())

	elif st == 'send_id':
		if not txt.isdigit():
			await bot.send_message(message.chat.id, TEXTS.is_not_int)
		else:
			film = Film.get_or_none(id=int(txt))
			if film is None:
				await bot.send_message(message.chat.id, TEXTS.admin_no_film)
			else:
				await bot.copy_message(message.chat.id, chat_data_id, film.message_id, reply_markup=markups.admin_edit_film(film.id))

	elif txt == kt.admin_back:
		state.clear(message.chat.id)
		films = Film.select()
		txt = TEXTS.films_start
		for film in films:
			t = TEXTS.film_form.format(id=film.id, title=film.title, code=film.code)
			txt += t
		txt += TEXTS.film_end.format(l=len(films))
		state.set(message.chat.id, 'send_id')
		await bot.send_message(message.chat.id, txt, reply_markup=markups.only_back())


	elif st.split('$')[0] == 'send_code':
		if len(txt) != 5:
			await bot.send_message(message.chat.id, TEXTS.incorect_code)
			return
		id = int(st.split('$')[1])
		code = txt.upper()
		film = Film.get_or_none(id=id)
		if film is None:
			await bot.send_message(message.chat.id, TEXTS.admin_no_film)
			await start_handler(message)
		else:
			film.code = code
			film.save()
			await bot.send_message(message.chat.id, TEXTS.admin_successful_edit_code)
			await start_handler(message)

	elif txt in kt.admin_start:
		await start_func(message)

	elif txt in kt.admin_settings:
		await settings_func(message)


@dp.message_handler(content_types=['photo'])
async def photo_handler(message: types.Message):
	if state.get(message.chat.id) == 'add_channel':
		try:
			chat_id = message.forward_from_chat.id
			members = await bot.get_chat_administrators(chat_id)
			flag = False
			for member in members:
				if member.user.id == 5305369632:
					flag = True
			if not flag:
				await bot.send_message(message.chat.id, TEXTS.add_first_bot)
				return
			chat = await bot.get_chat(chat_id)
			url = chat.invite_link
			channel = Channel.create(title=chat.title, chat_id=chat_id, url=url)
			channel.save()
			await bot.send_message(message.chat.id, TEXTS.channel_added, reply_markup=markups.admin_settings())
			state.clear(message.chat.id)
			channels = Channel.select()
			await bot.send_message(message.chat.id, TEXTS.admin_channels_message, reply_markup=markups.admin_channels(channels))

		except Exception as e:
			print(e)
			await bot.send_message(message.chat.id, TEXTS.no_admin)

		return

@dp.message_handler(content_types=['video'])
async def video_handler(message: types.Message):
	if state.get(message.chat.id) == 'add_channel':
		try:
			chat_id = message.forward_from_chat.id
			members = await bot.get_chat_administrators(chat_id)
			flag = False
			for member in members:
				if member.user.id == 5305369632:
					flag = True
			if not flag:
				await bot.send_message(message.chat.id, TEXTS.add_first_bot)
				return
			chat = await bot.get_chat(chat_id)
			url = chat.invite_link
			channel = Channel.create(title=chat.title, chat_id=chat_id, url=url)
			channel.save()
			await bot.send_message(message.chat.id, TEXTS.channel_added, reply_markup=markups.admin_settings())
			state.clear(message.chat.id)
			channels = Channel.select()
			await bot.send_message(message.chat.id, TEXTS.admin_channels_message, reply_markup=markups.admin_channels(channels))

		except Exception as e:
			print(e)
			await bot.send_message(message.chat.id, TEXTS.no_admin)

		return
	elif state.get(message.chat.id) == 'send_video':
		t = message.caption
		if t is None:
			await bot.send_message(message.chat.id, TEXTS.admin_send_video)
			return
		s = t.split('#')
		l = len(s)
		if l == 1:
			title = s[0]
			code = get_random_code()
			mes = await bot.send_video(chat_data_id, message.video.file_id, caption=TEXTS.video_form.format(title=title))
			mes_id = mes.message_id
			while not(Film.get_or_none(Film.code == code) is None):
				code = get_random_code()
			film = Film.create(title=title, code=code, message_id=mes_id)
			film.save()
			await start_handler(message)
		elif l == 2:
			title = s[0]
			description = s[1]
			code = get_random_code()
			mes = await bot.send_video(chat_data_id, message.video.file_id,
										   caption=TEXTS.video_form_with_description.format(title=title, description=description))
			mes_id = mes.message_id
			while not(Film.get_or_none(Film.code == code) is None):
				code = get_random_code()
			film = Film.create(title=title, description=description, code=code, message_id=mes_id)
			film.save()
			await bot.send_message(message.chat.id, TEXTS.code_form.format(code=code))
			await start_handler(message)
		elif l == 3:
			title = s[0]
			description = s[1]
			code = s[2]
			if len(code) != len_code:
				await bot.send_message(message.chat.id, TEXTS.admin_send_video_code_error)
				return
			if description == 'None':
				mes = await bot.send_video(chat_data_id, message.video.file_id, caption=TEXTS.video_form.format(title=title))
				mes_id = mes.message_id
				while not (Film.get_or_none(Film.code == code) is None):
					code = get_random_code()
				film = Film.create(title=title, code=code, message_id=mes_id)
				film.save()


			else:
				mes = await bot.send_video(chat_data_id, message.video.file_id,
										   caption=TEXTS.video_form_with_description.format(title=title, description=description))
				mes_id = mes.message_id
				while not (Film.get_or_none(Film.code == code) is None):
					code = get_random_code()
				film = Film.create(title=title, description=description, code=code, message_id=mes_id)
				film.save()
		else:
			await bot.send_message(message.chat.id, TEXTS.long_caption)
			return
		await bot.send_message(message.chat.id, TEXTS.code_form.format(code=code))
		await start_handler(message)


@dp.callback_query_handler(lambda c: c.data)
async def callback_handler(call: types.CallbackQuery):
	cll = call.data.split('$')
	c = cll[0]
	if c == 'edit_code':
		id = int(cll[1])
		film = Film.get_or_none(id=id)
		if film is None:
			await bot.send_message(call.message.chat.id, TEXTS.admin_no_film)
			return
		code = film.code
		await bot.send_message(call.message.chat.id, TEXTS.admin_edit_code.format(code=code), reply_markup=markups.admin_edit_code())
		state.set(call.message.chat.id, f'send_code${id}')

	elif c == 'delete_film':
		id = int(cll[1])
		film = Film.get_or_none(id=id)
		await call.message.delete()
		await bot.delete_message(chat_data_id, film.message_id)
		Film.delete_by_id(id)
		await bot.send_message(call.message.chat.id, TEXTS.admin_successful_delete_film)

	elif c == 'delete_message':
		await call.message.delete()

	elif c == 'add_channel':
		await bot.send_message(call.message.chat.id, TEXTS.admin_add_channel_message, reply_markup=markups.only_back())
		state.set(call.message.chat.id, 'add_channel')

	elif c == 'deactive_channels':
		channels = Channel.select()
		await call.message.edit_text(TEXTS.admin_deactive_channels_message, reply_markup=markups.admin_deactive_channels(channels))


	elif c == 'edit_channel':
		id = cll[1]
		channel = Channel.get_or_none(id=id)
		if channel is None:
			await bot.send_message(call.message.chat.id, TEXTS.no_channel)
		else:
			await call.message.edit_text(TEXTS.channel_form.format(title=channel.title, url=channel.url), reply_markup=markups.channel(id=id))

	elif c == 'deactivate':
		id = cll[1]
		channel = Channel.get_or_none(id=id)
		if channel is None:
			await bot.send_message(call.message.chat.id, TEXTS.no_channel)
		else:
			channel.active = not channel.active
			channel.save()
			await bot.send_message(call.message.chat.id, TEXTS.change_active_channel)
			return

	elif c == 'delete_channel':
		id = cll[1]
		Channel.delete_by_id(id)
		await bot.send_message(call.message.chat.id, TEXTS.channel_deleted)

	elif c == 'back_channels':
		channels = Channel.select()
		await call.message.edit_text(TEXTS.admin_channels_message, reply_markup=markups.admin_channels(channels))


if __name__ == '__main__':
	executor.start_polling(dp)
