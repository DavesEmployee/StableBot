# This example requires the 'message_content' privileged intent to function.

from typing import List
from discord.ext import commands
from discord import app_commands
import discord
import asyncio

import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin

url = "http://127.0.0.1:7860"

import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

MY_GUILD = discord.Object(id=GUILD)  # replace with your guild id

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)
        self.game = False
        self.playerlst = []
        self.playerdict = {}
        self.gameType = 'telephone'
        self.submissions = []

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


# class PrivGen(discord.ui.Modal, title='Private Prompt'):
#     prompt = discord.ui.TextInput(label='Prompt')


#     async def on_submit(self, interaction: discord.Interaction):
#         await interaction.response.defer(ephemeral=True, thinking=True)
#         payload = {
#             "prompt": str(self.prompt),
#             "steps": 35,
#             "sampler_index": 'DPM2'
#         }

#         response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
#         r = response.json()
#         load_r = json.loads(r['info'])
#         meta = load_r["infotexts"][0]
#         image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
#         pnginfo = PngImagePlugin.PngInfo()
#         pnginfo.add_text("parameters", meta)
#         image.save('testoutput2.png', pnginfo=pnginfo)
        
#         # await interaction.response.edit_message(content='Here you go!', attachments=[discord.File('testoutput2.png')], view=Buttons())
#         await interaction.followup.send(content='Here you go!', file =discord.File('testoutput2.png'), view=Buttons())


# class PubGen(discord.ui.Modal, title='Public Prompt'):
#     prompt = discord.ui.TextInput(label='Prompt')


#     async def on_submit(self, interaction: discord.Interaction):
#         await interaction.response.defer(thinking=True)
#         payload = {
#             "prompt": str(self.prompt),
#             "steps": 35,
#             "sampler_index": 'DPM2'
#         }

#         response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
#         r = response.json()
#         load_r = json.loads(r['info'])
#         meta = load_r["infotexts"][0]
#         image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
#         pnginfo = PngImagePlugin.PngInfo()
#         pnginfo.add_text("parameters", meta)
#         image.save('testoutput2.png', pnginfo=pnginfo)
        
#         # await interaction.response.edit_message(content='Here you go!', attachments=[discord.File('testoutput2.png')], view=Buttons())
#         await interaction.followup.send(content=str(self.prompt), file =discord.File('testoutput2.png'), view=Buttons())


# class Buttons(discord.ui.View):
#     def __init__(self, *, timeout=180):
#         super().__init__(timeout=timeout)

#     @discord.ui.button(label='Private Image', style=discord.ButtonStyle.gray)
#     async def private(self, interaction: discord.Interaction, button: discord.ui.Button,):
#         await interaction.response.send_modal(PrivGen())


#     @discord.ui.button(label='Public Image', style=discord.ButtonStyle.green)
#     async def public(self, interaction: discord.Interaction, button: discord.ui.Button,):
#         await interaction.response.send_modal(PubGen())


# @client.tree.command()
# async def game(interaction: discord.Interaction):
#     """Generate images"""
#     await interaction.response.send_message('Think up something good!', view=Buttons(), ephemeral=True)


@client.tree.command()
@app_commands.describe(
    prompt='What would you like to see?',
)
async def dream(interaction: discord.Interaction, prompt: str):
    """Generates an image."""
    await interaction.response.defer(thinking=True)
    payload = {
        "prompt": str(prompt),
        "steps": 35,
        "sampler_index": 'DPM2'
    }

    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    r = response.json()
    load_r = json.loads(r['info'])
    meta = load_r["infotexts"][0]
    image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text("parameters", meta)
    image.save('testoutput2.png', pnginfo=pnginfo)
    
    await interaction.followup.send(content=f'*{prompt}* \n -by {interaction.user.mention}', file=discord.File('testoutput2.png'))


##########
### Remember to change the interactions so that theyre not private and accessible by all users. Maybe a context object? Not sure if buttons work there. Check Tic Tac Toe?


# class GameModal(discord.ui.Modal, title='Shhh...!!!'):
#     prompt = discord.ui.TextInput(label='Game Modal')


#     async def on_submit(self, interaction: discord.Interaction):
#         client.playerdict[interaction.user].append(str(self.prompt)) # need to add empty list to player dict on game start
#         await interaction.response.send_message('Great response! Hit *Next Round* once all players have answered', ephemeral=True)

    
# class GameButtons0(discord.ui.View):
#     def __init__(self, *, timeout=180):
#         super().__init__(timeout=timeout)

#     @discord.ui.button(label='Join Game', style=discord.ButtonStyle.green)
#     async def private(self, interaction: discord.Interaction, button: discord.ui.Button,):

#         if interaction.user in client.playerslst:
#             await interaction.response.send_message("You've already joined, silly!", ephemeral=True)
#         client.playerlst.append(interaction.user)
#         client.playerdict[interaction.user] = []
#         await interaction.response.send_message('Have fun!', ephemeral=True)

#     @discord.ui.button(label='Start', style=discord.ButtonStyle.red)
#     async def private(self, interaction: discord.Interaction, button: discord.ui.Button,):
#         await interaction.response.send_message('Think up something good!', view=GameButtons1())


# class GameButtons1(discord.ui.View):
#     def __init__(self, *, timeout=180):
#         super().__init__(timeout=timeout)

#     @discord.ui.button(label='Describe', style=discord.ButtonStyle.gray)
#     async def private(self, interaction: discord.Interaction, button: discord.ui.Button,):
#         await interaction.response.send_modal(GameModal())


#     @discord.ui.button(label='Next Round', style=discord.ButtonStyle.green)
#     async def public(self, interaction: discord.Interaction, button: discord.ui.Button,):
#         await interaction.response.defer(thinking=True)
#         await interaction.response.edit_message('Think up something good!', view=GameButtons2())


# class GameButtons2(discord.ui.View):
#     def __init__(self, *, timeout=180):
#         super().__init__(timeout=timeout)

#     @discord.ui.button(label='Describe', style=discord.ButtonStyle.gray)
#     async def private(self, interaction: discord.Interaction, button: discord.ui.Button,):
#         await interaction.response.send_modal(GameModal())


#     @discord.ui.button(label='Next Round', style=discord.ButtonStyle.green)
#     async def public(self, interaction: discord.Interaction, button: discord.ui.Button,):
#         await interaction.response.defer(thinking=True)
#         for x in client.playerdict:
#             prompt = client.playerdict[x][-1] ### This probably isn't right. How do you access bot attributes?
#             payload = {
#             "prompt": prompt,
#             "steps": 35,
#             "sampler_index": 'DPM2'
#             }

#             response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
#             r = response.json()
#             load_r = json.loads(r['info'])
#             meta = load_r["infotexts"][0]
#             image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
#             pnginfo = PngImagePlugin.PngInfo()
#             pnginfo.add_text("parameters", meta)
#             image.save(f'./telephone/{x}{len(client.playerdict[x])}.png', pnginfo=pnginfo)

#         await interaction.response.edit_message('Think up something good!', attachments=[discord.File(file) for file in file_location], view=GameButtons2()) # need to add file location


# @client.command()
# async def play(ctx: commands.Context):
#     """Play a game of StablePhone"""
#     await ctx.send("Press *Start* once everyone has joined", view=GameButtons0())


client.run(TOKEN)