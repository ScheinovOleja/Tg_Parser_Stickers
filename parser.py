import asyncio
import configparser
import csv
import json
import os
import peewee as pw
import telethon
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetStickerSetRequest
from telebot import *

bot = TeleBot('1753538352:AAGW-cAk2fAT4n5rzp5tnljZIeWa6mD9udo')
database = pw.SqliteDatabase('database.db', pragmas={'foreign_keys': 4})


class Table(pw.Model):
    class Meta:
        database = database


class Packs(Table):
    title = pw.CharField(max_length=200)
    short_name = pw.CharField(max_length=200)
    file_path = pw.CharField(max_length=200)
    emoji = pw.CharField(max_length=10)
    file_name = pw.CharField(max_length=100)
    sticker_url = pw.CharField(max_length=200)


database.connect()
database.create_tables([Packs])
database.close()


async def parse_sticker_sets(channel):
    async for message in client.iter_messages(channel, reverse=True):
        if message.sticker is None:
            continue
        try:
            stickers = await client(GetStickerSetRequest(
                stickerset=message.sticker.attributes[1].stickerset)
            )
        except Exception as exc:
            continue
        try:
            test = Packs.get_or_none(title=stickers.set.title)
        except Exception as exc:
            test = None
        if test is None:
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
                    Packs.create(title=stickers.set.title,
                                 short_name=stickers.set.short_name,
                                 file_path=file_path,
                                 emoji=sticker.attributes[1].alt,
                                 file_name=file_path.split("/")[-1],
                                 sticker_url=f'tg://addstickers?set={stickers.set.short_name}').save()
                except Exception as exc:
                    print(exc)
                    continue


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
    client.flood_sleep_threshold = 10
    client.start()
    with client:
        chats = json.load(open('list_chats.json', 'r'))['chats']
        ioloop = asyncio.get_event_loop()
        for i in range(4, 21, 4):
            tasks = []
            for j in range(i):
                channel = client.get_entity(chats[j])
                tasks.append(parse_sticker_sets(channel))
                print(chats[j])
            ioloop.run_until_complete(asyncio.gather(tasks[0], tasks[1], tasks[2], tasks[3]))
        ioloop.close()
        me = client.get_entity('@SchulerBane')
        msg = client.send_message(me, 'Парсинг закончился!')
