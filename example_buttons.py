from typing import List
from discord.ext import commands
import discord

import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin, ImageFont, ImageDraw, ImageOps

URL = "http://127.0.0.1:7860"

import os

import glob

import shutil
import textwrap

import math
from moviepy.editor import *
from gtts import gTTS
from mutagen.mp3 import MP3

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

MY_GUILD = discord.Object(id=GUILD)


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        self.playerLst = []
        self.playerTurn = []
        self.playerDict = {}
        self.submissions = []
        self.gameMode = 'telephone'
        self.waiting = []
        self.turn = 1
        self.id = 0

        super().__init__(command_prefix=commands.when_mentioned_or('$'), intents=intents)


bot = Bot()


class GameModal(discord.ui.Modal, title='Shhh...!!!'):
    prompt = discord.ui.TextInput(label='Enter your idea:')


    async def on_submit(self, interaction: discord.Interaction):

        for player, turn in zip(bot.playerLst, bot.playerTurn):
            if player == interaction.user.display_name:
                break

        bot.playerDict[turn]['prompts'].append(str(self.prompt))
        bot.waiting.remove(interaction.user.display_name)
        await interaction.response.send_message('Great response! Hit *Next Round* once all players have answered', ephemeral=True)


class GameButtons0(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label='Join Game', style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button,):

        if interaction.user.display_name in bot.playerLst:
            await interaction.response.send_message("You've already joined, silly!", ephemeral=True)

        else:
            bot.playerLst.append(interaction.user.display_name)
            bot.playerDict[interaction.user.display_name] = {}
            bot.playerDict[interaction.user.display_name]['prompts'] = []
            bot.playerDict[interaction.user.display_name]['images'] = []
            bot.playerDict[interaction.user.display_name]['player'] = []
            await interaction.response.send_message('Have fun!', ephemeral=True)

    @discord.ui.button(label='Players', style=discord.ButtonStyle.grey)
    async def players(self, interaction: discord.Interaction, button: discord.ui.Button,):

        string = '\n'.join(bot.playerLst)
        
        await interaction.response.send_message(f'{string}', ephemeral=True)

    @discord.ui.button(label='How to Play', style=discord.ButtonStyle.blurple)
    async def how(self, interaction: discord.Interaction, button: discord.ui.Button,):
        
        await interaction.response.send_message(f"Each round, describe an image made by other players. At the end we'll see how the images have changed!", ephemeral=True)

    @discord.ui.button(label='Start', style=discord.ButtonStyle.red)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button,):
        bot.waiting = list(bot.playerDict.keys())

        for x in bot.playerLst:

            newpath = f'./telephone/players/{x}'
            if not os.path.exists(newpath):
                os.makedirs(newpath)

        bot.playerTurn = bot.playerLst.copy()

        await interaction.response.send_message(f"Round {bot.turn}. Think up something good!", view=GameButtons1())


class GameButtons1(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label='Describe', style=discord.ButtonStyle.green)
    async def describe(self, interaction: discord.Interaction, button: discord.ui.Button,):

        if len(bot.playerDict[interaction.user.display_name]['prompts']) < bot.turn:
            await interaction.response.send_modal(GameModal())

        else:
            await interaction.response.send_message("You've already answered this round!", ephemeral=True)


    @discord.ui.button(label='Next Round', style=discord.ButtonStyle.red)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button,):

        if len(bot.waiting) == 0:

            await interaction.response.defer(thinking=True)

            for x in bot.playerDict.keys():
                prompt = bot.playerDict[x]['prompts'][-1]
                payload = {
                "prompt": str(prompt),
                "steps": 35,
                "sampler_index": 'DPM2'
                }

                response = requests.post(url=f'{URL}/sdapi/v1/txt2img', json=payload)
                r = response.json()
                load_r = json.loads(r['info'])
                meta = load_r["infotexts"][0]
                image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
                pnginfo = PngImagePlugin.PngInfo()
                pnginfo.add_text("parameters", meta)
                image.save(f'./telephone/players/{x}/{bot.turn}.png', pnginfo=pnginfo)
                bot.playerDict[x]['images'] = f'./telephone/players/{x}/{bot.turn}.png'

            bot.turn += 1
            bot.waiting = list(bot.playerDict.keys())

            bot.playerTurn = bot.playerTurn[-1:] + bot.playerTurn[:-1]

            await interaction.followup.send(content = f"Round {bot.turn}. Think up something good!", view=GameButtons2())
            print(bot.playerDict)

        else:

            string = '\n'.join(bot.waiting)
            
            await interaction.response.send_message(f"We're still waiting for:\n{string}", ephemeral=True)


