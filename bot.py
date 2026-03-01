import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# --- 1. RENDER PORT BINDING ---
app = Flask('')
@app.route('/')
def home(): return "Bot is alive!"

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
KPAY_PHONE = "09982015936"; KPAY_NAME = "Thandar Soe"
WAVE_PHONE = "09740027247"; WAVE_NAME = "Soe Yan Naing"

bot = telebot.TeleBot(TOKEN)

# --- 3. PRICE LIST (Dia ဈေးနှုန်းအားလုံး) ---
MLBB_PRICES = {
    "Wkp 1": "6200", "Twlp": "33000", "Dia 257": "15000", "Dia 878": "50000",
    "Dia 28": "1500", "Dia 56": "3000", "Dia 112": "6000", "Dia 172": "9000",
    "Dia 429": "23000", "Dia 514": "28000", "Dia 706": "38000"
}
user_orders = {}
USER_FILE = "users.txt"

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
    with open(USER_FILE, "r") as f: return [line.strip() for line in f.readlines()]

# --- 4. ADMIN COMMANDS (/cast & /sent) ---

@bot.message_handler(commands=['cast'])
def broadcast_prompt(message):
    if message.chat.id == ADMIN_ID:
        sent = bot.send_message(ADMIN_ID, "📢 အားလုံးကိုပို့မည့် **စာ** (သို့) **ပုံ** ကို ပို့ပေးပါ။")
        bot.register_next_step_handler(sent, do_broadcast)

def do_broadcast(message):
    users = get_all_users()
    for u in users:
        try:
            if message.content_type == 'photo':
                bot.send_photo(u, message.photo[-1].file_id, caption=message.caption)
            else: bot.send_message(u, message.text)
        except: pass
    bot.send_message(ADMIN_ID, "✅ အားလုံးကို ပို့ပြီးပါပြီ။")

@bot.message_handler(commands=['sent'])
def send_to_user(message):
    if message.chat.id == ADMIN_ID:
        try:
            parts = message.text.split(" ", 2)
            bot.send_message(parts[1], f"✉️ **Admin မှ စာပြန်လာသည်:**\n\n{parts[2]}", parse_mode="HTML")
            bot.send_message(ADMIN_ID, "✅ ပို့ပြီးပါပြီ။")
        except: bot.send_message(ADMIN_ID, "သုံးနည်း- `/sent ID စာသား`")

# --- 5. MAIN MENU HANDLERS ---

@bot.message_handler(commands=['start'])
def welcome(message):
    save_user(message.chat.id)
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mk.add("🛍 ဈေးဝယ်ရန်", "🎁 ပရိုမိုးရှင်း")
    mk.add("👤 မိမိအကောင့်", "📜 order မှတ်တမ်း")
    mk.add("📞 Admin ဆက်သွယ်ရန်", "🤝 သင့်ငယ်ချင်းဖိတ်ရန်")
    bot.send_message(message.chat.id, f"👋 SinceKShop မှ ကြိုဆိုပါတယ် {message.from_user.first_name}။", reply_markup=mk)

