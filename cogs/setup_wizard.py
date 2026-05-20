import discord
from discord.ext import commands
from discord.ui import View, Button, Select, Modal, TextInput
import database
from utils.translations import get_text

# ================= [ نافذة إدخال البيانات النصية (Modal) ] =================
class ServerDataModal(Modal):
    def __init__(self, view_state, lang):
        super().__init__(title=get_text('setup_title', lang)[:45])
        self.view_state = view_state
        self.lang = lang

        # الحقول النصية
        self.session = TextInput(
            label="ATERNOS_SESSION",
            style=discord.TextStyle.short,
            placeholder="أدخل الكوكي هنا...",
            required=True
        )
        self.ip = TextInput(
            label=get_text('setup_server_ip', lang)[:45],
            style=discord.TextStyle.short,
            placeholder="مثال: netpulse.aternos.me",
            required=True
        )
        self.port = TextInput(
            label=get_text('setup_server_port', lang)[:45],
            style=discord.TextStyle.short,
            placeholder="مثال: 12345",
            required=False
        )
        self.version = TextInput(
            label=get_text('setup_server_version', lang)[:45],
            style=discord.TextStyle.short,
            placeholder="مثال: 1.20.1",
            required=False
        )
        self.bot_name = TextInput(
            label=get_text('setup_bot247_name', lang)[:45],
            style=discord.TextStyle.short,
            placeholder="اسم بوت الـ 24/7 إن وجد",
            required=False
        )

        self.add_item(self.session)
        self.add_item(self.ip)
        self.add_item(self.port)
        self.add_item(self.version)
        self.add_item(self.bot_name)

    async def on_submit(self, interaction: discord.Interaction):
        # حفظ البيانات المدخلة في حالة الواجهة (State)
        self.view_state.settings['aternos_session'] = self.session.value
        self.view_state.settings['server_ip'] = self.ip.value
        self.view_state.settings['server_port'] = self.port.value
        self.view_state.settings['server_version'] = self.version.value
        self.view_state.settings['bot_247_name'] = self.bot_name.value
        
        await interaction.response.send_message("✅ تم حفظ البيانات النصية. يمكنك إكمال باقي الإعدادات.", ephemeral=True)

