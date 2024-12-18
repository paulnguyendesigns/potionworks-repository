
import discord
from discord.ext import commands
import os
import pymongo

import asyncio

MONGO_URI = os.getenv('MONGO_URI')
client = pymongo.MongoClient(MONGO_URI)
db = client["potion_shop_db"]
users_collection = db["users_shop"]

async def start_pomodoro(ctx, cycles: int):
    user_id = ctx.author.id
    username = ctx.author.name

    study_duration = 25 * 60  # 25 minutes in seconds
    short_break_duration = 25 * 60  # 5 minutes in seconds
    long_break_duration = 25 * 60 # 30 minutes in seconds

    for cycle in range(1, cycles + 1):
        # Start study period
        embed = discord.Embed(colour=discord.Colour.from_rgb(255, 102, 102),
                              title=f"Pomodoro Timer | Cycle {cycle}/{cycles} - [Timer update every 10 seconds]")
        if cycle > 1:
            await ctx.send(f"<@{ctx.author.id}> **Study time!** 📚 Check the pomodoro timer ⬇️ **below** ⬇️ for an update. 📝")
        message = await ctx.respond(embed=embed)
        await update_timer(ctx, study_duration, embed, message, "Study")

        # Break period
        if cycle % 4 == 0:
            break_duration = long_break_duration
            await ctx.send(f"<@{ctx.author.id}> It's time for a brain **break**! 💆 Check the pomodoro timer ⬆️ **above** ⬆️ for an update. ☕")
            await update_timer(ctx, break_duration, embed, message, "Long Break")
        else:
            break_duration = short_break_duration
            await ctx.send(f"<@{ctx.author.id}> It's time for a brain **break**! 💆 Check the pomodoro timer ⬆️ **above** ⬆️ for an update. ☕")
            await update_timer(ctx, break_duration, embed, message, "Short Break")

    users_collection.update_one({"user_id": user_id}, {"$inc": {"elixirs": cycles}})

    embed = discord.Embed(colour=discord.Colour.from_rgb(0, 204, 102),
                          title="Pomodoro Timer Finished!",
                          description=f"Congrats! You have gained **+{cycles}** elixir for completing {cycles} pomodoro cycle(s)!")
    await ctx.send(embed=embed)

async def update_timer(ctx, duration, embed, message, phase):
    if embed.description is None:
        embed.description = ""
    previous_description = embed.description
    if phase == "Study":
        phrase = f" Hey <@{ctx.author.id}>, it's study time!"
    elif phase == "Short Break":
        phrase = f"Hey <@{ctx.author.id}>, it's time for a short break!"
    else:
        phrase = f"Hey <@{ctx.author.id}>, it's time for a long break!"

    for ten_seconds in range(duration, -1, -10):  # Update every 10 seconds
        mins, secs = divmod(ten_seconds, 60)
        new_timer = f"{phrase} ⏳ **{mins:02}:{secs:02}**"
        embed.description = f"{previous_description}\n{new_timer}"
        await message.edit(embed=embed)
        await asyncio.sleep(10)  # Wait 10 seconds

    embed.description += f"\n{phase} time over! Moving to the next phase."
    await message.edit(embed=embed)