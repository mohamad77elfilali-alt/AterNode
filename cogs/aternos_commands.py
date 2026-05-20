import discord
from discord.ext import commands
from discord.app_commands import command, Choice
from python_aternos import Client
import database
from utils.translations import get_text
import asyncio

class AternosCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _validate_and_connect(self, interaction: discord.Interaction, action_type: str):
        """
        دالة مركزية خارقة (Helper Method) للتحقق من:
        1. الإعدادات موجودة.
        2. القناة صحيحة.
        3. العضو يمتلك الرتبة المناسبة.
        4. تسجيل الدخول إلى Aternos وإرجاع كائن السيرفر.
        """
        settings = await database.get_settings(interaction.guild.id)
        
        if not settings or not settings.get('aternos_session'):
            await interaction.followup.send("❌ **النظام غير مهيأ!** يرجى من المشرف استخدام أمر `/setup` أولاً.", ephemeral=True)
            return None, None

        lang = settings.get('language', 'ar')

        # 1. التحقق من القناة
        target_channel_id = settings.get('start_channel') if action_type == 'start' else settings.get('power_channel')
        if target_channel_id and interaction.channel.id != target_channel_id:
            await interaction.followup.send(f"❌ يجب استخدام هذا الأمر في القناة المخصصة: <#{target_channel_id}>", ephemeral=True)
            return None, None

        # 2. التحقق من الرتبة
        target_role_id = settings.get(f'{action_type}_role')
        if target_role_id:
            user_role_ids = [role.id for role in interaction.user.roles]
            # إذا لم يكن لديه الرتبة، وليس بصلاحيات مسؤول
            if target_role_id not in user_role_ids and not interaction.user.guild_permissions.administrator:
                await interaction.followup.send(get_text('permission_denied', lang), ephemeral=True)
                return None, None

        # 3. الاتصال بـ Aternos (بدون تجميد البوت)
        try:
            # نستخدم to_thread لأن تسجيل الدخول قد يستغرق وقتاً
            aternos = await asyncio.to_thread(Client.from_credentials, session=settings['aternos_session'])
            servers = await asyncio.to_thread(aternos.list_servers)
            
            if not servers:
                await interaction.followup.send("❌ لم يتم العثور على أي سيرفر مرتبط بهذا الكوكي (Session).", ephemeral=True)
                return None, None
                
            return servers[0], settings
            
        except Exception as e:
            await interaction.followup.send(f"❌ **خطأ في الاتصال بـ Aternos:** قد يكون `ATERNOS_SESSION` منتهي الصلاحية.\n`{str(e)}`", ephemeral=True)
            return None, None

    # ================= [ أمر التشغيل ] =================
    @command(name="start", description="🚀 تشغيل سيرفر ماينكرافت")
    async def start_server(self, interaction: discord.Interaction):
        await interaction.response.defer() # نطلب وقتاً إضافياً من ديسكورد للرد
        
        server, settings = await self._validate_and_connect(interaction, 'start')
        if not server: return

        if server.status != "offline":
            await interaction.followup.send(f"⚠️ السيرفر ليس مغلقاً! الحالة الحالية: **{server.status}**")
            return

        # تشغيل السيرفر
        await asyncio.to_thread(server.start)
        
        embed = discord.Embed(
            title="🟢 جاري تشغيل السيرفر!",
            description=f"الآي بي: `{settings.get('server_ip', server.address)}`",
            color=discord.Color.from_str("#00ff66") # نيون أخضر
        )
        embed.set_footer(text="NetPulse Aternos System")
        await interaction.followup.send(embed=embed)

    # ================= [ أمر الإطفاء ] =================
    @command(name="stop", description="🔴 إطفاء سيرفر ماينكرافت")
    async def stop_server(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        server, settings = await self._validate_and_connect(interaction, 'stop')
        if not server: return

        if server.status == "offline":
            await interaction.followup.send("⚠️ السيرفر مغلق بالفعل!")
            return

        await asyncio.to_thread(server.stop)
        
        embed = discord.Embed(
            title="🔴 جاري إطفاء السيرفر!",
            description="يتم الآن حفظ البيانات وإغلاق السيرفر بأمان.",
            color=discord.Color.from_str("#ff003c") # أحمر
        )
        await interaction.followup.send(embed=embed)

    # ================= [ أمر إعادة التشغيل ] =================
    @command(name="restart", description="🔄 إعادة تشغيل سيرفر ماينكرافت")
    async def restart_server(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        server, settings = await self._validate_and_connect(interaction, 'restart')
        if not server: return

        if server.status == "offline":
            await interaction.followup.send("⚠️ السيرفر مغلق، الرجاء استخدام أمر `/start` بدلاً من ذلك.")
            return

        await asyncio.to_thread(server.restart)
        
        embed = discord.Embed(
            title="🔄 جاري إعادة تشغيل السيرفر!",
            color=discord.Color.from_str("#00f0ff") # نيون أزرق
        )
        await interaction.followup.send(embed=embed)

    # ================= [ أمر الحالة ] =================
    @command(name="status", description="📊 عرض حالة السيرفر الحالية واللاعبين المتصلين")
    async def server_status(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        # للحالة، نستخدم صلاحيات التشغيل (start) كمرجع أساسي
        server, settings = await self._validate_and_connect(interaction, 'start')
        if not server: return

        status = server.status
        color = discord.Color.from_str("#00ff66") if status == "online" else discord.Color.from_str("#ff003c")
        
        # استخراج عدد اللاعبين إذا كان السيرفر يعمل
        players_text = "0/0"
        if status == "online":
            players_text = f"{server.players_count}/{server.max_players}"

        embed = discord.Embed(
            title="📊 حالة سيرفر Aternos",
            color=color
        )
        embed.add_field(name="الحالة", value=f"**{status.upper()}**", inline=True)
        embed.add_field(name="اللاعبون", value=f"👥 {players_text}", inline=True)
        
        ip = settings.get('server_ip') or server.address
        port = settings.get('server_port') or server.port
        version = settings.get('server_version') or server.software
        
        embed.add_field(name="الآي بي (IP)", value=f"`{ip}`", inline=False)
        embed.add_field(name="البورت (Port)", value=f"`{port}`", inline=True)
        embed.add_field(name="الإصدار", value=f"`{version}`", inline=True)
        
        # إضافة اسم بوت الـ 24 ساعة إذا تم تسجيله في الإعدادات
        bot_247 = settings.get('bot_247_name')
        if bot_247:
            embed.add_field(name="بوت 24/7", value=f"🤖 `{bot_247}`", inline=False)

        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text="NetPulse Architecture")
        
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AternosCommands(bot))
