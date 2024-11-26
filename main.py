from telebot import *
from telebot import types
from mysql.connector import connect
import random
import json
import re
import secrets

token = "TOKEN"
bot_name = "BOTNAME"

welcome_text = "Hello! With this bot, you can send anonymous messages. Use /list for the list of people you’ve talked to."
my_link = "Get my anonymous link"
my_contact = "Connect me to a special contact"
write_name = "Write a name for yourself"


# for some languege we decode message to unicode 
def decode_unicode_string(unicode_str):
    decoded_str = ""
    parts = re.split(r'(u[0-9a-fA-F]{4})', unicode_str)
    for part in parts:
        if part.startswith('u'):
            try:
                decoded_str += chr(int(part[1:], 16))
            except ValueError:
                decoded_str += part
        else:
            decoded_str += part
    return decoded_str
def extract_number(start_str):
    try:
        number_str = start_str.split()[1]
        decoded_number_str = decode_unicode_string(number_str)
        number = int(decoded_number_str.replace('/', ''))
    except:
        pass
    finally:
        return number
conn = connect(
      user = 'root',
      password = '',
      host = 'localhost',
      database = 'bot')
bot = TeleBot(token)



@bot.callback_query_handler(func = lambda callback: callback.data)
def check_callback(callback):
    if callback.data.startswith('unbloc'):
        try:
            message_id, chat_id ,secret , text ,my_message_id  = callback.data.split('/')[1:]
            button_foo = types.InlineKeyboardButton('Block', callback_data='block'+"/"+str(message_id)+"/"+str(chat_id)+"/"+str(secret)+"/"+str(decode_unicode_string(text))+"/"+str(my_message_id))
            button_bar = types.InlineKeyboardButton('Reply', callback_data='reply' + "/" + str(message_id) + "/" + str(chat_id)+"/"+str(secret)+"/"+str(my_message_id))#need to test [to]
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(button_foo)
            keyboard.add(button_bar)
            bot.edit_message_text(chat_id=chat_id,message_id=message_id,text=decode_unicode_string(text),reply_markup=keyboard)
            cursor = conn.cursor()
            query = f"SELECT * FROM users WHERE secret_key = '{secret}'"
            cursor.execute(query)
            res = cursor.fetchall()
            list_block = json.loads(res[0][4])
            # remove user to block list and update block list 
            list_block.remove(int(secret))
            cursor = conn.cursor()
            query =f"""UPDATE users SET list_of_block = '{json.dumps(list_block)}' WHERE chat_id = '{chat_id}';""" # here
            cursor.execute(query)
            conn.commit()
            bot.send_message(chat_id=chat_id, text="The user has been unblocked")
        except Exception as er:
            print(er) 
        finally:
            pass
    if callback.data.startswith('block'):
        try:
            message_id, chat_id ,secret , text ,my_message_id  = callback.data.split('/')[1:]
            button_foo = types.InlineKeyboardButton('Unblock', callback_data='unbloc'+"/"+str(message_id)+"/"+str(chat_id)+"/"+str(secret)+"/"+str(decode_unicode_string(text))+"/"+str(my_message_id))
            button_bar = types.InlineKeyboardButton('reply', callback_data='reply' + "/" + str(message_id) + "/" + str(chat_id)+"/"+str(secret)+"/"+str(my_message_id))#need to test [to]
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(button_foo)
            keyboard.add(button_bar)
            bot.edit_message_text(chat_id=chat_id,message_id=message_id,text=decode_unicode_string(text),reply_markup=keyboard)
            cursor = conn.cursor()
            query = f"SELECT * FROM users WHERE secret_key = '{secret}'"
            cursor.execute(query)
            res = cursor.fetchall()
            list_block = json.loads(res[0][4])
            # add user to block list
            for any in list_block:
                a = int(any)
                if a ==int(secret):
                    break
            else:
                list_block.append(int(secret)) 
            cursor = conn.cursor()
            query =f"""UPDATE users SET list_of_block = '{json.dumps(list_block)}' WHERE chat_id = '{chat_id}';""" # here
            cursor.execute(query)
            conn.commit()
            bot.send_message(chat_id=chat_id, text="The user has been blocked")
            # update block list 
            print(list_block)
        except Exception as er:
            print(er) 
    if callback.data.startswith('reply'):
        message_id, chat_id ,secret , message_id_sender = callback.data.split('/')[1:]
        bot.send_message(chat_id, "You are replying to this message", reply_to_message_id=message_id)
        cursor = conn.cursor()
        query = f"SELECT * FROM users WHERE secret_key = {secret}"
        cursor.execute(query)
        result_ = cursor.fetchall()
        if len(result_) !=0:
         cursor = conn.cursor()
         query = f"UPDATE users SET status_to = '{secret}' WHERE chat_id = {chat_id};"
         cursor.execute(query)
         conn.commit()
         query = f"UPDATE users SET reply_message_id = {int(message_id_sender)} WHERE chat_id = {chat_id};"
         cursor.execute(query)
         conn.commit()
