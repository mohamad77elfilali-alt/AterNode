import discord
from discord.ext import commands
import os
import asyncio
import logging
from dotenv import load_dotenv
from utils.database import DatabaseManager  # أو من المكان الذي وضعت فيه الملف
# إعداد الـ Logging الاحترافي لمراقبة السيرفر ومعرفة أي حركة بدقة في Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("CentralCore")

load_dotenv()

class NextGenGamesBot(commands.Bot):
    def __init__(self):
        # تفعيل الخصائص الأساسية التي يحتاجها بوت الألعاب المتطور
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="g!", 
            intents=intents,
            chunk_guilds_at_startup=False # تحسين أداء الإقلاع وتقليل استهلاك الرام
        )

    async def setup_hook(self):
        """خطاف الإعداد المركزي - يتم شحن الملفات والأزرار هنا قبل الاتصال بالديسكورد"""
        logger.info("⚡ [Core] جاري بدء تشغيل المنظومة الذكية...")
        
        # 1. تحميل الـ Cogs ديناميكياً (قم بإنشاء المجلدات والملفات لتجنب أخطاء التحميل)
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
                logger.warning(f"⚠️ الملف {cog} غير موجود حالياً، سيتم تخطيه.")
            except Exception as e:
                logger.error(f"❌ فشل شحن الحزمة {cog} بسبب: {e}")

        # 2. مزامنة الأوامر بشكل ذكي وخلفي (Background Task) لكي لا نعطل إقلاع الـ Gateway
        self.loop.create_task(self.sync_slash_commands())

    async def sync_slash_commands(self):
        """مزامنة الأوامر بشكل منفصل لضمان عدم حدوث Timeout للبوت"""
        await self.wait_until_ready()
        try:
            logger.info("🔄 [Core] جاري مزامنة أوامر السلاش عالمياً مع ديسكورد...")
            synced = await self.tree.sync()
            logger.info(f"✨ تم مزامنة {len(synced)} أمر سلاش بنجاح وجاهزة للاستخدام!")
        except discord.HTTPException as e:
            logger.error(f"❌ فشل الاتصال بخوادم ديسكورد للمزامنة: {e}")

    async def on_ready(self):
        logger.info("=" * 60)
        logger.info(f"🕹️  NextGenGamesBot أصبح ONLINE الآن!")
        logger.info(f"👤 الاسم البرمجي: {self.user.name} | ID: {self.user.id}")
        logger.info("=" * 60)
        
        # تعيين الحالة الفخمة للبوت
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing, 
                name="🎮 الألعاب الذكية | /play"
            ),
            status=discord.Status.online
        )

# سحب التوكن بأمان من البيئة السحابية
TOKEN = os.getenv("GAMES_BOT_TOKEN") or os.getenv("BOT_TOKEN")

async def main():
    if not TOKEN:
        logger.critical("🛑 [Fatal] لم يتم العثور على التوكن البيئي! تحقق من المتغيرات في Railway.")
        return

    bot = NextGenGamesBot()
    
    # استخدام سياق الإغلاق الآمن لمنع تعليق العمليات في الخلفية
    try:
        await bot.start(TOKEN)
    except discord.LoginFailure:
        logger.critical("🛑 [Fatal] التوكن المستخدم غير صحيح أو منتهي الصلاحية!")
    except KeyboardInterrupt:
        logger.info("🔒 [Core] تم إغلاق البوت بأمان عبر المسؤول.")
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
