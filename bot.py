import discord
from discord.ext import commands
import pymongo
import os
from dotenv import load_dotenv
load_dotenv()

#import sys

from timed_commands import start_pomodoro
from potion_manage import shop_message, unlock_message, buy_message, sell_message
from settings import help_message, tutorial_message

MONGO_URI = os.getenv('MONGO_URI')
client = pymongo.MongoClient(MONGO_URI)
db = client["potion_shop_db"]
users_collection = db["users_shop"]

TOKEN = os.getenv('DISCORD_TOKEN')

bot_intents = discord.Intents.default()
bot_intents.message_content = True
bot = discord.Bot()

# starts the bot
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("/help"))
    print("Bot is ready: Welcome!")

async def shop_exist_error(ctx):
    embed = discord.Embed(colour=discord.Colour.from_rgb(155, 38, 155),
                          description="🧪 **Welcome to PotionWorks!**\n"
                                      "You do not own a potion shop yet!\n\n"
                                      "❓ Run </openshop:1307259236568272990> to create your own potion shop, or use </help:1314502336931958806> to browse the commands.")
    await ctx.respond(embed=embed)

# Slash command /openshop
@commands.slash_command(name="openshop", description="Open your own potion shop!")
async def openshop(ctx):
    user_id = ctx.author.id
    user_data = users_collection.find_one({"user_id": user_id})
    if not user_data:
        user_data = {"user_id": user_id, 
                     "username": ctx.author.name, 
                     "coins": 10,
                     "elixirs": 0, 
                     "potions": {},
                     "unlocked_potions": []}
        users_collection.insert_one(user_data)

        embed = discord.Embed(colour=discord.Colour.from_rgb(0, 204, 102),
                              description="✅ Congrats! You have opened your Potion Works shop! 💫\n\n"
                                          "🪙 Run /help to start your first task! Earn elixir, create potions, and sell them to earn gold coins!",)
    else:
        embed = discord.Embed(colour=discord.Colour.from_rgb(255, 102, 102),
                              description="❌ You already own a Potion Works shop!")
        embed.set_footer(text=f"{user_data.get("username")} | PotionWorks - /help")
    await ctx.respond(embed=embed)
bot.add_application_command(openshop)

# Slash command /help
@commands.slash_command(name="help", description="Information about PotionWorks")
async def help(ctx):
    await help_message(ctx)
bot.add_application_command(help)

# Slash command /tutorial
@commands.slash_command(name="tutorial", description="Tutorial for starting your potion shop")
async def tutorial(ctx):
    await tutorial_message(ctx)
bot.add_application_command(tutorial)

# Slash command /pomodoro
@commands.slash_command(name="pomodoro", description="Start a pomodoro timer!")
async def pomodoro(ctx, cycles:int):
    user_data = users_collection.find_one({"user_id": ctx.author.id})
    if user_data:
        await start_pomodoro(ctx, cycles)
    else:
        await shop_exist_error(ctx)
bot.add_application_command(pomodoro)

# Slash command /shop
@commands.slash_command(name="shop", description="View the available potions to purchase and unlock")
async def shop(ctx):
    user_data = users_collection.find_one({"user_id": ctx.author.id})
    if user_data:
        await shop_message(ctx, user_data)
    else:
        await shop_exist_error(ctx)
bot.add_application_command(shop)

# Slash command /unlock
@commands.slash_command(name="unlock", description="Unlock a potion")
async def unlock(ctx, id:str):
    user_data = users_collection.find_one({"user_id": ctx.author.id})
    if user_data:
        await unlock_message(ctx, user_data, id)
    else:
        await shop_exist_error(ctx)
bot.add_application_command(unlock)

# Slash command /buy
@commands.slash_command(name="buy", description="Buy a potion")
async def buy(ctx, id:str):
    user_data = users_collection.find_one({"user_id": ctx.author.id})
    if user_data:
        await buy_message(ctx, user_data, id)
    else:
        await shop_exist_error(ctx)
bot.add_application_command(buy)

# Slash command /sell
@commands.slash_command(name="sell", description="Sell a potion")
async def sell(ctx, id:str):
    user_data = users_collection.find_one({"user_id": ctx.author.id})
    if user_data:
        await sell_message(ctx, user_data, id)
    else:
        await shop_exist_error(ctx)
bot.add_application_command(sell)

bot.run(TOKEN)
