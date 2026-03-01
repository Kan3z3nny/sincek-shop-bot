import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# --- ၁။ RENDER PORT BINDING ---
app = Flask('')
@app.route('/')
def home(): return "Bot is alive!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- ၂။ CONFIGURATION ---
TOKEN = '8509360517:AAEGBq3B3kxqQNYJZN4KNjIII9G-ztPvSlo'
ADMIN_ID = 8046242647 
ADMIN_USERNAME = "@since_K" 
KPAY_PHONE = "09982015936"   
KPAY_NAME = "Thandar Soe"    
WAVE_PHONE = "09740027247"   
WAVE_NAME = "Soe Yan Naing"  

bot = telebot.TeleBot(TOKEN)

# --- ၃။ STORAGE SYSTEM ---
USER_FILE = "users.txt"
ORDER_FILE = "orders_history.txt"
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
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except: return []

# --- ၄။ ADMIN COMMANDS (/cast & /sent) ---

# အားလုံးကို စာပို့ရန် (Broadcast)
@bot.message_handler(commands=['cast'])
def broadcast_prompt(message):
    if message.chat.id == ADMIN_ID:
        sent = bot.send_message(ADMIN_ID, "📢 အားလုံးကိုပို့မည့် **စာ** သို့မဟုတ် **ပုံ** ကို ပို့ပေးပါ။")
        bot.register_next_step_handler(sent, do_broadcast)
    else:
        bot.send_message(message.chat.id, "⚠️ သင်သည် Admin မဟုတ်ပါ။")

def do_broadcast(message):
    users = get_all_users()
    count = 0
    bot.send_message(ADMIN_ID, f"⏳ လူပေါင်း {len(users)} ဦးထံ ပို့နေသည်...")
    for u in users:
        try:
            if message.content_type == 'photo':
                bot.send_photo(u, message.photo[-1].file_id, caption=message.caption)
            else:
                bot.send_message(u, message.text)
            count += 1
        except: pass
    bot.send_message(ADMIN_ID, f"✅ User {count} ဦးထံ ပို့ပြီးပါပြီ။")

# User တစ်ယောက်တည်းကို စာပြန်ရန် (ဥပမာ- /sent 123456 Hello)
@bot.message_handler(commands=['sent'])
def send_to_user(message):
    if message.chat.id == ADMIN_ID:
        try:
            parts = message.text.split(" ", 2)
            target_id = parts[1]
            text = parts[2]
            bot.send_message(target_id, f"✉️ **Admin မှ စာပြန်လာသည်:**\n\n{text}", parse_mode="HTML")
            bot.send_message(ADMIN_ID, "✅ စာပို့ပြီးပါပြီ။")
        except:
            bot.send_message(ADMIN_ID, "❌ ပုံစံမှားနေသည်။ `/sent ID စာသား` ဟု ရေးပါ။")

# --- ၅။ MENUS & SHOPPING ---

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🛍 ဈေးဝယ်ရန်", "🎁 ပိုမိုရှင်း")
    markup.add("👤 မိမိအကောင့်", "📜 order မှတ်တမ်း")
    markup.add("📞 Admin ဆက်သွယ်ရန်", "🤝 သင့်ငယ်ချင်းဖိတ်ရန်")
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    save_user(message.chat.id)
    bot.send_message(message.chat.id, f"👋 SinceKShop မှ ကြိုဆိုပါတယ် {message.from_user.first_name} ဗျာ။", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🛍 ဈေးဝယ်ရန်")
def shop_start(message):
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("🎮 Mobile Legend", callback_data="game_mlbb"))
    bot.send_message(message.chat.id, "🎮 Game ရွေးချယ်ပါ:", reply_markup=mk)

# ... (စျေးနှုန်းများ - အတိုချုံ့ထားသည်) ...
MLBB_PRICES = {"Wkp 1": "6200", "Dia 257": "15000", "Dia 878": "50000"} # စျေးနှုန်းအစုံ ပြန်ထည့်ပေးပါ

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
    bot.edit_message_text(f"✅ Selected: {item}\n📝 MLBB ID ပေးပို့ပါ။", call.message.chat.id, call.message.message_id)
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
    if method == "kpay":
        pay_dt = f"💰 **KBZ Pay**\nNo: `09982015936`\nName: **Thandar Soe**"
    else:
        pay_dt = f"💰 **Wave Pay**\nNo: `09740027247`\nName: **Soe Yan Naing**"
    
    msg = (f"📝 **Order Summary**\nProduct: {order['item']}\nID: {order['game_id']}\n\n{pay_dt}\n\n⚠️ Screenshot ပို့ပေးပါ။")
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode="HTML")

@bot.message_handler(content_types=['photo'])
def handle_ss(message):
    uid = message.chat.id
    if uid in user_orders:
        order = user_orders[uid]
        bot.reply_to(message, "✅ Screenshot ရရှိပါသည်။ Admin စစ်ဆေးနေပါပြီ။")
        admin_text = (f"🛒 **NEW ORDER**\n👤 Name: {message.from_user.first_name}\n🆔 UserID: `{uid}`\n📦 Item: {order['item']}\n🆔 Game ID: `{order['game_id']}`")
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("✅ Approve", callback_data=f"adm_app_{uid}"),
               types.InlineKeyboardButton("❌ Reject", callback_data=f"adm_rej_{uid}"))
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=admin_text, parse_mode="HTML", reply_markup=mk)

@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def admin_action(call):
    data = call.data.split("_")
    action, target_uid = data[1], int(data[2])
    if action == "rej":
        bot.send_message(target_uid, "❌ **သင့် Order ကို ပယ်ချလိုက်ပါသည်။**", parse_mode="HTML")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    # ... (တခြား Approve/Done logic များ) ...

if __name__ == "__main__":
    keep_alive()
    bot.remove_webhook()
    bot.infinity_polling(none_stop=True, skip_pending=True)
