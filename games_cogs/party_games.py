import discord
from discord import app_commands
from discord.ext import commands
from games_config import GamesConfig
import asyncio
import random
import time

# ==========================================
# 🔘 واجهة أزرار نظام التسجيل (Registration View)
# ==========================================
class GameRegistrationView(discord.ui.View):
    def __init__(self, entry_fee: int):
        super().__init__(timeout=30.0) # مهلة التسجيل 30 ثانية
        self.entry_fee = entry_fee
        self.registered_players = []

    @discord.ui.button(label="انضمام للعبة | Join", style=discord.ButtonStyle.blurple, emoji="🎮")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.registered_players:
            await interaction.response.send_message("❌ أنت مسجل بالفعل في هذه اللعبة!", ephemeral=True)
            return

        # فحص رصيد اللاعب من قاعدة البيانات المشتركة
        bal = await interaction.client.db.fetchrow(
            "SELECT wallet FROM economy WHERE guild_id = $1 AND user_id = $2",
            interaction.guild_id, interaction.user.id
        )
        user_wallet = bal['wallet'] if bal else 0

        if user_wallet < self.entry_fee:
            await interaction.response.send_message(f"❌ لا تملك رصيداً كافياً لدخول اللعبة! (رسوم الدخول: {self.entry_fee} عملة)", ephemeral=True)
            return

        # خصم رسوم الدخول وضخها في الحساب المشترك للعبة
        await interaction.client.db.execute(
            "UPDATE economy SET wallet = wallet - $1 WHERE guild_id = $2 AND user_id = $3",
            self.entry_fee, interaction.guild_id, interaction.user.id
        )

        self.registered_players.append(interaction.user.id)
        await interaction.response.send_message(f"✅ تم تسجيلك بنجاح! تم خصم {self.entry_fee} من محفظتك.", ephemeral=True)


# ==========================================
# 🔘 واجهة لعبة ردة الفعل السريعة (Reaction Gate View)
# ==========================================
class ReactionGateView(discord.ui.View):
    def __init__(self, allowed_players: list, prize_pool: int):
        super().__init__(timeout=15.0)
        self.allowed_players = allowed_players
        self.prize_pool = prize_pool
        self.winner = None

    @discord.ui.button(label="💥 احجز هنا وتأهل! 💥", style=discord.ButtonStyle.danger, custom_id="click_fast")
    async def click_fast(self, interaction: discord.Interaction, button: discord.ui.Button):
        # منع أي لاعب خارج قائمة التسجيل من التخريب والضغط
        if interaction.user.id not in self.allowed_players:
            await interaction.response.send_message("❌ لم تقم بالتسجيل في هذه اللعبة خلال الـ 30 ثانية الأولى!", ephemeral=True)
            return

        # آلية قفل الزر ومنع أي مستخدم آخر من الضغط عليه بعد حكزه
        self.winner = interaction.user
        button.disabled = True
        button.style = discord.ButtonStyle.success
        button.label = f"🔒 تم حجز المقعد بواسطة {interaction.user.name}!"
        self.stop() # إنهاء اللعبة فوراً بفوز الأسرع

        # تسليم الجائزة بالكامل للفائز في قاعدة البيانات
        await interaction.client.db.execute(
            "UPDATE economy SET wallet = wallet + $1 WHERE guild_id = $2 AND user_id = $3",
            self.prize_pool, interaction.guild_id, interaction.user.id
        )

        await interaction.response.edit_message(view=self)
        
        embed = discord.Embed(
            title="🏆 فائز سريع وصاعق!",
            description=f"اللاعب {interaction.user.mention} كان الأسرع وضغط على الزر قبل الجميع وتأهل للمرحلة التالية وفاز بـ **{self.prize_pool}** عملة! 💰",
            color=GamesConfig.COLOR_GAMES
        )
        await interaction.channel.send(embed=embed)


