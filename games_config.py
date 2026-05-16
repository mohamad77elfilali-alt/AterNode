import os
from dotenv import load_dotenv

# تحميل المتغيرات البيئية السرية
load_dotenv()

class GamesConfig:
    # التوكن الخاص ببوت الألعاب (يجب أن يكون مختلفاً عن البوت الأول)
    TOKEN = os.getenv("GAMES_BOT_TOKEN")
    
    # ربطه بنفس قاعدة بيانات PostgreSQL الخاصة بالبوت الأول ليتشاركا الأموال والمستويات!
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # الهوية البصرية النيونية المتناسقة (Neon Purple / Magenta كلون مميز للألعاب)
    COLOR_GAMES = 0xbd00ff   
    COLOR_SUCCESS = 0x2ecc71
    COLOR_ERROR = 0xe74c3c
    
    FOOTER_TEXT = "Ultra Games Companion • 2026"
