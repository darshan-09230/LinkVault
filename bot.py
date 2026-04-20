import discord
import re

import os

TOKEN = os.getenv("TOKEN")


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def extract_url(text):
    pattern = r"(https?://[^\s]+)"
    match = re.search(pattern, text)
    return match.group(0) if match else None

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    url = extract_url(message.content)

    if url:
        await message.channel.send("✅ Link received!")

client.run(TOKEN)