import discord
from discord.ext import commands
import os
from games_config import GamesConfig
from utils.db import DatabaseManager # سنعيد استخدام مدير قاعدة البيانات الذكي الذي كتبناه سابقاً
import asyncio

class UltraGamesBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        # بادئة الأوامر العادية وبوت الألعاب يدعم أوامر السلاش أيضاً
        super().__init__(command_prefix="g!", intents=intents)
        self.db = DatabaseManager()

    async def setup_hook(self):
        # 1. الاتصال بقاعدة البيانات المشتركة لجلب أرصدة اللاعبين
        await self.db.initialize()

        # 2. تحميل ملفات الألعاب ديناميكياً من مجلد خاص بها باسم games_cogs
        if os.path.exists('./games_cogs'):
            for filename in os.listdir('./games_cogs'):
                if filename.endswith('.py'):
                    await self.load_extension(f'games_cogs.{filename[:-3]}')
                    print(f'🎮 تم تحميل لعبة: {filename[:-3]}')
        
        # 3. مزامنة أوامر السلاش الخاصة بالألعاب عالمياً
        await self.tree.sync()
        print("🔄 تم مزامنة أوامر ألعاب السلاش بنجاح.")

    async def on_ready(self):
        print(f'🕹️ {self.user.name} (بوت الألعاب) جاهز ومستعد للتحدي!')
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.playing, name="with Server Economy!")
        )

bot = UltraGamesBot()

if __name__ == "__main__":
    asyncio.run(bot.start(GamesConfig.TOKEN))
