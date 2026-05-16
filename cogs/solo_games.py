import discord
from discord.ext import commands
import random

class SoloGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # تتبع الضغط على القوائم المنسدلة للألعاب الفردية
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        # التأكد من أن التفاعل قادم من قائمة منسدلة ولعبة فردية
        if interaction.type == discord.InteractionType.component:
            custom_id = interaction.data.get("custom_id")
            # إذا اختار اللاعب لعبة من القائمة المنسدلة لـ solo
            if interaction.data.get("component_type") == 3 and "dice" in interaction.data.get("values", []):
                await self.start_dice_game(interaction)
            elif interaction.type == discord.InteractionType.component and "slots" in interaction.data.get("values", []):
                await self.start_slots_game(interaction)

    async def start_dice_game(self, interaction: discord.Interaction):
        """منطق لعبة النرد السريع"""
        player_roll = random.randint(1, 6)
        bot_roll = random.randint(1, 6)
        
        if player_roll > bot_roll:
            result = f"🎉 لقد فزت! رميت `{player_roll}` والفرعون رمى `{bot_roll}`."
        elif player_roll < bot_roll:
            result = f"📉 خسرت! رميت `{player_roll}` والفرعون رمى `{bot_roll}`."
        else:
            result = f"🤝 تعادل! كلاككما رمى `{player_roll}`."

        embed = discord.Embed(
            title="🎲 جولة النرد السريع",
            description=result,
            color=discord.Color.green() if player_roll >= bot_roll else discord.Color.red()
        )
        # إرسال النتيجة في القناة المؤقتة التي تم إنشاؤها للاعب
        await interaction.channel.send(embed=embed)

    async def start_slots_game(self, interaction: discord.Interaction):
        """منطق لعبة آلة الحظ Slots"""
        emojis = ["🎰", "🍒", "💎", "🪙", "🔥"]
        slot1 = random.choice(emojis)
        slot2 = random.choice(emojis)
        slot3 = random.choice(emojis)

        if slot1 == slot2 == slot3:
            result = f"👑 **الربح الأكبر!!** تطابق ثلاثي مذهل: [ {slot1} | {slot2} | {slot3} ]"
            color = discord.Color.gold()
        elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
            result = f"✨ **ربح متوسط!** تطابق ثنائي: [ {slot1} | {slot2} | {slot3} ]"
            color = discord.Color.green()
        else:
            result = f"❌ **حظاً أوفر!** لم تتماثل الرموز: [ {slot1} | {slot2} | {slot3} ]"
            color = discord.Color.red()

        embed = discord.Embed(
            title="🎰 آلة الحظ (Slots)",
            description=result,
            color=color
        )
        await interaction.channel.send(embed=embed)

async def setup(bot):
    await bot.add_extension(SoloGames(bot))
