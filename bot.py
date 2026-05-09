import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()


import requests
from bs4 import BeautifulSoup

def contains_url(text):
   try:
    if not text.startswith(("http://", "https://")):
        text = "https://" + text
    response = requests.get(text,timeout=1) #it is an object not a string
    code=response.status_code
    print (response)
    print(code)
    if code < 400:
       return True
    else:
        return False
   except:
        return False
        
       


TOKEN = os.getenv("TOKEN")



intents = discord.Intents.default()
intents.message_content = True


bot = commands.Bot(command_prefix="!", intents=intents)


    


@bot.event
async def on_ready():

    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

@bot.tree.command(name="link", description="Add a website")
async def link(interaction: discord.Interaction, website: str):
    await interaction.response.defer()
    print(website)
    url = contains_url(website)

    if not url:
        await interaction.followup.send(
            f"❌ Invalid link! {interaction.user.mention}"
        )
        return

    await interaction.followup.send(
        f"✅ Link received! Thank you {interaction.user.mention}"
    )

    try:

        if not website.startswith(("http://", "https://")):
            website = "https://" + website

        response = requests.get(website)

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string.strip() if soup.title else "No title"

        description = "No description"

        desc_tag = soup.find(
            "meta",
            attrs={"name": "description"}
        )

        if desc_tag and desc_tag.get("content"):
            description = desc_tag["content"]

        keywords = "No keywords"

        key_tag = soup.find(
            "meta",
            attrs={"name": "keywords"}
        )

        if key_tag and key_tag.get("content"):
            keywords = key_tag["content"]

        streaming_id=1502352557564100688
        streaming = bot.get_channel(streaming_id)

        await streaming.send(            #change it so that it can send to multiple channels
            "Link: "+ website + '\n'
            f"Title: {title}\n"
            f"Description: {description}\n"
            f"Keywords: {keywords}"
        )

    except Exception as e:
        await interaction.followup.send(f"Error: {e}")
bot.run(TOKEN)