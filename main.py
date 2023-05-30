import telebot
import requests
import json
from telebot import types
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import time
import settings

def okr(a):
    return round(a, 4)

def dol_format(a):
    return str(format(okr(a)) + "$")

def price_percent(a, b):
    return str(okr(100 * b / (100 + a))) + "$"

def get_top20():
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=20&page=1&sparkline=false"
    response = requests.get(url)
    data = json.loads(response.text)
    return data

def telegram_bot(token):
    bot = telebot.TeleBot(settings.API_KEY)
    start_button = telebot.types.KeyboardButton("/start")
    cap_button = telebot.types.KeyboardButton("/cap")
    main_button = telebot.types.KeyboardButton("/main")
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(*[start_button])
    keyboard.row(*[cap_button])
    keyboard.row(*[main_button])

    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(message.chat.id, "Цей бот розпізнає в тексті числа та валюти, а потім автоматично відправляє повідомлення, в якому сума переведена в інші валюти. "
                                          "Ціну бере з сайту <a href='https://www.coingecko.com'>coingeko</a>. \n"
                                          "\n<b>На прикладах:</b>\nInput: 1 bitcoin\nOutput: 16,977.29$\n\nInput: 1.7 Ethereum\nOutput: 79,378.1₴\n"
                                          "\nДля початку роботи необхідно обрати необхідну вам валюту для конвертування. У випадку неіснуючої валюти бот виводить повідомлення "
                                          "\"Такої валюти немає\". Також бот попереджає про неправильний формат вхідних даних. \n\n<b>Список команд:</b>\n/start - початок роботи бота\n"
                                          "/info [crypto] - інформація про певну криптовалюту\n/main - вибір основної валюти для конвертування\n/cap - топ-20 криптовалют за капіталізацією."
                                          "\n/g [crypto] - графік вартості криптовалют."
                                          "\n\nСлужба підтримки: @b4dman", parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)

    @bot.message_handler(commands=["info"], content_types=["text"])
    def send_message(message):
        try:
            cur = message.text[6:]
            req = requests.get(f"https://api.coingecko.com/api/v3/coins/{cur.lower()}")
            response = req.json()
            symbol = response["symbol"]
            market_cap_rank = response["market_cap_rank"]
            mar_cap = response["market_data"]["market_cap"]["usd"]
            min_24h = response["market_data"]["low_24h"]["usd"]
            max_24h = response["market_data"]["high_24h"]["usd"]
            total_volume = response["market_data"]["total_volume"]["usd"]
            ath = response["market_data"]["ath"]["usd"]
            ath_change_per = response["market_data"]["ath_change_percentage"]["usd"]
            ath_date = response["market_data"]["ath_date"]["usd"]
            atl = response["market_data"]["atl"]["usd"]
            atl_change_per = response["market_data"]["atl_change_percentage"]["usd"]
            atl_date = response["market_data"]["atl_date"]["usd"]
            pc_24h = response["market_data"]["price_change_percentage_24h"]
            pc_7d = response["market_data"]["price_change_percentage_7d"]
            pc_30d = response["market_data"]["price_change_percentage_30d"]
            pc_1y = response["market_data"]["price_change_percentage_1y"]
            sell_price = response["market_data"]["current_price"]["usd"]
            bot.send_message(message.chat.id, f"<b>Інформація щодо криптовалюти <a href='https://www.coingecko.com/en/coins/{cur.lower()}'>{cur.lower()}</a></b>: \n\nСкорочена назва: {symbol.upper()}\n"
                                              f"Позиція в рейтингу по ринковій капіталізації: {market_cap_rank}\nРинкова капіталізація: {dol_format(mar_cap)}\nМаксимум за 24 години: {dol_format(max_24h)}\n"
                                              f"Мінімум за 24 години: {dol_format(min_24h)} \nОб'єм торгів за 24 години: {dol_format(total_volume)}\nАбсолютний максимум: {dol_format(ath)} "
                                              f"({ath_change_per}%) був {ath_date[:10]}\nАбсолютний мінімум: {dol_format(atl)} ({atl_change_per}%) був {atl_date[:10]}\n"
                                              f"Зміна вартості за 24 години: {price_percent(pc_24h, sell_price)} ({pc_24h}%) \nЗміна вартості за тиждень: {price_percent(pc_7d, sell_price)} ({pc_7d}%)\n"
                                              f"Зміна вартості за 30 діб: {price_percent(pc_30d, sell_price)} ({pc_30d}%) \nЗміна вартості за рік: {price_percent(pc_1y, sell_price)} ({pc_1y}%)",
                                              parse_mode="HTML", disable_web_page_preview=True)
        except Exception as ex:
            print(ex)
            bot.send_message(
                message.chat.id,
                "Такої криптовалюти немає"
            )

    @bot.message_handler(commands=["cap"])
    def send_top20(message):
        top20 = get_top20()
        response = ""
        for i, coin in enumerate(top20):
            response += f'{i + 1}. {coin["name"]} ({coin["symbol"].upper()}) - ${coin["current_price"]:,}\n'
        bot.send_message(message.chat.id, f"<b>Топ-20 криптовалют за капіталізацією:</b>\n\n" + response, parse_mode="HTML")

    @bot.message_handler(commands=["g"])
    def send_graph(message):
        global cur
        cur = message.text[3:]
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(
            types.InlineKeyboardButton(text="День", callback_data="day"),
            types.InlineKeyboardButton(text="Тиждень", callback_data="week")
        )
        keyboard.row(
            types.InlineKeyboardButton(text="Місяць", callback_data="month"),
            types.InlineKeyboardButton(text="Рік", callback_data="year")
        )
        bot.send_message(chat_id=message.chat.id, text="Оберіть проміжок часу:", reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        try:
            if call.message:
                global mv
                if call.data in ["usd", "uah", "eur", "jpy", "gbp", "chf", "cny", "mxn"]:
                    if call.data == "usd":
                        bot.send_message(call.message.chat.id, "В якості основної валюти обраний долар")
                        mv = "usd"
                    elif call.data == "uah":
                        bot.send_message(call.message.chat.id, "В якості основної валюти обрана гривня")
                        mv = "uah"
                    elif call.data == "eur":
                        bot.send_message(call.message.chat.id, "В якості основної валюти обране євро")
                        mv = "eur"
                    elif call.data == "jpy":
                        bot.send_message(call.message.chat.id, "В якості основної валюти обрана єна")
                        mv = "jpy"
                    elif call.data == "gbp":
                        bot.send_message(call.message.chat.id, "В якості основної валюти обраний фунт стерлінгів")
                        mv = "gbp"
                    elif call.data == "chf":
                        bot.send_message(call.message.chat.id, "В якості основної валюти обраний швейцарський франк")
                        mv = "chf"
                    elif call.data == "cny":
                        bot.send_message(call.message.chat.id, "В якості основної валюти обраний юань")
                        mv = "cny"
                    elif call.data == "mxn":
                        bot.send_message(call.message.chat.id, "В якості основної валюти обране мексиканське песо")
                        mv = "mxn"
                    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                    bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                              text="Основна валюта переобрана")

                elif call.data in ["day", "week", "month", "year"]:
                    period = ""
                    if call.data == "day":
                        period = "1"
                    elif call.data == "week":
                        period = "7"
                    elif call.data == "month":
                        period = "30"
                    elif call.data == "year":
                        period = "365"
                    data = get_data_for_period(period)
                    plot_graph(data)

                    with open("graph.png", "rb") as f:
                        bot.send_photo(chat_id=call.message.chat.id, photo=f)
                    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except Exception as ex:
            print(repr(ex))

    def get_data_for_period(period):
        url = f"https://api.coingecko.com/api/v3/coins/{cur.lower()}/market_chart?vs_currency=usd&days=" + period
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            prices = data["prices"]
            df = pd.DataFrame(prices, columns=["TimeStamp", "Price"])
            df["TimeStamp"] = df["TimeStamp"] / 1000
            df["TimeStamp"] = df["TimeStamp"].apply(lambda x: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(x)))
            df["TimeStamp"] = pd.to_datetime(df["TimeStamp"], format="%Y-%m-%d %H:%M:%S")
            df.set_index("TimeStamp", inplace=True)
            return df["Price"]
        else:
            return []

    def plot_graph(data):
        fig, ax = plt.subplots()
        ax.plot(data)
        ax.set_xticks(data.index[::len(data) // 4])
        ax.set_title(f"Графік вартості {cur.lower()}")
        ax.set_xlabel("Дата")
        ax.set_ylabel("Ціна ($)")
        plt.savefig("graph.png")
        plt.close()

    @bot.message_handler(commands=["main"])
    def maincur(message):
        markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton("Долар", callback_data="usd")
        item2 = types.InlineKeyboardButton("Гривня", callback_data="uah")
        item3 = types.InlineKeyboardButton("Євро", callback_data="eur")
        item4 = types.InlineKeyboardButton("Єна", callback_data="jpy")
        item5 = types.InlineKeyboardButton("Фунт стерлінгів", callback_data="gbp")
        item6 = types.InlineKeyboardButton("Швейцарський франк", callback_data="chf")
        item7 = types.InlineKeyboardButton("Юань", callback_data="cny")
        item8 = types.InlineKeyboardButton("Мексиканський песо", callback_data="mxn")
        markup.add(item1, item2, item3, item4, item5, item6, item7, item8)
        bot.send_message(message.chat.id, "Виберіть основну валюту для конвертування", reply_markup=markup)

    @bot.message_handler(content_types=["text"])
    def send_message(message):
        try:
            num = float(message.text.split(' ')[0])
            curr = message.text.split(' ')[1]
            req = requests.get(f"https://api.coingecko.com/api/v3/coins/{curr.lower()}")
            response = req.json()
            sell_price_usd = response["market_data"]["current_price"]["usd"]
            sell_price_uah = response["market_data"]["current_price"]["uah"]
            sell_price_eur = response["market_data"]["current_price"]["eur"]
            sell_price_jpy = response["market_data"]["current_price"]["jpy"]
            sell_price_gbp = response["market_data"]["current_price"]["gbp"]
            sell_price_chf = response["market_data"]["current_price"]["chf"]
            sell_price_cny = response["market_data"]["current_price"]["cny"]
            sell_price_mxn = response["market_data"]["current_price"]["mxn"]
            if mv == "usd":
                bot.send_message(
                    message.chat.id, message.text.lower() + " = " +
                    dol_format(float(sell_price_usd) * num)
                )
            if mv == "uah":
                bot.send_message(
                    message.chat.id, message.text.lower() + " = " +
                    str("{: }".format(okr(float(sell_price_uah) * num))) + "₴"
                )
            if mv == "eur":
                bot.send_message(
                    message.chat.id, message.text.lower() + " = " +
                    str("{: }".format(okr(float(sell_price_eur) * num))) + "€"
                )
            if mv == "jpy":
                bot.send_message(
                    message.chat.id, message.text.lower() + " = " +
                    str("{: }".format(okr(float(sell_price_jpy) * num))) + "¥"
                )
            if mv == "gbp":
                bot.send_message(
                    message.chat.id, message.text.lower() + " = " +
                    str("{: }".format(okr(float(sell_price_gbp) * num))) + "£"
                )
            if mv == "chf":
                bot.send_message(
                    message.chat.id, message.text.lower() + " = " +
                    str("{: }".format(okr(float(sell_price_chf) * num))) + "₣"
                )
            if mv == "cny":
                bot.send_message(
                    message.chat.id, message.text.lower() + " = " +
                    str("{: }".format(okr(float(sell_price_cny) * num))) + "¥"
                )
            if mv == "mxn":
                bot.send_message(
                    message.chat.id, message.text.lower() + " = " +
                    str("{: }".format(okr(float(sell_price_mxn) * num))) + "Mex$"
                )

        except ValueError as ve:
            print(ve)
            bot.send_message(
                message.chat.id,
                "Неправильний формат"
            )
        except Exception as ex:
            print(ex)
            bot.send_message(
                message.chat.id,
                "Такої криптовалюти немає"
            )
    bot.polling()

if __name__ == "__main__":
    telegram_bot(settings.API_KEY)