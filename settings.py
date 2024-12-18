
import discord
from discord.ext import commands
import os
import pymongo

MONGO_URI = os.getenv('MONGO_URI')
client = pymongo.MongoClient(MONGO_URI)
db = client["potion_shop_db"]
users_collection = db["users_shop"]

class SimpleView(discord.ui.View):
    @discord.ui.button(label="🛑 Stop Tutorial",
                       style=discord.ButtonStyle.red)
    async def stop_tutorial(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Work in progress...")

async def help_message(ctx):
    embed = discord.Embed(colour=discord.Colour.from_rgb(63, 80, 129),
                          title=f"PotionWorks - Help")
    embed.description = """
                        🧪 Welcome to PotionWorks!
                        
                        __**Beginner Commands**__
                        </tutorial:1314515623920795699> - Tutorial for starting your potion shop
                        </help:1314502336931958806> - Information about PotionWorks
                        </openshop:1307259236568272990> - Open your own potion shop!

                        __**Potion Shop Managing Commands**__
                        </shop:1310766949361389701> - View the available potions to purchase and unlock
                        </buy:1311095339897589841> - Buy a potion
                        </sell:1313770813434105879> - Sell a potion
                        </unlock:1310842018490220585> - Unlock a potion
                        
                        __**Ways to Earn Elixir**__
                        Timed Commands:
                        </pomodoro:1303997839247937536> - Start a pomodoro timer!
                        """
    await ctx.respond(embed=embed)

async def tutorial_message(ctx):
    embed = discord.Embed(colour=discord.Colour.from_rgb(63, 80, 129),
                          title=f"Welcome to the PotionWorks Tutorial!")
    embed.description = "Let's start by creating your PotionWorks shop! Use </openshop:1307259236568272990> to open your shop.\nWork in progres..."
    view = SimpleView()
    button = discord.ui.Button(label="Stop Tutorial")
    view.add_item(button)
    await ctx.respond(embed=embed, view=view)