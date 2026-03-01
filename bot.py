import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# --- 1. SERVER SETUP ---
app = Flask('')
@app.route('/')
def home(): return "SinceKShop Bot is Running!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. CONFIGURATION ---
TOKEN = '8509360517:AAEGBq3B3kxqQNYJZN4KNjIII9G-ztPvSlo'
ADMIN_ID = 8046242647 
ADMIN_USERNAME = "@since_K"
bot = telebot.TeleBot(TOKEN)

# --- 3. UPDATED PRICE LIST (ဈေးနှုန်းအသစ်များ) ---
MLBB_PRICES = {
    "Wkp 1": "6200", "Wkp 2": "12400", "Wkp 3": "18600", "Wkp 4": "24800", "Wkp 5": "31000",
    "Twlp": "33000", "Dia 50+50": "3800", "Dia 150+150": "11000", "Dia 250+250": "17000",
    "Dia 500+500": "35000", "Dia 86": "5000", "Dia 172": "10000", "Dia 257": "15000",
    "Dia 343": "20000", "Dia 429": "25000", "Dia 514": "30000", "Dia 600": "35000",
    "Dia 706": "40000", "Dia 878": "50000", "Dia 963": "55000", "Dia 1049": "60000",
    "Dia 1135": "65000", "Dia 1412": "80000", "Dia 2195": "120000", "Dia 3688": "200000",
    "Dia 5532": "300000", "Dia 9288": "500000"
}

USER_FILE = "users.txt"
user_orders = {}

def save_user(uid):
    uid = str(uid)
    try:
        if not os.path.exists(USER_FILE):
            with open(USER_FILE, "w") as f: f.write("")
        with open(USER_FILE, "r") as f:
            uids = [line.strip() for line in f.readlines()]
        if uid not in uids:
            with open(USER_FILE, "a") as f: f.write(uid + "\n")
    except: pass

def get_all_users():
    if not os.path.exists(USER_FILE): return []
    try:
        with open(USER_FILE, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except: return []

# --- 4. MAIN MENU ---
@bot.message_handler(commands=['start'])
def welcome(message):
    save_user(message.chat.id)
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mk.add("🛍 ဈေးဝယ်ရန်", "🎁 ပရိုမိုးရှင်း")
    mk.add("👤 မိမိအကောင့်", "📜 order မှတ်တမ်း")
    mk.add("📞 Admin ဆက်သွယ်ရန်", "🤝 သင့်ငယ်ချင်းဖိတ်ရန်")
    bot.send_message(message.chat.id, "👋 **SinceKShop** မှ ကြိုဆိုပါတယ်ခင်ဗျာ။", reply_markup=mk, parse_mode="HTML")

@bot.message_handler(func=lambda m: True)
def handle_menu(message):
    uid = message.chat.id
    if message.text == "🛍 ဈေးဝယ်ရန်":
        mk = types.InlineKeyboardMarkup(row_width=2)
        btns = [types.InlineKeyboardButton(f"{k} ({v} Ks)", callback_data=f"buy_{k}") for k, v in MLBB_PRICES.items()]
        mk.add(*btns)
        bot.send_message(uid, "💎 ဝယ်ယူလိုသည့် ပမာဏကို ရွေးချယ်ပါ -", reply_markup=mk)

    elif message.text == "🎁 ပရိုမိုးရှင်း":
        bot.send_message(uid, "ပရိုမိုးရှင်း မရှိသေးပါ 🙏")

    elif message.text == "👤 မိမိအကောင့်":
        bot.send_message(uid, f"👤 **မိမိအကောင့်အချက်အလက်**\n\nအမည်: {message.from_user.first_name}\nID: `{uid}`", parse_mode="HTML")

    elif message.text == "📜 order မှတ်တမ်း":
        bot.send_message(uid, "📅 သင်၏ Order မှတ်တမ်းမှာ လောလောဆယ် အားနေပါသည်။")

    elif message.text == "📞 Admin ဆက်သွယ်ရန်":
        bot.send_message(uid, f"👨‍💻 Admin ကို တိုက်ရိုက်ဆက်သွယ်ရန် - {ADMIN_USERNAME}")

    elif message.text == "🤝 သင့်ငယ်ချင်းဖိတ်ရန်":
        link = f"https://t.me/SinceKshop_Bot?start={uid}"
        bot.send_message(uid, f"🔗 သင့်သူငယ်ချင်းများကို ဖိတ်ခေါ်ရန် လင့်ခ်:\n`{link}`", parse_mode="HTML")

# --- 5. ADMIN TOOLS (/cast) ---
@bot.message_handler(commands=['cast'])
def broadcast(message):
    if message.chat.id == ADMIN_ID:
        sent = bot.send_message(ADMIN_ID, "📢 အားလုံးကိုပို့မည့် စာ (သို့မဟုတ်) ပုံ ကို ပို့ပေးပါ။")
        bot.register_next_step_handler(sent, start_broadcasting)

def start_broadcasting(message):
    users = get_all_users()
    count = 0
    for u in users:
        try:
            if message.content_type == 'photo':
                bot.send_photo(u, message.photo[-1].file_id, caption=message.caption)
            else:
                bot.send_message(u, message.text)
            count += 1
        except: pass
    bot.send_message(ADMIN_ID, f"✅ User {count} ယောက်ကို ပို့ပြီးပါပြီ။")

# --- 6. ORDER LOGIC ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def ask_id(call):
    item = call.data.replace("buy_", "")
    user_orders[call.message.chat.id] = {'item': item, 'price': MLBB_PRICES[item]}
    bot.edit_message_text(f"✅ Selected: **{item}**\n\n📝 MLBB ID နှင့် Server ID ပေးပို့ပါ။", call.message.chat.id, call.message.message_id, parse_mode="HTML")
    bot.register_next_step_handler(call.message, ask_payment)

def ask_payment(message):
    uid = message.chat.id
    if uid in user_orders:
        user_orders[uid]['game_id'] = message.text
        order = user_orders[uid]
        pay_msg = (
            f"📝 **Order Summary**\nProduct: {order['item']}\nID: {order['game_id']}\n\n"
            f"💰 **KBZ Pay**\nNo: `09982015936`\nName: **Thandar Soe**\n\n"
            f"💰 **Wave Pay**\nNo: `09740027247`\nName: **Soe Yan Naing**\n\n"
            f"⚠️ ငွေလွှဲပြီး Screenshot ပို့ပေးပါ။"
        )
        bot.send_message(uid, pay_msg, parse_mode="HTML")

@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    uid = message.chat.id
    if uid in user_orders:
        order = user_orders[uid]
        bot.reply_to(message, "✅ Screenshot ရရှိပါသည်။ Admin စစ်ဆေးနေပါပြီ။")
        admin_text = f"🛒 **NEW ORDER**\n👤 User: {message.from_user.first_name}\n🆔 ID: `{uid}`\n📦 Item: {order['item']}\n🆔 Game ID: `{order['game_id']}`"
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=admin_text, parse_mode="HTML")

if __name__ == "__main__":
    keep_alive()
    bot.remove_webhook()
    bot.infinity_polling(none_stop=True, skip_pending=True)
