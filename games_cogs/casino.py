import discord
from discord import app_commands
from discord.ext import commands
from games_config import GamesConfig
import asyncio
import random

# ==========================================
# 🔘 واجهة أزرار لعبة حجرة ورقة مقص (RPS View)
# ==========================================
class RPSView(discord.ui.View):
    def __init__(self, player_id: int, bet: int):
        super().__init__(timeout=30.0)
        self.player_id = player_id
        self.bet = bet

    @discord.ui.button(label="🪨 حجرة", style=discord.ButtonStyle.secondary, custom_id="rock")
    async def rock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_choice(interaction, "🪨")

    @discord.ui.button(label="📄 ورقة", style=discord.ButtonStyle.secondary, custom_id="paper")
    async def paper_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_choice(interaction, "📄")

    @discord.ui.button(label="✂️ مقص", style=discord.ButtonStyle.secondary, custom_id="scissors")
    async def scissors_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_choice(interaction, "✂️")

    async def process_choice(self, interaction: discord.Interaction, player_choice: str):
        # التأكد من أن الذي ضغط على الزر هو صاحب اللعبة فقط لنمش ع التخريب
        if interaction.user.id != self.player_id:
            await interaction.response.send_message("❌ هذه اللعبة ليست لك! اكتب الأمر لتلعب بنفسك.", ephemeral=True)
            return

        await interaction.response.defer()
        self.stop() # إيقاف الاستماع للأزرار

        bot_choices = ["🪨", "📄", "✂️"]
        bot_choice = random.choice(bot_choices)

        # منطق تحديد الفائز
        if player_choice == bot_choice:
            result_text = "🤝 النتيجة: **تعادل!** تم إعادة مبلغ الرهان إلى محفظتك."
            color = GamesConfig.COLOR_GAMES
            # إعادة مبلغ الرهان للمحفظة
            await interaction.client.db.execute(
                "UPDATE economy SET wallet = wallet + $1 WHERE guild_id = $2 AND user_id = $3",
                self.bet, interaction.guild_id, self.player_id
            )
        elif (player_choice == "🪨" and bot_choice == "✂️") or \
             (player_choice == "📄" and bot_choice == "🪨") or \
             (player_choice == "✂️" and bot_choice == "📄"):
            prize = self.bet * 2
            result_text = f"🏆 **لقد فزت على البوت!**\nكسبت ضعف الرهان: **{prize}** عملة! 🎉"
            color = GamesConfig.COLOR_SUCCESS
            # إضافة الجائزة (ضعف الرهان)
            await interaction.client.db.execute(
                "UPDATE economy SET wallet = wallet + $1 WHERE guild_id = $2 AND user_id = $3",
                prize, interaction.guild_id, self.player_id
            )
        else:
            result_text = f"💀 **لقد خسرت ضد البوت!**\nذهبت الـ **{self.bet}** عملة لذكاء البوت الاصطناعي."
            color = GamesConfig.COLOR_ERROR

        # تحديث الأزرار لتعطيلها بعد الانتهاء لجمالية الـ UX
        for item in self.children:
            item.disabled = True
            if item.label in [f"🪨 حجرة" if player_choice == "🪨" else "", f"📄 ورقة" if player_choice == "📄" else "", f"✂️ مقص" if player_choice == "✂️" else ""]:
                item.style = discord.ButtonStyle.success

        embed = discord.Embed(
            title="🪨✂️📄 نتيجة التحدي",
            description=f"اختيارك: **{player_choice}**\nاختيار البوت: **{bot_choice}**\n\n{result_text}",
            color=color
        )
        await interaction.edit_original_response(embed=embed, view=self)


