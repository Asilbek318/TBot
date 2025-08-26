import re
import json
import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# Load configuration directly
API_TOKEN = "7962161598:AAEkaFGdGzM4q0lcdVH5zApHLEhLTwnE5o8"
ADMIN_ID = 6532973155

bot = telebot.TeleBot(API_TOKEN, parse_mode='HTML')

# Channel information
CHANNEL_USERNAME = "@OffSec_uz"
CHANNEL_LINK = "https://t.me/OffSec_uz"

# Courses list
courses = [
    "🔠 Kompyuter savodxonligi",
    "🐍 Python dasturlash tili",
    "📜 Javascript dasturlash tili",
    "🌐 Web dasturlash",
    "🎨 Grafik dizayn",
    "🤖 Robototexnika",
    "🔐 Axborot xavfsizligi",
    "📱 SMM kursi",
]

# Languages list
languages = [
    "🇺🇸 Ingliz tili",
    "🇷🇺 Rus tili",
    "🇰🇷 Koreys tili",
    "🇩🇪 Nemis tili",
]

# Mental games list
mental_games = [
    "♟️ Shaxmat kursi",
    "🎯 Strategiya o'yinlari",
]

# User data storage
user_data = {}
DATA_FILE = "user_registrations.json"

# Create data file if it doesn't exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)


# Load existing registrations
def load_registrations():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


# Save registrations to file
def save_registration(user_id, data):
    registrations = load_registrations()
    registrations[str(user_id)] = {
        **data,
        "registration_date": datetime.now().isoformat()
    }

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(registrations, f, ensure_cii=False, indent=2)


# Foydalanuvchi kanalga obuna bo'lganligini tekshirish (optional)
def check_subscription(user_id):
    try:
        # Kanal username ni to'g'ri formatda tekshirish
        channel_username = CHANNEL_USERNAME.replace('@', '') if CHANNEL_USERNAME.startswith('@') else CHANNEL_USERNAME

        # Check if the channel username is valid
        if not channel_username:
            return True  # If no channel is set, allow all users

        member = bot.get_chat_member(f"@{channel_username}", user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Obunani tekshirishda xatolik: {e}")
        # Xatolik yuzaga kelsa, foydalanuvchiga imkoniyat berish uchun True qaytarish
        return True


# Input validation functions
def is_valid_name(text):
    return bool(re.match(r'^[A-Za-zА-Яа-яЁёЎўҚқҒғҲҳ\s-]{2,50}$', text))


def is_valid_address(text):
    return bool(re.match(r'^[A-Za-zА-Яа-яЁёЎўҚқҒғҲҳ0-9\s,.\-]{5,100}$', text))


def is_valid_phone(phone):
    return bool(re.match(r'^\+?[1-9]\d{1,14}$', phone))


def is_valid_age(age_text):
    try:
        age = int(age_text)
        return 5 <= age <= 100
    except ValueError:
        return False


# Main menu keyboard
def main_menu_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        KeyboardButton("📚 Kurslar"),
        KeyboardButton("🌍 Tillar"),
        KeyboardButton("🧠 Mental O'yinlar"),
        KeyboardButton("📍 Manzil"),
        KeyboardButton("📞 Aloqa"),
        KeyboardButton("⬅️ Orqaga"),
        KeyboardButton("🔄 Qayta boshlash")
    ]
    markup.add(buttons[0], buttons[1])
    markup.add(buttons[2], buttons[3])
    markup.add(buttons[4])
    markup.add(buttons[5], buttons[6])
    return markup


# Start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id

    # Telefon raqam so'rash
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)
    markup.add(button)

    welcome_text = """
Assalomu alaykum! Xush kelibsiz!
Kurslarimizga ro'yxatdan o'tish uchun telefon raqamingizni yuboring.
"""
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

    # Initialize user data
    user_data[user_id] = {'step': 'awaiting_phone'}


# Contact handler
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user_id = message.chat.id

    if message.contact is not None:
        phone = message.contact.phone_number
        user_data[user_id] = {'phone': phone, 'step': 'confirm_phone'}

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(KeyboardButton("✅ Tasdiqlash"), KeyboardButton("❌ Qayta kiritish"))

        bot.send_message(
            user_id,
            f"📱 Sizning telefon raqamingiz: {phone}\n\nTo'g'ri bo'lsa 'Tasdiqlash' tugmasini bosing, aks holda 'Qayta kiritish' tugmasini bosing:",
            reply_markup=markup
        )
    else:
        bot.send_message(user_id, "❌ Iltimos, telefon raqamingizni yuboring.")


