import discord
from discord.ext import commands
import random

class MultiGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.truths = [
            "ما هو أكثر شيء تندم عليه في حياتك؟",
            "لو أتيحت لك فرصة تغيير صفة واحدة في نفسك، ماذا ستختار؟",
            "ما هي الكذبة الأكبر التي أخبرتها لوالديك؟"
        ]
        self.dares = [
            "قم بكتابة رسالة غريبة في الشات العام واقفل حسابك لمدة ساعة.",
            "قم بتغيير صورتك الشخصية في ديسكورد إلى صورة مضحكة يختارها الأعضاء.",
            "اعترف للشخص الثالث في قائمة المتصلين لديك باعتراف عشوائي."
        ]

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component:
            values = interaction.data.get("values", [])
            if "truth_or_dare" in values:
                await self.start_truth_or_dare(interaction)

    async def start_truth_or_dare(self, interaction: discord.Interaction):
        """فعالية صراحة أم تحدي الجماعية"""
        view = discord.ui.View(timeout=60)
        
        # أزرار الاختيار المباشر لقنوات الشات
        truth_btn = discord.ui.Button(label="🗣️ صراحة", style=discord.ButtonStyle.primary, custom_id="game:truth")
        dare_btn = discord.ui.Button(label="🔥 تحدي", style=discord.ButtonStyle.danger, custom_id="game:dare")
        
        async def truth_callback(inter: discord.Interaction):
            question = random.choice(self.truths)
            await inter.response.send_message(f"🗣️ **سؤال الصراحة لـ {inter.user.mention}:**\n`{question}`")
            
        async def dare_callback(inter: discord.Interaction):
            action = random.choice(self.dares)
            await inter.response.send_message(f"🔥 **التحدي المطلوب من {inter.user.mention}:**\n`{action}`")

        truth_btn.callback = truth_callback
        dare_btn.callback = dare_callback
        
        view.add_item(truth_btn)
        view.add_item(dare_btn)

        await interaction.channel.send(
            content=f"🎉 {interaction.user.mention} فتح فعالية **صراحة أم تحدي**! اضغط على الأزرار بالأسفل للمشاركة:",
            view=view
        )

async def setup(bot):
    await bot.add_extension(MultiGames(bot))