# ==========================================
# 📦 الوحدة البرمجية لكازينو الحظ والتسلية
# ==========================================
class Casino(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 1. لعبة السلوت ماشين التفاعلية والحركية
    @app_commands.command(name="slots", description="🎰 العب بآلة الحظ والمراهنة - اربح أضعاف رهانك!")
    async def slots(self, interaction: discord.Interaction, bet: int):
        if bet <= 0:
            await interaction.response.send_message("❌ يجب أن يكون مبلغ الرهان أكبر من صفر!", ephemeral=True)
            return

        # جلب رصيد المستخدم والتحقق منه أولاً
        bal = await self.bot.db.fetchrow(
            "SELECT wallet FROM economy WHERE guild_id = $1 AND user_id = $2",
            interaction.guild_id, interaction.user.id
        )
        wallet = bal['wallet'] if bal else 0

        if wallet < bet:
            await interaction.response.send_message(f"❌ لا تملك رصيداً كافياً في محفظتك لهذا الرهان! (رصيدك الحالي: {wallet})", ephemeral=True)
            return

        # خصم مبلغ الرهان مبدئياً لبدء تدوير البكرات
        await self.bot.db.execute(
            "UPDATE economy SET wallet = wallet - $1 WHERE guild_id = $2 AND user_id = $3",
            bet, interaction.guild_id, interaction.user.id
        )

        # قائمة الرموز ونسب ظهورها في الآلة
        emojis = ["🍒", "🍋", "🍇", "💎", "🔔", "7️⃣"]

        embed = discord.Embed(
            title="🎰 آلة السلوت تدور الآن... 🎰",
            description="[ 🟥 | 🟥 | 🟥 ]\n\nجاري تدوير البكرات، انتظر حظك الساحر...",
            color=0xffd700 # اللون الذهبي الحماسي
        )
        await interaction.response.send_message(embed=embed)

        # التأثير الحركي الأسطوري: تحديث الرسالة مرتين لإعطاء شعور الحركة الواقعية للآلة
        for i in range(2):
            await asyncio.sleep(0.8)
            roll_1 = random.choice(emojis)
            roll_2 = random.choice(emojis)
            roll_3 = random.choice(emojis)
            embed.description = f"[ {roll_1} | {roll_2} | {roll_3} ]\n\nتتحرك البكرات بقوة..."
            await interaction.edit_original_response(embed=embed)

        # النتيجة النهائية الحاسمة
        final_1 = random.choice(emojis)
        final_2 = random.choice(emojis)
        final_3 = random.choice(emojis)

        # احتساب الفوز والخسارة والمضاعفات
        if final_1 == final_2 == final_3:
            # إذا تشابهت الثلاثة رموز بالكامل
            if final_1 == "💎" or final_1 == "7️⃣":
                multiplier = 10 # الجاكبوت الخارق للرموز النادرة
                result_title = "🚨 🎉 الجاكبوت الخارق!!! 🎉 🚨"
            else:
                multiplier = 5 # فوز كبير للرموز العادية
                result_title = "🔥 فوز ثلاثي كبير! 🔥"
            
            winnings = bet * multiplier
            color = GamesConfig.COLOR_SUCCESS
            status_text = f"مذهل! تشابهت جميع الرموز! فزت بـ **{multiplier} أضعاف** رهانك!\n💰 المبلغ المضاف لمحفظتك: **+{winnings}** عملة."
            
            # تسليم الأرباح الفخمة للقاعدة
            await self.bot.db.execute(
                "UPDATE economy SET wallet = wallet + $1 WHERE guild_id = $2 AND user_id = $3",
                winnings, interaction.guild_id, interaction.user.id
            )
        elif final_1 == final_2 or final_2 == final_3 or final_1 == final_3:
            # إذا تشابه رمزان فقط من الثلاثة
            multiplier = 2
            winnings = bet * multiplier
            result_title = "✨ فوز ثنائي! ✨"
            color = GamesConfig.COLOR_GAMES
            status_text = f"جيد جداً! تشابه رمزان في الآلة! فزت بـ **ضعف الرهان**.\n💰 المبلغ المضاف لمحفظتك: **+{winnings}** عملة."
            
            await self.bot.db.execute(
                "UPDATE economy SET wallet = wallet + $1 WHERE guild_id = $2 AND user_id = $3",
                winnings, interaction.guild_id, interaction.user.id
            )
        else:
            # خسارة كاملة
            result_title = "💔 حظاً أوفر المرة القادمة"
            color = GamesConfig.COLOR_ERROR
            status_text = f"للأسف، لم يتشابه أي رمز في الآلة.\n📉 خسرت رهانك بقيمة: **-{bet}** عملة."

        # عرض لوحة النتيجة النهائية الفخمة
        await asyncio.sleep(0.8)
        final_embed = discord.Embed(
            title=result_title,
            description=f"**[ {final_1} | {final_2} | {final_3} ]**\n\n{status_text}",
            color=color
        )
        final_embed.set_footer(text=f"لاعب الحظ: {interaction.user.name}")
        await interaction.edit_original_response(embed=final_embed)


    # 2. لعبة حجرة ورقة مقص التفاعلية بالأزرار
    @app_commands.command(name="game-rps", description="🪨✂️📄 تحدى ذكاء البوت في لعبة حجرة ورقة مقص بمبالغ مالية!")
    async def game_rps(self, interaction: discord.Interaction, bet: int):
        if bet <= 0:
            await interaction.response.send_message("❌ يجب أن يكون مبلغ الرهان أكبر من صفر!", ephemeral=True)
            return

        bal = await self.bot.db.fetchrow(
            "SELECT wallet FROM economy WHERE guild_id = $1 AND user_id = $2",
            interaction.guild_id, interaction.user.id
        )
        wallet = bal['wallet'] if bal else 0

        if wallet < bet:
            await interaction.response.send_message(f"❌ لا تملك رصيداً كافياً في محفظتك! (رصيدك الحالي: {wallet})", ephemeral=True)
            return

        # خصم الرهان لبدء اللعب
        await self.bot.db.execute(
            "UPDATE economy SET wallet = wallet - $1 WHERE guild_id = $2 AND user_id = $3",
            bet, interaction.guild_id, interaction.user.id
        )

        embed = discord.Embed(
            title="🪨✂️📄 تحدي حجرة ورقة مقص",
            description=f"لقد راهنت بـ **{bet}** عملة ضد البوت!\nيرجى تحديد سلاحك الآن بالضغط على الأزرار التفاعلية أدناه في غضون 30 ثانية.",
            color=GamesConfig.COLOR_GAMES
        )
        
        view = RPSView(interaction.user.id, bet)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(Casino(bot))
