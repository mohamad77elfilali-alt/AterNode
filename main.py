"""
Elite Discord Entertainment & Gaming Bot - Main Core Engine
Production-Ready | Discord.py v2.4+ | Async PostgreSQL
Premium Cyberpunk/Neon Themed Gaming Hub with Dynamic Channel Creation
"""

import asyncio
import logging
import os
from typing import Optional
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncpg
from dotenv import load_dotenv

# ============================================================================
# ENVIRONMENT & CONFIGURATION
# ============================================================================
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DiscordGamingBot")

# Color scheme for embeds (Cyberpunk/Neon)
NEON_PURPLE = 0x9D00FF
NEON_CYAN = 0x00F0FF
NEON_MAGENTA = 0xFF00FF
NEON_GREEN = 0x39FF14

# ============================================================================
# DATABASE CONNECTION POOL
# ============================================================================
class DatabasePool:
    """Manages async PostgreSQL connection pooling"""
    pool: Optional[asyncpg.Pool] = None
    
    @classmethod
    async def initialize(cls) -> None:
        """Initialize the connection pool"""
        try:
            cls.pool = await asyncpg.create_pool(
                DATABASE_URL,
                min_size=5,
                max_size=20,
                command_timeout=60,
            )
            logger.info("✅ PostgreSQL Connection Pool Initialized")
            await cls.create_tables()
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    @classmethod
    async def create_tables(cls) -> None:
        """Create necessary database tables if they don't exist"""
        async with cls.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS game_channels (
                    id SERIAL PRIMARY KEY,
                    guild_id BIGINT NOT NULL,
                    channel_id BIGINT NOT NULL UNIQUE,
                    host_id BIGINT NOT NULL,
                    lobby_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    max_players INT,
                    is_private BOOLEAN DEFAULT FALSE,
                    invited_users TEXT[] DEFAULT '{}'
                );
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_guild_channel 
                ON game_channels(guild_id, channel_id);
            """)
            logger.info("✅ Database tables initialized")
    
    @classmethod
    async def close(cls) -> None:
        """Close the connection pool"""
        if cls.pool:
            await cls.pool.close()
            logger.info("✅ PostgreSQL Connection Pool Closed")

# ============================================================================
# MAIN BOT CLASS
# ============================================================================
class DiscordGamingBot(commands.Cog):
    """Core gaming bot with dynamic channel provisioning"""
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.cleanup_channels.start()
    
    @tasks.loop(minutes=5)
    async def cleanup_channels(self) -> None:
        """Cleanup inactive game channels from database and Discord"""
        try:
            if DatabasePool.pool is None:
                return
            
            async with DatabasePool.pool.acquire() as conn:
                # Get all tracked channels
                channels = await conn.fetch(
                    "SELECT guild_id, channel_id, host_id FROM game_channels"
                )
                
                for row in channels:
                    try:
                        channel = self.bot.get_channel(row['channel_id'])
                        if channel is None:
                            # Channel doesn't exist, remove from database
                            await conn.execute(
                                "DELETE FROM game_channels WHERE channel_id = $1",
                                row['channel_id']
                            )
                            logger.info(f"🗑️ Removed orphaned channel from database: {row['channel_id']}")
                    except Exception as e:
                        logger.error(f"Error checking channel {row['channel_id']}: {e}")
        except Exception as e:
            logger.error(f"Cleanup task error: {e}")
    
    @cleanup_channels.before_loop
    async def before_cleanup(self) -> None:
        await self.bot.wait_until_ready()
    
    @app_commands.command(
        name="setup_gaming_hub",
        description="🎮 Initialize the Entertainment & Gaming Hub (Admin Only)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_gaming_hub(self, interaction: discord.Interaction) -> None:
        """Setup command to create gaming hub category and channels"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            guild = interaction.guild
            if not guild:
                await interaction.followup.send(
                    "❌ This command can only be used in a server.",
                    ephemeral=True
                )
                return
            
            # Create category
            category = await guild.create_category(
                name="🎮 ENTERTAINMENT HUB",
                reason="Gaming Hub Setup by Admin"
            )
            logger.info(f"✅ Created category: {category.name} in {guild.name}")
            
            # Create solo arcade channel
            solo_channel = await guild.create_text_channel(
                name="👤-solo-arcade",
                category=category,
                topic="🕹️ Single-player games and arcade challenges",
                reason="Gaming Hub Setup"
            )
            
            # Create multiplayer lobbies channel
            multi_channel = await guild.create_text_channel(
                name="👥-multiplayer-lobbies",
                category=category,
                topic="⚔️ Multiplayer matches and party games",
                reason="Gaming Hub Setup"
            )
            
            logger.info(f"✅ Created solo channel: {solo_channel.name}")
            logger.info(f"✅ Created multiplayer channel: {multi_channel.name}")
            
            # Send solo arcade embed
            solo_embed = discord.Embed(
                title="🕹️ SOLO ARCADE ENGINE",
                description=(
                    "**Welcome to the Ultimate Single-Player Gaming Experience!**\n\n"
                    "Dive into our extensive collection of **50+ thrilling mini-games**, each crafted for maximum entertainment. "
                    "From classic arcade challenges to mind-bending puzzles, strategy games to lightning-fast reflexes tests — "
                    "there's something for everyone.\n\n"
                    "🎯 **Features:**\n"
                    "✨ Instant private session creation\n"
                    "🎮 50+ unique games across multiple categories\n"
                    "📊 Real-time gameplay feedback\n"
                    "🏆 Competitive high-score tracking\n"
                    "⚡ Auto-cleanup when you're done\n\n"
                    "**Click the button below to launch your personal arcade!**"
                ),
                color=NEON_PURPLE
            )
            solo_embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2159/2159517.png")
            solo_embed.set_footer(text="🤖 Powered by Elite Gaming Bot | Cyberpunk Edition")
            
            # Import here to avoid circular imports
            from cogs.solo_manager import SoloGameView
            
            await solo_channel.send(embed=solo_embed, view=SoloGameView(self.bot))
            
            # Send multiplayer lobbies embed
            multi_embed = discord.Embed(
                title="⚔️ MULTIPLAYER MATCHMAKING HUB",
                description=(
                    "**Unleash the Power of Multiplayer Gaming!**\n\n"
                    "Team up with friends or challenge strangers in our elite collection of **10 premium multiplayer games**. "
                    "Host custom lobbies with full control over player limits, privacy settings, and exclusive invitations.\n\n"
                    "🎯 **Features:**\n"
                    "👥 Dynamic player capacity configuration\n"
                    "🔐 Public or private lobby modes\n"
                    "🎮 10 distinct multiplayer game modes\n"
                    "📢 Real-time player synchronization\n"
                    "🏅 Victory declarations and stat tracking\n\n"
                    "**Ready to dominate? Create your matchmaking lobby now!**"
                ),
                color=NEON_CYAN
            )
            multi_embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/747/747376.png")
            multi_embed.set_footer(text="🤖 Powered by Elite Gaming Bot | Cyberpunk Edition")
            
            from cogs.multi_manager import MultiplayerLobbyView
            
            await multi_channel.send(embed=multi_embed, view=MultiplayerLobbyView(self.bot))
            
            await interaction.followup.send(
                f"✅ **Gaming Hub Setup Complete!**\n\n"
                f"📍 Category: {category.mention}\n"
                f"👤 Solo Arcade: {solo_channel.mention}\n"
                f"👥 Multiplayer Hub: {multi_channel.mention}\n\n"
                f"Your elite gaming platform is ready!",
                ephemeral=True
            )
            
            logger.info(f"✅ Gaming Hub fully setup in {guild.name}")
            
        except Exception as e:
            logger.error(f"❌ Setup error: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ Setup failed: {str(e)}",
                ephemeral=True
            )