# Phone confirmation handler
@bot.message_handler(
    func=lambda m: m.text == "✅ Tasdiqlash" and user_data.get(m.chat.id, {}).get('step') == 'confirm_phone')
def confirm_phone(message):
    user_id = message.chat.id
    phone = user_data[user_id]['phone']

    bot.send_message(
        user_id,
        f"✅ Telefon raqamingiz qabul qilindi: {phone}\n\nEndi quyidagi menyudan birini tanlang:",
        reply_markup=main_menu_keyboard()
    )

    user_data[user_id]['step'] = 'main_menu'


# Phone re-entry handler
@bot.message_handler(func=lambda m: m.text == "❌ Qayta kiritish")
def request_phone_again(message):
    user_id = message.chat.id

    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)
    markup.add(button)

    bot.send_message(user_id, "Iltimos, telefon raqamingizni qayta yuboring:", reply_markup=markup)
    user_data[user_id] = {'step': 'awaiting_phone'}


# Back button handler
@bot.message_handler(func=lambda m: m.text == "⬅️ Orqaga")
def handle_back(message):
    user_id = message.chat.id
    current_step = user_data.get(user_id, {}).get('step', '')

    if current_step in ['entering_name', 'entering_surname', 'entering_age', 'entering_address']:
        if current_step == 'entering_name':
            show_courses(message)
        elif current_step == 'entering_surname':
            get_name(message)
        elif current_step == 'entering_age':
            get_surname(message)
        elif current_step == 'entering_address':
            get_age(message)
    else:
        # Agar asosiy menyuda "Orqaga" bosilsa, start boshlaymiz
        restart_bot(message)


# Courses menu handler
@bot.message_handler(func=lambda m: m.text == "📚 Kurslar")
def show_courses(message):
    user_id = message.chat.id

    markup = InlineKeyboardMarkup()
    for course in courses:
        markup.add(InlineKeyboardButton(course, callback_data=f"course_{course}"))

    bot.send_message(user_id, "Quyidagi kurslardan birini tanlang:", reply_markup=markup)


# Languages menu handler
@bot.message_handler(func=lambda m: m.text == "🌍 Tillar")
def show_languages(message):
    user_id = message.chat.id

    markup = InlineKeyboardMarkup()
    for language in languages:
        markup.add(InlineKeyboardButton(language, callback_data=f"language_{language}"))

    bot.send_message(user_id, "Quyidagi tillardan birini tanlang:", reply_markup=markup)


# Mental games menu handler
@bot.message_handler(func=lambda m: m.text == "🧠 Mental O'yinlar")
def show_mental_games(message):
    user_id = message.chat.id

    markup = InlineKeyboardMarkup()
    for game in mental_games:
        markup.add(InlineKeyboardButton(game, callback_data=f"game_{game}"))

    bot.send_message(user_id, "Quyidagi mental o'yinlardan birini tanlang:", reply_markup=markup)


# Course selection handler
@bot.callback_query_handler(func=lambda call: call.data.startswith('course_'))
def handle_course_selection(call):
    user_id = call.from_user.id
    course_name = call.data.replace('course_', '')

    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id]['course'] = course_name
    user_data[user_id]['step'] = 'entering_name'

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("⬅️ Orqaga"))

    bot.send_message(user_id, f"Siz {course_name} kursini tanladingiz.\n\nEndi ismingizni kiriting:",
                     reply_markup=markup)
    bot.answer_callback_query(call.id)


# Language selection handler
@bot.callback_query_handler(func=lambda call: call.data.startswith('language_'))
def handle_language_selection(call):
    user_id = call.from_user.id
    language_name = call.data.replace('language_', '')

    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id]['course'] = language_name
    user_data[user_id]['step'] = 'entering_name'

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("⬅️ Orqaga"))

    bot.send_message(user_id, f"Siz {language_name} kursini tanladingiz.\n\nEndi ismingizni kiriting:",
                     reply_markup=markup)
    bot.answer_callback_query(call.id)


