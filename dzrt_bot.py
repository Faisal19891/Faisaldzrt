import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ApplicationBuilder, ContextTypes
import logging
import nest_asyncio
import asyncio

# تطبيق nest_asyncio لتجنب مشكلة تداخل حلقات الأحداث
nest_asyncio.apply()

# التوكن الخاص بالبوت الذي حصلت عليه من BotFather
TOKEN = '7169459362:AAEGNBBl65d4q21nqxaFLbCTCYbXcVM-uAs'

# إعداد سجل التتبع لتسهيل عملية التصحيح
logging.basicConfig(format='%(asctime)s - %(name)s - %(levellevelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# تخزين الحالة السابقة للمنتجات
previous_availability = {}

# دالة لفحص توفر السلع على صفحة dzrt.com
async def check_products(context: ContextTypes.DEFAULT_TYPE):
    global previous_availability
    url = 'https://www.dzrt.com/ar/our-products.html'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # العثور على جميع المنتجات في الصفحة
    products = soup.find_all('li', {'class': 'product-item'})
    
    results = []
    new_availability = {}
    for product in products:
        product_name = product.find('a', {'class': 'product-item-link'}).get_text(strip=True)
        product_image = product.find('img', {'class': 'product-image-photo'})['src']
        availability = product.find('div', {'class': 'stock'}).get_text(strip=True)
        
        new_availability[product_name] = availability
        
        # التحقق من التغير في حالة التوفر
        if product_name not in previous_availability or previous_availability[product_name] != availability:
            results.append(f"Product: {product_name}\nAvailability: {availability}\nImage: {product_image}")
    
    # تحديث الحالة السابقة
    previous_availability = new_availability
    
    if results:
        results_text = "\n\n".join(results)
        await context.bot.send_message(chat_id=context.job.chat_id, text=results_text)

# دالة لإرسال إشعار عند توفر منتج جديد
async def notify_new_products(context: ContextTypes.DEFAULT_TYPE):
    await check_products(context)

# دالة بدء البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! I will now check the product availability every minute.')

    # إضافة الوظيفة إلى JobQueue للتحقق من التوفر كل دقيقة
    context.job_queue.run_repeating(notify_new_products, interval=60, first=0, chat_id=update.message.chat_id)

# دالة للرد على الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Send me a product link from dzrt.com to check availability automatically every minute.')

# دالة إعداد البوت
async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    
    # إضافة Handlers للأوامر والرسائل
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # بدء البوت
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
