import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
from dotenv import load_dotenv
from utils.db import DatabaseManager

# شحن المتغيرات البيئية من Railway
load_dotenv()

# --- 1. واجهات الأزرار التفاعلية ونظام القوائم ---

class GameSelectionMenu(discord.ui.Select):
    """قائمة منسدلة لاختيار اللعبة المطلوبة"""
    def __init__(self, mode: str):
        self.mode = mode # إما 'solo' أو 'multiplayer'
        
        options = []
        if mode == 'solo':
            options = [
                discord.SelectOption(label="🎲 لعبة النرد السريع", value="dice", description="راهن بعملاتك ضد حظ البوت", emoji="🎲"),
                discord.SelectOption(label="🎰 آلة الحظ (Slots)", value="slots", description="تحدي الرموز المتطابقة والأرباح المضاعفة", emoji="🎰"),
                discord.SelectOption(label="🧠 مسابقة الأسئلة", value="trivia", description="اختبر معلوماتك العامة بمفردك", emoji="🧠")
            ]
        else:
            options = [
                discord.SelectOption(label="✂️ حجر ورقة مقص", value="rps", description="تحدي لاعب آخر في السيرفر", emoji="✂️"),
                discord.SelectOption(label="❌ لعبة إكس أو (Tic-Tac-Toe)", value="tic_tac_toe", description="مواجهة استراتيجية مباشرة بين شخصين", emoji="⭕"),
                discord.SelectOption(label="🗣️ صراحة أم تحدي", value="truth_or_dare", description="فعالية تجمعات جماعية ممتعة", emoji="🔥")
            ]
            
        super().__init__(placeholder="🎯 اختر اللعبة التي تريد بدءها الآن...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        game_selected = self.values[0]
        guild = interaction.guild

        if self.mode == 'solo':
            # --- مسار الشخص الفردي: إنشاء قناة خاصة ومخفية ---
            await interaction.followup.send("⏳ جاري تهيئة غرفتك الخاصة وبدء اللعبة...", ephemeral=True)
            
            # إعداد صلاحيات القناة (رؤية كاملة للاعب والبوت، مخفية عن البقية)
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
            }
            
            # إنشاء القناة المؤقتة
            channel_name = f"🕹️-{interaction.user.display_name}"
            try:
                temp_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites, topic=f"قناة ألعاب فردية مخصصة لـ {interaction.user.name}. تُحذف تلقائياً عند الانتهاء.")
                
                # إرسال رسالة الترحيب واللعبة داخل القناة الجديدة
                embed = discord.Embed(
                    title=f"🎮 غرفتك جاهزة يا {interaction.user.display_name}!",
                    description=f"تم تشغيل لعبة `{game_selected}` بنجاح.\n\n💡 *ملاحظة: هذه القناة مؤقتة وخاصة بك وحدك، سيتم تنظيفها وحذفها فور إغلاق اللعبة.*",
                    color=discord.Color.from_rgb(0, 240, 255) # لون نيون سيبربانك
                )
                await temp_channel.send(content=interaction.user.mention, embed=embed)
                
                # هنا نقوم باستدعاء اللعبة المحددة داخلياً من الـ Cogs وتشغيلها في هذه القناة
                bot = interaction.client
                cog_name = "GamesCog" # الاسم البرمجي لكلاس الألعاب لديك
                # ملاحظة مبرمج: سنمرر temp_channel للعبة لتبدأ بالداخل مباشرة
                
            except Exception as e:
                await interaction.followup.send(f"❌ حدث خطأ أثناء إنشاء قناتك الخاصة: {e}", ephemeral=True)

        else:
            # --- مسار اللعب الجماعي: اللعب في قنوات الألعاب العامة المفتوحة للجميع ---
            await interaction.followup.send(f"🎉 قمت باختيار اللعبة الجماعية: `{game_selected}`! سيتم فتح التحدي للجميع الآن في القناة المخصصة.", ephemeral=True)
            # هنا يتم توجيه وإطلاق كود اللعبة الجماعية مباشرة ليراها الجميع ويشاركون بالأزرار


class GameControlView(discord.ui.View):
    """لوحة التحكم الثابتة التي تحتوي على أزرار اللعب الجماعي والفردي"""
    def __init__(self):
        super().__init__(timeout=None) # timeout=None يجعل الأزرار دائمة ولا تموت أبداً

    @discord.ui.button(label="👥 بدء تحدي جماعي", style=discord.ButtonStyle.success, custom_id="persistent:multiplayer")
    async def multiplayer_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        # فتح قائمة خيارات الألعاب الجماعية
        view = discord.ui.View(timeout=60)
        view.add_item(GameSelectionMenu(mode="multiplayer"))
        await interaction.response.send_message("👥 اختر اللعبة الجماعية ليتنافس فيها الجميع بالشات العام:", view=view, ephemeral=True)

    @discord.ui.button(label="👤 لعب فردي (سولو)", style=discord.ButtonStyle.primary, custom_id="persistent:solo")
    async def solo_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        # فتح قائمة خيارات الألعاب الفردية
        view = discord.ui.View(timeout=60)
        view.add_item(GameSelectionMenu(mode="solo"))
        await interaction.response.send_message("👤 اختر لعبتك المفضلة لبدء الجولة في غرفتك الخاصة:", view=view, ephemeral=True)

