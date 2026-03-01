import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# --- ၁။ RENDER PORT BINDING SYSTEM (PORT ERROR မတက်အောင် ထည့်ခြင်း) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running on Render!"

def run():
    # Render ရဲ့ Port ကို ဖမ်းယူခြင်း၊ မရှိပါက 8080 ကို သုံးခြင်း
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
        with open(USER_FILE, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except: return []

def save_order_history(uid, item, price):
    try:
        with open(ORDER_FILE, "a", encoding="utf-8") as f:
            f.write(f"{uid}|{item}|{price}\n")
    except: pass

def get_order_history(uid):
    if not os.path.exists(ORDER_FILE): return "❌ မှတ်တမ်းမရှိသေးပါ။"
    history = ""
    try:
        with open(ORDER_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("|")
                if parts[0] == str(uid):
                    history += f"📦 {parts[1]} - {parts[2]} Ks\n"
    except: return "❌ မှတ်တမ်းဖတ်မရပါ။"
    return history if history else "❌ မှတ်တမ်းမရှိသေးပါ။"

# --- ၄။ MENUS & BROADCAST ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🛍 ဈေးဝယ်ရန်", "🎁 ပိုမိုရှင်း")
    markup.add("👤 မိမိအကောင့်", "📜 order မှတ်တမ်း")
    markup.add("📞 Admin ဆက်သွယ်ရန်", "🤝 သင့်ငယ်ချင်းဖိတ်ရန်")
    return markup

@bot.message_handler(commands=['cast'])
def broadcast_prompt(message):
    if message.chat.id == ADMIN_ID:
        sent = bot.send_message(ADMIN_ID, "📢 အားလုံးကိုပို့မည့် **စာ** သို့မဟုတ် **ပုံ** ကို ပို့ပေးပါ။")
        bot.register_next_step_handler(sent, do_broadcast)

def do_broadcast(message):
    users = get_all_users()
    if not users:
        bot.send_message(ADMIN_ID, "❌ ပို့ရန် User မရှိသေးပါ။")
        return
    count = 0
    bot.send_message(ADMIN_ID, f"⏳ လူပေါင်း {len(users)} ဦးထံ ပို့ဆောင်နေပါပြီ...")
    for u in users:
        try:
            if message.content_type == 'photo':
                bot.send_photo(u, message.photo[-1].file_id, caption=message.caption)
            elif message.content_type == 'text':
                bot.send_message(u, message.text)
            count += 1
        except: pass
    bot.send_message(ADMIN_ID, f"✅ စုစုပေါင်း User {count} ဦးထံ အောင်မြင်စွာ ပို့ပြီးပါပြီ။")

# --- ၅။ SHOPPING LOGIC (စျေးနှုန်းများအားလုံး ပါဝင်သည်) ---
MLBB_PRICES = {
    "Wkp 1": "6200", "Wkp 2": "12400", "Wkp 3": "18600", "Wkp 4": "24800", "Wkp 5": "31000",
    "Twlp": "33000", "Dia 50+50": "3800", "Dia 150+150": "11000", "Dia 250+250": "17000",
    "Dia 500+500": "35000", "Dia 86": "5000", "Dia 172": "10000", "Dia 257": "15000",
    "Dia 343": "20000", "Dia 429": "25000", "Dia 514": "30000", "Dia 600": "35000",
    "Dia 706": "40000", "Dia 878": "50000", "Dia 963": "55000", "Dia 1049": "60000",
    "Dia 1135": "65000", "Dia 1412": "80000", "Dia 2195": "120000", "Dia 3688": "200000",
    "Dia 5532": "300000", "Dia 9288": "500000"
}

@bot.message_handler(commands=['start'])
def welcome(message):
    save_user(message.chat.id)
    bot.send_message(message.chat.id, f"👋 SinceKShop မှ ကြိုဆိုပါတယ် {message.from_user.first_name} ဗျာ။", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def handle_menu(message):
    uid = message.chat.id
    if message.text == "🛍 ဈေးဝယ်ရန်":
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🎮 Mobile Legend", callback_data="game_mlbb"))
        bot.send_message(uid, "🎮 Game ရွေးချယ်ပါ:", reply_markup=mk)
    elif message.text == "🎁 ပိုမိုရှင်း":
        bot.send_message(uid, "🎁 <b>SinceK Shop Promotion</b>\n\nPromotion များအတွက် Channel ကို စောင့်ကြည့်ပေးပါ။", parse_mode="HTML")
    elif message.text == "📜 order မှတ်တမ်း":
        history = get_order_history(uid)
        bot.send_message(uid, f"📜 <b>သင်၏ ဝယ်ယူမှုမှတ်တမ်း</b>\n\n{history}", parse_mode="HTML")
    elif message.text == "🤝 သင့်ငယ်ချင်းဖိတ်ရန်":
        bot_info = bot.get_me()
        bot_link = f"https://t.me/{bot_info.username}"
        share_msg = f"🎮 Mobile Legends Diamond တွေကို SinceK Shop မှာ ဝယ်ယူနိုင်ပါပြီ!\n\nLink: {bot_link}"
        bot.send_message(uid, f"🤝 <b>သင့်သူငယ်ချင်းများကို ဖိတ်ခေါ်ပါ</b>\n\nအောက်ပါစာသားကို ကူးယူပြီး Share ပါ။\n\n<code>{share_msg}</code>", parse_mode="HTML")
    elif message.text == "👤 မိမိအကောင့်":
        bot.send_message(uid, f"👤 <b>Account Info</b>\nName: {message.from_user.first_name}\nID: <code>{uid}</code>", parse_mode="HTML")
    elif message.text == "📞 Admin ဆက်သွယ်ရန်":
        bot.send_message(uid, f"📞 Admin Contact: {ADMIN_USERNAME}")

@bot.callback_query_handler(func=lambda call: call.data == "game_mlbb")
def mlbb_list(call):
    mk = types.InlineKeyboardMarkup(row_width=2)
    btns = [types.InlineKeyboardButton(f"{k} ({v} Ks)", callback_data=f"buy_{k}") for k, v in MLBB_PRICES.items()]
    mk.add(*btns)
    bot.edit_message_text("💎 ဝယ်ယူလိုသည့် ပမာဏကို ရွေးချယ်ပါ -", call.message.chat.id, call.message.message_id, reply_markup=mk)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def ask_id(call):
    item = call.data.replace("buy_", "")
    price = MLBB_PRICES.get(item)
    user_orders[call.message.chat.id] = {'item': item, 'price': price}
    bot.edit_message_text(f"✅ Selected: {item} ({price} Ks)\n\n📝 MLBB Player ID နှင့် Server ID ပေးပို့ပါ။", 
                          call.message.chat.id, call.message.message_id)
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
    if not order: return
    pay_dt = f"<b>KBZ Pay</b>\nNo: <code>{KPAY_PHONE}</code>" if method == "kpay" else f"<b>Wave Pay</b>\nNo: <code>{WAVE_PHONE}</code>"
    msg = (f"📝 <b>Order Summary</b>\nProduct: {order['item']}\nPrice: {order['price']} Ks\nID: {order['game_id']}\n\n"
           f"💰 {pay_dt}\n\n⚠️ Screenshot ပို့ပေးပါ။")
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode="HTML")

@bot.message_handler(content_types=['photo'])
def handle_ss(message):
    uid = message.chat.id
    if uid in user_orders:
        order = user_orders[uid]
        bot.reply_to(message, "✅ Screenshot ရရှိပါသည်။ Admin စစ်ဆေးနေပါပြီ။")
        admin_text = (f"🛒 <b>NEW ORDER</b>\n👤 Name: {message.from_user.first_name}\n🆔 UserID: <code>{uid}</code>\n📦 Item: {order['item']}\n💰 Price: {order['price']} Ks\n🆔 Game ID: <code>{order['game_id']}</code>")
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("✅ Approve", callback_data=f"adm_app_{uid}"),
               types.InlineKeyboardButton("❌ Reject", callback_data=f"adm_rej_{uid}"))
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=admin_text, parse_mode="HTML", reply_markup=mk)

@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def admin_action(call):
    data = call.data.split("_")
    action, target_uid = data[1], int(data[2])
    if action == "app":
        bot.send_message(target_uid, "⌛ <b>Admin မှ စတင်စစ်ဆေးနေပါပြီ။</b>", parse_mode="HTML")
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("📦 ပစ္စည်းထည့်ပြီးကြောင်း ပို့ရန်", callback_data=f"adm_done_{target_uid}"))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=mk)
    elif action == "rej":
        bot.send_message(target_uid, "❌ <b>သင့် Order ကို ပယ်ချလိုက်ပါသည်။</b>")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    elif action == "done":
        order = user_orders.get(target_uid)
        if order:
            save_order_history(target_uid, order['item'], order['price'])
        bot.send_message(target_uid, "✅ ဝယ်ယူမှု အောင်မြင်ပါသည် ခင်ဗျာ။🙏")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        if target_uid in user_orders: del user_orders[target_uid]

# --- ၆။ STARTUP (Flask နဲ့ Bot polling ကို တွဲနှိုးခြင်း) ---
if __name__ == "__main__":
    keep_alive() # Render အတွက် Port အရင်ဖွင့်ပေးမှာပါ
    print("Bot is starting...")
    bot.infinity_polling(none_stop=True)
