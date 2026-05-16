import discord
from discord import app_commands
from discord.ext import commands
from games_config import GamesConfig
import asyncio

# ==========================================
# 🔘 واجهة أزرار لعبة XO التفاعلية
# ==========================================
class TicTacToeView(discord.ui.View):
    def __init__(self, p1: discord.Member, p2: discord.Member, bet: int):
        super().__init__(timeout=60.0)
        self.p1 = p1 # اللاعب الأول (X)
        self.p2 = p2 # اللاعب الثاني (O)
        self.bet = bet
        self.current_turn = p1 # اللاعب صاحب الدور الحالي
        
        # تمثيل رقعة اللعب (0 تعني فارغ، 1 تعني X، 2 تعني O)
        self.board = [0, 0, 0,
                      0, 0, 0,
                      0, 0, 0]

        # إنشاء الأزرار التسعة تلقائياً وإضافتها للواجهة
        for i in range(9):
            # حساب السطر والعمود لتوزيع الأزرار بشكل شبكة 3x3 متناسقة
            row = i // 3
            button = discord.ui.Button(label=" ", style=discord.ButtonStyle.secondary, row=row, custom_id=str(i))
            button.callback = self.button_callback
            self.add_item(button)

    async def button_callback(self, interaction: discord.Interaction):
        # 1. التحقق من أن الشخص الذي ضغط هو صاحب الدور الحالي
        if interaction.user.id != self.current_turn.id:
            await interaction.response.send_message("❌ ليس دورك الآن! انتظر خصمك ليلعب.", ephemeral=True)
            return

        await interaction.response.defer()
        
        button_id = int(interaction.data['custom_id'])
        button = self.children[button_id]

        # 2. تسجيل الحركة وتحديث شكل ونمط الزر حسب اللاعب
        if self.current_turn == self.p1:
            self.board[button_id] = 1
            button.label = "❌"
            button.style = discord.ButtonStyle.danger # اللون الأحمر لـ X
            button.disabled = True
            next_turn = self.p2
        else:
            self.board[button_id] = 2
            button.label = "⭕"
            button.style = discord.ButtonStyle.primary # اللون الأزرق لـ O
            button.disabled = True
            next_turn = self.p1

        # 3. فحص هل حدث فوز أو تعادل بعد هذه الحركة
        winner_status = self.check_winner()

        if winner_status == 1: # فوز اللاعب الأول X
            await self.end_game(interaction, self.p1, f"🏆 فاز اللاعب {self.p1.mention} بالتحدي وحصد الجائزة المالية بقيمة **{self.bet * 2}** عملة! 🔥")
            return
        elif winner_status == 2: # فوز اللاعب الثاني O
            await self.end_game(interaction, self.p2, f"🏆 فاز اللاعب {self.p2.mention} بالتحدي وحصد الجائزة المالية بقيمة **{self.bet * 2}** عملة! 🔥")
            return
        elif 0 not in self.board: # تعادل (الرقعة امتلأت بالكامل دون فائز)
            await self.end_game(interaction, None, "🤝 **النتيجة: تعادل!** تم إعادة أموال الرهان لكلا اللاعبين بالتساوي.")
            return

        # 4. نقل الدور للاعب التالي وتحديث الرسالة
        self.current_turn = next_turn
        embed = discord.Embed(
            title="❌ ضد ⭕ لعبة إكس أو اللوحية",
            description=f"المواجهة مشتعلة بين {self.p1.mention} و {self.p2.mention}!\n\n"
                        f"🎯 الدور الحالي الآن لـ: {self.current_turn.mention}",
            color=GamesConfig.COLOR_GAMES
        )
        await interaction.edit_original_response(embed=embed, view=self)

    def check_winner(self) -> int:
        """دالة لفحص شروط الفوز الثمانية في اللعبة اللوحية"""
        winning_combinations = [
            # صفوف أفقية
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            # أعمدة عمودية
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            # أقطار مائلة
            [0, 4, 8], [2, 4, 6]
        ]
        for combo in winning_combinations:
            if self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != 0:
                return self.board[combo[0]] # يعود بـ 1 لـ X أو 2 لـ O
        return 0

    async def end_game(self, interaction: discord.Interaction, winner: discord.Member, result_message: str):
        """دالة إنهاء اللعبة، تعطيل كل الأزرار، وتوزيع الجوائز المالية من قاعدة البيانات"""
        self.stop()
        
        # تعطيل جميع الأزرار المتبقية لضمان جمالية الـ UX بعد الانتهاء
        for item in self.children:
            item.disabled = True

        if winner:
            # إضافة ضعف الرهان الإجمالي للفائز
            prize = self.bet * 2
            await interaction.client.db.execute(
                "UPDATE economy SET wallet = wallet + $1 WHERE guild_id = $2 AND user_id = $3",
                prize, interaction.guild_id, winner.id
            )
            color = GamesConfig.COLOR_SUCCESS
        else:
            # في حالة التعادل، نعيد لكل لاعب رهانه الأصلي
            await interaction.client.db.execute(
                "UPDATE economy SET wallet = wallet + $1 WHERE guild_id = $2 AND user_id = $3",
                self.bet, interaction.guild_id, self.p1.id
            )
            await interaction.client.db.execute(
                "UPDATE economy SET wallet = wallet + $1 WHERE guild_id = $2 AND user_id = $3",
                self.bet, interaction.guild_id, self.p2.id
            )
            color = GamesConfig.COLOR_GAMES

        embed = discord.Embed(
            title="🏁 انتهت المباراة!",
            description=result_message,
            color=color
        )
        await interaction.edit_original_response(embed=embed, view=self)


