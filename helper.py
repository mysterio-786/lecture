import json
import logging
import subprocess
import datetime
import asyncio
import os
import requests
import time
from p_bar import progress_bar
import aiohttp
import tgcrypto
import aiofiles
from pyrogram.types import Message
from pyrogram import Client, filters

def get_title(url):
    try:
        result = subprocess.run(
            ["yt-dlp", "--get-title", url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        title = result.stdout.strip()
        return title if title else None
    except:
        return None

async def generate_thumbnail(filename, width=1280, height=720, time="0.0"):
    return None

def get_video_duration(filename, max_attempts=3):
    return 0


async def download(url, name):
    ka = f'{name}.pdf'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(ka, mode='wb')
                await f.write(await resp.read())
                await f.close()
    return ka
    
async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    print(f'[{cmd!r} exited with {proc.returncode}]')
    if proc.returncode == 1:
        return False
    if stdout:
        return f'[stdout]\n{stdout.decode()}'
    if stderr:
        return f'[stderr]\n{stderr.decode()}'


def old_download(url, file_name, chunk_size=1024 * 10):
    if os.path.exists(file_name):
        os.remove(file_name)
    r = requests.get(url, allow_redirects=True, stream=True)
    with open(file_name, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                fd.write(chunk)
    return file_name


def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"


def time_name():
    date = datetime.date.today()
    now = datetime.datetime.now()
    current_time = now.strftime("%H%M%S")
    return f"{date} {current_time}.mp4"


async def download_video(url, name, raw_text2):
    try:
        output_file = f"{name}.mp4"
        
        # 🔹 YouTube ke liye
        if "youtube.com" in url or "youtu.be" in url:
            command = [
                "yt-dlp",
                "-f", "bv*+ba/b",
                "--geo-bypass",
                "--concurrent-fragments", "10",
                "--retries", "10",
                "--fragment-retries", "10",
                url,
                "--output", output_file,
                "--merge-output-format", "mp4",
            ]
        
        # 🔹 DRM / Classplus (same as before)
        else:
            command = [
                "yt-dlp",
                "-k", 
                "--allow-unplayable-formats", 
                "--geo-bypass",
                * (["--cookies", "cookies.txt"] if os.path.exists("cookies.txt") else []),
                "--concurrent-fragments", "10",
                "--retries", "10",
                "--fragment-retries", "10",
                "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b",
                "-S", f"res~{raw_text2},+size,+br",
                "--fixup", "never",
                url,
                "--output", output_file,
                "--merge-output-format", "mp4",
            ]
            
        result = subprocess.run(command, check=True, text=True, stderr=subprocess.PIPE)
        
        if result.returncode == 0:
            print(f"Successfully downloaded: {output_file}")
                                
            if os.path.isfile(output_file):
                return output_file

        else:
            print(f"yt-dlp command failed: {result.stderr.strip()}")
            return None

    except FileNotFoundError as exc:
        print(f"File not found: {exc}")
        return None

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else "yt-dlp failed"
        print(f"An error occurred: {error_msg}")
        return None

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
        

async def send_vid(bot: Client, m: Message, cc, filename, thumb, name):

    generated_thumb = None
    generated_thumb = None
    
    reply = await m.reply_text(f"**UPLOADING » {name}**")

    thumbnail = thumb if thumb and thumb != "No" else generated_thumb

    duration = get_video_duration(filename)

    start_time = time.time()

    try:        
        await m.reply_video(
            filename,
            caption=cc,
            supports_streaming=True,
            height=720,
            width=1280,
            thumb=thumbnail,
            duration=duration,
            progress=progress_bar,
            progress_args=(reply, start_time)
        )
                
    except Exception as e:
        print(str(e))
                
    os.remove(filename)
    if thumbnail and os.path.exists(thumbnail):
        os.remove(thumbnail)
    
    await reply.delete(True)