# Mental game selection handler
@bot.callback_query_handler(func=lambda call: call.data.startswith('game_'))
def handle_game_selection(call):
    user_id = call.from_user.id
    game_name = call.data.replace('game_', '')

    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id]['course'] = game_name
    user_data[user_id]['step'] = 'entering_name'

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("⬅️ Orqaga"))

    bot.send_message(user_id, f"Siz {game_name} kursini tanladingiz.\n\nEndi ismingizni kiriting:",
                     reply_markup=markup)
    bot.answer_callback_query(call.id)


# Name input handler
@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get('step') == 'entering_name')
def get_name(message):
    user_id = message.chat.id

    if message.text == "⬅️ Orqaga":
        show_courses(message)
        user_data[user_id]['step'] = 'main_menu'
        return

    name = message.text.strip()

    if not is_valid_name(name):
        error_msg = "❌ Noto'g'ri ism formati. Iltimos, faqat harflardan foydalaning (2-50 belgi)."
        bot.send_message(user_id, error_msg)
        return

    user_data[user_id]['name'] = name
    user_data[user_id]['step'] = 'entering_surname'

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("⬅️ Orqaga"))

    bot.send_message(user_id, "Familiyangizni kiriting:", reply_markup=markup)


# Surname input handler
@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get('step') == 'entering_surname')
def get_surname(message):
    user_id = message.chat.id

    if message.text == "⬅️ Orqaga":
        user_data[user_id]['step'] = 'entering_name'
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(KeyboardButton("⬅️ Orqaga"))
        bot.send_message(user_id, "Ismingizni kiriting:", reply_markup=markup)
        return

    surname = message.text.strip()

    if not is_valid_name(surname):
        error_msg = "❌ Noto'g'ri familiya formati. Iltimos, faqat harflardan foydalaning (2-50 belgi)."
        bot.send_message(user_id, error_msg)
        return

    user_data[user_id]['surname'] = surname
    user_data[user_id]['step'] = 'entering_age'

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("⬅️ Orqaga"))

    bot.send_message(user_id, "Yoshingizni kiriting:", reply_markup=markup)


# Age input handler
@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get('step') == 'entering_age')
def get_age(message):
    user_id = message.chat.id

    if message.text == "⬅️ Orqaga":
        user_data[user_id]['step'] = 'entering_surname'
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(KeyboardButton("⬅️ Orqaga"))
        bot.send_message(user_id, "Familiyangizni kiriting:", reply_markup=markup)
        return

    age_text = message.text.strip()

    if not is_valid_age(age_text):
        error_msg = "❌ Noto'g'ri yosh. Iltimos, 5 dan 100 gacha bo'lgan raqam kiriting."
        bot.send_message(user_id, error_msg)
        return

    user_data[user_id]['age'] = int(age_text)
    user_data[user_id]['step'] = 'entering_address'

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("⬅️ Orqaga"))

    bot.send_message(user_id, "Manzilingizni kiriting (shahar/tuman, ko'cha, uy):", reply_markup=markup)


# Address input handler
@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get('step') == 'entering_address')
def get_address(message):
    user_id = message.chat.id

    if message.text == "⬅️ Orqaga":
        user_data[user_id]['step'] = 'entering_age'
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(KeyboardButton("⬅️ Orqaga"))
        bot.send_message(user_id, "Yoshingizni kiriting:", reply_markup=markup)
        return

    address = message.text.strip()

    if not is_valid_address(address):
        error_msg = "❌ Noto'g'ri manzil formati. Iltimos, manzilingizni to'liq va aniq kiriting."
        bot.send_message(user_id, error_msg)
        return

    user_data[user_id]['address'] = address

    # Save registration
    save_registration(user_id, user_data[user_id])

    # Format the registration message for admin
    data = user_data[user_id]
    msg = f"""📥 Yangi ro'yxatdan o'tish:

📞 Telefon raqam: {data.get('phone', 'Noma\'lum')}
📚 Kurs: {data.get('course', 'Noma\'lum')}
👤 Ism: {data.get('name', 'Noma\'lum')}
👤 Familiya: {data.get('surname', 'Noma\'lum')}
🎂 Yosh: {data.get('age', 'Noma\'lum')}
📍 Manzil: {data.get('address', 'Noma\'lum')}
👤 Foydalanuvchi ID: {user_id}
"""

    # Send to admin
    bot.send_message(ADMIN_ID, msg)

    # Send confirmation to user
    confirmation_text = f"""
✅ Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!

Siz quyidagi ma'lumotlar bilan ro'yxatdan o'tdingiz:
📚 Kurs: {data.get('course', 'Noma\'lum')}
👤 Ism: {data.get('name', 'Noma\'lum')} {data.get('surname', 'Noma\'lum')}

Tez orada administratorlarimiz siz bilan bog'lanadi.
"""

    bot.send_message(user_id, confirmation_text, reply_markup=main_menu_keyboard())
    user_data[user_id]['step'] = 'main_menu'