# ==========================================
# 📦 الوحدة البرمجية للألعاب اللوحية والكلاسيكية
# ==========================================
class BoardGames(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="game-xo", description="❌⭕ تحدى عضواً آخر في سيرفرك بلعبة إكس أو بمبالغ مالية رهان!")
    async def game_xo(self, interaction: discord.Interaction, opponent: discord.Member, bet: int):
        # منع التحدي مع البوتات أو مع النفس
        if opponent.bot or opponent.id == interaction.user.id:
            await interaction.response.send_message("❌ لا يمكنك تحدي البوتات أو تحدي نفسك!", ephemeral=True)
            return

        if bet <= 0:
            await interaction.response.send_message("❌ يجب أن يكون مبلغ الرهان أكبر من صفر!", ephemeral=True)
            return

        # 1. التحقق من رصيد المتحدي (اللاعب الأول)
        bal1 = await self.bot.db.fetchrow("SELECT wallet FROM economy WHERE guild_id = $1 AND user_id = $2", interaction.guild_id, interaction.user.id)
        w1 = bal1['wallet'] if bal1 else 0
        if w1 < bet:
            await interaction.response.send_message(f"❌ لا تملك رصيداً كافياً في محفظتك لهذا الرهان! رصيدك: {w1}", ephemeral=True)
            return

        # 2. التحقق من رصيد الخصم (اللاعب الثاني)
        bal2 = await self.bot.db.fetchrow("SELECT wallet FROM economy WHERE guild_id = $1 AND user_id = $2", interaction.guild_id, opponent.id)
        w2 = bal2['wallet'] if bal2 else 0
        if w2 < bet:
            await interaction.response.send_message(f"❌ الخصم {opponent.mention} لا يملك رصيداً كافياً لتغطية هذا الرهان في محفظته!", ephemeral=True)
            return

        # 3. خصم مبلغ الرهان من الطرفين لبدء المباراة وحجزه في صندوق اللعبة
        await self.bot.db.execute("UPDATE economy SET wallet = wallet - $1 WHERE guild_id = $2 AND user_id = $3", bet, interaction.guild_id, interaction.user.id)
        await self.bot.db.execute("UPDATE economy SET wallet = wallet - $1 WHERE guild_id = $2 AND user_id = $3", bet, interaction.guild_id, opponent.id)

        # 4. إطلاق لوحة اللعبة المشتعلة بالأزرار والبدء باللاعب الأول
        embed = discord.Embed(
            title="❌ ضد ⭕ مباراة إكس أو اللوحية",
            description=f"المواجهة مشتعلة بين {interaction.user.mention} (❌) ضد {opponent.mention} (⭕)!\n\n"
                        f"💰 إجمالي الجائزة المرصودة في الصندوق: **{bet * 2}** عملة.\n\n"
                        f"🎯 ضربة البداية والدور الحالي لـ: {interaction.user.mention}",
            color=GamesConfig.COLOR_GAMES
        )

        view = TicTacToeView(interaction.user, opponent, bet)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(BoardGames(bot))
