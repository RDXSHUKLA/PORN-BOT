from __future__ import unicode_literals

import os
import requests
import asyncio
import math
import time
import wget
import re
import sys
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from youtube_search import YoutubeSearch
from youtubesearchpython import SearchVideos
from yt_dlp import YoutubeDL

youtube_regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"


@Client.on_message(filters.private & filters.regex(youtube_regex))
async def handle_youtube_video(client: Client, message: Message):
    ms = await message.reply_text("**Please Wait...**", reply_to_message_id=message.id)
    await ms.edit(text="**What you want to do ?**", reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton('Video 📹', callback_data='ytdl_video')],
         [InlineKeyboardButton('Music 🎵', callback_data='ytdl_music')]]
    ))


@Client.on_callback_query(filters.regex('^ytdl_music'))
async def song(client: Client, update: CallbackQuery):
    query = update.message.reply_to_message.text
    m = await update.message.edit(f"**ѕєαrchíng чσur ѕσng...!\n `{query}`**")
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f'thumb{title}.jpg'
        thumb = requests.get(thumbnail, allow_redirects=True)
        # Sanitize the filename by removing invalid characters
        thumb_name = re.sub(r'[<>:"/\\|?*]', '', thumb_name)
        with open(thumb_name, 'wb') as f:
            f.write(thumb.content)
        performer = f"[R͏ғᴛ]"
        duration = results[0]["duration"]
        url_suffix = results[0]["url_suffix"]
        views = results[0]["views"]
    except Exception as e:
        return await m.edit("**Fᴏᴜɴᴅ Nᴏᴛʜɪɴɢ Pʟᴇᴀsᴇ Cᴏʀʀᴇᴄᴛ Tʜᴇ Sᴘᴇʟʟɪɴɢ Oʀ Cʜᴇᴄᴋ Tʜᴇ LIɴᴋ**")

    await m.edit("**dσwnlσαdíng чσur ѕσng...!**")
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)

        cap = "\n**BY › [STRANGER](https://t.me/SHIVANSH474)**"
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr)-1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        await update.message.reply_audio(
            audio_file,
            caption=cap,
            quote=False,
            title=title,
            duration=dur,
            performer=performer,
            thumb=thumb_name,
            reply_to_message_id=update.message.reply_to_message.id
        )
        await m.delete()
    except Exception as e:
        await m.edit("**🚫 𝙴𝚁𝚁𝙾𝚁 🚫**")
        print('Error on line {}'.format(
            sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        # print(e)
    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)


# Modify the callback data to include quality options
@Client.on_callback_query(filters.regex('^ytdl_video'))
async def vsong(client: Client, update: CallbackQuery):
    # Add more quality options as needed
    quality_buttons = [
            [InlineKeyboardButton('High', callback_data='quality_video:high')],
            [InlineKeyboardButton('Medium', callback_data='quality_video:medium')],
            [InlineKeyboardButton('Low', callback_data='quality_video:low')]
    ]
    await update.message.edit("**Select Video Quality:**", reply_markup=InlineKeyboardMarkup(quality_buttons))

# Modify the callback function to handle quality selection


@Client.on_callback_query(filters.regex('^quality_video'))
async def vsong_quality(client: Client, update: CallbackQuery):
    quality = update.data.split(':')[-1]
    urlissed = update.message.reply_to_message.text
    pablo = await update.message.edit(f"**Fɪɴᴅɪɴɢ Yᴏᴜʀ Vɪᴅᴇᴏ** `{urlissed}`")
    search = SearchVideos(f"{urlissed}", offset=1, mode="dict", max_results=1)
    mi = search.result()
    mio = mi["search_result"]
    mo = mio[0]["link"]
    thum = mio[0]["title"]
    fridayz = mio[0]["id"]
    mio[0]["channel"]
    kekme = f"https://img.youtube.com/vi/{fridayz}/hqdefault.jpg"
    await asyncio.sleep(0.6)
    url = mo
    sedlyf = wget.download(kekme)
    opts = {
        "format": f"bestvideo[ext=mp4]+bestaudio[ext=m4a]/best/{quality}",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "outtmpl": "%(id)s.mp4",
        "logtostderr": False,
        "quiet": True,
    }
    try:
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(url, download=True)
    except Exception as e:
        print(e)
        return await pablo.edit(f"**𝙳𝚘𝚠𝚗𝚕𝚘𝚊𝚍 𝙵𝚊𝚒𝚕𝚎𝚍 𝙿𝚕𝚎𝚊𝚜𝚎 𝚃𝚛𝚢 𝙰𝚐𝚊𝚒𝚗..♥️**")

    file_stark = f"{ytdl_data['id']}.mp4"
    capy = f"""**TITLE :** [{thum}]({mo})\n**Rᴇǫᴜᴇsᴛᴇᴅ Bʏ :** {update.from_user.mention}"""

    await client.send_video(
        update.from_user.id,
        video=open(file_stark, "rb"),
        duration=int(ytdl_data["duration"]),
        file_name=str(ytdl_data["title"]),
        thumb=sedlyf,
        caption=capy,
        supports_streaming=True,
        reply_to_message_id=update.message.reply_to_message.id
    )
    await pablo.delete()
    for files in (sedlyf, file_stark):
        if files and os.path.exists(files):
            os.remove(files)