# ================= [ الواجهة التفاعلية الرئيسية (Setup Wizard) ] =================
class SetupWizardView(View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__(timeout=600) # مهلة 10 دقائق للإعداد
        self.interaction = interaction
        self.guild_id = interaction.guild.id
        self.current_step = 1
        
        # الذاكرة المؤقتة للإعدادات قبل حفظها في قاعدة البيانات
        self.settings = {
            'language': 'ar', 'aternos_session': None, 'start_role': None, 
            'restart_role': None, 'stop_role': None, 'start_channel': None, 
            'power_channel': None, 'bot_channel': None, 'server_ip': None, 
            'server_port': None, 'server_version': None, 'bot_247_name': None,
            'is_owner': True, 'bot_send_roles': None
        }
        self.update_components()

    def get_embed(self):
        lang = self.settings['language']
        embed = discord.Embed(
            title=get_text('setup_title', lang),
            color=discord.Color.from_str("#00f0ff") # لون النيون الأزرق
        )
        
        if self.current_step == 1:
            embed.description = f"**الخطوة 1/4: اللغة والأساسيات**\n{get_text('lang_select_desc', lang)}\n\n*يمكنك الضغط على 'استرجاع' لجلب إعداداتك السابقة.*"
        elif self.current_step == 2:
            embed.description = f"**الخطوة 2/4: إعداد الرتب (Roles)**\nحدد الرتب المسموح لها بالتحكم في السيرفر."
        elif self.current_step == 3:
            embed.description = f"**الخطوة 3/4: إعداد القنوات (Channels)**\nحدد القنوات المخصصة لأوامر التشغيل والإطفاء."
        elif self.current_step == 4:
            embed.description = f"**الخطوة 4/4: بيانات السيرفر (Server Data)**\nاضغط على الزر أدناه لإدخال الـ Session وباقي البيانات، ثم اضغط حفظ وإنهاء."
            
        embed.set_footer(text="NetPulse Auto-Setup Architecture")
        return embed

    def update_components(self):
        self.clear_items()
        lang = self.settings['language']

        # ================= [ الخطوة 1: اللغة والاسترجاع ] =================
        if self.current_step == 1:
            lang_select = Select(placeholder="🌐 اختر اللغة / Select Language", options=[
                discord.SelectOption(label="العربية", value="ar", emoji="🇸🇦"),
                discord.SelectOption(label="English", value="en", emoji="🇬🇧"),
                discord.SelectOption(label="Русский", value="ru", emoji="🇷🇺")
            ])
            async def lang_callback(inter):
                self.settings['language'] = lang_select.values[0]
                self.update_components()
                await inter.response.edit_message(embed=self.get_embed(), view=self)
            lang_select.callback = lang_callback
            self.add_item(lang_select)

            # زر استرجاع الإعدادات
            restore_btn = Button(label=get_text('btn_restore', lang), style=discord.ButtonStyle.secondary, row=1)
            async def restore_callback(inter):
                old_settings = await database.get_settings(self.guild_id)
                if old_settings:
                    self.settings.update(old_settings)
                    await inter.response.send_message("✅ تم استرجاع الإعدادات السابقة بنجاح!", ephemeral=True)
                else:
                    await inter.response.send_message("❌ لا توجد إعدادات سابقة محفوظة.", ephemeral=True)
            restore_btn.callback = restore_callback
            self.add_item(restore_btn)

        # ================= [ الخطوة 2: الرتب (Role Selectors) ] =================
        elif self.current_step == 2:
            # ديسكورد يوفر RoleSelect بشكل مدمج!
            start_role = discord.ui.RoleSelect(placeholder=get_text('setup_roles_start', lang)[:100], row=0)
            restart_role = discord.ui.RoleSelect(placeholder=get_text('setup_roles_restart', lang)[:100], row=1)
            stop_role = discord.ui.RoleSelect(placeholder=get_text('setup_roles_stop', lang)[:100], row=2)

            async def role_callback(inter):
                self.settings['start_role'] = start_role.values[0].id if start_role.values else None
                self.settings['restart_role'] = restart_role.values[0].id if restart_role.values else None
                self.settings['stop_role'] = stop_role.values[0].id if stop_role.values else None
                await inter.response.defer()

            start_role.callback = restart_role.callback = stop_role.callback = role_callback
            self.add_item(start_role)
            self.add_item(restart_role)
            self.add_item(stop_role)

        # ================= [ الخطوة 3: القنوات (Channel Selectors) ] =================
        elif self.current_step == 3:
            start_channel = discord.ui.ChannelSelect(placeholder=get_text('setup_channels_start', lang)[:100], channel_types=[discord.ChannelType.text], row=0)
            power_channel = discord.ui.ChannelSelect(placeholder=get_text('setup_channels_power', lang)[:100], channel_types=[discord.ChannelType.text], row=1)
            
            async def channel_callback(inter):
                self.settings['start_channel'] = start_channel.values[0].id if start_channel.values else None
                self.settings['power_channel'] = power_channel.values[0].id if power_channel.values else None
                await inter.response.defer()

            start_channel.callback = power_channel.callback = channel_callback
            self.add_item(start_channel)
            self.add_item(power_channel)

        # ================= [ الخطوة 4: البيانات النصية والإنهاء ] =================
        elif self.current_step == 4:
            data_btn = Button(label="📝 إدخال بيانات Aternos والسيرفر", style=discord.ButtonStyle.primary, row=0)
            async def data_callback(inter):
                await inter.response.send_modal(ServerDataModal(self, lang))
            data_btn.callback = data_callback
            self.add_item(data_btn)

            finish_btn = Button(label=get_text('btn_finish', lang), style=discord.ButtonStyle.success, row=1)
            async def finish_callback(inter):
                # حفظ كل شيء في قاعدة البيانات
                await database.save_settings(self.guild_id, **self.settings)
                
                success_embed = discord.Embed(
                    title="System Online", 
                    description=get_text('setup_completed', lang),
                    color=discord.Color.from_str("#b026ff") # نيون بنفسجي للنجاح
                )
                await inter.response.edit_message(embed=success_embed, view=None)
            finish_btn.callback = finish_callback
            self.add_item(finish_btn)

        # ================= [ أزرار التنقل (Next / Back) ] =================
        if self.current_step < 4:
            next_btn = Button(label=get_text('btn_next', lang), style=discord.ButtonStyle.primary, row=4)
            async def next_callback(inter):
                self.current_step += 1
                self.update_components()
                await inter.response.edit_message(embed=self.get_embed(), view=self)
            next_btn.callback = next_callback
            self.add_item(next_btn)

        if self.current_step > 1:
            back_btn = Button(label=get_text('btn_back', lang), style=discord.ButtonStyle.secondary, row=4)
            async def back_callback(inter):
                self.current_step -= 1
                self.update_components()
                await inter.response.edit_message(embed=self.get_embed(), view=self)
            back_btn.callback = back_callback
            self.add_item(back_btn)


# ================= [ الـ Cog الأساسي لتسجيل الأمر ] =================
class SetupWizardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="setup", description="تشغيل نظام الإعداد الذكي للسيرفر (للمشرفين فقط)")
    @discord.app_commands.default_permissions(administrator=True) # حماية الأمر للمشرفين فقط
    async def setup(self, interaction: discord.Interaction):
        view = SetupWizardView(interaction)
        await interaction.response.send_message(embed=view.get_embed(), view=view, ephemeral=True)

# دالة أساسية لتحميل الـ Cog داخل main.py
async def setup(bot):
    await bot.add_cog(SetupWizardCog(bot))
