import configparser
import json
import os
import peewee as pw
import telethon
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetStickerSetRequest
from telebot import *

bot = TeleBot('your_token_bot')
database = pw.SqliteDatabase('database_copy.db', pragmas={'foreign_keys': 4})


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


async def parse_sticker_sets_from_file():
    sets = json.load(open('pop_packs.json', 'r'))['sets']
    for item in sets:
        try:
            sticker_set = bot.get_sticker_set(item.split('?set=')[1])
        except:
            continue
        try:
            test = Packs.get_or_none(title=sticker_set.title)
        except Exception as exc:
            test = None
        if test is None:
            print(item)
            try:
                os.mkdir(os.getcwd() + f'/stickers/{sticker_set.title.replace(" ", "_").lower()}')
            except:
                pass
            for sticker in sticker_set.stickers:
                try:
                    # sticker_path = bot.get_file(telethon.utils.pack_bot_file_id(sticker.file_id))
                    sticker_path = bot.get_file(sticker.file_id)
                    downloaded_file = bot.download_file(sticker_path.file_path)
                    file_path = f'/stickers/{sticker_set.title.replace(" ", "_").lower()}/' \
                                f'{sticker_path.file_path.split("/")[1]}'
                    if not sticker_set.is_animated and '.webp' not in sticker_path.file_path:
                        file_path += ".webp"
                    elif sticker_set.is_animated and '.tgs' not in sticker_path.file_path:
                        file_path += '.tgs'
                    else:
                        pass
                    with open(os.getcwd() + file_path, 'wb') as new_file:
                        new_file.write(downloaded_file)
                    Packs.create(title=sticker_set.title,
                                 short_name=sticker_set.name,
                                 file_path=file_path,
                                 emoji=sticker.emoji,
                                 file_name=file_path.split("/")[-1],
                                 sticker_url=item).save()
                except Exception as exc:
                    print(exc)
                    continue


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
        client.loop.run_until_complete(parse_sticker_sets_from_file())
        # client.loop.run_until_complete(parse_sticker_sets_from_file())
        me = client.get_entity('@SchulerBane')
        msg = client.send_message(me, 'Парсинг закончился!')
