import asyncpg
import os
from dotenv import load_dotenv

# شحن متغيرات البيئة تلقائياً
load_dotenv()

class DatabaseManager:
    """مدير الاتصال بقاعدة البيانات PostgreSQL لبوت الألعاب"""
    def __init__(self):
        self.pool = None

    async def initialize(self):
        # جلب رابط قاعدة البيانات المحفوظ في متغيرات Railway البيئية
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ [Database] خطأ: لم يتم العثور على DATABASE_URL في الـ Environment Variables!")
            return False
        
        try:
            # إنشاء حوض اتصالات (Connection Pool) للتعامل مع الطلبات المتزامنة للألعاب
            self.pool = await asyncpg.create_pool(database_url)
            print("✅ [Database] تم الاتصال بقاعدة البيانات بنجاح تام!")
            
            # تهيئة الجداول الأساسية للأعضاء إذا لم تكن موجودة مسبقاً
            await self.create_tables()
            return True
        except Exception as e:
            print(f"❌ [Database] فشل في إنشاء حوض الاتصال: {e}")
            return False

    async def create_tables(self):
        """إنشاء جداول الاقتصاد، العملات، والنقاط لملفات الألعاب الثلاثة"""
        async with self.pool.acquire() as conn:
            # جدول الحسابات المالية ونقاط الخبرة للألعاب
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users_economy (
                    user_id BIGINT PRIMARY KEY,
                    coins BIGINT DEFAULT 1000,
                    xp INT DEFAULT 0,
                    wins INT DEFAULT 0,
                    losses INT DEFAULT 0
                );
            ''')
            print("✅ [Database] تم فحص وتأمين جداول بيانات الألعاب بنجاح.")

    async def close(self):
        """إغلاق الاتصال بأمان عند إعادة تشغيل البوت أو إطفائه"""
        if self.pool:
            await self.pool.close()
            print("🔒 [Database] تم قطع الاتصال بقاعدة البيانات بأمان.")