@bot.message_handler(content_types=['photo','video','text','call'],func=lambda message:True)
def greet(message):
    print(message.chat.id)
    if message.text == "/start":
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = telebot.types.KeyboardButton(my_link)
        button2 = telebot.types.KeyboardButton(my_contact)
        keyboard.add(button1, button2)
        bot.reply_to(message,welcome_text,reply_markup=keyboard)
    else:
            if message.text is not None  and  bytes(message.text,'UTF-8') in bytes(my_link,'UTF-8'):
                cursor = conn.cursor()
                query = f"SELECT * FROM users WHERE chat_id = {message.chat.id}"
                cursor.execute(query)
                result = cursor.fetchall()
                if len(result) == 0:
                    query = f"INSERT INTO last (chat_id, message) VALUES ({message.chat.id},'chose')"
                    cursor.execute(query)
                    cursor.fetchall()
                    bot.send_message(message.chat.id,write_name)
                    conn.commit()
                else:
                    query = f"UPDATE users SET status_to = '0' WHERE chat_id = {message.chat.id};"
                    cursor.execute(query)
                    conn.commit()
                    bot.send_message(
                        message.chat.id, 
                        f"Your anonymous link is: https://telegram.me/{bot_name}?start={result[0][3]}"
                    )

            else:
                try:
                    cursor = conn.cursor()
                    query = f"SELECT * FROM users WHERE secret_key = {extract_number(message.text)}"
                    cursor.execute(query)
                    result_ = cursor.fetchall()

                    query = f"SELECT * FROM users WHERE chat_id = {message.chat.id}"
                    cursor.execute(query)
                    result = cursor.fetchall()
                    list_freadn = json.loads(result[0][9])
                    for any in list_freadn:
                        if any['secretkey'] ==result_[0][3]:
                            break
                    else:
                        list_freadn.append({"name":result_[0][2],"secretkey":result_[0][3]})
                    # check is blocked or not 
                    is_i_blocked = False
                    is_h_blocked = False
                    if result[0][3] in json.loads(result_[0][4]):
                        is_h_blocked =True
                    if result_[0][3] in json.loads(result[0][4]):
                        is_i_blocked =True
                    if is_i_blocked or is_h_blocked:
                        if is_i_blocked:
                            bot.send_message(
                                chat_id=message.chat.id, 
                                text="You have blocked this person, so you cannot talk to them."
                            )
                        else:
                            bot.send_message(
                                chat_id=message.chat.id, 
                                text="You cannot talk to this user."
                            )

                    else:
                        if len(result_) !=0:
                            cursor = conn.cursor()
                            query = f"UPDATE users SET status_to = '{extract_number(message.text)}',list_of_freand = '{json.dumps(list_freadn)}' WHERE chat_id = {message.chat.id};"
                            cursor.execute(query)
                            conn.commit()
                            bot.send_message(
                                message.chat.id, 
                                f"You are talking to {result_[0][2]}"
                            )

                except Exception as er:
                 print(er)
                 try:
                    cursor = conn.cursor()
                    query = f"SELECT * FROM last WHERE chat_id = {message.chat.id}"
                    cursor.execute(query)
                    result = cursor.fetchall()
                    if result[0][1] == 'chose':
                        t = message.from_user.username or "_"
                        query = f"INSERT INTO users (chat_id, username,name,list_of_block,secret_key,chats,list_of_freand) VALUES ({message.chat.id},'{t}','{message.text}','[]',{secrets.randbits(256)},'[]','[]')"
                        cursor.execute(query)
                        query = f"UPDATE last SET message = 'okey' WHERE chat_id = {message.chat.id};"
                        cursor.execute(query)
                        conn.commit()
                        # Update 
                    else:
                       cursor = conn.cursor()
                       query = f"SELECT * FROM users WHERE chat_id = '{message.chat.id}'"
                       cursor.execute(query)
                       result_p = cursor.fetchall()
                       #get geter info 
                       cursor = conn.cursor()
                       query = f"SELECT * FROM users WHERE secret_key = '{result_p[0][5]}'"
                       cursor.execute(query)
                       result_ = cursor.fetchall()
                       if result_p[0][5] !='0':
                           cursor = conn.cursor()
                           query = f"UPDATE users SET status_to = '0' WHERE chat_id = {message.chat.id};"
                           cursor.execute(query)
                           conn.commit()
                           # get my secret id 
                           # get list of chats 
                           cursor = conn.cursor()
                           query = f"SELECT * FROM users WHERE secret_key = '{result_[0][3]}'"
                           cursor.execute(query)
                           res = cursor.fetchall()
                           list_chats = json.loads(res[0][7])
                           # set data type
                           if message.video:
                               datatyp = "video"
                               data = message.video.file_id
                           if message.text:
                               datatyp = "text"
                           #check is reply or not
                           if message.text is None:
                               m = message.caption
                               data = message.text
                           else:
                               m = message.text


                           if message.photo:
                               datatyp = "photo"
                               data = message.photo[0].file_id
                           else:
                               data = message.text
                           if result_p[0][8]!=0 and result_p[0][8] != "0":
                               list_chats.append({"datatype":datatyp,"data":decode_unicode_string(str(data)),"caption":decode_unicode_string(m),"to":result_p[0][8],"secret_id":result_p[0][3],"my_message_id":message.message_id})# 0 it means its a new conversition
                           else:
                               list_chats.append({"datatype":datatyp,"data":decode_unicode_string(str(data)),"caption":decode_unicode_string(m),"to":0,"secret_id":result_p[0][3],"my_message_id":message.message_id})# 0 it means its a new conversition
                           cursor = conn.cursor()
                           query =f"""UPDATE users SET chats = '{json.dumps(list_chats)}' WHERE secret_key = '{result_[0][3]}';""" # here
                           cursor.execute(query)# geter result_[0]
                           query =f"""UPDATE users SET reply_message_id = 0 WHERE secret_key = '{result_[0][3]}';""" # here
                           cursor.execute(query)
                           conn.commit()
                           bot.send_message(
                                message.chat.id, 
                                "Message sent"
                            )
                           bot.send_message(
                                result_[0][0], 
                                "You have a new message. To view it, use /newmessages"
                            )

                       else:
                        if message.text=="/list":
                            query = f"SELECT * FROM users WHERE chat_id = '{message.chat.id}'"
                            cursor.execute(query)
                            result = cursor.fetchall()
                            for item in result:
                                data = eval(item[-1])
                                for entry in data:
                                    name = entry["name"]
                                    secretkey = entry["secretkey"]
                                    bot.send_message(message.chat.id,f"{name}\n{"https://telegram.me/{bot_name}?start="+str(secretkey)}")
                        if message.text=="/newmessages":
                            f = message.message_id
                            cursor = conn.cursor()
                            query = f"SELECT * FROM users WHERE chat_id = '{message.chat.id}'"
                            cursor.execute(query)
                            result = cursor.fetchall()
                            list_new_message = json.loads(result[0][7])
                            for anydata in list_new_message:
                                f = f+1
                                button_foo = types.InlineKeyboardButton('Block', callback_data='block'+"/"+str(f)+"/"+str(message.chat.id)+"/"+str(anydata["secret_id"])+"/"+str(decode_unicode_string(anydata["data"]))+"/"+str(anydata["my_message_id"]))
                                button_bar = types.InlineKeyboardButton('Reply', callback_data='reply' + "/" + str(f) + "/" + str(message.chat.id)+"/"+str(anydata["secret_id"])+"/"+str(anydata["my_message_id"]))
                                keyboard = types.InlineKeyboardMarkup()
                                keyboard.add(button_foo)
                                keyboard.add(button_bar)
                                if anydata["datatype"]=="photo":
                                   if anydata["to"] ==0:
                                        bot.send_photo(message.chat.id,anydata["data"],caption=decode_unicode_string(anydata["caption"]),reply_markup=keyboard)
                                   else:
                                        bot.send_photo(message.chat.id,anydata["data"],reply_to_message_id=anydata["to"],caption=decode_unicode_string(anydata["caption"]),reply_markup=keyboard)
                                else:
                                   if anydata["to"] ==0:
                                    k = bot.send_message(message.chat.id, decode_unicode_string(anydata["data"]),reply_markup=keyboard)
                                   else:
                                    bot.send_message(message.chat.id,decode_unicode_string(anydata["data"]), reply_to_message_id=anydata["to"],reply_markup=keyboard)

                            else:
                                cursor = conn.cursor()
                                query =f"""UPDATE users SET chats = '[]' WHERE chat_id = '{message.chat.id}';""" # here
                                cursor.execute(query)
                                conn.commit()
                        else:
                            print(message.message_id)
                            bot.send_message(message.chat.id,"I didn't understand")
                 except Exception as error:
                    bot.send_message(message.chat.id,"I didn't understand")

bot.polling()