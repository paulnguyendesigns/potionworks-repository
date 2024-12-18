
import discord
from discord.ext import commands
import os
import pymongo

MONGO_URI = os.getenv('MONGO_URI')
client = pymongo.MongoClient(MONGO_URI)
db = client["potion_shop_db"]
users_collection = db["users_shop"]

POTION_TYPES = {
    "health": {"price": 5, "elixir_cost": 1, "unlock_cost": 10},
    "shield": {"price": 7, "elixir_cost": 3, "unlock_cost": 40}
}

async def shop_message(ctx, user_data):
    embed = discord.Embed(colour=discord.Colour.from_rgb(63, 80, 129),
                          title="🫧 Potion Works Shop 🫧",
                          description="")
    index = 1
    for potion_type, potion_data in POTION_TYPES.items():
        elixir_cost = potion_data["elixir_cost"]
        price = potion_data["price"]
        unlock_cost = potion_data["unlock_cost"]
        if potion_type not in user_data.get("unlocked_potions"):
            embed.description += f"__**{potion_type.capitalize()} Potion**__ 🔒\nElixir Cost: {elixir_cost} elixir\nSelling Price: {price} gold coins/potion\nUnlock Cost: {unlock_cost} gold coins\nID: `{potion_type}`\n"
        else:
            embed.description += f"""__**{potion_type.capitalize()} Potion**__ 🧪\nElixir Cost: {elixir_cost} elixir\nSelling Price: {price} gold coins/potion 
                                     Potions in stock: {user_data.get("potions", {}).get(potion_type, 0)} potion(s)\nID: `{potion_type}`\n"""
        
        if index == len(POTION_TYPES):
            embed.description += "---------------\n"
        else:
            embed.description += "\n"
        index += 1
    embed.description += f"🪙 Gold Storage: {user_data.get("coins", 0)} gold coins\n💧 Elixir Storage: {user_data.get("elixirs", 0)} elixir\n"
    embed.description += "Use `/buy [id]` to purchase a potion!\nUse `/sell [id]` to unlock a potion!\nUse `/unlock [id]` to unlock a potion!"
    embed.set_footer(text=f"{user_data.get("username")} | PotionWorks - /help")
    with open("/Users/paulnguyen/Desktop/potionworks discord bot/potion_logo.png", "rb") as f:
        file = discord.File(f, filename="potion_logo.png")
        embed.set_thumbnail(url="attachment://potion_logo.png")
    await ctx.respond(file=file, embed=embed)

async def unlock_message(ctx, user_data, id):
    potion_type = id.lower()
    if potion_type not in POTION_TYPES:
        embed = discord.Embed(colour=discord.Colour.from_rgb(255, 102, 102),
                              description="❌ Please unlock a valid potion type!")
        embed.set_footer(text=f"{user_data.get("username")} | PotionWorks - /help")
        await ctx.respond(embed=embed)
        return
    
    if potion_type in user_data.get("unlocked_potions"):
        embed = discord.Embed(colour=discord.Colour.from_rgb(255, 102, 102),
                              description=f"❌ You already unlocked the {potion_type.capitalize()} potion!")
        embed.set_footer(text=f"{user_data.get("username")} | PotionWorks - /help")
        await ctx.respond(embed=embed)
        return

    unlock_cost = POTION_TYPES[potion_type]["unlock_cost"]
    if user_data["coins"] < unlock_cost:
        embed = discord.Embed(colour=discord.Colour.from_rgb(255, 102, 102),
                              description=f"❌ You need {unlock_cost} coins to unlock the {potion_type.capitalize()} potion!")
        embed.set_footer(text=f"{user_data.get("username")} | PotionWorks - /help")
        await ctx.respond(embed=embed)
        return
    
    users_collection.update_one({"user_id": ctx.author.id}, 
                                {"$inc": {"coins": -(unlock_cost)},
                                "$push": {"unlocked_potions": potion_type}})
    embed = discord.Embed(colour=discord.Colour.from_rgb(0, 204, 102),
                          description=f"✅ Congrats! You have unlocked the **{potion_type.capitalize()} Potion** for **{unlock_cost} gold coins**!")
    await ctx.respond(embed=embed)

async def buy_message(ctx, user_data, id):
    potion_type = id.lower()
    if potion_type not in POTION_TYPES:
        embed = discord.Embed(colour=discord.Colour.from_rgb(255, 102, 102),
                              description="❌ Please buy a valid potion type!")
        embed.set_footer(text=f"{user_data.get("username")} | PotionWorks - /help")
        await ctx.respond(embed=embed)
        return
    
    if potion_type not in user_data.get("unlocked_potions"):
        embed = discord.Embed(colour=discord.Colour.from_rgb(255, 102, 102),
                              description=f"❌ You need to unlock the {potion_type.capitalize()} potion first!\nUse `/unlock [id]` to unlock a potion.")
        embed.set_footer(text=f"{user_data.get("username")} | PotionWorks - /help")
        await ctx.respond(embed=embed)
        return
    
    elixir_cost = POTION_TYPES[potion_type]["elixir_cost"]
    if user_data["elixirs"] < elixir_cost:
        embed = discord.Embed(colour=discord.Colour.from_rgb(255, 102, 102),
                              description=f"❌ You need {elixir_cost} elixir to buy the {potion_type.capitalize()} potion!")
        embed.set_footer(text=f"{user_data.get("username")} | PotionWorks - /help")
        await ctx.respond(embed=embed)
        return
    
    users_collection.update_one({"user_id": ctx.author.id},
                                {"$inc": {"elixirs": -(elixir_cost), f"potions.{potion_type}": 1}})
    embed = discord.Embed(colour=discord.Colour.from_rgb(0, 204, 102),
                          description=f"✅ Congrats! You have bought a **{potion_type.capitalize()} Potion** for **{elixir_cost} elixir**!")
    await ctx.respond(embed=embed)

async def sell_message(ctx, user_data, id):
    potion_type = id.lower()
    if potion_type not in POTION_TYPES:
        embed = discord.Embed(colour=discord.Colour.from_rgb(255, 102, 102),
                              description="❌ Please buy a valid potion type!")
        await ctx.respond(embed=embed)
        return

    if potion_type not in user_data.get("unlocked_potions"):
        embed = discord.Embed(colour=discord.Colour.from_rgb(255, 102, 102),
                              description=f"❌ You need to unlock the {potion_type.capitalize()} potion first!\nUse `/unlock [id]` to unlock a potion.")
        await ctx.respond(embed=embed)
        return
    
    potion_quantity = user_data["potions"].get(potion_type)
    if potion_quantity == 0:
        embed = discord.Embed(colour=discord.Colour.from_rgb(255, 102, 102),
                              description=f"❌ You do not have any {potion_type.capitalize()} potions!")
        await ctx.respond(embed=embed)
        return
    
    users_collection.update_one({"user_id": ctx.author.id},
                                {"$inc": {"coins": POTION_TYPES[potion_type]["price"], f"potions.{potion_type}": -1}})
    embed = discord.Embed(colour=discord.Colour.from_rgb(0, 204, 102),
                          description=f"✅ Congrats! You have sold a **{potion_type.capitalize()} Potion** and earned **{POTION_TYPES[potion_type]["price"]} gold coins**!")
    await ctx.respond(embed=embed)