# ==========================================
# 📦 الوحدة البرمجية الكبرى للألعاب الجماعية
# ==========================================
class PartyGames(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 1. لعبة ردة الفعل السريعة والأزرار المحجوزة
    @app_commands.command(name="game-reaction", description="⏱️ لعبة ردة الفعل السريعة - من يحجز الزر أولاً يفوز بالرهان بالكامل!")
    async def game_reaction(self, interaction: discord.Interaction, entry_fee: int = 100):
        await interaction.response.defer()

        # إطلاق مرحلة التسجيل (30 ثانية)
        reg_embed = discord.Embed(
            title="🎮 بدء التسجيل | لعبة ردة الفعل السريعة",
            description=f"قم بالضغط على الزر أدناه للانضمام للعبة!\n\n"
                        f"💵 رسوم الدخول: **{entry_fee}** عملة.\n"
                        f"⏳ تنتهي مهلة التسجيل ويغلق الباب بعد **30 ثانية** تلقائياً.",
            color=GamesConfig.COLOR_GAMES
        )
        
        reg_view = GameRegistrationView(entry_fee)
        msg = await interaction.followup.send(embed=reg_embed, view=reg_view)

        # الانتظار 30 ثانية لانتهاء مرحلة التسجيل تماماً
        await asyncio.sleep(30)
        
        # تعطيل زر التسجيل رسمياً
        reg_view.clear_items()
        await msg.edit(content="⚠️ **انتهى وقت التسجيل! لا يمكن لأي عضو آخر الانضمام الآن.**", view=reg_view)

        if len(reg_view.registered_players) < 2:
            # إعادة الأموال للاعب الوحيد إن لم يكتمل العدد الكافي للمنافسة
            if len(reg_view.registered_players) == 1:
                await self.bot.db.execute(
                    "UPDATE economy SET wallet = wallet + $1 WHERE guild_id = $2 AND user_id = $3",
                    entry_fee, interaction.guild_id, reg_view.registered_players[0]
                )
            await interaction.channel.send("❌ تم إلغاء اللعبة لعدم وجود لاعبين كافيين لتفعيل المنافسة الجماعية (مطلوب لاعبين على الأقل).")
            return

        # حساب مجموع الجائزة الكبرى
        total_prize = entry_fee * len(reg_view.registered_players)

        ready_msg = await interaction.channel.send("🚦 استعدوا... سيظهر الزر المشتعل فجأة خلال لحظات عشوائية!")
        # توليد وقت ظهور عشوائي بين 3 إلى 7 ثوانٍ لزيادة الحماس
        await asyncio.sleep(random.randint(3, 7))
        await ready_msg.delete()

        # إرسال زر ردة الفعل السريع
        game_view = ReactionGateView(reg_view.registered_players, total_prize)
        game_embed = discord.Embed(
            title="🚨 اضغط الآن! 🔥",
            description="أسرع شخص يضغط على الزر أدناه سيحجزه فوراً ويتأهل ويفوز بكل الأموال المجموعة!",
            color=discord.Color.red()
        )
        
        await interaction.channel.send(embed=game_embed, view=game_view)


    # 2. لعبة أسرع كتابة للجمل المشفرة والمبعثرة
    @app_commands.command(name="game-typing", description="📝 لعبة أسرع كتابة - أسرع عضو يفك شفرة الكلمة ويكتبها يفوز")
    async def game_typing(self, interaction: discord.Interaction, entry_fee: int = 100):
        await interaction.response.defer()

        reg_view = GameRegistrationView(entry_fee)
        reg_embed = discord.Embed(
            title="📝 بدء التسجيل | لعبة أسرع كتابة",
            description=f"اضغط على الزر أدناه لحجز مقعدك.\n💵 الرسوم: **{entry_fee}** عملة.\n⏳ يغلق التسجيل بعد **30 ثانية**.",
            color=GamesConfig.COLOR_GAMES
        )
        msg = await interaction.followup.send(embed=reg_embed, view=reg_view)

        await asyncio.sleep(30)
        reg_view.clear_items()
        await msg.edit(content="⚠️ **انتهى وقت التسجيل! لا يمكن لأي عضو آخر الانضمام الآن.**", view=reg_view)

        if len(reg_view.registered_players) < 2:
            if len(reg_view.registered_players) == 1:
                await self.bot.db.execute("UPDATE economy SET wallet = wallet + $1 WHERE guild_id = $2 AND user_id = $3", entry_fee, interaction.guild_id, reg_view.registered_players[0])
            await interaction.channel.send("❌ تم إلغاء اللعبة لعدم وجود لاعبين كافيين.")
            return

        total_prize = entry_fee * len(reg_view.registered_players)

        # بنك الكلمات البرمجية والتكنولوجية الفخمة
        words = ["ديسكورد", "مطورين", "قاعدة بيانات", "برمجة", "سيرفر الألعاب", "بلوجر التفاعلي", "ذكاء اصطناعي"]
        chosen_word = random.choice(words)
        
        # بعثرة الكلمة لتصبح مشفرة وعلى اللاعبين تخمينها وكتابتها بسرعة
        scrambled_word = "".join(random.sample(chosen_word, len(chosen_word)))

        await interaction.channel.send(f"🔮 الجملة/الكلمة المبعثرة هي: **`{scrambled_word}`**\nاكتب الكلمة الصحيحة فوراً! (متاح فقط للاعبين المسجلين)")

        def check(m):
            return m.channel == interaction.channel and m.author.id in reg_view.registered_players and m.content == chosen_word

        try:
            # انتظار أول إجابة صحيحة خلال 20 ثانية فقط
            winner_msg = await self.bot.wait_for('message', check=check, timeout=20.0)
            
            # تسليم الأموال
            await self.bot.db.execute("UPDATE economy SET wallet = wallet + $1 WHERE guild_id = $2 AND user_id = $3", total_prize, interaction.guild_id, winner_msg.author.id)
            
            win_embed = discord.Embed(
                title="🏆 فائز أسرع كاتب!",
                description=f"تهانينا {winner_msg.author.mention}! لقد عرفت الكلمة الصحيحة وهي (`{chosen_word}`) وفزت بـ **{total_prize}** عملة! 📝🔥",
                color=GamesConfig.COLOR_SUCCESS
            )
            await interaction.channel.send(embed=win_embed)
            
        except asyncio.TimeoutError:
            await interaction.channel.send(f"⏱️ انتهى الوقت ولم يكتب أحد الكلمة الصحيحة! الكلمة كانت: **`{chosen_word}`**")

async def setup(bot: commands.Bot):
    await bot.add_cog(PartyGames(bot))
