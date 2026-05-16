import discord
from discord.ext import commands
import asyncpg
import random
import logging
from typing import Optional, Dict, List
import asyncio
from datetime import datetime

logger = logging.getLogger("GamingBot")

class RPSChoiceView(discord.ui.View):
    """حجر ورقة مقص - خيارات المستخدم"""
    def __init__(self, bot_choice: str, user_id: int):
        super().__init__(timeout=30)
        self.bot_choice = bot_choice
        self.user_id = user_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ هذه اللعبة ليست لك!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="🪨 حجر", style=discord.ButtonStyle.secondary, custom_id="rps_rock")
    async def rock(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_result(interaction, "Rock")

    @discord.ui.button(label="📄 ورقة", style=discord.ButtonStyle.secondary, custom_id="rps_paper")
    async def paper(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_result(interaction, "Paper")

    @discord.ui.button(label="✂️ مقص", style=discord.ButtonStyle.secondary, custom_id="rps_scissors")
    async def scissors(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_result(interaction, "Scissors")

    async def process_result(self, interaction: discord.Interaction, user_choice: str):
        # تعطيل الأزرار بعد الاختيار
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)

        translations = {"Rock": "🪨 حجر", "Paper": "📄 ورقة", "Scissors": "✂️ مقص"}
        
        if user_choice == self.bot_choice:
            result_str = "🤝 تعادل!"
            color = 0xFFA500
        elif (user_choice == "Rock" and self.bot_choice == "Scissors") or \
             (user_choice == "Paper" and self.bot_choice == "Rock") or \
             (user_choice == "Scissors" and self.bot_choice == "Paper"):
            result_str = "🎉 أنت الفائز!"
            color = 0x00FF00
        else:
            result_str = "😢 البوت فاز عليك!"
            color = 0xFF0000

        embed = discord.Embed(title="✂️ نتيجة تحدي حجر ورقة مقص", color=color)
        embed.add_field(name="اختيارك", value=translations[user_choice], inline=True)
        embed.add_field(name="اختيار البوت", value=translations[self.bot_choice], inline=True)
        embed.add_field(name="النتيجة", value=result_str, inline=False)
        await interaction.followup.send(embed=embed)

class TriviaView(discord.ui.View):
    """عرض خيارات لعبة الأسئلة الفردية وتصحيحها فوراً"""
    def __init__(self, correct_answer: str, options: list, user_id: int):
        super().__init__(timeout=30)
        self.correct_answer = correct_answer
        self.user_id = user_id
        
        # إنشاء الأزرار برمجياً بناءً على الخيارات العشوائية المعطاة
        for idx, option in enumerate(options):
            btn = discord.ui.Button(label=f"خيار {idx+1}: {option}", style=discord.ButtonStyle.primary, custom_id=f"trivia_opt_{idx}")
            btn.callback = self.make_callback(option)
            self.add_item(btn)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ هذه اللعبة ليست لك!", ephemeral=True)
            return False
        return True

    def make_callback(self, chosen_option):
        async def callback(interaction: discord.Interaction):
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(view=self)
            
            if chosen_option == self.correct_answer:
                embed = discord.Embed(title="🎉 إجابة صحيحة!", description=f"أحسنت الاختيار: **{self.correct_answer}**", color=0x00FF00)
            else:
                embed = discord.Embed(title="😢 إجابة خاطئة!", description=f"الإجابة الصحيحة هي: **{self.correct_answer}**", color=0xFF0000)
            await interaction.followup.send(embed=embed)
        return callback

class SoloGamePage1View(discord.ui.View):
    """لوحة التحكم بألعاب السولو - الأزرار الآن تفاعلية بالكامل ومتصلة بالوظائف"""
    def __init__(self, user_id: int, channel_id: int, bot):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.channel_id = channel_id
        self.bot = bot
    
    async def update_activity(self):
        try:
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE game_channels SET last_activity = NOW() WHERE channel_id = $1",
                    self.channel_id
                )
        except Exception as e:
            logger.error(f"❌ Failed to update activity: {e}", exc_info=True)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ هذه الجلسة مخصصة لشخص آخر!", ephemeral=True)
            return False
        return True
    
    @discord.ui.button(label="🎲 رمي النرد", style=discord.ButtonStyle.primary, custom_id="solo_dice_roll_fixed")
    async def dice_roll(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.update_activity()
        
        result = random.randint(1, 6)
        outcome_emoji = ["⚪", "⚫", "🔴", "🟡", "🟢", "🔵"][result - 1]
        
        embed = discord.Embed(
            title="🎲 نتيجة رمي النرد الفردي",
            description=f"{outcome_emoji} لقد حصلت على الرقم: **{result}**!",
            color=0x00D9FF
        )
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="🎰 آلة الحظ Slots", style=discord.ButtonStyle.primary, custom_id="solo_slots_fixed")
    async def slots(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.update_activity()
        
        symbols = ["🍒", "🍋", "🍊", "🍇", "💎", "👑", "🎯", "⭐"]
        spin1, spin2, spin3 = random.choice(symbols), random.choice(symbols), random.choice(symbols)
        is_winner = (spin1 == spin2 == spin3)
        
        embed = discord.Embed(
            title="🎰 آلة الحظ التفاعلية",
            description=f"```\n   [ {spin1} | {spin2} | {spin3} ]\n```",
            color=0xFF1493
        )
        if is_winner:
            embed.add_field(name="🎉 الجائزة الكبرى!", value="تهانينا! تطابقت جميع الرموز بنجاح!", inline=False)
        else:
            embed.add_field(name="🎲 النتيجة", value="لم يحالفك الحظ، حاول مرة أخرى للاستمرار!", inline=False)
        await interaction.followup.send(embed=embed)

    @discord.ui.button(label="✂️ حجر ورقة مقص", style=discord.ButtonStyle.primary, custom_id="solo_rps_fixed")
    async def rock_paper_scissors(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.update_activity()
        
        bot_choice = random.choice(["Rock", "Paper", "Scissors"])
        view = RPSChoiceView(bot_choice, self.user_id)
        embed = discord.Embed(title="✂️ لعبة حجر ورقة مقص ضد البوت", description="اختر حركتك القادمة بذكاء باستخدام الأزرار أدناه:", color=0x00D9FF)
        await interaction.followup.send(embed=embed, view=view)

    @discord.ui.button(label="🧠 تحدي الأسئلة العامة", style=discord.ButtonStyle.success, custom_id="solo_trivia_fixed")
    async def trivia(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.update_activity()
        
        trivia_questions = [
            {"question": "ما هي عاصمة دولة فرنسا؟", "correct": "باريس", "options": ["باريس", "ليون", "مارسيليا"]},
            {"question": "كم ناتج عملية 5 × 5؟", "correct": "25", "options": ["20", "25", "30"]},
            {"question": "ما هو أكبر كوكب في المجموعة الشمسية؟", "correct": "المشتري", "options": ["المريخ", "المشتري", "زحل"]}
        ]
        q = random.choice(trivia_questions)
        options = q["options"].copy()
        random.shuffle(options)
        
        view = TriviaView(q["correct"], options, self.user_id)
        embed = discord.Embed(title="🧠 تحدي الذكاء والأسئلة السريعة", description=f"**سؤال:** {q['question']}", color=0x00D9FF)
        await interaction.followup.send(embed=embed, view=view)

class SoloManager(commands.Cog):
    """إدارة قنوات الـ Solo Arcade والتحكم بالحذف التلقائي الفوري فور خروج اللاعب"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """ميزة الحذف الفوري: إذا غادر العضو أي قناة صوتية مرتبطة بغرفة ألعاب السولو، يتم تدميرها"""
        if before.channel and before.channel != after.channel:
            async with self.bot.db_pool.acquire() as conn:
                row = await conn.fetchrow("SELECT channel_id FROM game_channels WHERE host_id = $1 AND lobby_type = 'solo'", member.id)
                if row and before.channel.id == row['channel_id']:
                    # حذف قناة الصوت النصية التابعة فور مغادرة العضو تماماً لقناته الصوتية الخاصة باللعب
                    try:
                        channel = member.guild.get_channel(row['channel_id'])
                        if channel:
                            await channel.delete(reason="مغادرة اللاعب التلقائية لجلسة السولو الخاصة به")
                        await conn.execute("DELETE FROM game_channels WHERE channel_id = $1", row['channel_id'])
                        logger.info(f"🗑️ تم حذف قناة السولو {row['channel_id']} بنجاح نظراً لمغادرة اللاعب")
                    except Exception as e:
                        logger.error(f"Error auto-deleting solo channel: {e}")

async def setup(bot):
    await bot.add_cog(SoloManager(bot))
