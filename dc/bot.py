import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import requests
import io
import random
import time
import textwrap

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='-', intents=intents)

last_used = {}

def create_fake_tweet(ctx, message):
    display_name = ctx.author.display_name
    username = ctx.author.name

    background_paths = [
        'Backgrounds/back1.png', 'Backgrounds/back2.png', 'Backgrounds/back3.png',
        'Backgrounds/back4.png', 'Backgrounds/back5.png', 'Backgrounds/back6.png', 'Backgrounds/back7.png'
    ]

    background_path = random.choice(background_paths)

    try:
        background = Image.open(background_path)
    except FileNotFoundError:
        return "Arka plan resmi bulunamadı!"

    width, height = 1024, 614
    background = background.resize((width, height))
    image = background.copy()
    draw = ImageDraw.Draw(image)

    try:
        bold_font = ImageFont.truetype("arialbd.ttf", 41)
        normal_font = ImageFont.truetype("arial.ttf", 32)
        message_font = ImageFont.truetype("arial.ttf", 38)
    except IOError:
        bold_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()
        message_font = ImageFont.load_default()

    avatar_url = ctx.author.avatar.url
    response = requests.get(avatar_url)
    avatar = Image.open(io.BytesIO(response.content))
    avatar = avatar.resize((106, 106))

    avatar_x, avatar_y = 35, 112
    image.paste(avatar, (avatar_x, avatar_y))

    display_name_x, display_name_y = 158, 119
    draw.text((display_name_x, display_name_y), f"{display_name}", font=bold_font, fill=(255, 255, 255))

    username_x, username_y = display_name_x, display_name_y + bold_font.getbbox(display_name)[3] + 5
    draw.text((username_x, username_y), f"@{username}", font=normal_font, fill=(110, 115, 120))

    message_x, message_y = 35, 254
    max_width = width - message_x - 35
    max_height = 330

    wrapped_text = textwrap.wrap(message, width=40)  

    line_spacing = 8
    current_y = message_y
    for line in wrapped_text:
        draw.text((message_x, current_y), line, font=message_font, fill=(255, 255, 255))
        current_y += message_font.getbbox(line)[3] + line_spacing  

    output = "fake_tweet.webp"
    image.save(output, format="WebP")

    return output

@bot.command()
async def tweet(ctx, *, message: str):
    user_id = ctx.author.id
    current_time = time.time()

    if user_id in last_used:
        last_time = last_used[user_id]
        if current_time - last_time < 300:
            remaining_time = 300 - (current_time - last_time)
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)
            await ctx.send(f"Bir sonraki tweet için {minutes} dakika {seconds} saniye bekleyin.")
            return

    last_used[user_id] = current_time

    mentions = ctx.message.mentions
    if mentions:
        user = mentions[0]
        message = message.replace(f"<@{user.id}>", f"@{user.display_name}")

    tweet_image = create_fake_tweet(ctx, message)

    if tweet_image == "Arka plan resmi bulunamadı!":
        await ctx.send(tweet_image)
        return

    with open(tweet_image, 'rb') as f:
        await ctx.send(file=discord.File(f, "fake_tweet.webp"))

        
bot.run('BOT TOKEN')
