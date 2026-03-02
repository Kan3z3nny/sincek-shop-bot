import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# --- 1. SERVER SETUP ---
app = Flask('')
@app.route('/')
def home(): return "SinceKShop is Live!"

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

# --- 3. PRICE LIST ---
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

# --- 4. MAIN INTERFACE ---
@bot.message_handler(commands=['start'])
def welcome(message):
    save_user(message.chat.id)
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mk.add("🛍 ဈေးဝယ်ရန်", "🎁 ပရိုမိုးရှင်း")
    mk.add("👤 မိမိအကောင့်", "📜 order မှတ်တမ်း")
    mk.add("📞 Admin ဆက်သွယ်ရန်", "🤝 သင့်ငယ်ချင်းဖိတ်ရန်")
    bot.send_message(message.chat.id, "👋 <b>SinceKShop</b> မှ ကြိုဆိုပါတယ်!", reply_markup=mk, parse_mode="HTML")

@bot.message_handler(func=lambda m: True)
def handle_menu(message):
    uid = message.chat.id
    if message.text == "🛍 ဈေးဝယ်ရန်":
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🎮 Mobile Legend", callback_data="game_mlbb"))
        bot.send_message(uid, "🎮 Game ရွေးချယ်ပါ:", reply_markup=mk)
    elif message.text == "🎁 ပရိုမိုးရှင်း":
        bot.send_message(uid, "ပရိုမိုးရှင်း မရှိသေးပါ 🙏")
    elif message.text == "👤 မိမိအကောင့်":
        bot.send_message(uid, f"👤 <b>Account</b>\nName: {message.from_user.first_name}\nID: <code>{uid}</code>", parse_mode="HTML")
    elif message.text == "📜 order မှတ်တမ်း":
        bot.send_message(uid, "📜 Order မှတ်တမ်းမရှိသေးပါ။")
    elif message.text == "📞 Admin ဆက်သွယ်ရန်":
        bot.send_message(uid, f"👨‍💻 Admin: {ADMIN_USERNAME}")
    elif message.text == "🤝 သင့်ငယ်ချင်းဖိတ်ရန်":
        bot.send_message(uid, "🤝 https://t.me/SinceKshop_Bot")

# --- 5. SHOPPING & PAYMENT FLOW ---
@bot.callback_query_handler(func=lambda call: call.data == "game_mlbb")
def mlbb_list(call):
    mk = types.InlineKeyboardMarkup(row_width=2)
    btns = [types.InlineKeyboardButton(f"{k} ({v} Ks)", callback_data=f"buy_{k}") for k, v in MLBB_PRICES.items()]
    mk.add(*btns)
    bot.edit_message_text("💎 ဝယ်ယူလိုသည့် ပမာဏကို ရွေးချယ်ပါ -", call.message.chat.id, call.message.message_id, reply_markup=mk)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def ask_id(call):
    item = call.data.replace("buy_", "")
    user_orders[call.message.chat.id] = {'item': item, 'price': MLBB_PRICES[item]}
    bot.edit_message_text(f"✅ Selected: <b>{item}</b>\n\n📝 MLBB ID နှင့် Server ID ပေးပို့ပါ။", call.message.chat.id, call.message.message_id, parse_mode="HTML")
    bot.register_next_step_handler(call.message, ask_pay_method)

def ask_pay_method(message):
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
    if not order: return
    
    pay_no = "09982015936" if method == "kpay" else "09740027247"
    pay_name = "Thandar Soe" if method == "kpay" else "Soe Yan Naing"
    
    msg = (f"📋 <b>Order Summary</b>\nProduct: {order['item']}\nID: <code>{order['game_id']}</code>\n\n"
           f"💰 <b>{method.upper()}</b>\nNo: <code>{pay_no}</code>\nName: <b>{pay_name}</b>\n\n"
           f"⚠️ ငွေလွှဲပြီး SS ပို့ပေးပါ။")
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode="HTML")

@bot.message_handler(content_types=['photo'])
def handle_ss(message):
    uid = message.chat.id
    if uid in user_orders:
        order = user_orders[uid]
        bot.reply_to(message, "✅ SS ရရှိပါသည်။ Admin စစ်ဆေးနေပါပြီ။")
        admin_text = f"🛒 <b>NEW ORDER</b>\n👤 Name: {message.from_user.first_name}\n🆔 UserID: <code>{uid}</code>\n📦 Item: {order['item']}\n🎮 GameID: <code>{order['game_id']}</code>"
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("✅ Approve", callback_data=f"adm_app_{uid}"),
               types.InlineKeyboardButton("❌ Reject", callback_data=f"adm_rej_{uid}"))
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=admin_text, parse_mode="HTML", reply_markup=mk)

# --- 6. ADMIN ACTIONS ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def admin_action(call):
    _, act, target_uid = call.data.split("_")
    target_uid = int(target_uid)
    try:
        if act == "app":
            bot.send_message(target_uid, "⌛ <b>Admin မှ စတင်စစ်ဆေးနေပါပြီ။</b>", parse_mode="HTML")
        else:
            bot.send_message(target_uid, "❌ <b>သင့် Order အချက်အလက် မပြည့်စုံသဖြင့် ပယ်ချလိုက်ပါသည်။ ကျေးဇူးပြု၍ Admin ကို ပြန်လည်ဆက်သွယ်ပေးပါ။</b>", parse_mode="HTML")
        
        bot.edit_message_reply_markup(ADMIN_ID, call.message.message_id, reply_markup=None)
        bot.answer_callback_query(call.id, "Done!")
    except: pass

# --- 7. BROADCAST ---
@bot.message_handler(commands=['cast'])
def broadcast(message):
    if message.chat.id == ADMIN_ID:
        sent = bot.send_message(ADMIN_ID, "📢 ပို့မည့် စာ သို့မဟုတ် ပုံ ပို့ပေးပါ။")
        bot.register_next_step_handler(sent, start_cast)

def start_cast(message):
    users = get_all_users()
    for u in users:
        try:
            if message.content_type == 'photo': bot.send_photo(u, message.photo[-1].file_id, caption=message.caption)
            else: bot.send_message(u, message.text)
        except: pass
    bot.send_message(ADMIN_ID, "✅ ပို့ပြီးပါပြီ။")

if __name__ == "__main__":
    keep_alive()
    bot.remove_webhook()
    bot.infinity_polling(none_stop=True, skip_pending=True)
