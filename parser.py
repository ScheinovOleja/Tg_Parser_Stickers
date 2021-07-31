import configparser
import csv
import json
import os

import telethon
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetStickerSetRequest
from telebot import *

bot = TeleBot('1753538352:AAGW-cAk2fAT4n5rzp5tnljZIeWa6mD9udo')


async def parse_sticker_sets(channel):
    async for message in client.iter_messages(channel, reverse=True):
        if message.sticker is None:
            continue
        try:
            stickers = await client(GetStickerSetRequest(
                stickerset=message.sticker.attributes[1].stickerset)
            )
            with open('stickers.csv', 'a+', encoding='utf-8') as file:
                for sticker in stickers.documents:
                    try:
                        sticker_path = bot.get_file(telethon.utils.pack_bot_file_id(sticker))
                        path = f'{os.getcwd()}/sets/{stickers.set.title.replace(" ", "_").lower()}/' \
                               f'{sticker_path.file_path.split("/")[1]}'
                        await client.download_file(sticker, path)
                        data = [stickers.set.title, stickers.set.short_name, path,
                                sticker.attributes[1].alt,
                                sticker.id,
                                f'tg://addstickers?set={stickers.set.short_name}']
                        writer = csv.writer(file, delimiter=';')
                        writer.writerow(data)
                    except Exception as exc:
                        print(exc)
                        continue
        except Exception as exc:
            print(exc)


async def main():
    chats = json.load(open('list_chats.json', 'r'))['chats']
    for chat in chats:
        channel = await client.get_entity(chat)
        await parse_sticker_sets(channel)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("config.ini")
    api_id = int(config['Telegram']['api_id'])
    api_hash = config['Telegram']['api_hash']
    username = config['Telegram']['username']
    client = TelegramClient(username, api_id, api_hash)
    client.start()
    with client:
        client.loop.run_until_complete(main())
        user = client.get_entity('@grekov')
        client.send_message(user, 'Парсинг закончился!')