# --- 2. الهيكل الرئيسي للبوت وإدارته ---

class UltraGamesBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="g!", intents=intents)
        self.db = DatabaseManager()

    async def setup_hook(self):
        # 1. ربط قاعدة البيانات
        print("⚡ [System] جاري تشغيل حوض اتصالات قاعدة البيانات...")
        await self.db.initialize()

        # register للـ View الدائم لكي يتعرف عليه ديسكورد فوراً عند إعادة التشغيل
        self.add_view(GameControlView())

        # 2. تحميل ملفات الألعاب من مجلد games_cogs
        cogs_to_load = [
            "games_cogs.board_games",
            "games_cogs.casino",
            "games_cogs.party_games"
        ]

        print("🎮 [System] جاري تحميل ملفات الألعاب وتجهيز الأوامر السحابية...")
        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                print(f"✅ تم تفعيل ملف: {cog.split('.')[-1]}")
            except Exception as e:
                print(f"❌ فشل تحميل ملف {cog}: {e}")
        
        # 3. المزامنة العالمية لأوامر السلاش
        try:
            synced = await self.tree.sync()
            print(f"🔄 تم مزامنة {len(synced)} من أوامر السلاش بنجاح.")
        except Exception as e:
            print(f"❌ فشل مزامنة الأوامر: {e}")

    async def on_ready(self):
        print("=" * 50)
        print(f'🕹️ {self.user.name} (نظام التحكم المركزي للألعاب جاهز بالكامل!)')
        print("=" * 50)
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.playing, name="🎮 /setup_games")
        )

bot = UltraGamesBot()

# --- 3. أمر إعداد وتجهيز قناة الألعاب الرئيسية ---

@bot.tree.command(name="setup_games", description="إعداد وتخصيعة قناة التحكم الرئيسية في منظومة الألعاب والأزرار الدائمة")
@app_commands.checks.has_permissions(administrator=True) # للمسؤولين فقط لتفادي التخريب
async def setup_games(interaction: discord.Interaction, channel: discord.TextChannel = None):
    await interaction.response.defer()
    
    # إذا لم يحدد قناة، نعتمد القناة الحالية التي كتب فيها الأمر
    target_channel = channel or interaction.channel
    
    # بناء رسالة التحكم الفخمة بنمط النيون
    embed = discord.Embed(
        title="🎮 مركز ألعاب ومنافسات السيرفر ➔ CONTROL PANEL",
        description=(
            "أهلاً بك في المنظومة التفاعلية للألعاب! من هنا يمكنك خوض التحديات الكبرى وكسب العملات والمنافسة على صدارة الترتيب.\n\n"
            "**⚙️ خيارات اللعب المتاحة:**\n"
            "• **`👥 بدء تحدي جماعي`**: لفتح تحدي علني يشارك فيه جميع أعضاء السيرفر في القنوات العامة المفتوحة.\n"
            "• **`👤 لعب فردي (سولو)`**: لفتح غرفة نصية مؤقتة خاصة ومخفية بك تماماً، تلعب فيها وحدك لحفظ رصيدك ونقاطك ثم تُحذف تلقائياً.\n\n"
            "👇 *اضغط على الزر أدناه لتحديد واختيار نوع اللعبة والبدء فوراً!*"
        ),
        color=discord.Color.from_rgb(180, 0, 255) # نيون بنفسجي فخم
    )
    embed.set_image(url="https://i.imgur.com/x9n7SjN.gif") # يمكنك استبداله برابط خلفية متحركة تناسب ذوقك
    embed.set_footer(text="🌟 نظام إداري ذكي - تم التأمين والحفظ بقاعدة البيانات")
    
    # إرسال لوحة الأزرار في القناة المحددة
    panel_message = await target_channel.send(embed=embed, view=GameControlView())
    
    # حفظ البيانات في PostgreSQL لكي لا ينساها البوت أبداً عند الريستارت
    await bot.db.set_game_channel(interaction.guild_id, target_channel.id, panel_message.id)
    
    await interaction.followup.send(f"✅ تم تهيئة وإطلاق لوحة التحكم بنجاح وحفظها في قاعدة البيانات داخل قناة: {target_channel.mention}!")

# تتبع وقراءة التوكن من لوحة تحكم Railway البيئية
TOKEN = os.getenv("GAMES_BOT_TOKEN") or os.getenv("BOT_TOKEN")

if __name__ == "__main__":
    if not TOKEN:
        print("🛑 [Fatal Error] لم يتم العثور على التوكن! تأكد من إضافة متغير GAMES_BOT_TOKEN في Railway Variables.")
    else:
        try:
            asyncio.run(bot.start(TOKEN))
        except KeyboardInterrupt:
            print("🔒 [System] تم إغلاق السيرفر بأمان.")
