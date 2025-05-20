import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)
from keep_alive import keep_alive
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")
CHANNELS = ['@marcoshots', '@marcoshotpot', '@earnyvlackyo', '@giftcodedaily100', '@jiyajishots', '@aarohiloots']
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    with open('front.png', 'rb') as photo:
        await context.bot.send_photo(chat_id=chat_id, photo=photo,
                                     caption="👋 Welcome! Join all channels below to get ₹100 Paytm cash.")
    with open('voice.ogg', 'rb') as voice:
        await context.bot.send_voice(chat_id=chat_id, voice=voice)
    buttons = [
        [InlineKeyboardButton("Join ↗️", url="https://t.me/marcoshots"),
         InlineKeyboardButton("Join ↗️", url="https://t.me/marcoshotpot"),
         InlineKeyboardButton("Join ↗️", url="https://t.me/earnyvlackyo")],
        [InlineKeyboardButton("Join ↗️", url="https://t.me/giftcodedaily100"),
         InlineKeyboardButton("Join ↗️", url="https://t.me/jiyajishots"),
         InlineKeyboardButton("Join ↗️", url="https://t.me/aarohiloots")],
        [InlineKeyboardButton("✅ VERIFY ✅", callback_data="verify")]
    ]
    await context.bot.send_message(chat_id=chat_id, text="Please join all the above channels and then click 'I've Joined All'.",
                                   reply_markup=InlineKeyboardMarkup(buttons))

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id
    not_joined = []
    for channel in CHANNELS:
        try:
            member = await context.bot.get_chat_member(channel, user.id)
            if member.status not in ["member", "administrator", "creator"]:
                not_joined.append(channel)
        except:
            not_joined.append(channel)
    if not_joined:
        await query.answer("Please join all channels before verifying.", show_alert=True)
        return
    await query.answer("✅ Verified successfully!", show_alert=False)
    await context.bot.send_message(chat_id=chat_id, text="✅ Verification successful!")
    with open("wheel.jpg", "rb") as photo:
        await context.bot.send_photo(chat_id=chat_id, photo=photo,
            caption="🎯 Spin the wheel to win up to ₹100 Paytm cash!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎰 Spin Now", callback_data="spin")]]))

async def spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id
    await query.answer("Spinning the wheel...")
    won_amount = random.choice([33, 55])
    user_data[user.id] = {'balance': won_amount, 'referrals': 0, 'upi': None}
    await context.bot.send_message(chat_id=chat_id,
        text=f"🎉 You won ₹{won_amount}. Minimum withdrawal is ₹100. Refer friends to earn more.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")],
            [InlineKeyboardButton("📢 Refer Friends", callback_data="refer")]
        ]))

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id
    info = user_data.get(user.id, {'balance': 0})
    if info['balance'] >= 100:
        await context.bot.send_message(chat_id=chat_id, text="Enter your UPI ID:")
    else:
        await context.bot.send_message(chat_id=chat_id,
            text=f"Your balance is ₹{info['balance']}. Refer more friends.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📢 Refer Friends", callback_data="refer")]]))

async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    link = f"https://t.me/GETUPIINSTANTBOT?start={user.id}"
    await context.bot.send_message(chat_id=query.message.chat.id, text=f"Refer & Earn: {link}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    text = update.message.text
    if "@" in text or "." in text:
        data = user_data.get(user.id)
        if data and data['balance'] >= 100:
            data['upi'] = text
            await context.bot.send_message(chat_id=chat_id, text="✅ UPI received. ₹100 will be sent soon.")
        else:
            await context.bot.send_message(chat_id=chat_id, text="You need ₹100 to withdraw.")

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify, pattern="^verify$"))
    app.add_handler(CallbackQueryHandler(spin, pattern="^spin$"))
    app.add_handler(CallbackQueryHandler(withdraw, pattern="^withdraw$"))
    app.add_handler(CallbackQueryHandler(refer, pattern="^refer$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    keep_alive()
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
