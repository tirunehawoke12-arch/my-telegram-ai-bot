import asyncio
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types

# ቁልፎችን ከRender ሲስተም (Environment Variables) በደህንነት ለመቀበል
GEMINI_KEY = os.getenv("GEMINI_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

client = genai.Client(api_key=GEMINI_KEY)
logging.basicConfig(level=logging.INFO)

SYSTEM_INSTRUCTION = (
    "አንተ ረዳት AI ነህ። ማንኛውንም ጥያቄ ስትመልስ ወይም ምስል ስትተነትን "
    "ሁልጊዜ መልስህን በማስረጃ፣ በምክንያት እና በዝርዝር ማብራሪያ አስደግፈህ በአማርኛ መልስ።"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ሰላም! እኔ በቋሚነት ሰርቨር ላይ የምሰራው የላቀው የGemini AI ቦት ነኝ።\n\n"
        "የሚፈልጉትን ጥያቄ በጽሑፍ መጠየቅ ወይም ፎቶ (ምስል) መላክ ይችላሉ።"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=user_text,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("ይቅርታ፣ መረጃውን ማስተናገድ አልቻልኩም።")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        
        user_caption = update.message.caption if update.message.caption else "ይህንን ምስል በዝርዝር ግለጽልኝ።"
        image_part = types.Part.from_bytes(data=bytes(photo_bytes), mime_type="image/jpeg")
        
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=[image_part, user_caption],
            config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("ይቅርታ፣ ምስሉን ማንበብ አልቻልኩም።")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("🤖 ቦትዎ በሰርቨር ላይ እየሰራ ነው...")
    application.run_polling()

if __name__ == '__main__':
    main()