# Location handler
@bot.message_handler(func=lambda m: m.text == "📍 Manzil")
def send_location(message):
    location_text = """
📍 Bizning manzilimiz:

🏢 "LinuX" o'quv markazi
🌐 Manzil: Farg'ona tumani, Xonqiz qishlog'i, Poliklinika ro'parasi.
📞 Telefon: +998 90 779 73 80
🕒 Ish vaqti: 9:00 - 18:00 (Dushanba - Shanba)

🗺️ Google Maps: https://goo.gl/maps/pQbF6EWQ1CatypUz6

📍 Joylashuvni ko'rish uchun yuqoridagi linkni bosing yoki pastdagi tugma orqali oching.
"""

    # Create inline keyboard with location button
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🗺️ Google Maps da ochish", url="https://goo.gl/maps/9UAyEN4i1SXd4Lh8A"))

    bot.send_message(message.chat.id, location_text, reply_markup=markup)


# Contact info handler
@bot.message_handler(func=lambda m: m.text == "📞 Aloqa")
def contact_info(message):
    contact_text = """
📞 Biz bilan bog'laning:

☎️ Call-markaz: +998 90 779 73 80
📱 Telegram: @OffSec_uz
📧 Email: linuxoquvmarkazi@gmail.com

🕒 Ish vaqti: 9:00 - 18:00 (Dushanba - Shanba)
"""
    bot.send_message(message.chat.id, contact_text)


# Restart handler
@bot.message_handler(func=lambda m: m.text == "🔄 Qayta boshlash")
def restart_bot(message):
    user_id = message.chat.id

    if user_id in user_data:
        del user_data[user_id]

    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)
    markup.add(button)

    welcome_text = """
🔄 Bot qayta ishga tushirildi!
Kurslarimizga ro'yxatdan o'tish uchun avval telefon raqamingizni yuboring.
"""
    bot.send_message(user_id, welcome_text, reply_markup=markup)


# Default message handler
@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    user_id = message.chat.id
    current_step = user_data.get(user_id, {}).get('step', '')

    if current_step in ['entering_name', 'entering_surname', 'entering_age', 'entering_address']:
        if message.text == "⬅️ Orqaga":
            if current_step == 'entering_name':
                show_courses(message)
            elif current_step == 'entering_surname':
                get_name(message)
            elif current_step == 'entering_age':
                get_surname(message)
            elif current_step == 'entering_address':
                get_age(message)
    else:
        bot.send_message(user_id, "Iltimos, quyidagi menyulardan birini tanlang 👇", reply_markup=main_menu_keyboard())


# Admin command to get statistics
@bot.message_handler(commands=['stats'])
def get_stats(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Sizda bu komanda uchun ruxsat yo'q.")
        return

    registrations = load_registrations()
    total = len(registrations)

    # Count registrations by course
    course_counts = {}
    for user_id, data in registrations.items():
        course = data.get('course', 'Noma\'lum')
        course_counts[course] = course_counts.get(course, 0) + 1

    stats_text = f"📊 Bot statistikasi:\n\n👥 Jami ro'yxatdan o'tganlar: {total}\n\n"

    for course, count in course_counts.items():
        stats_text += f"{course}: {count} ta\n"

    bot.send_message(ADMIN_ID, stats_text)


if __name__ == "__main__":
    print("Bot ishga tushyapti...")
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Botda xatolik yuz berdi: {e}")