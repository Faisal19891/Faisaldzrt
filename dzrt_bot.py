import os
import requests
from bs4 import BeautifulSoup
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler
import nest_asyncio
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

nest_asyncio.apply()

# تخزين توكن البوت
TOKEN = "7169459362:AAFZXUoe_QEK9kyw53g01XqOr1UbmoFjBwo"

URL = "https://www.dzrt.com/ar/our-products.html"
INTERVAL = 60  # check every 60 seconds

bot = Bot(token=TOKEN)

async def start(update: Update, context):
    await update.message.reply_text("Bot started!")
    print("Bot started!")

async def check_products(context):
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, "html.parser")
    products = soup.find_all("div", class_="product-item-info")
    
    message = ""
    for product in products:
        title = product.find("a", class_="product-item-link").text.strip()
        availability = "Available" if product.find("div", class_="stock available") else "Not Available"
        image_tag = product.find("img", class_="product-image-photo")
        image_url = image_tag['src'] if image_tag and 'src' in image_tag.attrs else "No Image Available"

        message += f"Product: {title}\nAvailability: {availability}\nImage: {image_url}\n\n"
    
    if message:
        # إرسال الرسالة إلى المعرّفات المحددة
        chat_ids = [383184072]  # قم بتغييرها وفقًا لاحتياجاتك
        for chat_id in chat_ids:
            await bot.send_message(chat_id=chat_id, text=message)
    print("Checked products and sent message")

async def main():
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    job_queue = AsyncIOScheduler()
    job_queue.add_job(check_products, 'interval', seconds=INTERVAL)
    job_queue.start()

    print("Scheduler started")

    await application.run_polling()

if __name__ == '__main__':
    print("Starting bot")
    asyncio.run(main())
