import asyncio
import configparser
import csv
import json
import os

import telethon
from telethon.errors import FloodWaitError
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetStickerSetRequest
from telebot import *

bot = TeleBot('1753538352:AAGW-cAk2fAT4n5rzp5tnljZIeWa6mD9udo')


async def parse_sticker_sets(channel):
    async for message in client.iter_messages(channel, reverse=True):
        if message.sticker is None:
            continue
        stickers = await client(GetStickerSetRequest(
            stickerset=message.sticker.attributes[1].stickerset)
        )
        with open('stickers.csv', 'a+', encoding='utf-8') as file:
            try:
                os.mkdir(os.getcwd() + f'/stickers/{stickers.set.short_name.replace(" ", "_").lower()}')
            except:
                pass
            for sticker in stickers.documents:
                try:
                    sticker_path = bot.get_file(telethon.utils.pack_bot_file_id(sticker))
                    downloaded_file = bot.download_file(sticker_path.file_path)
                    file_path = f'/stickers/{stickers.set.short_name.replace(" ", "_").lower()}/' \
                                f'{sticker_path.file_path.split("/")[1]}'
                    if sticker.mime_type == 'image/webp' and '.webp' not in file_path:
                        file_path += ".webp"
                    elif sticker.mime_type == 'application/x-tgsticker' and '.tgs' not in file_path:
                        file_path += '.tgs'
                    else:
                        pass
                    with open(os.getcwd() + file_path, 'wb') as new_file:
                        new_file.write(downloaded_file)
                    data = [stickers.set.title, stickers.set.short_name,
                            file_path,
                            sticker.attributes[1].alt,
                            file_path.split("/")[-1],
                            f'tg://addstickers?set={stickers.set.short_name}']
                    writer = csv.writer(file, delimiter=';')
                    writer.writerow(data)
                    await asyncio.sleep(0.1)
                except Exception as exc:
                    print(exc)
                    continue


async def main():
    chats = json.load(open('list_chats.json', 'r'))['chats']
    for chat in chats:
        channel = await client.get_entity(chat)
        await parse_sticker_sets(channel)


if __name__ == '__main__':
    try:
        os.mkdir(os.getcwd() + '/stickers')
    except:
        pass
    config = configparser.ConfigParser()
    config.read("config.ini")
    api_id = int(config['Telegram']['api_id'])
    api_hash = config['Telegram']['api_hash']
    username = config['Telegram']['username']
    client = TelegramClient(username, api_id, api_hash)
    client.flood_sleep_threshold = 1
    client.start()
    with client:
        client.loop.run_until_complete(main())
        me = client.get_me()
        client.send_message(me, 'Парсинг закончился!')