class GameButtons2(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    
    @discord.ui.button(label='Get Image', style=discord.ButtonStyle.green)
    async def getimage(self, interaction: discord.Interaction, button: discord.ui.Button,):
        for player, turn in zip(bot.playerLst, bot.playerTurn):
            if player == interaction.user.display_name:
                # print(bot.playerDict[turn])
                # break

                await interaction.response.send_message("Click *Describe* when you're ready", file=discord.File(f'./telephone/players/{turn}/{bot.turn - 1}.png'), ephemeral=True)
                break
        # await interaction.response.send_message("Click *Describe* when you're ready", file=discord.File(f'./telephone/players/{turn}/{bot.turn - 1}.png'), ephemeral=True)

    @discord.ui.button(label='Describe', style=discord.ButtonStyle.green)
    async def describe2(self, interaction: discord.Interaction, button: discord.ui.Button,):

        if len(bot.playerDict[interaction.user.display_name]['prompts']) < bot.turn:
            await interaction.response.send_modal(GameModal())

        else:
            await interaction.response.send_message("You've already answered this round!", ephemeral=True)


    @discord.ui.button(label='Next Round', style=discord.ButtonStyle.red)
    async def next2(self, interaction: discord.Interaction, button: discord.ui.Button,):
        
        if len(bot.waiting) == 0:

            await interaction.response.defer(thinking=True)

            for x in bot.playerDict.keys():
                prompt = bot.playerDict[x]['prompts'][-1]
                payload = {
                "prompt": str(prompt),
                "steps": 35,
                "sampler_index": 'DPM2'
                }

                response = requests.post(url=f'{URL}/sdapi/v1/txt2img', json=payload)
                r = response.json()
                load_r = json.loads(r['info'])
                meta = load_r["infotexts"][0]
                image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
                pnginfo = PngImagePlugin.PngInfo()
                pnginfo.add_text("parameters", meta)
                image.save(f'./telephone/players/{x}/{bot.turn}.png', pnginfo=pnginfo)
                bot.playerDict[x]['images'] = f'./telephone/players/{x}/{bot.turn}.png'

            if len(bot.playerLst) <= bot.turn:
                # print('End Game')
                newpath = f'./telephone/slides'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                
                print(bot.playerDict)

                i = 1
                caps = []
                for folder in glob.glob(f"./telephone/players/**/"):


                    MAX_W, MAX_H = 512, 200
                    current_h, pad = 50, 10

                    for prompt, image in zip(bot.playerDict[folder[20:-1]]['prompts'], glob.glob(f"{folder}/*.png")):
                        back = Image.new('RGB', (512, 712))
                        img = Image.open(image)
                        back.paste(img, (0,200))
                        draw = ImageDraw.Draw(back)
                        font = ImageFont.truetype("FONTS/arial.ttf", 15)
                        title = textwrap.wrap(prompt, width=50)
                        caps.append(prompt)
                        for line in title:
                            w, h = draw.textsize(line, font=font)
                            draw.text(((MAX_W - w) / 2, current_h), line, font=font)
                            current_h += h + pad

                        back.save(f'./telephone/slides/{i}.png')
                        i += 1

                files = [image[19:].split('.')[0] for image in glob.glob(f"./telephone/slides/*.png")]
                clips = []
                language = "en"
                for cap, img in zip(caps, files):
                    obs = gTTS(text=cap, lang=language, slow=False)
                    aud = f"./telephone/slides/{img}.mp3"
                    obs.save(aud)

                for file in files:
                    length = math.ceil(MP3(f"./telephone/slides/{file}.mp3").info.length + 4)
                    clip = ImageClip(f"./telephone/slides/{file}.png").set_duration(length)
                    clip.audio = AudioFileClip(f"./telephone/slides/{file}.mp3")
                    clips.append(clip)


                concat_clip = concatenate_videoclips(clips, method="compose")
                concat_clip.write_videofile("./telephone/slides/final.mp4", fps=1)


                bot.playerLst = []
                bot.playerTurn = []
                bot.playerDict = {}
                bot.submissions = []
                bot.gameMode = 'telephone'
                bot.waiting = []
                bot.turn = 1
                bot.id = 0


                await interaction.followup.send(content = f"Game over. Take a look at your masterpiece!", file=discord.File(f'./telephone/slides/final.mp4'))
                for folder in glob.glob(f"./telephone/**/"):
                    shutil.rmtree(f'{folder}')

            else:
                bot.turn += 1
                bot.waiting = list(bot.playerDict.keys())
                bot.playerTurn = bot.playerTurn[-1:] + bot.playerTurn[:-1]
            
                await interaction.followup.send(content = f"Round {bot.turn}. Think up something good!", view=GameButtons2())

        else:

            string = '\n'.join(bot.waiting)
            
            await interaction.response.send_message(f"We're still waiting for:\n{string}", ephemeral=True)


@bot.command()
async def play(ctx: commands.Context):
    """Play a game of StablePhone"""
    bot.playerLst.append(ctx.author.name)
    bot.playerDict[ctx.author.name] = {}
    bot.playerDict[ctx.author.name]['prompts'] = []
    bot.playerDict[ctx.author.name]['images'] = []
    bot.playerDict[ctx.author.name]['player'] = []

    await ctx.send("Press *Start* once everyone has joined", view=GameButtons0())


bot.run(TOKEN)