@bot.message_handler(func=lambda m: True)
def handle_menu(message):
    uid = message.chat.id
    if message.text == "🛍 ဈေးဝယ်ရန်":
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🎮 Mobile Legend", callback_data="game_mlbb"))
        bot.send_message(uid, "🎮 Game ရွေးချယ်ပါ:", reply_markup=mk)
    
    elif message.text == "🎁 ပရိုမိုးရှင်း":
        bot.send_message(uid, "🎉 **ယခုလအတွက် ပရိုမိုးရှင်း**\n\n- Weekly Pass ၁၀ ခုဝယ်လျှင် ၁ ခု လက်ဆောင်!\n- Dia အများဆုံးဝယ်ယူသူအတွက် Skin လက်ဆောင်ရှိပါသည်။", parse_mode="HTML")

    elif message.text == "👤 မိမိအကောင့်":
        info = f"👤 **Account Info**\n\nName: {message.from_user.first_name}\nID: `{uid}`"
        bot.send_message(uid, info, parse_mode="HTML")

    elif message.text == "📜 order မှတ်တမ်း":
        bot.send_message(uid, "📅 သင်၏ Order မှတ်တမ်းမှာ လောလောဆယ် အားနေပါသည်။")

    elif message.text == "📞 Admin ဆက်သွယ်ရန်":
        bot.send_message(uid, f"👨‍💻 Admin ကို ဆက်သွယ်ရန် - {ADMIN_USERNAME}")

    elif message.text == "🤝 သင့်ငယ်ချင်းဖိတ်ရန်":
        bot.send_message(uid, f"🔗 သင့်သူငယ်ချင်းများကို ဖိတ်ခေါ်ရန် Link:\nhttps://t.me/SinceKshop_Bot?start={uid}")

# --- 6. SHOPPING LOGIC ---
@bot.callback_query_handler(func=lambda call: call.data == "game_mlbb")
def mlbb_list(call):
    mk = types.InlineKeyboardMarkup(row_width=2)
    btns = [types.InlineKeyboardButton(f"{k} ({v} Ks)", callback_data=f"buy_{k}") for k, v in MLBB_PRICES.items()]
    mk.add(*btns)
    bot.edit_message_text("💎 ဝယ်ယူလိုသည့် ပမာဏကို ရွေးချယ်ပါ -", call.message.chat.id, call.message.message_id, reply_markup=mk)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def ask_id(call):
    item = call.data.replace("buy_", "")
    user_orders[call.message.chat.id] = {'item': item, 'price': MLBB_PRICES.get(item)}
    bot.edit_message_text(f"✅ Selected: {item}\n📝 MLBB ID နှင့် Server ID ပေးပို့ပါ။", call.message.chat.id, call.message.message_id)
    bot.register_next_step_handler(call.message, ask_payment)

def ask_payment(message):
    uid = message.chat.id
    if uid in user_orders:
        user_orders[uid]['game_id'] = message.text
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("KBZ Pay", callback_data="pay_kpay"),
               types.InlineKeyboardButton("Wave Pay", callback_data="pay_wave"))
        bot.send_message(uid, "💳 ငွေပေးချေမည့် နည်းလမ်းကို ရွေးချယ်ပါ -", reply_markup=mk)

@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_"))
def show_pay_info(call):
    method = call.data.split("_")[1]
    order = user_orders.get(call.message.chat.id)
    pay_dt = f"💰 **KBZ Pay**\nNo: `{KPAY_PHONE}`\nName: **{KPAY_NAME}**" if method == "kpay" else f"💰 **Wave Pay**\nNo: `{WAVE_PHONE}`\nName: **{WAVE_NAME}**"
    msg = f"📝 **Order Summary**\nProduct: {order['item']}\nID: {order['game_id']}\n\n{pay_dt}\n\n⚠️ Screenshot ပို့ပေးပါ။"
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode="HTML")

@bot.message_handler(content_types=['photo'])
def handle_ss(message):
    uid = message.chat.id
    if uid in user_orders:
        order = user_orders[uid]
        bot.reply_to(message, "✅ Screenshot ရရှိပါသည်။ Admin စစ်ဆေးနေပါပြီ။")
        admin_text = f"🛒 **NEW ORDER**\n👤 Name: {message.from_user.first_name}\n🆔 UserID: `{uid}`\n📦 Item: {order['item']}\n🆔 Game ID: `{order['game_id']}`"
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("✅ Approve", callback_data=f"adm_app_{uid}"),
               types.InlineKeyboardButton("❌ Reject", callback_data=f"adm_rej_{uid}"))
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=admin_text, parse_mode="HTML", reply_markup=mk)

if __name__ == "__main__":
    keep_alive()
    bot.remove_webhook()
    bot.infinity_polling(none_stop=True, skip_pending=True)
