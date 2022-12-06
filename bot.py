# public key:   28ab56bdf33a0c105aec0f085cb4e1a48a23da909a8de2f6d976357c42eb0992
# app ID:   1029238046362718219
# token:    MTAyOTIzODA0NjM2MjcxODIxOQ.G_dD3x.1FBnh4hjU0S9qhwWqvPZxZoPoD9Wdq40Tom2F8

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


client.run(TOKEN)
