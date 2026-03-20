import telebot
import os

# توكن البوت الخاص بك
API_TOKEN = '8738207627:AAHH711Z28AkbtuZnjKA9Kq2kPU8baAZxUk'
bot = telebot.TeleBot(API_TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً يا أحمد! ابعتلي ملف الـ Combo (txt) وقولي عايز تقسمه لكام ملف؟")

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    if message.document.file_name.endswith('.txt'):
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        file_name = message.document.file_name
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        user_data[message.chat.id] = file_name
        bot.reply_to(message, "تمام، قولي دلوقتي الرقم.. عايز تقسم الملف ده لـ كام جزء؟")
    else:
        bot.reply_to(message, "يا ريت تبعت ملف بصيغة txt بس.")

@bot.message_handler(func=lambda message: message.chat.id in user_data)
def process_split(message):
    try:
        num_files = int(message.text)
        file_name = user_data[message.chat.id]
        
        with open(file_name, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        total_lines = len(lines)
        if num_files <= 0:
            bot.reply_to(message, "العدد لازم يكون أكبر من صفر.")
            return

        lines_per_file = (total_lines + num_files - 1) // num_files
        bot.send_message(message.chat.id, f"جاري التقسيم لـ {num_files} أجزاء...")

        for i in range(num_files):
            start = i * lines_per_file
            end = (i + 1) * lines_per_file
            part_lines = lines[start:end]
            if not part_lines: break
                
            part_name = f"part_{i+1}_{file_name}"
            with open(part_name, 'w', encoding='utf-8') as f_out:
                f_out.writelines(part_lines)
            
            with open(part_name, 'rb') as f_send:
                bot.send_document(message.chat.id, f_send)
            os.remove(part_name)

        os.remove(file_name)
        del user_data[message.chat.id]
        bot.send_message(message.chat.id, "تم التقسيم بنجاح! ✅")
    except Exception as e:
        bot.reply_to(message, f"حصل مشكلة: {e}")

bot.polling()
