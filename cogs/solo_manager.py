import discord
from discord.ext import commands
import asyncpg
import random
import logging
from typing import Optional, Dict, List
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger("GamingBot")

class SoloGamePage1View(discord.ui.View):
    """Solo arcade games - Page 1 (Buttons 1-12)"""
    
    def __init__(self, user_id: int, channel_id: int, bot):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.channel_id = channel_id
        self.bot = bot
    
    async def update_activity(self):
        """Update last activity timestamp in database"""
        try:
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE game_channels SET last_activity = NOW() WHERE channel_id = $1",
                    self.channel_id
                )
        except Exception as e:
            logger.error(f"❌ Failed to update activity: {e}", exc_info=True)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Verify only the authorized user can interact"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ This is not your solo session!",
                ephemeral=True
            )
            return False
        return True
    
    @discord.ui.button(label="🎲 Dice Roll", style=discord.ButtonStyle.primary, custom_id="solo_dice_roll")
    async def dice_roll(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Classic dice roll game"""
        await interaction.response.defer()
        await self.update_activity()
        
        result = random.randint(1, 6)
        outcome_emoji = ["⚪", "⚫", "🔴", "🟡", "🟢", "🔵"][result - 1]
        
        embed = discord.Embed(
            title="🎲 DICE ROLL RESULTS",
            description=f"{outcome_emoji} You rolled a **{result}**!",
            color=0x00D9FF
        )
        embed.add_field(name="Outcome", value=f"Roll: {result}/6", inline=False)
        
        if result >= 5:
            embed.add_field(name="🎉 Status", value="Lucky roll!", inline=False)
        elif result == 1:
            embed.add_field(name="😢 Status", value="Better luck next time!", inline=False)
        else:
            embed.add_field(name="➡️ Status", value="Average roll", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="🎰 Slots", style=discord.ButtonStyle.primary, custom_id="solo_slots")
    async def slots(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Slot machine game"""
        await interaction.response.defer()
        await self.update_activity()
        
        symbols = ["🍒", "🍋", "🍊", "🍇", "💎", "👑", "🎯", "⭐"]
        spin1 = random.choice(symbols)
        spin2 = random.choice(symbols)
        spin3 = random.choice(symbols)
        
        is_winner = spin1 == spin2 == spin3
        
        embed = discord.Embed(
            title="🎰 SLOT MACHINE",
            description=f"```\n   {spin1}  {spin2}  {spin3}\n```",
            color=0xFF1493
        )
        
        if is_winner:
            embed.add_field(name="🎉 JACKPOT!", value=f"All three match! {spin1} {spin1} {spin1}", inline=False)
        else:
            embed.add_field(name="🎲 Result", value="No match - try again!", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="🪙 Coin Flip", style=discord.ButtonStyle.primary, custom_id="solo_coin_flip")
    async def coin_flip(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Coin flip game"""
        await interaction.response.defer()
        await self.update_activity()
        
        result = random.choice(["Heads", "Tails"])
        result_emoji = "🟡" if result == "Heads" else "⚫"
        
        embed = discord.Embed(
            title="🪙 COIN FLIP",
            description=f"{result_emoji} **{result}**!",
            color=0xFFD700
        )
        embed.add_field(name="Result", value=result, inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="🎡 Spin Wheel", style=discord.ButtonStyle.primary, custom_id="solo_spin_wheel")
    async def spin_wheel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Spin wheel game"""
        await interaction.response.defer()
        await self.update_activity()
        
        options = ["🔴 Red", "🟣 Purple", "🟢 Green", "🟡 Yellow", "🔵 Blue", "⚪ White"]
        result = random.choice(options)
        
        embed = discord.Embed(
            title="🎡 SPIN THE WHEEL",
            description=f"The wheel landed on: **{result}**",
            color=0x00D9FF
        )
        embed.add_field(name="Lucky Color", value=result, inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="🎡 Roulette", style=discord.ButtonStyle.primary, custom_id="solo_roulette")
    async def roulette(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Roulette game"""
        await interaction.response.defer()
        await self.update_activity()
        
        number = random.randint(0, 36)
        color = "🔴 Red" if number % 2 == 1 else "⚫ Black"
        if number == 0:
            color = "🟢 Green"
        
        embed = discord.Embed(
            title="🎡 ROULETTE SPIN",
            description=f"Number: **{number}** - {color}",
            color=0xFF1493
        )
        embed.add_field(name="Result", value=f"Landed on {number}", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="✂️ RPS", style=discord.ButtonStyle.primary, custom_id="solo_rps")
    async def rock_paper_scissors(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Rock Paper Scissors game"""
        await interaction.response.defer()
        await self.update_activity()
        
        choices = ["Rock", "Paper", "Scissors"]
        bot_choice = random.choice(choices)
        
        view = RPSChoiceView(bot_choice)
        embed = discord.Embed(
            title="✂️ ROCK PAPER SCISSORS",
            description="Choose your move!",
            color=0x00D9FF
        )
        
        await interaction.followup.send(embed=embed, view=view)
    
    @discord.ui.button(label="🧠 Trivia", style=discord.ButtonStyle.success, custom_id="solo_trivia")
    async def trivia(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Trivia challenge game"""
        await interaction.response.defer()
        await self.update_activity()
        
        trivia_questions = [
            {"question": "What is the capital of France?", "correct": "Paris", "options": ["Paris", "Lyon", "Marseille"]},
            {"question": "What is 2 + 2?", "correct": "4", "options": ["3", "4", "5"]},
            {"question": "What is the largest planet?", "correct": "Jupiter", "options": ["Mars", "Jupiter", "Saturn"]},
            {"question": "Who wrote Hamlet?", "correct": "Shakespeare", "options": ["Marlowe", "Shakespeare", "Jonson"]},
            {"question": "What is the smallest prime number?", "correct": "2", "options": ["1", "2", "3"]},
        ]
        
        q = random.choice(trivia_questions)
        random.shuffle(q["options"])
        
        view = TriviaView(q["correct"])
        embed = discord.Embed(
            title="🧠 TRIVIA CHALLENGE",
            description=q["question"],
            color=0x00D9FF
        )
        
        for idx, option in enumerate(q["options"], 1):
            embed.add_field(name=f"Option {idx}", value=option, inline=False)
        
        await interaction.followup.send(embed=embed, view=view)
    
    @discord.ui.button(label="🌍 Capitals", style=discord.ButtonStyle.success, custom_id="solo_capitals")
    async def capitals(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Capital guesser game"""
        await interaction.response.defer()
        await self.update_activity()
        
        capitals = {
            "France": "Paris",
            "Germany": "Berlin",
            "Spain": "Madrid",
            "Italy": "Rome",
            "Japan": "Tokyo",
            "Brazil": "Brasília",
            "Canada": "Ottawa",
            "Australia": "Canberra",
            "Egypt": "Cairo",
            "India": "New Delhi",
        }
        
        country = random.choice(list(capitals.keys()))
        correct_answer = capitals[country]
        wrong_answers = [v for k, v in capitals.items() if k != country]
        options = [correct_answer] + random.sample(wrong_answers, 2)
        random.shuffle(options)
        
        view = CapitalsView(correct_answer, country)
        embed = discord.Embed(
            title="🌍 CAPITAL GUESSER",
            description=f"What is the capital of **{country}**?",
            color=0x00D9FF
        )
        
        for idx, option in enumerate(options, 1):
            embed.add_field(name=f"Option {idx}", value=option, inline=False)
        
        await interaction.followup.send(embed=embed, view=view)
    
    @discord.ui.button(label="🗺️ Flags", style=discord.ButtonStyle.success, custom_id="solo_flags")
    async def flags(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Flag identifier game"""
        await interaction.response.defer()
        await self.update_activity()
        
        flags = {
            "🇫🇷": "France",
            "🇬🇧": "United Kingdom",
            "🇩🇪": "Germany",
            "🇪🇸": "Spain",
            "🇮🇹": "Italy",
            "🇯🇵": "Japan",
            "🇧🇷": "Brazil",
            "🇨🇦": "Canada",
            "🇦🇺": "Australia",
            "🇿🇦": "South Africa",
        }
        
        flag = random.choice(list(flags.keys()))
        correct_answer = flags[flag]
        wrong_answers = [v for k, v in flags.items() if k != flag]
        options = [correct_answer] + random.sample(wrong_answers, 2)
        random.shuffle(options)
        
        view = FlagsView(correct_answer, flag)
        embed = discord.Embed(
            title="🗺️ FLAG IDENTIFIER",
            description=f"What country is this flag? {flag}",
            color=0x00D9FF
        )
        
        for idx, option in enumerate(options, 1):
            embed.add_field(name=f"Option {idx}", value=option, inline=False)
        
        await interaction.followup.send(embed=embed, view=view)
    
    @discord.ui.button(label="🧮 Math Mania", style=discord.ButtonStyle.success, custom_id="solo_math")
    async def math_mania(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Math challenge game"""
        await interaction.response.defer()
        await self.update_activity()
        
        num1 = random.randint(1, 100)
        num2 = random.randint(1, 100)
        operations = ["+", "-", "*"]
        op = random.choice(operations)
        
        if op == "+":
            answer = num1 + num2
        elif op == "-":
            answer = num1 - num2
        else:
            answer = num1 * num2
        
        wrong1 = answer + random.randint(1, 10)
        wrong2 = answer - random.randint(1, 10)
        options = [str(answer), str(wrong1), str(wrong2)]
        random.shuffle(options)
        
        view = MathView(str(answer))
        embed = discord.Embed(
            title="🧮 MATH MANIA",
            description=f"**{num1} {op} {num2} = ?**",
            color=0x00D9FF
        )
        
        for idx, option in enumerate(options, 1):
            embed.add_field(name=f"Option {idx}", value=option, inline=False)
        
        await interaction.followup.send(embed=embed, view=view)
    
    @discord.ui.button(label="📜 Proverbs", style=discord.ButtonStyle.success, custom_id="solo_proverbs")
    async def proverbs(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Proverb meaning game"""
        await interaction.response.defer()
        await self.update_activity()
        
        proverbs_dict = {
            "A bird in the hand is worth two in the bush": "It's better to have something certain than to risk it for something better",
            "Actions speak louder than words": "What you do is more important than what you say",
            "Better late than never": "It's better to do something late than not do it at all",
            "Don't cry over spilled milk": "Don't waste energy on things you can't change",
            "Practice makes perfect": "Regular training improves your skills",
        }
        
        proverb = random.choice(list(proverbs_dict.keys()))
        correct_meaning = proverbs_dict[proverb]
        
        wrong_meanings = [v for k, v in proverbs_dict.items() if k != proverb]
        options = [correct_meaning] + random.sample(wrong_meanings, 2)
        random.shuffle(options)
        
        view = ProverbsView(correct_meaning, proverb)
        embed = discord.Embed(
            title="📜 PROVERB MEANING",
            description=f"**\"{proverb}\"**\n\nWhat does this mean?",
            color=0x00D9FF
        )
        
        for idx, option in enumerate(options, 1):
            embed.add_field(name=f"Option {idx}", value=option, inline=True)
        
        await interaction.followup.send(embed=embed, view=view)
    
    @discord.ui.button(label="📖 Page 2 ➡️", style=discord.ButtonStyle.secondary, custom_id="solo_page2")
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Navigate to page 2"""
        await interaction.response.defer()
        await self.update_activity()
        
        embed = discord.Embed(
            title="🕹️ SOLO ARCADE - PAGE 2/4",
            description="More amazing games await!",
            color=0x00D9FF
        )
        embed.add_field(name="Available Games", value="13-25 games on this page", inline=False)
        
        from cogs.solo_manager import SoloGamePage2View
        await interaction.followup.send(embed=embed, view=SoloGamePage2View(self.user_id, self.channel_id, self.bot))

class SoloGamePage2View(discord.ui.View):
    """Solo arcade games - Page 2 (Buttons 13-25)"""
    
    def __init__(self, user_id: int, channel_id: int, bot):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.channel_id = channel_id
        self.bot = bot
    
    async def update_activity(self):
        """Update last activity timestamp in database"""
        try:
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE game_channels SET last_activity = NOW() WHERE channel_id = $1",
                    self.channel_id
                )
        except Exception as e:
            logger.error(f"❌ Failed to update activity: {e}", exc_info=True)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Verify only the authorized user can interact"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ This is not your solo session!",
                ephemeral=True
            )
            return False
        return True
    
    @discord.ui.button(label="🔤 Anagrams", style=discord.ButtonStyle.success, custom_id="solo_anagrams")
    async def anagrams(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Anagram solver game"""
        await interaction.response.defer()
        await self.update_activity()
        
        words = ["GAMING", "DISCORD", "PYTHON", "AMAZING", "BUTTERFLY", "MOUNTAIN"]
        correct_word = random.choice(words)
        scrambled = "".join(random.sample(list(correct_word), len(correct_word)))
        
        other_words = [w for w in words if w != correct_word]
        options = [correct_word] + random.sample(other_words, 2)
        random.shuffle(options)
        
        view = AnagramsView(correct_word, scrambled)
        embed = discord.Embed(
            title="🔤 ANAGRAM SOLVER",
            description=f"Unscramble: **{scrambled}**",
            color=0x00D9FF
        )
        
        for idx, option in enumerate(options, 1):
            embed.add_field(name=f"Option {idx}", value=option, inline=False)
        
        await interaction.followup.send(embed=embed, view=view)
    
    @discord.ui.button(label="🔤 Reverse", style=discord.ButtonStyle.success, custom_id="solo_reverse")
    async def word_reverse(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Word reverse game"""
        await interaction.response.defer()
        await self.update_activity()
        
        words = ["GAMING", "DISCORD", "PYTHON", "HELLO", "WORLD", "AMAZING"]
        correct_word = random.choice(words)
        reversed_word = correct_word[::-1]
        
        embed = discord.Embed(
            title="🔤 WORD REVERSE",
            description=f"Reverse this word: **{reversed_word}**\n\nYour answer: **{correct_word}**",
            color=0x00D9FF
        )
        embed.add_field(name="✅ Answer", value=correct_word, inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="🔤 Palindrome", style=discord.ButtonStyle.success, custom_id="solo_palindrome")
    async def palindrome(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Palindrome finder game"""
        await interaction.response.defer()
        await self.update_activity()
        
        palindromes = ["RACECAR", "LEVEL", "NOON", "RADAR", "KAYAK", "CIVIC"]
        non_palindromes = ["GAMING", "PYTHON", "HELLO", "WORLD", "DISCORD"]
        
        word = random.choice(palindromes + non_palindromes)
        is_palindrome = word in palindromes
        
        embed = discord.Embed(
            title="🔤 PALINDROME FINDER",
            description=f"Is **{word}** a palindrome?\n\n**Answer: {'YES ✅' if is_palindrome else 'NO ❌'}**",
            color=0x00D9FF
        )
        embed.add_field(name="Definition", value="A palindrome reads the same forwards and backwards", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="📊 Patterns", style=discord.ButtonStyle.success, custom_id="solo_patterns")
    async def pattern_finder(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Pattern finder game"""
        await interaction.response.defer()
        await self.update_activity()
        
        patterns = [
            {"series": "2, 4, 6, 8, ?", "answer": "10", "type": "Even numbers"},
            {"series": "1, 1, 2, 3, 5, 8, ?", "answer": "13", "type": "Fibonacci"},
            {"series": "100, 90, 80, 70, ?", "answer": "60", "type": "Decreasing by 10"},
            {"series": "1, 4, 9, 16, 25, ?", "answer": "36", "type": "Perfect squares"},
            {"series": "3, 6, 12, 24, ?", "answer": "48", "type": "Doubling"},
        ]
        
        pattern = random.choice(patterns)
        options = [pattern["answer"], str(int(pattern["answer"]) + 5), str(int(pattern["answer"]) - 5)]
        random.shuffle(options)
        
        view = PatternView(pattern["answer"], pattern["type"])
        embed = discord.Embed(
            title="📊 PATTERN FINDER",
            description=f"What's next? **{pattern['series']}**",
            color=0x00D9FF
        )
        
        for idx, option in enumerate(options, 1):
            embed.add_field(name=f"Option {idx}", value=option, inline=False)
        
        await interaction.followup.send(embed=embed, view=view)
    
    @discord.ui.button(label="⚡ Alphabet", style=discord.ButtonStyle.success, custom_id="solo_alphabet")
    async def alphabet_speed(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Alphabet speed challenge"""
        await interaction.response.defer()
        await self.update_activity()
        
        start_letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        position = ord(start_letter) - ord("A") + 1
        
        embed = discord.Embed(
            title="⚡ ALPHABET SPEED CHALLENGE",
            description=f"**{start_letter}** is the **{position}th** letter of the alphabet",
            color=0x00D9FF
        )
        embed.add_field(name="Position", value=f"{position}/26", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="🧭 Brain Teaser", style=discord.ButtonStyle.success, custom_id="solo_teaser")
    async def brain_teaser(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Brain teaser game"""
        await interaction.response.defer()
        await self.update_activity()
        
        teasers = [
            {"q": "I have cities, but no houses. I have mountains, but no trees. What am I?", "a": "A map"},
            {"q": "What has a head and a tail, but no body?", "a": "A coin"},
            {"q": "I speak without a mouth and hear without ears. What am I?", "a": "An echo"},
            {"q": "What can run but never walks?", "a": "Water"},
            {"q": "What has keys but no locks?", "a": "A piano"},
        ]
        
        teaser = random.choice(teasers)
        
        embed = discord.Embed(
            title="🧭 BRAIN TEASER",
            description=teaser["q"],
            color=0x00D9FF
        )
        embed.add_field(name="Answer", value=f"||{teaser['a']}||", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="🔤 Unscramble", style=discord.ButtonStyle.success, custom_id="solo_unscramble")
    async def unscramble(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Word unscramble game"""
        await interaction.response.defer()
        await self.update_activity()
        
        words_dict = {
            "NOHTYP": "PYTHON",
            "GNGAMII": "GAMING",
            "TCIDDORS": "DISCORD",
            "LOHEL": "HELLO",
            "WROLD": "WORLD",
        }
        
        scrambled = random.choice(list(words_dict.keys()))
        correct = words_dict[scrambled]
        
        embed = discord.Embed(
            title="🔤 UNSCRAMBLE",
            description=f"Unscramble: **{scrambled}**",
            color=0x00D9FF
        )
        embed.add_field(name="Answer", value=f"||{correct}||", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="🔗 Word Chain", style=discord.ButtonStyle.success, custom_id="solo_wordchain")
    async def word_chain(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Word chain game"""
        await interaction.response.defer()
        await self.update_activity()
        
        chains = [
            {"start": "CAT", "next": "TIGER", "hint": "Both are felines"},
            {"start": "BOOK", "next": "AUTHOR", "hint": "Related to writing"},
            {"start": "MOON", "next": "STAR", "hint": "Both are celestial"},
            {"start": "FIRE", "next": "WATER", "hint": "Opposites in nature"},
        ]
        
        chain = random.choice(chains)
        
        embed = discord.Embed(
            title="🔗 WORD CHAIN",
            description=f"**{chain['start']}** → **?** → ... \n\nHint: {chain['hint']}",
            color=0x00D9FF
        )
        embed.add_field(name="Next Word", value=f"||{chain['next']}||", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="🎣 Fishing", style=discord.ButtonStyle.danger, custom_id="solo_fishing")
    async def cyber_fishing(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cyber fishing simulator"""
        await interaction.response.defer()
        await self.update_activity()
        
        fish_types = ["🐠 Common Fish", "🐟 Rare Fish", "🦈 Shark", "🐙 Octopus", "🦑 Squid", "🐡 Pufferfish"]
        caught_fish = random.choice(fish_types)
        weight = random.randint(1, 50)
        
        embed = discord.Embed(
            title="🎣 CYBER FISHING SIMULATOR",
            description=f"You cast your line...",
            color=0x00D9FF
        )
        embed.add_field(name="Caught!", value=caught_fish, inline=False)
        embed.add_field(name="Weight", value=f"{weight} lbs", inline=False)
        
        if weight > 40:
            embed.add_field(name="🏆 Size", value="LEGENDARY CATCH!", inline=False)
        elif weight > 25:
            embed.add_field(name="⭐ Size", value="Great catch!", inline=False)
        else:
            embed.add_field(name="Size", value="Good catch!", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="⛏️ Mining", style=discord.ButtonStyle.danger, custom_id="solo_mining")
    async def cyber_mining(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cyber mining simulator"""
        await interaction.response.defer()
        await self.update_activity()
        
        ores = ["💎 Diamond", "🥇 Gold", "🥈 Silver", "🪨 Stone", "⚒️ Iron", "🟫 Coal"]
        mined_ore = random.choice(ores)
        amount = random.randint(1, 100)
        
        embed = discord.Embed(
            title="⛏️ CYBER MINING SIMULATOR",
            description="You swing your pickaxe...",
            color=0x00D9FF
        )
        embed.add_field(name="Mined", value=mined_ore, inline=False)
        embed.add_field(name="Amount", value=f"{amount} units", inline=False)
        
        if amount > 80:
            embed.add_field(name="🎉 Quality", value="PREMIUM YIELD!", inline=False)
        elif amount > 50:
            embed.add_field(name="Quality", value="Good yield!", inline=False)
        else:
            embed.add_field(name="Quality", value="Small yield", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="🧠 Memory", style=discord.ButtonStyle.danger, custom_id="solo_memory")
    async def memory_tiles(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Memory tiles game"""
        await interaction.response.defer()
        await self.update_activity()
        
        tiles = ["🟨", "🟩", "🟦", "🟪", "🟥", "🟧"]
        sequence = random.sample(tiles, 3)
        
        embed = discord.Embed(
            title="🧠 MEMORY TILES",
            description=f"Memorize: **{' '.join(sequence)}**\n\nSequence will be hidden in 3 seconds...",
            color=0x00D9FF
        )
        
        await interaction.followup.send(embed=embed)
        
        await asyncio.sleep(3)
        
        hidden_embed = discord.Embed(
            title="🧠 MEMORY TILES",
            description="What was the sequence?",
            color=0x00D9FF
        )
        
        await interaction.channel.send(embed=hidden_embed)
    
    @discord.ui.button(label="🎨 Color Match", style=discord.ButtonStyle.danger, custom_id="solo_colormatch")
    async def color_match(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Color matching game"""
        await interaction.response.defer()
        await self.update_activity()
        
        colors = {
            "🔴 Red": "❤️",
            "🔵 Blue": "💙",
            "🟢 Green": "💚",
            "🟡 Yellow": "💛",
            "🟣 Purple": "💜",
            "🟤 Brown": "🤎"
        }
        
        color_name = random.choice(list(colors.keys()))
        correct_emoji = colors[color_name]
        wrong_emojis = [v for k, v in colors.items() if k != color_name]
        options = [correct_emoji] + random.sample(wrong_emojis, 2)
        random.shuffle(options)
        
        view = ColorMatchView(correct_emoji, color_name)
        embed = discord.Embed(
            title="🎨 COLOR MATCH",
            description=f"Match the color: **{color_name}**",
            color=0x00D9FF
        )
        
        for idx, option in enumerate(options, 1):
            embed.add_field(name=f"Option {idx}", value=option, inline=False)
        
        await interaction.followup.send(embed=embed, view=view)
    
    @discord.ui.button(label="⚡ Reaction", style=discord.ButtonStyle.danger, custom_id="solo_reaction")
    async def quick_reaction(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Quick reaction test"""
        await interaction.response.defer()
        await self.update_activity()
        
        embed = discord.Embed(
            title="⚡ QUICK REACTION TEST",
            description="Get ready!",
            color=0x00D9FF
        )
        
        await interaction.followup.send(embed=embed)
        
        await asyncio.sleep(random.randint(2, 5))
        
        reaction_embed = discord.Embed(
            title="⚡ CLICK NOW!",
            description="How fast can you react?",
            color=0xFF1493
        )
        
        await interaction.channel.send(embed=reaction_embed)
    
    @discord.ui.button(label="📖 Page 3 ➡️", style=discord.ButtonStyle.secondary, custom_id="solo_page3")
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Navigate to page 3"""
        await interaction.response.defer()
        await self.update_activity()
        
        embed = discord.Embed(
            title="🕹️ SOLO ARCADE - PAGE 3/4",
            description="Even more games to discover!",
            color=0x00D9FF
        )
        embed.add_field(name="Available Games", value="Games 26-38 on this page", inline=False)
        
        from cogs.solo_manager import SoloGamePage3View
        await interaction.followup.send(embed=embed, view=SoloGamePage3View(self.user_id, self.channel_id, self.bot))

class SoloGamePage3View(discord.ui.View):
    """Solo arcade games - Page 3 (Buttons 26-38)"""
    
    def __init__(self, user_id: int, channel_id: int, bot):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.channel_id = channel_id
        self.bot = bot
    
    async def update_activity(self):
        """Update last activity timestamp in database"""
        try:
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE game_channels SET last_activity = NOW() WHERE channel_id = $1",
                    self.channel_id
                )
        except Exception as e:
            logger.error(f"❌ Failed to update activity: {e}", exc_info=True)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Verify only the authorized user can interact"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ This is not your solo session!",
                ephemeral=True
            )
            return False
        return True
    
    @discord.ui.button(label="🌑 Shadows", style=discord.ButtonStyle.danger, custom_id="solo_shadows")
    async def shadow_matching(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Shadow matching game"""
        await interaction.response.defer()
        await self.update_activity()
        
        objects = ["🎲", "🎯", "🎪", "🎭", "🎬", "🎤"]
        correct_object = random.choice(objects)
        wrong_objects = [o for o in objects if o != correct_object]
        options = [correct_object] + random.sample(wrong_objects, 2)
        random.shuffle(options)
        
        view = ShadowView(correct_object)
        embed = discord.Embed(
            title="🌑 SHADOW MATCHING",
            description=f"Which object matches this shadow? **?**",
            color=0x00D9FF
        )
        
        for idx, option in enumerate(options, 1):
            embed.add_field(name=f"Option {idx}", value=option, inline=False)
        
        await interaction.followup.send(embed=embed, view=view)
    
    @discord.ui.button(label="🎵 Sequence", style=discord.ButtonStyle.danger, custom_id="solo_sequence")
    async def sequence_memory(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Sequence memory game"""
        await interaction.response.defer()
        await self.update_activity()
        
        notes = ["🎵", "🎶", "🎼", "🎹", "🎸"]
        sequence = random.choices(notes, k=4)
        
        embed = discord.Embed(
            title="🎵 SEQUENCE MEMORY",
            description=f"Remember: **{' '.join(sequence)}**",
            color=0x00D9FF
        )
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="⚙️ Logic Gates", style=discord.ButtonStyle.danger, custom_id="solo_logic")
    async def logic_gates(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Logic gates puzzle"""
        await interaction.response.defer()
        await self.update_activity()
        
        gates = [
            {"problem": "If A=1 and B=0, what is A AND B?", "answer": "0"},
            {"problem": "If A=1 and B=0, what is A OR B?", "answer": "1"},
            {"problem": "If A=1, what is NOT A?", "answer": "0"},
            {"problem": "If A=0 and B=0, what is A AND B?", "answer": "0"},
        ]
        
        gate = random.choice(gates)
        
        embed = discord.Embed(
            title="⚙️ LOGIC GATES",
            description=gate["problem"],
            color=0x00D9FF
        )
        embed.add_field(name="Answer", value=f"||{gate['answer']}||", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="🔄 Rotation", style=discord.ButtonStyle.danger, custom_id="solo_rotation")
    async def rotation_puzzle(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Rotation puzzle game"""
        await interaction.response.defer()
        await self.update_activity()
        
        rotations = ["0°", "90°", "180°", "270°"]
        correct = random.choice(rotations)
        
        embed = discord.Embed(
            title="🔄 ROTATION PUZZLE",
            description=f"Rotate 🎯 clockwise 90°. Result: **{correct}**",
            color=0x00D9FF
        )
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="👁️ Focus", style=discord.ButtonStyle.danger, custom_id="solo_focus")
    async def focus_test(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Focus test game"""
        await interaction.response.defer()
        await self.update_activity()
        
        embed = discord.Embed(
            title="👁️ FOCUS TEST",
            description="Count the circles in your mind for 10 seconds:\n🔴🔴🔴\n🔴🔴🔴\n🔴🔴🔴",
            color=0x00D9FF
        )
        embed.add_field(name="Total Circles", value="9", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="👁️ Visual Memory", style=discord.ButtonStyle.danger, custom_id="solo_visual")
    async def visual_memory(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Visual memory test"""
        await interaction.response.defer()
        await self.update_activity()
        
        grid = ["🟩", "🟥", "🟦", "🟨", "🟪", "🟧"]
        random.shuffle(grid)
        
        embed = discord.Embed(
            title="👁️ VISUAL MEMORY TEST",
            description=f"Memorize this grid:\n{' '.join(grid[:3])}\n{' '.join(grid[3:6])}",
            color=0x00D9FF
        )
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="🔍 Spot Difference", style=discord.ButtonStyle.danger, custom_id="solo_spot")
    async def spot_difference(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Spot the difference game"""
        await interaction.response.defer()
        await self.update_activity()
        
        embed = discord.Embed(
            title="🔍 SPOT THE DIFFERENCE",
            description="Image A: 🎯🎯🎯\nImage B: 🎯🎯🎪\n\nDifference: The third emoji",
            color=0x00D9FF
        )
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="⚡ Reflex", style=discord.ButtonStyle.danger, custom_id="solo_reflex")
    async def reflex_trainer(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Reflex trainer game"""
        await interaction.response.defer()
        await self.update_activity()
        
        embed = discord.Embed(
            title="⚡ REFLEX TRAINER",
            description="Reflex time: ~150ms\nPress the button as fast as you can!",
            color=0x00D9FF
        )
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="✍️ Speed Typer", style=discord.ButtonStyle.danger, custom_id="solo_typer")
    async def speed_typer(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Speed typing game"""
        await interaction.response.defer()
        await self.update_activity()
        
        words = ["GAMING", "DISCORD", "PYTHON", "AMAZING", "ELITE"]
        text = " ".join(random.sample(words, 3))
        
        embed = discord.Embed(
            title="✍️ SPEED TYPER",
            description=f"Type this: **{text}**",
            color=0x00D9FF
        )
        embed.add_field(name="Characters", value=f"{len(text)}", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="🎨 Color Blindness", style=discord.ButtonStyle.danger, custom_id="solo_colorblind")
    async def color_blindness_test(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Color blindness test"""
        await interaction.response.defer()
        await self.update_activity()
        
        embed = discord.Embed(
            title="🎨 COLOR BLINDNESS TEST",
            description="Can you see the number in these dots?\n🔴🔴🔴🔴\n🔴🟠🟠🔴\n🔴🟠🟠🔴\n🔴🔴🔴🔴",
            color=0x00D9FF
        )
        embed.add_field(name="Answer", value="||8||", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="🍀 Lucky Draw", style=discord.ButtonStyle.secondary, custom_id="solo_lucky")
    async def lucky_number_draw(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Lucky number draw game"""
        await interaction.response.defer()
        await self.update_activity()
        
        lucky_number = random.randint(1, 100)
        
        embed = discord.Embed(
            title="🍀 LUCKY NUMBER DRAW",
            description=f"Your lucky number: **{lucky_number}**",
            color=0x00D9FF
        )
        
        if lucky_number % 7 == 0:
            embed.add_field(name="🌟 Divisible", value="By 7 - Extra lucky!", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="📈 High or Low", style=discord.ButtonStyle.secondary, custom_id="solo_higher")
    async def higher_or_lower_cards(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Higher or Lower card game"""
        await interaction.response.defer()
        await self.update_activity()
        
        card1 = random.randint(2, 14)
        card2 = random.randint(2, 14)
        
        embed = discord.Embed(
            title="📈 HIGHER OR LOWER",
            description=f"First card: **{card1}**\n\nSecond card: **{card2}**\n\nResult: {'HIGHER ⬆️' if card2 > card1 else 'LOWER ⬇️' if card2 < card1 else 'SAME ='}",
            color=0x00D9FF
        )
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="🎯 Number Guess", style=discord.ButtonStyle.secondary, custom_id="solo_numguess")
    async def number_guessing_1_100(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Number guessing game (1-100)"""
        await interaction.response.defer()
        await self.update_activity()
        
        secret_number = random.randint(1, 100)
        
        embed = discord.Embed(
            title="🎯 NUMBER GUESSING (1-100)",
            description="I'm thinking of a number between 1 and 100...",
            color=0x00D9FF
        )
        embed.add_field(name="Secret Number", value=f"||{secret_number}||", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="📖 Page 4 ➡️", style=discord.ButtonStyle.secondary, custom_id="solo_page4")
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Navigate to page 4"""
        await interaction.response.defer()
        await self.update_activity()
        
        embed = discord.Embed(
            title="🕹️ SOLO ARCADE - PAGE 4/4",
            description="Final set of amazing games!",
            color=0x00D9FF
        )
        embed.add_field(name="Available Games", value="Games 39-50 to complete your collection", inline=False)
        
        from cogs.solo_manager import SoloGamePage4View
        await interaction.followup.send(embed=embed, view=SoloGamePage4View(self.user_id, self.channel_id, self.bot))

class SoloGamePage4View(discord.ui.View):
    """Solo arcade games - Page 4 (Buttons 39-50)"""
    
    def __init__(self, user_id: int, channel_id: int, bot):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.channel_id = channel_id
        self.bot = bot
    
    async def update_activity(self):
        """Update last activity timestamp in database"""
        try:
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE game_channels SET last_activity = NOW() WHERE channel_id = $1",
                    self.channel_id
                )
        except Exception as e:
            logger.error(f"❌ Failed to update activity: {e}", exc_info=True)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Verify only the authorized user can interact"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ This is not your solo session!",
                ephemeral=True
            )
            return False
        return True
    
    @discord.ui.button(label="♠️ Blackjack", style=discord.ButtonStyle.secondary, custom_id="solo_blackjack")
    async def blackjack_simulator(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Blackjack simulator"""
        await interaction.response.defer()
        await self.update_activity()
        
        player_cards = [random.randint(2, 11), random.randint(2, 11)]
        player_total = sum(player_cards)
        
        dealer_cards = [random.randint(2, 11), random.randint(2, 11)]
        dealer_total = sum(dealer_cards)
        
        result = "BLACKJACK! 🎉" if player_total == 21 else "WIN! 🎊" if player_total > dealer_total else "LOSE ❌"
        
        embed = discord.Embed(
            title="♠️ BLACKJACK SIMULATOR",
            description=f"Your cards: {player_cards[0]} + {player_cards[1]} = **{player_total}**",
            color=0x00D9FF
        )
        embed.add_field(name="Dealer", value=f"{dealer_total}", inline=False)
        embed.add_field(name="Result", value=result, inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="🎲 Dice Duel", style=discord.ButtonStyle.secondary, custom_id="solo_diceduel")
    async def dice_duel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Dice duel game"""
        await interaction.response.defer()
        await self.update_activity()
        
        player_roll = random.randint(1, 6)
        bot_roll = random.randint(1, 6)
        
        result = "YOU WIN! 🎉" if player_roll > bot_roll else "BOT WINS ❌" if bot_roll > player_roll else "TIE 🤝"
        
        embed = discord.Embed(
            title="🎲 DICE DUEL",
            description=f"Your roll: **{player_roll}**\nBot roll: **{bot_roll}**",
            color=0x00D9FF
        )
        embed.add_field(name="Result", value=result, inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="🃏 Card Guess", style=discord.ButtonStyle.secondary, custom_id="solo_cardguess")
    async def card_guess(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Card guessing game"""
        await interaction.response.defer()
        await self.update_activity()
        
        suits = ["♠️ Spades", "♥️ Hearts", "♦️ Diamonds", "♣️ Clubs"]
        correct_suit = random.choice(suits)
        wrong_suits = [s for s in suits if s != correct_suit]
        options = [correct_suit] + random.sample(wrong_suits, 2)
        random.shuffle(options)
        
        view = CardGuessView(correct_suit)
        embed = discord.Embed(
            title="🃏 CARD GUESS",
            description="What suit is the card?",
            color=0x00D9FF
        )
        
        for idx, option in enumerate(options, 1):
            embed.add_field(name=f"Option {idx}", value=option, inline=False)
        
        await interaction.followup.send(embed=embed, view=view)
    
    @discord.ui.button(label="🏆 Achievement", style=discord.ButtonStyle.secondary, custom_id="solo_achievement")
    async def achievement_unlocked(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Achievement unlocked game"""
        await interaction.response.defer()
        await self.update_activity()
        
        achievements = [
            "🏆 First Steps - Played your first game",
            "⭐ Speed Racer - Completed 5 games",
            "🎯 Accuracy Master - Got 10 correct answers",
            "🔥 Hot Streak - Won 3 games in a row",
            "💎 Legendary - Played all games",
        ]
        
        achievement = random.choice(achievements)
        
        embed = discord.Embed(
            title="🏆 ACHIEVEMENT UNLOCKED",
            description=achievement,
            color=0x00D9FF
        )
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="💎 Treasure", style=discord.ButtonStyle.secondary, custom_id="solo_treasure")
    async def treasure_hunt(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Treasure hunt game"""
        await interaction.response.defer()
        await self.update_activity()
        
        treasures = ["💎 Diamond", "🥇 Gold Coins", "👑 Crown", "💍 Ring", "📿 Pearls", "🗝️ Ancient Key"]
        found_treasure = random.choice(treasures)
        
        embed = discord.Embed(
            title="💎 TREASURE HUNT",
            description=f"You found: **{found_treasure}**",
            color=0x00D9FF
        )
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="🚪 Escape Room", style=discord.ButtonStyle.secondary, custom_id="solo_escape")
    async def escape_room_puzzle(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Escape room puzzle"""
        await interaction.response.defer()
        await self.update_activity()
        
        puzzles = [
            {"puzzle": "What opens with a key but has no lock?", "answer": "A piano"},
            {"puzzle": "I have cities but no houses. What am I?", "answer": "A map"},
            {"puzzle": "What can travel the world while staying in a corner?", "answer": "A stamp"},
            {"puzzle": "What has hands but cannot clap?", "answer": "A clock"},
        ]
        
        puzzle = random.choice(puzzles)
        
        embed = discord.Embed(
            title="🚪 ESCAPE ROOM PUZZLE",
            description=puzzle["puzzle"],
            color=0x00D9FF
        )
        embed.add_field(name="Answer", value=f"||{puzzle['answer']}||", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="🎭 Riddle", style=discord.ButtonStyle.secondary, custom_id="solo_riddle")
    async def riddle_solver(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Riddle solver game"""
        await interaction.response.defer()
        await self.update_activity()
        
        riddles = [
            {"riddle": "The more you take, the more you leave behind. What am I?", "answer": "Footsteps"},
            {"riddle": "I'm light as a feather, yet the strongest person can't hold me for five minutes. What am I?", "answer": "Your breath"},
            {"riddle": "What can be cracked, made, told, and played?", "answer": "A joke"},
            {"riddle": "I have a face and two hands, but no arms or legs. What am I?", "answer": "A clock"},
        ]
        
        riddle = random.choice(riddles)
        
        embed = discord.Embed(
            title="🎭 RIDDLE SOLVER",
            description=riddle["riddle"],
            color=0x00D9FF
        )
        embed.add_field(name="Answer", value=f"||{riddle['answer']}||", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="🔤 Emoji Puzzle", style=discord.ButtonStyle.secondary, custom_id="solo_emoji")
    async def emoji_puzzle(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Emoji puzzle game"""
        await interaction.response.defer()
        await self.update_activity()
        
        puzzles = [
            {"puzzle": "🚗 + 🚗 = ?", "answer": "A traffic jam"},
            {"puzzle": "👨 + 👰 = ?", "answer": "A wedding"},
            {"puzzle": "☀️ + 🌙 = ?", "answer": "Day and night"},
            {"puzzle": "🍕 + 🍕 = ?", "answer": "Pizza party"},
        ]
        
        puzzle = random.choice(puzzles)
        
        embed = discord.Embed(
            title="🎭 EMOJI PUZZLE",
            description=puzzle["puzzle"],
            color=0x00D9FF
        )
        embed.add_field(name="Answer", value=f"||{puzzle['answer']}||", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="⚡ Math Sprint", style=discord.ButtonStyle.secondary, custom_id="solo_mathsprint")
    async def fast_math_sprint(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Fast math sprint game"""
        await interaction.response.defer()
        await self.update_activity()
        
        problems = []
        for _ in range(3):
            a = random.randint(1, 20)
            b = random.randint(1, 20)
            op = random.choice(["+", "-", "*"])
            
            if op == "+":
                result = a + b
            elif op == "-":
                result = a - b
            else:
                result = a * b
            
            problems.append(f"{a} {op} {b} = {result}")
        
        embed = discord.Embed(
            title="⚡ FAST MATH SPRINT",
            description="\n".join(problems),
            color=0x00D9FF
        )
        embed.add_field(name="Score", value="3/3 ✅", inline=False)
        
        await interaction.followup.send(embed=embed)

# Helper Views for Answer Selection

class RPSChoiceView(discord.ui.View):
    def __init__(self, bot_choice: str):
        super().__init__(timeout=None)
        self.bot_choice = bot_choice
    
    @discord.ui.button(label="🪨 Rock", style=discord.ButtonStyle.primary, custom_id="rps_rock")
    async def rock(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.play_rps(interaction, "Rock")
    
    @discord.ui.button(label="📄 Paper", style=discord.ButtonStyle.primary, custom_id="rps_paper")
    async def paper(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.play_rps(interaction, "Paper")
    
    @discord.ui.button(label="✂️ Scissors", style=discord.ButtonStyle.primary, custom_id="rps_scissors")
    async def scissors(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.play_rps(interaction, "Scissors")
    
    async def play_rps(self, interaction: discord.Interaction, user_choice: str):
        await interaction.response.defer()
        result = "TIE 🤝"
        if (user_choice == "Rock" and self.bot_choice == "Scissors") or \
           (user_choice == "Paper" and self.bot_choice == "Rock") or \
           (user_choice == "Scissors" and self.bot_choice == "Paper"):
            result = "YOU WIN! 🎉"
        elif user_choice != self.bot_choice:
            result = "BOT WINS ❌"
        embed = discord.Embed(title="✂️ ROCK PAPER SCISSORS", description=f"Your choice: **{user_choice}**\nBot choice: **{self.bot_choice}**", color=0x00D9FF)
        embed.add_field(name="Result", value=result, inline=False)
        await interaction.followup.send(embed=embed)

class TriviaView(discord.ui.View):
    def __init__(self, correct_answer: str):
        super().__init__(timeout=None)
        self.correct_answer = correct_answer
    
    @discord.ui.button(label="1", style=discord.ButtonStyle.primary, custom_id="tri_1")
    async def opt1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_answer else "❌ WRONG!", ephemeral=True)
    
    @discord.ui.button(label="2", style=discord.ButtonStyle.primary, custom_id="tri_2")
    async def opt2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_answer else "❌ WRONG!", ephemeral=True)
    
    @discord.ui.button(label="3", style=discord.ButtonStyle.primary, custom_id="tri_3")
    async def opt3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_answer else "❌ WRONG!", ephemeral=True)

class CapitalsView(discord.ui.View):
    def __init__(self, correct_answer: str, country: str):
        super().__init__(timeout=None)
        self.correct_answer = correct_answer
        self.country = country
    
    @discord.ui.button(label="1", style=discord.ButtonStyle.primary, custom_id="cap_1")
    async def opt1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(f"✅ CORRECT!" if button.label == self.correct_answer else "❌ WRONG!", ephemeral=True)
    
    @discord.ui.button(label="2", style=discord.ButtonStyle.primary, custom_id="cap_2")
    async def opt2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(f"✅ CORRECT!" if button.label == self.correct_answer else "❌ WRONG!", ephemeral=True)
    
    @discord.ui.button(label="3", style=discord.ButtonStyle.primary, custom_id="cap_3")
    async def opt3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(f"✅ CORRECT!" if button.label == self.correct_answer else "❌ WRONG!", ephemeral=True)

class FlagsView(discord.ui.View):
    def __init__(self, correct_answer: str, flag: str):
        super().__init__(timeout=None)
        self.correct_answer = correct_answer
        self.flag = flag
    
    @discord.ui.button(label="1", style=discord.ButtonStyle.primary, custom_id="flg_1")
    async def opt1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_answer else "❌ WRONG!", ephemeral=True)
    
    @discord.ui.button(label="2", style=discord.ButtonStyle.primary, custom_id="flg_2")
    async def opt2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_answer else "❌ WRONG!", ephemeral=True)
    
    @discord.ui.button(label="3", style=discord.ButtonStyle.primary, custom_id="flg_3")
    async def opt3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_answer else "❌ WRONG!", ephemeral=True)

class MathView(discord.ui.View):
    def __init__(self, correct_answer: str):
        super().__init__(timeout=None)
        self.correct_answer = correct_answer
    
    @discord.ui.button(label="1", style=discord.ButtonStyle.primary, custom_id="mth_1")
    async def opt1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_answer else "❌ WRONG!", ephemeral=True)
    
    @discord.ui.button(label="2", style=discord.ButtonStyle.primary, custom_id="mth_2")
    async def opt2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_answer else "❌ WRONG!", ephemeral=True)
    
    @discord.ui.button(label="3", style=discord.ButtonStyle.primary, custom_id="mth_3")
    async def opt3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_answer else "❌ WRONG!", ephemeral=True)

class ProverbsView(discord.ui.View):
    def __init__(self, correct_answer: str, proverb: str):
        super().__init__(timeout=None)
        self.correct_answer = correct_answer
        self.proverb = proverb
    
    @discord.ui.button(label="1", style=discord.ButtonStyle.primary, custom_id="prv_1")
    async def opt1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_answer else "❌ WRONG!", ephemeral=True)
    
    @discord.ui.button(label="2", style=discord.ButtonStyle.primary, custom_id="prv_2")
    async def opt2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_answer else "❌ WRONG!", ephemeral=True)
    
    @discord.ui.button(label="3", style=discord.ButtonStyle.primary, custom_id="prv_3")
    async def opt3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_answer else "❌ WRONG!", ephemeral=True)

class AnagramsView(discord.ui.View):
    def __init__(self, correct_answer: str, scrambled: str):
        super().__init__(timeout=None)
        self.correct_answer = correct_answer
        self.scrambled = scrambled
    
    @discord.ui.button(label="1", style=discord.ButtonStyle.primary, custom_id="ana_1")
    async def opt1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_answer else "❌ WRONG!", ephemeral=True)
    
    @discord.ui.button(label="2", style=discord.ButtonStyle.primary, custom_id="ana_2")
    async def opt2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_answer else "❌ WRONG!", ephemeral=True)
    
    @discord.ui.button(label="3", style=discord.ButtonStyle.primary, custom_id="ana_3")
    async def opt3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_answer else "❌ WRONG!", ephemeral=True)

class PatternView(discord.ui.View):
    def __init__(self, correct_answer: str, pattern_type: str):
        super().__init__(timeout=None)
        self.correct_answer = correct_answer
        self.pattern_type = pattern_type
    
    @discord.ui.button(label="1", style=discord.ButtonStyle.primary, custom_id="pat_1")
    async def opt1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_answer else "❌ WRONG!", ephemeral=True)
    
    @discord.ui.button(label="2", style=discord.ButtonStyle.primary, custom_id="pat_2")
    async def opt2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_answer else "❌ WRONG!", ephemeral=True)
    
    @discord.ui.button(label="3", style=discord.ButtonStyle.primary, custom_id="pat_3")
    async def opt3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_answer else "❌ WRONG!", ephemeral=True)

class ColorMatchView(discord.ui.View):
    def __init__(self, correct_emoji: str, color_name: str):
        super().__init__(timeout=None)
        self.correct_emoji = correct_emoji
        self.color_name = color_name
    
    @discord.ui.button(label="1", style=discord.ButtonStyle.primary, custom_id="col_1")
    async def opt1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_emoji else "❌ WRONG!", ephemeral=True)
    
    @discord.ui.button(label="2", style=discord.ButtonStyle.primary, custom_id="col_2")
    async def opt2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_emoji else "❌ WRONG!", ephemeral=True)
    
    @discord.ui.button(label="3", style=discord.ButtonStyle.primary, custom_id="col_3")
    async def opt3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_emoji else "❌ WRONG!", ephemeral=True)

class ShadowView(discord.ui.View):
    def __init__(self, correct_object: str):
        super().__init__(timeout=None)
        self.correct_object = correct_object
    
    @discord.ui.button(label="1", style=discord.ButtonStyle.primary, custom_id="shd_1")
    async def opt1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_object else "❌ WRONG!", ephemeral=True)
    
    @discord.ui.button(label="2", style=discord.ButtonStyle.primary, custom_id="shd_2")
    async def opt2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_object else "❌ WRONG!", ephemeral=True)
    
    @discord.ui.button(label="3", style=discord.ButtonStyle.primary, custom_id="shd_3")
    async def opt3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_object else "❌ WRONG!", ephemeral=True)

class CardGuessView(discord.ui.View):
    def __init__(self, correct_suit: str):
        super().__init__(timeout=None)
        self.correct_suit = correct_suit
    
    @discord.ui.button(label="1", style=discord.ButtonStyle.primary, custom_id="crd_1")
    async def opt1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_suit else "❌ WRONG!", ephemeral=True)
    
    @discord.ui.button(label="2", style=discord.ButtonStyle.primary, custom_id="crd_2")
    async def opt2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_suit else "❌ WRONG!", ephemeral=True)
    
    @discord.ui.button(label="3", style=discord.ButtonStyle.primary, custom_id="crd_3")
    async def opt3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ CORRECT!" if button.label == self.correct_suit else "❌ WRONG!", ephemeral=True)

class SoloCreationView(discord.ui.View):
    """Main button to create solo arcade session"""
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🕹️ Create Solo Session", style=discord.ButtonStyle.primary, custom_id="solo_create_session")
    async def create_solo_session(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Create a private solo gaming channel for the user"""
        
        await interaction.response.defer(ephemeral=True)
        
        user_id = interaction.user.id
        guild_id = interaction.guild.id
        
        try:
            logger.info(f"👤 User {interaction.user} ({user_id}) creating solo session in guild {guild_id}")
            
            category_name = "🎮 Gaming Hub"
            category = discord.utils.get(interaction.guild.categories, name=category_name)
            
            if not category:
                logger.error(f"❌ Gaming Hub category not found in guild {guild_id}")
                await interaction.followup.send(
                    "❌ Gaming Hub category not found! Please run `/setup_gaming_hub` first.",
                    ephemeral=True
                )
                return
            
            channel_name = f"🎮-{interaction.user.name}-arcade"
            
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                interaction.client.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            }
            
            solo_channel = await interaction.guild.create_text_channel(
                channel_name,
                category=category,
                overwrites=overwrites,
                topic=f"Private solo arcade for {interaction.user.name}"
            )
            
            logger.info(f"✅ Created solo channel {solo_channel.id} for user {user_id}")
            
            async with interaction.client.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO game_channels (guild_id, channel_id, host_id, lobby_type, last_activity)
                    VALUES ($1, $2, $3, $4, NOW())
                    """,
                    guild_id, solo_channel.id, user_id, "solo"
                )
            
            logger.info(f"📊 Recorded solo channel {solo_channel.id} in database")
            
            welcome_embed = discord.Embed(
                title="🕹️ SOLO ARCADE GRID - PAGE 1/4",
                description="Select a game from the grid below to start playing!",
                color=0x00D9FF
            )
            welcome_embed.add_field(
                name="📊 Game Selection",
                value="Click any button to play that game. Each game is unique! Navigate pages with arrows.",
                inline=False
            )
            welcome_embed.set_footer(text="Your channel will auto-delete after 15 minutes of inactivity")
            
            await solo_channel.send(embed=welcome_embed, view=SoloGamePage1View(user_id, solo_channel.id, interaction.client))
            
            logger.info(f"✅ Game grid deployed to solo channel {solo_channel.id}")
            
            await interaction.followup.send(
                f"✅ Solo session created! Check {solo_channel.mention}",
                ephemeral=True
            )
        
        except Exception as e:
            logger.error(f"❌ Failed to create solo session: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ Failed to create solo session: {str(e)}",
                ephemeral=True
            )

class SoloManager(commands.Cog):
    """Solo Arcade Manager Cog"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_load(self):
        logger.info("✅ SoloManager cog loaded successfully")

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(SoloManager(bot))
    logger.info("✅ SoloManager cog registered")
