# Настройки
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from bs4 import BeautifulSoup
from googlesearch import search
from pydub import AudioSegment
from midi2audio import FluidSynth
import eyed3
import telegram
import apiai
import json
import requests
import timeit
import filetype
import zipfile
import shutil
import os, fnmatch, sys

TB_TOKEN = '1158668959:AAGfQxKXHm3UoXK9Y15GVuEiYGfNsNukc4E'
DF_TOKEN = '0576b8c465a44e33a6b877c6580a5bde'
proxy = {'proxy_url': 'socks5h://163.172.152.192:1080'}
keyboards = {'full': [['NES', 'CAVE', 'NINTENDO', 'ATARI'], ['PONG', 'STAIN', 'MOBILE', 'FAMICOM']], 'most': [['NES', 'CAVE']]}
root_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
black_names = []

with open(root_dir +'/user_states.json', 'r') as fp:
    user_states = json.load(fp)

# Обработка команд
def helpCommand(bot, update):
    global user_states
    chat_id = update.message.chat_id
    text = '''1. Ты даешь мне запрос
(акуна матата, все идет по плану, eminem lose yourself, daria theme...)
2. Выбираешь стиль кавера
3. Ждешь...
4. Я скидываю тебе от 0 до 3 версий трека (Как повезёт)

Команды:
/start - нажимай в любой непонятной ситуации(возврат в начало)
/moreless - дает на выбор БОЛЬШЕ стилей
/moreless - если еще раз нажать, то делает как было
/help - инструкция
/offer - посмотреть, что может предложить разработчик'''
    text = text + '\n\nТеперь давай название песни, я попробую что-нибудь найти...'
    reply_markup = telegram.ReplyKeyboardRemove()
    bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    user_states[chat_id]['state'] = 1


def offerCommand(bot, update):
    global user_states
    chat_id = update.message.chat_id
    text = '''Привет, меня зовут Искандер, я умею программировать. В том числе делать телеграмм ботов.
Если у вас есть интерес к ботам, то смотрите 1-й пункт;
если хочется просто потратить деньги -- 2-й.

1) Потенциальному клиенту:

Во-первых, Бот нужен НЕ каждому. Поэтому:
Могу БЕСПЛАТНО проконсультировать в конкретно вашем случае.

Вот примеры задач, которые может решить бот:
-Бронирование времени, запись, отмена, перенос
-Оформление заказа
-Оповещение о статусах обработки заказа, просто оповещение, микроотчет
-услуги, которые работают полностью без людей(экспресс дизайн от Искуственного Интелекта за 1000 руб)
-мониторинг цен избранного(авито)
-мониторинг мест(бла-бла кар, в ресторане)
-рекомендательная система выбирает оптимальные варианты(кроссовки: из 1000 выдает 3 на выбор)
-текстовый квест
-да и вообще все что придет в голову: от генерации картинок, до автоматического управления самолетом...

Помимо предложенных вариантов, можно БЕСПЛАТНО рассмотреть ВАШ конкретный случай, и я скажу, насколько применим бот у Вас.

Возможности чат-бота:
-не нужно логиниться
-отправка/прием файлов
-кнопки(легче для конечного пользователя)
-групповой чат
-голосовые сообщения
-серверная часть(от создания картинок до управления самолетом)
-мини-игры


2) Потенциальному спонсору видео:
Вот на какие проекты вы можете потратить деньги:
-сигнализация, фары, стартер, (управление автомобиля) с управлением через телеграмм
-если что придет в голову -- пишите, может быть реализую


Писать сюда @crtr1'''
    text = text + '\n\nТеперь давай название песни, я попробую что-нибудь найти...'
    reply_markup = telegram.ReplyKeyboardRemove()
    bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    user_states[chat_id]['state'] = 1


def moreCommand(bot, update):
    chat_id = update.message.chat_id
    global keyboards
    global user_states
    if user_states[chat_id]['width'] == 'full':
        user_states[chat_id]['width'] = 'most'
    else:
        user_states[chat_id]['width'] = 'full'
    text = 'Готово, давай пробовать!\nВведи название трека: '
    reply_markup = telegram.ReplyKeyboardRemove()
    bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    user_states[chat_id]['state'] = 1


def startCommand(bot, update):
    global user_states
    text = 'Привет! Я могу делать восьмибитный каверы.\nВведи имя и исполнителя: '
    chat_id = update.message.chat_id
    user_states[chat_id] = {'required_name': '', 'state': 1, 'style': 'NES', 'width': 'most'}
    reply_markup = telegram.ReplyKeyboardRemove()
    bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

