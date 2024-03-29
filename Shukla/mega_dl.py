
import asyncio
import os
import time
import shutil
import logging
import filetype
import subprocess
import moviepy.editor
from mega import Mega
from config import Config
from posixpath import join
from functools import partial
from genericpath import isfile
from hurry.filesize import size
from asyncio import get_running_loop
from pyrogram import Client, filters
from helper.utils import progress_for_pyrogram, force_sub, is_subscribed
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

# Logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Mega Client
mega = Mega()
m = mega.login()

# Temp Download Directory
basedir = Config.DOWNLOAD_LOCATION

# Telegram's Max File Size
TG_MAX_FILE_SIZE = Config.TG_MAX_SIZE

# Automatic Url Detection
MEGA_REGEX = "https?:\/\/mega\.nz\/(?:[^\/\s]+\/)+"

# Download Mega Link

def DownloadMegaLink(url, alreadylol, download_msg):
    try:
        m.download_url(url, alreadylol, statusdl_msg=download_msg)
    except Exception as e:
        print(e)


@Client.on_message(filters.regex(MEGA_REGEX) & filters.private)
async def megadl(bot, message: Message):

    if not await is_subscribed(bot, message):
        return await force_sub(bot, message)

    url = message.text
    user_info = f'**User ID:** #id{message.from_user.id} \n**User Name:** [{message.from_user.first_name}](tg://user?id={message.from_user.id})'
    userpath = str(message.from_user.id)
    alreadylol = basedir + "/" + userpath
    try:
        if os.path.isdir(alreadylol):
            await message.reply_text(
                "**Already One Process is Going On! \nPlease Wait Until It's Get Finished 😕!**",
                reply_to_message_id=message.id,
            )
            return
        else:
            os.makedirs(alreadylol)
    except Exception as e:
        print(e)

    try:
        if 'folder' in url:
            await message.reply_text(
                "**Mega Folder Isn't Supported Yet 🤒!**",
                reply_to_message_id=message.id,
            )
            return
        else:

            logs_msg = await message.forward(Config.LOG_CHANNEL)
            trace_msg = await logs_msg.reply_text(f"#MegaDL: Download Started! \n\n{user_info}")
            download_msg = await message.reply_text(
                "**Trying To Download ...** \n\nThis Process May Take Some Time 🤷\u200d♂️!",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Cancel Mega DL", callback_data="cancel_mega"
                            )
                        ]
                    ]
                ),
                reply_to_message_id=message.id,
            )
            loop = get_running_loop()
            await loop.run_in_executor(None, partial(DownloadMegaLink, url, alreadylol, download_msg))
            getfiles = [f for f in os.listdir(
                alreadylol) if isfile(join(alreadylol, f))]
            files = getfiles[0]
            magapylol = f"{alreadylol}/{files}"
            await download_msg.edit("**Downloaded Successfully 😉!**")
            await trace_msg.edit(f"#MegaDL: Download Done! \n\n{user_info}")
    except Exception as e:
        if "list index out of range" in str(e):
            await download_msg.edit("**Please Try Again After 30 Seconds 🤒!**")
            await trace_msg.edit(
                f"#MegaDL: Download Canceled! \nReason: `{e}` \n\n{user_info}"
            )
            os.system(f"kill -9 {os.getpid()} && python3 main.py")
        else:
            await download_msg.edit(f"**Error:** `{e}`")
            await trace_msg.edit(
                f"#MegaDL: Download Failed! \nReason: `{e}` \n\n{user_info}"
            )
        shutil.rmtree(basedir + '/' + userpath)
        return
    lmaocheckdis = os.stat(alreadylol).st_size
    readablefilesize = size(lmaocheckdis)  # Convert Bytes into readable size
    if lmaocheckdis > TG_MAX_FILE_SIZE:
        await download_msg.edit(f"**Detected File Size:** `{readablefilesize}` \n**Accepted File Size:** `2.0 GB` \n\nOops! File Is Too Large To Send In Telegram 🤒!")
        await trace_msg.edit(f"#MegaDL: Upload Failed! \nReason: `File is Larger Than 2GB.` \n\n{user_info}")
        shutil.rmtree(basedir + "/" + userpath)
        return
    else:
        try:
            start_time = time.time()
            guessedfilemime = filetype.guess(magapylol)  # Detecting file type

            await download_msg.edit("**Trying To Upload ...**")
            safone = await message.reply_document(magapylol, progress=progress_for_pyrogram, progress_args=("**Uploading ...** \n", download_msg, start_time), reply_to_message_id=message.id)
            await safone.reply_text(
                "**Cont. @Snowball_Official! \nThanks For Using Me 😘!**",

                reply_to_message_id=message.id,
            )
            await download_msg.delete()
            await trace_msg.edit(f"#MegaDL: Upload Done! \n\n{user_info}")
            shutil.rmtree(basedir + "/" + userpath)
            return
        except Exception as e:
            print(e)
        # Checking file type
        filemimespotted = guessedfilemime.mime
        await download_msg.edit("**Trying To Upload ...**")
        if "image/gif" in filemimespotted:
            safone = await message.reply_animation(magapylol, progress=progress_for_pyrogram, progress_args=("**Uploading ...** \n", download_msg, start_time), reply_to_message_id=message.id)
        elif "image" in filemimespotted:
            safone = await message.reply_photo(magapylol, progress=progress_for_pyrogram, progress_args=("**Uploading ...** \n", download_msg, start_time), reply_to_message_id=message.id)
        elif "video" in filemimespotted:
            viddura = moviepy.editor.VideoFileClip(f"{magapylol}")
            vidduration = int(viddura.duration)
            thumbnail_path = f"{alreadylol}/thumbnail.jpg"
            subprocess.call(['ffmpeg', '-i', magapylol, '-ss',
                            '00:00:10.000', '-vframes', '1', thumbnail_path])
            safone = await message.reply_video(magapylol, duration=vidduration, thumb=thumbnail_path, progress=progress_for_pyrogram, progress_args=("**Uploading ...** \n", download_msg, start_time), reply_to_message_id=message.id)
        elif "audio" in filemimespotted:
            safone = await message.reply_audio(magapylol, progress=progress_for_pyrogram, progress_args=("**Uploading ...** \n", download_msg, start_time), reply_to_message_id=message.id)
        else:
            safone = await message.reply_document(magapylol, progress=progress_for_pyrogram, progress_args=("**Uploading ...** \n", download_msg, start_time), reply_to_message_id=message.id)
        await safone.reply_text(
            "**Cont. @STRANGERXWOLRD \nThanks For Using Me 😘!**",

            reply_to_message_id=safone.id,
        )
        await download_msg.delete()
        await trace_msg.edit(f"#MegaDL: Upload Done! \n\n{user_info}")
    try:
        shutil.rmtree(basedir + "/" + userpath)
        print("[ MegaDL-Bot ] Successfully Cleaned Temp Download Directory!")
    except Exception as e:
        print(e)
        return


@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_dl(bot, message):
    userpath = str(message.from_user.id)
    try:
        shutil.rmtree(basedir + "/" + userpath)
        await message.reply_text("✅ **Downloading Canceled Successfully!**", reply_to_message_id=message.id)
    except Exception as e:
        await print(e)
        await message.reply_text("❌ **No Active Download Process To Cancel!**", reply_to_message_id=message.id)
