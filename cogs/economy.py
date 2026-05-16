import discord
from discord.ext import commands

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # هنا سيتم إضافة أوامر كشف الحساب /coins وتعديل الرصيد فور ربط الرهانات بالكامل

async def setup(bot):
    await bot.add_extension(Economy(bot))
