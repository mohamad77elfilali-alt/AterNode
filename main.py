import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
import logging
import asyncpg
from typing import Optional
from dotenv import load_dotenv

# تشغيل نظام الـ Logging لمراقبة السيرفر ومعرفة أي حركة بدقة في Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("CentralCore")

load_dotenv()

# --- 1. نظام إدارة قاعدة البيانات المطور والمقاوم للانهيار ---

class DatabaseManager:
    def __init__(self):
        self.db_url: Optional[str] = os.getenv("DATABASE_URL")
        self.pool: Optional[asyncpg.Pool] = None
        self._lock = asyncio.Lock() # قفل أمان لمنع التداخل أثناء إعادة الاتصال

    async def initialize(self) -> bool:
        """إنشاء حوض الاتصالات والتأكد من سلامة الجلسة والجداول"""
        if not self.db_url:
            logger.critical("🛑 [Database] لم يتم العثور على المتغير البيئي DATABASE_URL!")
            return False

        async with self._lock:
            if self.pool is not None:
                return True

            try:
                logger.info("⚡ [Database] جاري إنشاء حوض اتصالات PostgreSQL جديد...")
                self.pool = await asyncpg.create_pool(
                    self.db_url,
                    min_size=2,       # الحد الأدنى للاتصالات الجاهزة دائماً
                    max_size=10,      # الحد الأقصى لتفادي استهلاك خوادم Railway
                    max_queries=1000, # إعادة تدوير الاتصال لمنع تسريب الذاكرة
                    timeout=30.0      # مهلة زمنية قصوى للاستجابة
                )
                
                # اختبار الحوض باستعلام سريع
                async with self.pool.acquire() as conn:
                    await conn.execute("SELECT 1;")
                
                logger.info("✅ [Database] تم الاتصال بقاعدة البيانات بنجاح وإنشاء الحوض المطور!")
                await self._create_tables()
                return True

            except Exception as e:
                logger.error(f"❌ [Database] فشل ذريع في الاتصال بقاعدة البيانات: {e}")
                self.pool = None
                return False

    async def _create_tables(self):
        """إنشاء جداول النظام الأساسية بنية نظيفة متوافقة مع الـ Cogs"""
        async with self.pool.acquire() as conn:
            # جدول قنوات الألعاب واللوحات الدائمة لضمان عدم ضياع الأزرار بعد الريستارت
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS game_channels (
                    guild_id BIGINT PRIMARY KEY,
                    channel_id BIGINT NOT NULL,
                    message_id BIGINT NOT NULL
                );
            """)
            
            # جدول اقتصاد الألعاب (العملات والنقاط) لحفظ رصيد اللاعبين
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users_economy (
                    user_id BIGINT PRIMARY KEY,
                    coins BIGINT DEFAULT 1000,
                    xp INT DEFAULT 0,
                    wins INT DEFAULT 0
                );
            """)
            logger.info("📦 [Database] تم التحقق من سلامة الجداول الهيكلية بنجاح.")

    async def ensure_connection(self) -> bool:
        """دالة حماية ذاتية تستدعيها الاستعلامات للتأكد من أن الحوض لم يمت"""
        if self.pool is None:
            logger.warning("⚠️ [Database] الحوض ميت! جاري محاولة إعادة البناء تلقائياً...")
            return await self.initialize()
        return True

    async def set_game_channel(self, guild_id: int, channel_id: int, message_id: int) -> bool:
        """حفظ أو تحديث قناة التحكم بالألعاب للأزرار الدائمة"""
        if not await self.ensure_connection():
            return False
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO game_channels (guild_id, channel_id, message_id)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (guild_id) 
                    DO UPDATE SET channel_id = EXCLUDED.channel_id, message_id = EXCLUDED.message_id;
                """, guild_id, channel_id, message_id)
                return True
        except Exception as e:
            logger.error(f"❌ [Database] خطأ أثناء حفظ قناة الألعاب: {e}")
            return False

# --- 2. واجهات الأزرار التفاعلية ونظام القوائم ---

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
            await interaction.followup.send("⏳ جاري تهيئة غرفتك الخاصة وبدء اللعبة...", ephemeral=True)
            
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
            }
            
            channel_name = f"🕹️-{interaction.user.display_name}"
            try:
                temp_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites, topic=f"قناة ألعاب فردية مخصصة لـ {interaction.user.name}. تُحذف تلقائياً عند الانتهاء.")
                
                embed = discord.Embed(
                    title=f"🎮 غرفتك جاهزة يا {interaction.user.display_name}!",
                    description=f"تم تشغيل لعبة `{game_selected}` بنجاح.\n\n💡 *ملاحظة: هذه القناة مؤقتة وخاصة بك وحدك، سيتم تنظيفها وحذفها فور إغلاق اللعبة.*",
                    color=discord.Color.from_rgb(0, 240, 255) # لون نيون سيبربانك
                )
                await temp_channel.send(content=interaction.user.mention, embed=embed)
                
            except Exception as e:
                await interaction.followup.send(f"❌ حدث خطأ أثناء إنشاء قناتك الخاصة: {e}", ephemeral=True)
        else:
            await interaction.followup.send(f"🎉 قمت باختيار اللعبة الجماعية: `{game_selected}`! سيتم فتح التحدي للجميع الآن في القناة المخصصة.", ephemeral=True)


class GameControlView(discord.ui.View):
    """لوحة التحكم الثابتة التي تحتوي على أزرار اللعب الجماعي والفردي"""
    def __init__(self):
        super().__init__(timeout=None) # تفعيل الحالة الدائمة للأزرار الأبديّة

    @discord.ui.button(label="👥 بدء تحدي جماعي", style=discord.ButtonStyle.success, custom_id="persistent:multiplayer")
    async def multiplayer_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = discord.ui.View(timeout=60)
        view.add_item(GameSelectionMenu(mode="multiplayer"))
        await interaction.response.send_message("👥 اختر اللعبة الجماعية ليتنافس فيها الجميع بالشات العام:", view=view, ephemeral=True)

    @discord.ui.button(label="👤 لعب فردي (سولو)", style=discord.ButtonStyle.primary, custom_id="persistent:solo")
    async def solo_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = discord.ui.View(timeout=60)
        view.add_item(GameSelectionMenu(mode="solo"))
        await interaction.response.send_message("👤 اختر لعبتك المفضلة لبدء الجولة في غرفتك الخاصة:", view=view, ephemeral=True)


# --- 3. الهيكل الرئيسي للبوت وإدارته المطور ---

class NextGenGamesBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="g!", 
            intents=intents,
            chunk_guilds_at_startup=False # تحسين أداء الإقلاع وتقليل استهلاك الرام
        )
        self.db = DatabaseManager() # ربط قاعدة البيانات مباشرة داخل كلاس البوت

    async def setup_hook(self):
        """خطاف الإعداد المركزي - يتم شحن قاعدة البيانات والملفات بشكل متسلسل آمن"""
        logger.info("⚡ [Core] جاري بدء تشغيل المنظومة الذكية...")
        
        # 1. شحن قاعدة البيانات أولاً والتأكد من نجاحها قبل المتابعة
        db_connected = await self.db.initialize()
        if not db_connected:
            logger.critical("🛑 [Core] فشل إقلاع البوت لعدم وجود اتصال مستقر بقاعدة البيانات!")
            return

        # 2. تسجيل واجهة الأزرار التفاعلية الدائمة
        self.add_view(GameControlView())

        # 3. تحميل حزم الألعاب ديناميكيًا من مجلد cogs
        cogs_to_load = [
            "cogs.solo_games",
            "cogs.multi_games",
            "cogs.economy"
        ]

        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                logger.info(f"✅ تم تحميل الحزمة بنجاح: {cog}")
            except commands.ExtensionNotFound:
                logger.warning(f"⚠️ الملف {cog} غير موجود حالياً، سيتم شحنه لاحقاً.")
            except Exception as e:
                logger.error(f"❌ فشل شحن الحزمة {cog} بسبب: {e}")
        
        # 4. تشغيل مزامنة أوامر السلاش في الخلفية لضمان عدم حدوث Gateway Timeout
        self.loop.create_task(self.sync_slash_commands())

    async def sync_slash_commands(self):
        """مزامنة الأوامر بشكل منفصل بعد اتصال البوت الكامل"""
        await self.wait_until_ready()
        try:
            logger.info("🔄 [Core] جاري مزامنة أوامر السلاش عالمياً مع ديسكورد...")
            synced = await self.tree.sync()
            logger.info(f"✨ تم مزامنة {len(synced)} أمر سلاش بنجاح وجاهزة للاستخدام!")
        except Exception as e:
            logger.error(f"❌ فشل مزامنة الأوامر: {e}")

    async def on_ready(self):
        logger.info("=" * 60)
        logger.info(f"🕹️  {self.user.name} أصبح ONLINE الآن وجاهز بالكامل!")
        logger.info("=" * 60)
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.playing, name="🎮 الألعاب الذكية | /setup_games"),
            status=discord.Status.online
        )

bot = NextGenGamesBot()

# --- 4. أمر إعداد وتجهيز قناة الألعاب الرئيسية ---

@bot.tree.command(name="setup_games", description="إعداد وتخصيص قناة التحكم الرئيسية في منظومة الألعاب والأزرار الدائمة")
@app_commands.checks.has_permissions(administrator=True)
async def setup_games(interaction: discord.Interaction, channel: discord.TextChannel = None):
    await interaction.response.defer()
    target_channel = channel or interaction.channel
    
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
    embed.set_image(url="https://i.imgur.com/x9n7SjN.gif")
    embed.set_footer(text="🌟 نظام إداري ذكي - تم التأمين والحفظ بقاعدة البيانات")
    
    panel_message = await target_channel.send(embed=embed, view=GameControlView())
    
    # حفظ الإعدادات في PostgreSQL مباشرة عبر كلاس الـ db المربوط
    await bot.db.set_game_channel(interaction.guild_id, target_channel.id, panel_message.id)
    await interaction.followup.send(f"✅ تم تهيئة وإطلاق لوحة التحكم بنجاح وحفظها داخل قناة: {target_channel.mention}!")

# تتبع وقراءة التوكن من لوحة تحكم Railway البيئية
TOKEN = os.getenv("GAMES_BOT_TOKEN") or os.getenv("BOT_TOKEN")

async def main():
    if not TOKEN:
        logger.critical("🛑 [Fatal] لم يتم العثور على التوكن البيئي! تحقق من المتغيرات في Railway.")
        return
    try:
        await bot.start(TOKEN)
    except Exception as e:
        logger.critical(f"🛑 [Fatal] فشل تشغيل البوت: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
