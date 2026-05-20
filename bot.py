import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import websitecheck
from dataextractorv2 import WebsiteDataExtractor
import joblib
import sqlite3

load_dotenv()

conn = sqlite3.connect("database.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS URLs (
    URL TEXT PRIMARY KEY,
    Category TEXT,
    Username TEXT           
)
""")

conn.commit()

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
            f"❌ The link is either invalid or unreachable by me! {interaction.user.mention}"
        )
        return
    elif websitecheck.check(website) == "Unsafe URL":
        await interaction.followup.send(
        f"❌ Unsafe link! {interaction.user.mention}"
    )
        return
    try:
        cursor.execute(
            "INSERT INTO URLs (URL,Username) VALUES (?,?)",
            (website,interaction.user.name)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        await interaction.followup.send(
        f"❌ Link already exists! {interaction.user.mention}"
    )
        return

    await interaction.followup.send(
        f"✅ Link received! Thank you {interaction.user.mention}"
    )

    try:
        
        model=joblib.load('discord-link-bot\website_categorizer3.joblib')
        vectorizer=joblib.load(r'discord-link-bot\vectorizer3.joblib')
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



        extractor=WebsiteDataExtractor(website)
        data=extractor.extract()
        x=vectorizer.transform([data])
        prediction = model.predict(x)[0]
        prediction=prediction.lower()
        prob=model.predict_proba(x)[0]
        best_prob=max(prob)
        cursor.execute(
            "UPDATE URLs SET Category = ? WHERE URL = ?",
             (prediction, website)
                )
        conn.commit()
                
        # print(prediction)
        # print(best_prob)
        channel_ids={
            "ai":1506644918985293894,
            "image":1506645841136586974,
            "developer":1506645892818665584,
            "pdf":1506645938024747110,
            "learning":1506646017385173045,
            "research":1506646066391548108,
            "productivity":1506646129687658566,
            "audio/video":1506646202912079922,
            "design":1506646256406233108,
            "data":1506646312656048250,
            "gaming":1506646346713661500,
            "other":1506646382914568202
        }
        if best_prob>0.4:
            if prediction =="ai tools":
                message = bot.get_channel(channel_ids["ai"])
               
            elif prediction == "image tools":
                message = bot.get_channel(channel_ids["image"])
                
            elif prediction == "developer tools":
                message = bot.get_channel(channel_ids["developer"])
                
            elif prediction == "pdf tools":
                message = bot.get_channel(channel_ids["pdf"])
                
            elif prediction == "learning platforms":
                message = bot.get_channel(channel_ids["learning"])
                
            elif prediction == "research resources":
                message = bot.get_channel(channel_ids["research"])

            elif prediction == "productivity apps":
                message = bot.get_channel(channel_ids["productivity"])

            elif prediction == "audio/video tools":
                message = bot.get_channel(channel_ids["audio/video"])

            elif prediction == "design tools":
                message = bot.get_channel(channel_ids["design"])

            elif prediction == "data tools":
                message = bot.get_channel(channel_ids["data"])

            elif prediction == "gaming tools":
                message = bot.get_channel(channel_ids["gaming"])
        else:
            message = bot.get_channel(channel_ids["other"])
        await message.send(            
            "Link: "+ website + '\n'
            f"Title: {title}\n"
            f"Description: {description}\n"
            # f"Keywords: {keywords}"
        )

    except Exception as e:
        await interaction.followup.send(f"Error: {e}")
bot.run(TOKEN)
conn.close()