def textMessage(bot, update):
    global user_states
    request_text = update.message.text
    chat_id = update.message.chat_id
    try:
        current_state = user_states[chat_id]['state']
        if current_state == 1:
            state1(bot, chat_id, request_text)
        elif current_state == 2:
            state2(bot, chat_id, request_text)
        elif current_state == 3:
            state3(bot, chat_id)
        elif current_state == 5:
            state5(bot, chat_id, request_text)
    except:
        startCommand(bot, update)
            
def state1(bot, chat_id, request_text):
    text = "Выберите подстиль трека:"
    global user_states
    user_states[chat_id]['required_name'] = request_text
    user_states[chat_id]['state'] = 2
    custom_keyboard = keyboards[user_states[chat_id]['width']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

    
def state2(bot, chat_id, request_text):
    global user_states
    global root_dir
    with open(root_dir +'/user_states.json', 'w') as fp:
        json.dump(user_states, fp)
    if request_text not in ['NINTENDO', 'FAMICOM', 'ATARI', 'MOBILE', 'NES', 'CAVE', 'STAIN', 'PONG']:
        return startCommand(bot, update)
    user_states[chat_id]['style'] = request_text
    text = 'Подождите, обработка может занять некоторое время...'
    reply_markup = telegram.ReplyKeyboardRemove()
    bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    user_states[chat_id]['state'] = 3
    state_midi_find(bot, chat_id, root_dir, user_states[chat_id]['required_name'])
    
def state3(bot, chat_id):
    text = 'Ищу, не мешай.'
    reply_markup = telegram.ReplyKeyboardRemove()
    bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    
def state6(bot, chat_id):
    global user_states
    text = 'Не смог найти трек, попробуйте ввести другой: '
    user_states[chat_id]['state'] = 1
    reply_markup = telegram.ReplyKeyboardRemove()
    bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    
    
def state5(bot, chat_id, request_text):
    global user_states
    if request_text not in ['NINTENDO', 'FAMICOM', 'ATARI', 'MOBILE', 'NES', 'CAVE', 'STAIN', 'PONG', '\u2705 Другая песня']:
        state1(bot, chat_id, request_text)
    elif request_text == '\u2705 Другая песня':
        user_states[chat_id]['state'] = 1
        text = 'Введите имя и исполнителя: '
        reply_markup = telegram.ReplyKeyboardRemove()
        bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    else:
        user_states[chat_id]['state'] = 2
        state2(bot, chat_id, request_text)
    
    
def state_mp3_compile(bot, chat_id, root_dir, midi_files, style, request_text):
    global user_states
    mp3_files = []
    for i in midi_files:
        wav = midi2wav(i, root_dir + '/soundfonts/' + style.lower() + '.sf2')
        mp3 = wav2mp3(wav)
        new_mp3 = root_dir + '/mp3s/' + mp3.split('/')[-1]
        shutil.move(mp3, new_mp3)
        mp3_files.append(new_mp3)
        os.remove(wav)
    mp3_files_raw = mp3_files
    mp3_files = []
    size_50 = 52428700
    for i in mp3_files_raw:
        audiofile = eyed3.load(i)
        audiofile.tag.artist = "@awesome_8bit_bot"
        audiofile.tag.save()
        if os.path.getsize(i) < size_50:
            mp3_files.append(i)
    if len(mp3_files) < 1:
        return state6(bot, chat_id)
    text = 'Вот несколько вариантов:' if len(mp3_files) > 1 else 'Слушай:'
    text = 'Трек: ' + request_text + '\n' + 'Стиль: ' + style + '\n' + text
    custom_keyboard = keyboards[user_states[chat_id]['width']] + [['\u2705 Другая песня']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    for i in mp3_files:
        send_file(bot, chat_id, i)
    user_states[chat_id]['state'] = 5


def state_midi_find(bot, chat_id, root_dir, request_text):
    global user_states
    counter = 0
    links = get_urls(request_text)
    file_name = allow_file_name(request_text)
    exist = find(file_name + '_?.mid', root_dir + '/midis/')
    if len(exist) > 0:
        midi_files = exist
    else:
        midi_files = []
        bufer = []
        for i in links:
            bufer, counter = download_midis(i, file_name, counter, root_dir)
            midi_files = midi_files + bufer
    if len(midi_files) > 3:
        midi_files = midi_files[:3]
    fl = len(midi_files) > 0
    if fl:
        state_mp3_compile(bot, chat_id, root_dir, midi_files, user_states[chat_id]['style'], request_text)
    else:
        state6(bot, chat_id)


def send_file(bot, chat_id, file_name_or_path):
    with open(file_name_or_path, 'rb') as f:
        bot.send_document(document=f, chat_id=chat_id)
        f.close()


def midi2wav(file_path, sound_font):
    fs = FluidSynth(sound_font=sound_font,)
    new_path = file_path[:-4] + '.wav'
    fs.midi_to_audio(file_path, new_path)
    return new_path


def wav2mp3(file_path):
    new_path = file_path[:-4] + '.mp3'
    AudioSegment.from_wav(file_path).export(new_path, format="mp3")
    return new_path

# for zip unpack
def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


def get_urls(request_text):
    outmassive = []
    for i in search(request_text + ' midi', tld='com', num=16, stop=16):
        if 'youtube.' not in i:
            outmassive.append(i)
    if len(outmassive) >= 7:
      outmassive = outmassive[:7]
    return outmassive


def download_midis(url0, music_name, counter, root_dir):
    num_of_tracks = 3

    if counter >= num_of_tracks:
        return [], counter
    few_files = []
    triggers = ['скачать', 'download']

    try:
        page = requests.get(url0)
    except:
        return [], counter

    soup = BeautifulSoup(page.content, 'html.parser')
    buttons = soup.find_all(href=True)

    but_len = len(buttons)
    href_part = []
    for i in buttons:
        element_text = i.get_text().lower()
        for j in triggers:
            if j in element_text:
                href_part.append(i['href'])

    url0_splitted = url0.split('/')[:3]
    for i in href_part:
        if 'http' in i:
            url = i
        else:
            url = url0_splitted[0] + '//' + url0_splitted[2] + i
        try:
            if counter >= num_of_tracks:
                break
            r = requests.get(url)
            content = r.content
            extension = filetype.guess(content).extension
            file_name = root_dir + '/midis/' +music_name + '_' + str(counter)
            if extension == 'midi':
                file_name += '.mid'
                with open(file_name, 'wb') as f:
                    f.write(content)
                few_files.append(file_name)
                counter += 1
            elif extension == 'zip':
                file_name += '.zip'
                with open(file_name, 'wb') as f:
                    f.write(content)
                with zipfile.ZipFile(file_name, 'r') as zip_ref:
                    zip_ref.extractall(file_name[:-4])
                zipenmidis = find('*.mid', file_name[:-4])
                if zipenmidis is not None:
                    for k in zipenmidis:
                        midi_file_name = root_dir + '/midis/' + music_name + '_' + str(counter) + '.mid'
                        shutil.move(k, midi_file_name)
                        few_files.append(midi_file_name)
                        counter += 1
                shutil.rmtree(file_name[:-4])
                os.remove(file_name)
        except:
            continue
    return few_files, counter
    
# Not path!!!
def allow_file_name(old_name):
    new_name = old_name
    black_list = ["\u0000",'\n', '\r', '!', '@','#', '$', '&', '~', '%', '*', '(', ')', '[', ']', '{', '}', '\'', '\"', '\\', ':', ';', '>', '<', '\`', ' ', ]
    for k in black_list:
        new_name = new_name.replace(k, '_')
        new_name = new_name.replace('__', '_')
    return new_name
    

updater = Updater(TB_TOKEN, request_kwargs=proxy)
dispatcher = updater.dispatcher
# Хендлеры
start_command_handler = CommandHandler('start', startCommand)
more_command_handler = CommandHandler('moreless', moreCommand)
offer_command_handler = CommandHandler('offer', offerCommand)
help_command_handler = CommandHandler('help', helpCommand)
text_message_handler = MessageHandler(Filters.text, textMessage)
# Добавляем хендлеры в диспетчер
dispatcher.add_handler(start_command_handler)
dispatcher.add_handler(more_command_handler)
dispatcher.add_handler(offer_command_handler)
dispatcher.add_handler(help_command_handler)
dispatcher.add_handler(text_message_handler)
# Начинаем поиск обновлений
updater.start_polling(clean=False)
# Останавливаем бота, если были нажаты Ctrl + C
updater.idle()
