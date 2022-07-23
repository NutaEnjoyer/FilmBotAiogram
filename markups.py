from aiogram import types
import keyboard_text as kt


def start():
	m = types.ReplyKeyboardMarkup(resize_keyboard=True)
	t = kt.start
	b1 = types.KeyboardButton(t[0])
	b2 = types.KeyboardButton(t[1])
	b3 = types.KeyboardButton(t[2])
	m.add(b1, b2)
	m.add(b3)
	return m

def only_back():
	m = types.ReplyKeyboardMarkup(resize_keyboard=True)
	t = kt.back
	b = types.KeyboardButton(t)
	m.add(b)
	return m

def premium():
	m = types.InlineKeyboardMarkup()
	t = kt.premium[0]
	b = types.InlineKeyboardButton(t, callback_data='premium')
	m.add(b)
	return m

def premium_buy(bill_id, bill_url):
	m = types.InlineKeyboardMarkup()
	t = kt.premium_buy
	b1 = types.InlineKeyboardButton(t[0], url=bill_url)
	b2 = types.InlineKeyboardButton(t[1], callback_data=f'check${bill_id}')
	m.add(b1)
	m.add(b2)
	return m

def admin_start():
	m = types.ReplyKeyboardMarkup(resize_keyboard=True)
	t = kt.admin_start
	b1 = types.KeyboardButton(t[0])
	b2 = types.KeyboardButton(t[1])
	b3 = types.KeyboardButton(t[2])
	m.add(b1, b2)
	m.add(b3)
	return m

def admin_settings():
	m = types.ReplyKeyboardMarkup(resize_keyboard=True)
	t = kt.admin_settings
	b1 = types.KeyboardButton(t[0])
	b2 = types.KeyboardButton(t[1])
	b3 = types.KeyboardButton(t[2])
	b4 = types.KeyboardButton(t[3])
	m.add(b1, b2)
	m.add(b3)
	m.add(b4)
	return m

def admin_back_settings():
	m = types.ReplyKeyboardMarkup(resize_keyboard=True)
	t = kt.admin_back_settings
	b1 = types.KeyboardButton(t)
	m.add(b1)
	return m

def admin_edit_film(film_id):
	m = types.InlineKeyboardMarkup()
	t = kt.admin_edit_film
	b1 = types.InlineKeyboardButton(t[0], callback_data=f'edit_code${film_id}')
	b2 = types.InlineKeyboardButton(t[1], callback_data=f'delete_film${film_id}')
	b3 = types.InlineKeyboardButton(t[2], callback_data='delete_message')
	m.add(b1)
	m.add(b2)
	m.add(b3)
	return m

def admin_edit_code():
	m = types.ReplyKeyboardMarkup(resize_keyboard=True)
	t = kt.admin_back
	b1 = types.KeyboardButton(t)
	m.add(b1)
	return m

def admin_channels(channels):
	m = types.InlineKeyboardMarkup()
	for channel in channels:
		if channel.active:
			b = types.InlineKeyboardButton(channel.title, callback_data=f'edit_channel${channel.id}')
			m.add(b)
	b = types.InlineKeyboardButton(kt.deactive_channels, callback_data='deactive_channels')
	m.add(b)
	b = types.InlineKeyboardButton(kt.admin_add_channel, callback_data='add_channel')
	m.add(b)
	return m

def admin_deactive_channels(channels):
	m = types.InlineKeyboardMarkup()
	for channel in channels:
		if not channel.active:
			b = types.InlineKeyboardButton(channel.title, callback_data=f'edit_channel${channel.id}')
			m.add(b)
	b = types.InlineKeyboardButton(kt.channel[2], callback_data=f'back_channels')
	m.add(b)
	return m

def channel(id):
	m = types.InlineKeyboardMarkup()
	t = kt.channel
	b1 = types.InlineKeyboardButton(t[0], callback_data=f'deactivate${id}')
	b2 = types.InlineKeyboardButton(t[1], callback_data=f'delete_channel${id}')
	b3 = types.InlineKeyboardButton(t[2], callback_data=f'back_channels')
	m.add(b1)
	m.add(b2)
	m.add(b3)
	return m

def follow(channels):
	m = types.InlineKeyboardMarkup()
	for channel in channels:
		if channel.active:
			b = types.InlineKeyboardButton(channel.title, url=channel.url)
			m.add(b)
	b = types.InlineKeyboardButton(kt.check_follow, callback_data='check_follow')
	m.add(b)
	return m



