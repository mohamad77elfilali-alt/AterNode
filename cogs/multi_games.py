import discord
from discord.ext import commands
import random

class MultiGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.truths = ["ما هو أكثر شيء تندم عليه في حياتك؟", "ما هي الكذبة الأكبر التي أخبرتها لوالديك؟"]
        self.dares = ["قم بكتابة رسالة غريبة في الشات العام", "قم بتغيير صورتك الشخصية بصورة مضحكة"]

    async def trigger_truth_or_dare(self, channel: discord.TextChannel, user: discord.User):
        """يتم استدعاؤها فوراً عند اختيار صراحة أو تحدي من اللوحة العامة"""
        view = discord.ui.View(timeout=60)
        
        truth_btn = discord.ui.Button(label="🗣️ صراحة", style=discord.ButtonStyle.primary)
        dare_btn = discord.ui.Button(label="🔥 تحدي", style=discord.ButtonStyle.danger)
        
        async def truth_callback(inter: discord.Interaction):
            await inter.response.send_message(f"🗣️ **سؤال الصراحة لـ {inter.user.mention}:**\n`{random.choice(self.truths)}`")
            
        async def dare_callback(inter: discord.Interaction):
            await inter.response.send_message(f"🔥 **التحدي المطلوب من {inter.user.mention}:**\n`{random.choice(self.dares)}`")

        truth_btn.callback = truth_callback
        dare_btn.callback = dare_callback
        view.add_item(truth_btn)
        view.add_item(dare_btn)

        await channel.send(content=f"🎉 {user.mention} يفتح فعالية **صراحة أم تحدي** للجميع بالعام! شاركوا:", view=view)

async def setup(bot):
    await bot.add_extension(MultiGames(bot))
