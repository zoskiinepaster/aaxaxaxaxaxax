import discord
from discord.ext import commands
import random
import string
from PIL import Image, ImageDraw, ImageFont
import os
import json
from keep_alive import keep_alive
keep_alive()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
my_secret = os.environ['TOKEN']


def generate_captcha(text, path):
  width, height = 280, 90
  image = Image.new('RGB', (width, height), (255, 255, 255))
  # Указать путь к шрифту, если нужно. В противном случае PIL использует стандартный шрифт.
  font = ImageFont.truetype("arial.ttf", size=45)
  draw = ImageDraw.Draw(image)
  # Рандомное смещение и поворот для каждого симвоcла
  for i, char in enumerate(text):
    x = 55 * i + random.randint(5, 15)
    y = random.randint(0, 15)
    draw.text((x, y), char, fill=(0, 0, 0), font=font)

  image.save(path)


@bot.event
async def on_ready():
  print(f'Logged in as {bot.user.name}')


@bot.event
async def on_member_join(member):
  letters = string.ascii_lowercase
  captcha_text = ''.join(random.choice(letters) for i in range(5))

  captcha_path = f'{member.id}_captcha.png'
  generate_captcha(captcha_text, captcha_path)

  try:
    channel = await member.create_dm()
    await channel.send(
        "Пожалуйста, введите текст с изображения, чтобы верифицироваться на сервере. Чтобы пройти заново верификацию, перезайдите заново на сервер по этой ссылке: https://discord.gg/tSr4tTuCTx"
    )
    await channel.send(file=discord.File(captcha_path))

    def check(m):
      return m.author == member and m.channel == channel

    msg = await bot.wait_for('message', check=check)

    if msg.content == captcha_text:
      role = discord.utils.get(member.guild.roles, name="Участник сервера")
      await member.add_roles(role)
      await channel.send("Вы успешно верифицированы!")
    else:
      await channel.send("Неправильно, попробуйте снова!")
  finally:
    os.remove(captcha_path)


bot.run(my_secret)