# ============================================================================
# BOT INITIALIZATION
# ============================================================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready() -> None:
    """Called when the bot is ready"""
    logger.info(f"✅ Bot logged in as {bot.user}")
    logger.info(f"🎮 Gaming Bot is online and operational")
    try:
        synced = await bot.tree.sync()
        logger.info(f"✅ Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"❌ Command sync failed: {e}")


async def load_cogs() -> None:
    """Load all cogs from the cogs directory"""
    cogs_dir = "cogs"
    
    if not os.path.exists(cogs_dir):
        os.makedirs(cogs_dir)
    
    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py") and not filename.startswith("_"):
            try:
                cog_name = filename[:-3]
                await bot.load_extension(f"cogs.{cog_name}")
                logger.info(f"✅ Loaded cog: {cog_name}")
            except Exception as e:
                logger.error(f"❌ Failed to load cog {filename}: {e}", exc_info=True)


async def main() -> None:
    """Main bot startup sequence"""
    async with bot:
        # Initialize database
        await DatabasePool.initialize()
        
        # Add main cog
        await bot.add_cog(DiscordGamingBot(bot))
        
        # Load extension cogs
        await load_cogs()
        
        # Start bot
        logger.info("🚀 Launching Discord Gaming Bot...")
        try:
            await bot.start(TOKEN)
        except KeyboardInterrupt:
            logger.info("⚠️ Bot shutdown requested")
        finally:
            await DatabasePool.close()


if __name__ == "__main__":
    asyncio.run(main())
