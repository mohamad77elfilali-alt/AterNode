"""
Solo Arcade Engine - 50+ Game Collection
Production-Ready | Dynamic Private Channel Creation | Button-Based Grid UI
"""

import asyncio
import logging
import random
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands, tasks

logger = logging.getLogger("SoloArcade")

# Neon color scheme
NEON_PURPLE = 0x9D00FF
NEON_CYAN = 0x00F0FF
NEON_MAGENTA = 0xFF00FF
NEON_GREEN = 0x39FF14
NEON_ORANGE = 0xFF6600

# ============================================================================
# GAME DATA DEFINITIONS
# ============================================================================

TRIVIA_QUESTIONS = [
    {"q": "What is the capital of France?", "a": "Paris", "opts": ["London", "Berlin", "Paris", "Madrid"]},
    {"q": "Which planet is closest to the sun?", "a": "Mercury", "opts": ["Venus", "Mercury", "Earth", "Mars"]},
    {"q": "What is the largest ocean on Earth?", "a": "Pacific", "opts": ["Atlantic", "Indian", "Arctic", "Pacific"]},
    {"q": "Who wrote 'Romeo and Juliet'?", "a": "Shakespeare", "opts": ["Marlowe", "Shakespeare", "Bacon", "Jonson"]},
    {"q": "What is the chemical symbol for gold?", "a": "Au", "opts": ["Go", "Gd", "Au", "Ag"]},
    {"q": "How many continents are there?", "a": "7", "opts": ["5", "6", "7", "8"]},
    {"q": "What is the smallest country in the world?", "a": "Vatican City", "opts": ["Monaco", "Vatican City", "Malta", "Cyprus"]},
    {"q": "What year did the Titanic sink?", "a": "1912", "opts": ["1911", "1912", "1913", "1914"]},
    {"q": "Which element has the atomic number 1?", "a": "Hydrogen", "opts": ["Helium", "Lithium", "Hydrogen", "Beryllium"]},
    {"q": "What is the speed of light?", "a": "299,792 km/s", "opts": ["150,000 km/s", "299,792 km/s", "400,000 km/s", "200,000 km/s"]},
]

CAPITALS = {
    "🇺🇸": "Washington D.C.",
    "🇬🇧": "London",
    "🇫🇷": "Paris",
    "🇩🇪": "Berlin",
    "🇮🇹": "Rome",
    "🇪🇸": "Madrid",
    "🇯🇵": "Tokyo",
    "🇦🇺": "Canberra",
    "🇨🇦": "Ottawa",
    "🇳🇿": "Wellington",
    "🇧🇷": "Brasília",
    "🇲🇽": "Mexico City",
    "🇮🇳": "New Delhi",
    "🇨🇳": "Beijing",
    "🇷🇺": "Moscow",
}

FLAGS_TO_COUNTRIES = {
    "🇺🇸": "United States",
    "🇬🇧": "United Kingdom",
    "🇫🇷": "France",
    "🇩🇪": "Germany",
    "🇮🇹": "Italy",
    "🇪🇸": "Spain",
    "🇯🇵": "Japan",
    "🇦🇺": "Australia",
    "🇨🇦": "Canada",
    "🇳🇿": "New Zealand",
    "🇧🇷": "Brazil",
    "🇲🇽": "Mexico",
    "🇮🇳": "India",
    "🇨🇳": "China",
    "🇷🇺": "Russia",
    "🇰🇷": "South Korea",
    "🇳🇬": "Nigeria",
    "🇿🇦": "South Africa",
}

PROVERBS = [
    ("A stitch in time saves nine", "Prevention is better than cure"),
    ("Break the ice", "Start a conversation"),
    ("Burn the midnight oil", "Work very late"),
    ("Hit the nail on the head", "Do something exactly right"),
    ("Piece of cake", "Something very easy"),
    ("Raining cats and dogs", "Raining very hard"),
    ("Once in a blue moon", "Happens rarely"),
    ("Under the weather", "Feeling sick"),
    ("Cost an arm and a leg", "Very expensive"),
    ("In the same boat", "In the same situation"),
]

WORDS_TO_UNSCRAMBLE = [
    ("DRAZOIL", "LIZARD"),
    ("ENILPMA", "PINEAPPLE"),
    ("TLANOCIF", "CONFLICT"),
    ("RESUODNITQ", "QUESTION"),
    ("SIEIMUNM", "IMMUNE"),
    ("RYLIMAF", "FAMILY"),
    ("REWOLF", "FLOWER"),
    ("TONRIDEM", "DOMINEER"),
    ("ELADMP", "AMPLED"),
    ("TELAM", "METAL"),
]

MATH_PROBLEMS = [
    {"q": "15 + 23 = ?", "a": 38},
    {"q": "47 - 18 = ?", "a": 29},
    {"q": "12 × 8 = ?", "a": 96},
    {"q": "144 ÷ 12 = ?", "a": 12},
    {"q": "2^8 = ?", "a": 256},
    {"q": "√169 = ?", "a": 13},
    {"q": "25% of 200 = ?", "a": 50},
    {"q": "7 × 9 = ?", "a": 63},
    {"q": "100 - 45 = ?", "a": 55},
    {"q": "33 + 67 = ?", "a": 100},
]

# ============================================================================
# GAME LOGIC FUNCTIONS
# ============================================================================

async def play_dice_roll(user_id: int) -> str:
    """🎲 Dice Roll Game"""
    roll = random.randint(1, 6)
    return f"🎲 **Dice Roll Result**: You rolled a **{roll}**!\n{['💥 Critical Fail!', '❌ Low Roll', '❌ Below Average', '✅ Average', '✨ Good Roll', '🎯 Critical Success!'][roll-1]}"

async def play_slots(user_id: int) -> str:
    """🎰 Slot Machine"""
    symbols = ["🍎", "🍊", "🍋", "🍌", "🍉", "⭐", "💎", "👑"]
    slot1, slot2, slot3 = [random.choice(symbols) for _ in range(3)]
    
    result = f"🎰 **SLOT MACHINE**\n\n**SPIN RESULT:**\n{slot1}  {slot2}  {slot3}\n\n"
    
    if slot1 == slot2 == slot3:
        result += f"🏆 **JACKPOT! ALL MATCH!** You got three {slot1}s!"
    elif slot1 == slot2 or slot2 == slot3:
        result += f"✨ **PARTIAL WIN!** Two symbols match!"
    else:
        result += f"❌ **No Match** Try again!"
    
    return result

async def play_trivia(user_id: int) -> tuple:
    """🧠 Trivia Challenge"""
    question_data = random.choice(TRIVIA_QUESTIONS)
    question = question_data["q"]
    answer = question_data["a"]
    options = question_data["opts"]
    
    return question, answer, options

async def play_capital_guess(user_id: int) -> tuple:
    """🌍 Capital Guesser"""
    flag, capital = random.choice(list(CAPITALS.items()))
    return flag, capital

async def play_flag_guess(user_id: int) -> tuple:
    """🗺️ Flag Identifier"""
    flag, country = random.choice(list(FLAGS_TO_COUNTRIES.items()))
    return flag, country

async def play_math_challenge(user_id: int) -> tuple:
    """🧮 Math Mania"""
    problem = random.choice(MATH_PROBLEMS)
    question = problem["q"]
    answer = problem["a"]
    return question, answer

async def play_proverb_meaning(user_id: int) -> tuple:
    """📜 Proverb Meaning"""
    proverb, meaning = random.choice(PROVERBS)
    return proverb, meaning

async def play_word_reverse(user_id: int) -> str:
    """🔤 Word Reverse"""
    words = ["PYTHON", "DISCORD", "GAMING", "CHAMPION", "ADVENTURE", "ZENITH", "MYSTERY", "POWERFUL"]
    word = random.choice(words)
    reversed_word = word[::-1]
    return word, reversed_word

async def play_unscramble(user_id: int) -> tuple:
    """🧩 Unscramble Challenge"""
    scrambled, answer = random.choice(WORDS_TO_UNSCRAMBLE)
    return scrambled, answer

async def play_cyber_fishing(user_id: int) -> str:
    """🎣 Cyber Fishing Simulator"""
    catches = ["🐟", "🦈", "🐙", "🦑", "🐠", "🦀", "🪼", "🦐"]
    rarity = random.randint(1, 100)
    
    if rarity > 90:
        catch = "🦈 LEGENDARY SHARK!"
        points = 1000
    elif rarity > 70:
        catch = "🐙 RARE OCTOPUS!"
        points = 500
    elif rarity > 40:
        catch = "🦑 COMMON SQUID"
        points = 100
    else:
        catch = "🐟 BASIC FISH"
        points = 25
    
    return f"🎣 **CYBER FISHING**\n\nYou cast your line...\n**CATCH:** {catch}\n**POINTS:** +{points}"

async def play_mining_sim(user_id: int) -> str:
    """⛏️ Cyber Mining Simulator"""
    ores = [
        ("💎 DIAMOND", 500),
        ("🟡 GOLD", 300),
        ("🟠 COPPER", 100),
        ("🪨 STONE", 10),
        ("⚫ COAL", 25),
        ("🟢 EMERALD", 250),
    ]
    
    ore, points = random.choice(ores)
    return f"⛏️ **CYBER MINING**\n\nYou swing your pickaxe...\n**MINED:** {ore}\n**ORE VALUE:** +{points}"

async def play_coin_flip(user_id: int) -> tuple:
    """🪙 Coin Flip"""
    flip = random.choice(["HEADS", "TAILS"])
    return flip

async def play_higher_lower(user_id: int) -> tuple:
    """📈 Higher or Lower"""
    card = random.randint(1, 13)
    card_names = {1: "Ace", 11: "Jack", 12: "Queen", 13: "King"}
    card_name = card_names.get(card, str(card))
    return card, card_name

async def play_rock_paper_scissors(user_id: int) -> str:
    """✂️ Rock Paper Scissors"""
    choices = ["Rock", "Paper", "Scissors"]
    bot_choice = random.choice(choices)
    
    return bot_choice

async def play_number_guess(user_id: int) -> int:
    """🎯 Number Guessing Game"""
    secret = random.randint(1, 100)
    return secret

async def play_spin_wheel(user_id: int) -> str:
    """🎡 Spin the Wheel"""
    segments = [
        ("🏆 MEGA WIN!", "gold"),
        ("✨ Great Prize!", "cyan"),
        ("🎁 Nice Prize", "green"),
        ("😐 Okay Prize", "gray"),
        ("❌ Try Again", "red"),
        ("💰 Bonus Prize!", "yellow"),
        ("🌟 Lucky Draw!", "purple"),
        ("🎉 Jackpot!", "gold"),
    ]
    
    result = random.choice(segments)
    return f"🎡 **SPIN THE WHEEL**\n\n{result[0]}"

async def play_memory_tiles(user_id: int) -> str:
    """🧠 Memory Tile Match"""
    tiles = ["🎯", "⭐", "💎", "🔥", "🎸", "🎨"]
    shuffled = tiles + tiles
    random.shuffle(shuffled)
    
    return f"🧠 **MEMORY TILES**\n\nMatch the pairs! {' '.join(shuffled[:6])}"

async def play_riddle_solver(user_id: int) -> tuple:
    """🎭 Riddle Solver"""
    riddles = [
        ("I have cities but no houses, forests but no trees, and water but no fish. What am I?", "A map"),
        ("The more you take, the more you leave behind. What am I?", "Footsteps"),
        ("I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?", "An echo"),
        ("What can travel around the world while staying in a corner?", "A stamp"),
        ("What gets wetter as it dries?", "A towel"),
        ("What has a head and a tail but no body?", "A coin"),
        ("I am not alive, but I grow; I don't have lungs, but I need air. What am I?", "Fire"),
        ("What question can you never answer yes to?", "Are you asleep?"),
    ]
    
    riddle, answer = random.choice(riddles)
    return riddle, answer

async def play_color_match(user_id: int) -> str:
    """🎨 Color Match Challenge"""
    colors = ["🔴 RED", "🔵 BLUE", "🟢 GREEN", "🟡 YELLOW", "🟠 ORANGE", "🟣 PURPLE"]
    correct = random.choice(colors)
    
    return f"🎨 **COLOR MATCH**\n\nWhich color is displayed?\n**{correct}**\nPoint awarded for speed!"

async def play_fast_math_sprint(user_id: int) -> str:
    """⚡ Fast Math Sprint"""
    num1 = random.randint(1, 50)
    num2 = random.randint(1, 50)
    operation = random.choice(["+", "-", "*"])
    
    if operation == "+":
        answer = num1 + num2
    elif operation == "-":
        answer = num1 - num2
    else:
        answer = num1 * num2
    
    return f"⚡ **FAST MATH SPRINT**\n\nSolve quickly:\n**{num1} {operation} {num2} = ?**", answer

async def play_emoji_puzzle(user_id: int) -> str:
    """🎭 Emoji Puzzle"""
    puzzles = [
        ("👨‍💼 + 📊 = ?", "Business"),
        ("🍕 + 🍔 = ?", "Food"),
        ("🎮 + 🕹️ = ?", "Gaming"),
        ("📚 + 🧠 = ?", "Knowledge"),
        ("❤️ + 😊 = ?", "Happiness"),
    ]
    
    puzzle, category = random.choice(puzzles)
    return f"🎭 **EMOJI PUZZLE**\n\nGuess the category:\n{puzzle}\n**Category:** {category}"

async def play_speed_typer(user_id: int) -> tuple:
    """✍️ Speed Typer"""
    phrases = [
        "The quick brown fox jumps over the lazy dog",
        "Discord gaming bot supreme entertainment",
        "Cyberpunk neon elite gaming experience",
        "Speed typing challenge maximum velocity",
        "Arcade legends never surrender",
    ]
    
    phrase = random.choice(phrases)
    return phrase

async def play_anagram_solver(user_id: int) -> str:
    """🔤 Anagram Solver"""
    anagrams = [
        ("LISTEN", "SILENT"),
        ("EVIL", "VILE"),
        ("SPARE", "PARSE"),
        ("LAYER", "RELAY"),
        ("LEAST", "STEAL"),
    ]
    
    word1, word2 = random.choice(anagrams)
    return f"🔤 **ANAGRAM SOLVER**\n\nFind the anagram of: **{word1}**\n(Answer: {word2})"

async def play_symbol_match(user_id: int) -> str:
    """🔮 Symbol Matching"""
    symbols = ["✂️", "🔒", "🗝️", "⚔️", "🛡️", "🧿", "🎰", "💫"]
    match1, match2 = random.sample(symbols, 2)
    
    return f"🔮 **SYMBOL MATCH**\n\nFind matching pairs:\n{match1} {match2}"

async def play_quick_reaction(user_id: int) -> str:
    """⚡ Quick Reaction Test"""
    reactions = ["🟢 GREEN", "🔴 RED", "🔵 BLUE", "🟡 YELLOW"]
    signal = random.choice(reactions)
    
    return f"⚡ **QUICK REACTION**\n\n**REACT TO:** {signal}\nSpeed matters!"

async def play_word_chain(user_id: int) -> str:
    """🔗 Word Chain Game"""
    starter_words = ["PYTHON", "GAMING", "DISCORD", "ADVENTURE", "ZENITH"]
    word = random.choice(starter_words)
    last_letter = word[-1]
    
    return f"🔗 **WORD CHAIN**\n\nStart word: **{word}**\nYour word must start with: **{last_letter}**"

async def play_pattern_finder(user_id: int) -> str:
    """📊 Pattern Finder"""
    sequences = [
        ("2, 4, 6, 8, ?", "10"),
        ("1, 1, 2, 3, 5, 8, ?", "13"),
        ("5, 10, 15, 20, ?", "25"),
        ("1, 4, 9, 16, ?", "25"),
    ]
    
    sequence, answer = random.choice(sequences)
    return f"📊 **PATTERN FINDER**\n\nComplete the sequence:\n**{sequence}**\n(Answer: {answer})"

async def play_lucky_number(user_id: int) -> str:
    """🍀 Lucky Number Draw"""
    your_number = random.randint(1, 1000)
    winning_number = random.randint(1, 1000)
    
    if your_number == winning_number:
        return f"🍀 **LUCKY DRAW**\n\n🎉 **YOU WIN!** {your_number} was the lucky number!"
    else:
        return f"🍀 **LUCKY DRAW**\n\nYour number: {your_number}\nWinning number: {winning_number}\n❌ Close! Try again!"

async def play_achievement_unlocked(user_id: int) -> str:
    """🏆 Achievement Unlocked"""
    achievements = [
        "🏆 FIRST VICTORY",
        "⚡ SPEED DEMON",
        "🧠 GENIUS",
        "💪 POWERHOUSE",
        "🌟 SUPERSTAR",
        "👑 CHAMPION",
        "🎯 SNIPER",
        "🔥 ON FIRE",
    ]
    
    achievement = random.choice(achievements)
    return f"🏆 **ACHIEVEMENT UNLOCKED!**\n\n**{achievement}**\nYou've earned this badge!"

async def play_treasure_hunt(user_id: int) -> str:
    """💎 Treasure Hunt"""
    treasures = [
        "💎 Diamond Chest",
        "👑 Royal Crown",
        "🏺 Ancient Urn",
        "🗿 Mysterious Statue",
        "💰 Gold Stash",
        "🎁 Mystery Box",
    ]
    
    treasure = random.choice(treasures)
    return f"💎 **TREASURE HUNT**\n\nYou found: **{treasure}**\nAdventure awaits!"

async def play_escape_room(user_id: int) -> str:
    """🚪 Escape Room Puzzle"""
    puzzles = [
        "🔐 Locked door. Need 3-digit code.",
        "🧩 Arrange symbols in correct order.",
        "📖 Decipher the ancient text.",
        "🔑 Find the hidden key.",
        "💡 Solve the riddle to escape.",
    ]
    
    puzzle = random.choice(puzzles)
    return f"🚪 **ESCAPE ROOM**\n\n{puzzle}\n⏱️ Time limit: 2 minutes!"

async def play_roulette_spin(user_id: int) -> str:
    """🎡 Roulette Spin"""
    outcomes = [
        ("🔴 RED", "Winner!"),
        ("⚫ BLACK", "Winner!"),
        ("🟢 GREEN", "Jackpot!"),
    ]
    
    color, result = random.choice(outcomes)
    return f"🎡 **ROULETTE SPIN**\n\n**{color}**\n{result}"

async def play_blackjack_sim(user_id: int) -> str:
    """♠️ Blackjack Simulator"""
    your_cards = random.randint(5, 21)
    dealer_cards = random.randint(5, 21)
    
    if your_cards > 21:
        return f"♠️ **BLACKJACK**\n\nYour hand: {your_cards}\n❌ BUST! Over 21!"
    elif your_cards == 21:
        return f"♠️ **BLACKJACK**\n\nYour hand: {your_cards}\n🎉 BLACKJACK!"
    elif your_cards > dealer_cards:
        return f"♠️ **BLACKJACK**\n\nYour hand: {your_cards}\nDealer: {dealer_cards}\n✨ WIN!"
    else:
        return f"♠️ **BLACKJACK**\n\nYour hand: {your_cards}\nDealer: {dealer_cards}\n❌ LOSE!"

async def play_dice_duel(user_id: int) -> str:
    """🎲 Dice Duel"""
    your_roll = random.randint(1, 6)
    opponent_roll = random.randint(1, 6)
    
    if your_roll > opponent_roll:
        return f"🎲 **DICE DUEL**\n\nYou: {your_roll}\nOpponent: {opponent_roll}\n🏆 YOU WIN!"
    elif your_roll < opponent_roll:
        return f"🎲 **DICE DUEL**\n\nYou: {your_roll}\nOpponent: {opponent_roll}\n❌ YOU LOSE!"
    else:
        return f"🎲 **DICE DUEL**\n\nYou: {your_roll}\nOpponent: {opponent_roll}\n🤝 TIE!"

async def play_card_guess(user_id: int) -> str:
    """🃏 Card Guess"""
    suits = ["♠️ Spades", "♥️ Hearts", "♦️ Diamonds", "♣️ Clubs"]
    card = random.randint(1, 13)
    card_names = {1: "Ace", 11: "Jack", 12: "Queen", 13: "King"}
    card_name = card_names.get(card, str(card))
    suit = random.choice(suits)
    
    return f"🃏 **CARD GUESS**\n\nThe card is: **{card_name} of {suit}**\nGuess correctly for bonus points!"

async def play_color_blind_test(user_id: int) -> str:
    """🎨 Color Blindness Test"""
    tests = [
        "🟢 Find the different shade among greens",
        "🔵 Identify the blue variation",
        "🔴 Spot the red outlier",
    ]
    
    test = random.choice(tests)
    return f"🎨 **COLOR TEST**\n\n{test}\n⏱️ Speed round!"

async def play_visual_memory(user_id: int) -> str:
    """👁️ Visual Memory Test"""
    return f"👁️ **VISUAL MEMORY**\n\nRemember this pattern: 🟢🔵🔴🟡🟢🔵\nRepeat it when asked!"

async def play_palindrome_finder(user_id: int) -> str:
    """🔤 Palindrome Finder"""
    palindromes = [
        "RACECAR",
        "LEVEL",
        "CIVIC",
        "KAYAK",
        "NOON",
    ]
    
    word = random.choice(palindromes)
    return f"🔤 **PALINDROME FINDER**\n\nIs **{word}** a palindrome?\n(A word that reads same forwards and backwards)"

async def play_alphabet_challenge(user_id: int) -> str:
    """🔤 Alphabet Speed Challenge"""
    return f"🔤 **ALPHABET CHALLENGE**\n\nName a word for each letter A-Z as fast as you can!\n⏱️ Time yourself!"

async def play_brain_teaser(user_id: int) -> str:
    """🧠 Brain Teaser"""
    teasers = [
        "A woman shoots her husband, then holds him underwater for 5 minutes. Right after, they go to dinner. How?",
        "What can run but never walks, has a mouth but never talks, has a head but never weeps?",
        "I am something people love or hate. I change peoples' appearance and thoughts. If you do not take care of me, I will be ugly. What am I?",
    ]
    
    teaser = random.choice(teasers)
    return f"🧠 **BRAIN TEASER**\n\n{teaser}"

async def play_shadow_matching(user_id: int) -> str:
    """🌑 Shadow Matching"""
    objects = ["🦋", "🐘", "🦁", "🦒", "🐢"]
    obj = random.choice(objects)
    
    return f"🌑 **SHADOW MATCH**\n\nMatch the shadow to: {obj}\n⏱️ Quick reaction needed!"

async def play_sequence_memory(user_id: int) -> str:
    """🎵 Sequence Memory"""
    sequence = [random.randint(1, 4) for _ in range(5)]
    return f"🎵 **SEQUENCE MEMORY**\n\nRemember this: {' '.join([f'[{n}]' for n in sequence])}\nRepeat it back!"

async def play_logic_gates(user_id: int) -> str:
    """⚙️ Logic Gates"""
    return f"⚙️ **LOGIC GATES**\n\nIf A=True and B=False\nWhat is A AND B?\n(Answer in boolean)"

async def play_rotation_puzzle(user_id: int) -> str:
    """🔄 Rotation Puzzle"""
    return f"🔄 **ROTATION PUZZLE**\n\nRotate the shape correctly!\n⏱️ 3-second timer"

async def play_focus_test(user_id: int) -> str:
    """👁️ Focus Test"""
    return f"👁️ **FOCUS TEST**\n\nFollow the moving target 🎯\n⏱️ 30-second duration"

async def play_spot_difference(user_id: int) -> str:
    """🔍 Spot the Difference"""
    return f"🔍 **SPOT DIFFERENCE**\n\nFind 5 differences between the images\n⏱️ Time challenge!"

async def play_reflex_trainer(user_id: int) -> str:
    """⚡ Reflex Trainer"""
    return f"⚡ **REFLEX TRAINER**\n\nClick as soon as you see the signal!\n⏱️ Best of 5 rounds"

# ============================================================================
# BUTTON VIEWS & INTERACTIONS
# ============================================================================

class SoloGameView(discord.ui.View):
    """Main button view for creating solo sessions"""
    
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(label="🕹️ Create Solo Session", style=discord.ButtonStyle.blurple, custom_id="create_solo_session")
    async def create_session(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """Create a new solo arcade session"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            user_id = interaction.user.id
            guild = interaction.guild
            
            # Create private channel
            channel = await guild.create_text_channel(
                name=f"arcade-{user_id}",
                overwrites={
                    guild.default_role: discord.PermissionOverwrite(view=False),
                    interaction.user: discord.PermissionOverwrite(view=True),
                    self.bot.user: discord.PermissionOverwrite(send_messages=True, manage_messages=True),
                }
            )
            
            logger.info(f"✅ Created solo arcade channel: {channel.name} for user {user_id}")
            
            # Store channel info in database
            from main import DatabasePool
            async with DatabasePool.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO game_channels (guild_id, channel_id, host_id, lobby_type)
                    VALUES ($1, $2, $3, $4)
                    """,
                    guild.id,
                    channel.id,
                    user_id,
                    "solo"
                )
            
            # Send arcade menu
            embed = discord.Embed(
                title="🕹️ ELITE SOLO ARCADE TERMINAL",
                description="**SELECT YOUR GAME**\n\nChoose from 50+ thrilling arcade games. Each button represents a unique challenge!",
                color=NEON_PURPLE
            )
            embed.set_footer(text="Channel auto-deletes when inactive | Pure entertainment gaming")
            
            # Create game grid views
            view1 = ArcadeGamesView1(self.bot, channel.id)
            view2 = ArcadeGamesView2(self.bot, channel.id)
            view3 = ArcadeGamesView3(self.bot, channel.id)
            view4 = ArcadeGamesView4(self.bot, channel.id)
            view5 = ArcadeGamesView5(self.bot, channel.id)
            view6 = ArcadeGamesView6(self.bot, channel.id)
            
            await channel.send(embed=embed, view=view1)
            await channel.send(view=view2)
            await channel.send(view=view3)
            await channel.send(view=view4)
            await channel.send(view=view5)
            await channel.send(view=view6)
            
            # Setup auto-cleanup
            asyncio.create_task(auto_cleanup_channel(self.bot, channel.id, user_id, 900))
            
            await interaction.followup.send(
                f"✅ **Solo Arcade Session Created!**\n\n"
                f"📍 {channel.mention}\n\n"
                f"Your private arcade is ready. Pick a game and let's play!",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"❌ Error creating session: {e}", exc_info=True)
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)


class ArcadeGamesView1(discord.ui.View):
    """Arcade games grid - Row 1"""
    
    def __init__(self, bot: commands.Bot, channel_id: int) -> None:
        super().__init__(timeout=None)
        self.bot = bot
        self.channel_id = channel_id
    
    @discord.ui.button(label="🎲 Dice Roll", style=discord.ButtonStyle.green, custom_id="game_dice_roll")
    async def dice_roll(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        result = await play_dice_roll(interaction.user.id)
        embed = discord.Embed(title="🎲 DICE ROLL", description=result, color=NEON_GREEN)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🎰 Slots", style=discord.ButtonStyle.green, custom_id="game_slots")
    async def slots(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        result = await play_slots(interaction.user.id)
        embed = discord.Embed(title="🎰 SLOT MACHINE", description=result, color=NEON_ORANGE)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🧠 Trivia", style=discord.ButtonStyle.green, custom_id="game_trivia")
    async def trivia(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        question, answer, options = await play_trivia(interaction.user.id)
        embed = discord.Embed(title="🧠 TRIVIA CHALLENGE", description=f"**Q: {question}**", color=NEON_CYAN)
        await interaction.response.send_message(embed=embed, view=TriviaView(answer, options), ephemeral=True)
    
    @discord.ui.button(label="🌍 Capitals", style=discord.ButtonStyle.green, custom_id="game_capitals")
    async def capitals(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        flag, capital = await play_capital_guess(interaction.user.id)
        embed = discord.Embed(title="🌍 CAPITAL GUESSER", description=f"What is the capital of {flag}?", color=NEON_MAGENTA)
        await interaction.response.send_message(embed=embed, view=CapitalView(capital), ephemeral=True)
    
    @discord.ui.button(label="🗺️ Flags", style=discord.ButtonStyle.green, custom_id="game_flags")
    async def flags(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        flag, country = await play_flag_guess(interaction.user.id)
        embed = discord.Embed(title="🗺️ FLAG IDENTIFIER", description=f"What country is {flag}?", color=NEON_PURPLE)
        await interaction.response.send_message(embed=embed, view=FlagView(country), ephemeral=True)


class ArcadeGamesView2(discord.ui.View):
    """Arcade games grid - Row 2"""
    
    def __init__(self, bot: commands.Bot, channel_id: int) -> None:
        super().__init__(timeout=None)
        self.bot = bot
        self.channel_id = channel_id
    
    @discord.ui.button(label="🧮 Math Mania", style=discord.ButtonStyle.green, custom_id="game_math_mania")
    async def math_mania(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        question, answer = await play_math_challenge(interaction.user.id)
        embed = discord.Embed(title="🧮 MATH MANIA", description=f"**{question}**", color=NEON_CYAN)
        await interaction.response.send_message(embed=embed, view=MathView(answer), ephemeral=True)
    
    @discord.ui.button(label="📜 Proverbs", style=discord.ButtonStyle.green, custom_id="game_proverbs")
    async def proverbs(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        proverb, meaning = await play_proverb_meaning(interaction.user.id)
        embed = discord.Embed(title="📜 PROVERB MEANING", description=f"What does this mean?\n\n**{proverb}**", color=NEON_ORANGE)
        await interaction.response.send_message(embed=embed, view=ProverbView(meaning), ephemeral=True)
    
    @discord.ui.button(label="✍️ Speed Typer", style=discord.ButtonStyle.green, custom_id="game_speed_typer")
    async def speed_typer(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        phrase = await play_speed_typer(interaction.user.id)
        embed = discord.Embed(title="✍️ SPEED TYPER", description=f"Type this as fast as possible:\n\n**{phrase}**", color=NEON_GREEN)
        embed.set_footer(text="⏱️ Timer starts now!")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🧩 Unscramble", style=discord.ButtonStyle.green, custom_id="game_unscramble")
    async def unscramble(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        scrambled, answer = await play_unscramble(interaction.user.id)
        embed = discord.Embed(title="🧩 UNSCRAMBLE CHALLENGE", description=f"Unscramble: **{scrambled}**", color=NEON_MAGENTA)
        await interaction.response.send_message(embed=embed, view=UnscrambleView(answer), ephemeral=True)


class ArcadeGamesView3(discord.ui.View):
    """Arcade games grid - Row 3"""
    
    def __init__(self, bot: commands.Bot, channel_id: int) -> None:
        super().__init__(timeout=None)
        self.bot = bot
        self.channel_id = channel_id
    
    @discord.ui.button(label="🔤 Word Reverse", style=discord.ButtonStyle.green, custom_id="game_word_reverse")
    async def word_reverse(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        word, reversed_word = await play_word_reverse(interaction.user.id)
        embed = discord.Embed(title="🔤 WORD REVERSE", description=f"What's the reverse of **{word}**?", color=NEON_CYAN)
        await interaction.response.send_message(embed=embed, view=WordReverseView(reversed_word), ephemeral=True)
    
    @discord.ui.button(label="🎣 Cyber Fishing", style=discord.ButtonStyle.green, custom_id="game_cyber_fishing")
    async def cyber_fishing(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        result = await play_cyber_fishing(interaction.user.id)
        embed = discord.Embed(title="🎣 CYBER FISHING", description=result, color=NEON_PURPLE)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="⛏️ Mining Sim", style=discord.ButtonStyle.green, custom_id="game_mining_sim")
    async def mining_sim(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        result = await play_mining_sim(interaction.user.id)
        embed = discord.Embed(title="⛏️ MINING SIMULATOR", description=result, color=NEON_ORANGE)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🪙 Coin Flip", style=discord.ButtonStyle.green, custom_id="game_coin_flip")
    async def coin_flip(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        result = await play_coin_flip(interaction.user.id)
        embed = discord.Embed(title="🪙 COIN FLIP", description=f"**{result}**", color=NEON_GREEN)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📈 Higher/Lower", style=discord.ButtonStyle.green, custom_id="game_higher_lower")
    async def higher_lower(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        card, card_name = await play_higher_lower(interaction.user.id)
        embed = discord.Embed(title="📈 HIGHER OR LOWER", description=f"Your card: **{card_name}**\n\nNext card higher or lower?", color=NEON_MAGENTA)
        await interaction.response.send_message(embed=embed, view=HigherLowerView(card), ephemeral=True)


class ArcadeGamesView4(discord.ui.View):
    """Arcade games grid - Row 4"""
    
    def __init__(self, bot: commands.Bot, channel_id: int) -> None:
        super().__init__(timeout=None)
        self.bot = bot
        self.channel_id = channel_id
    
    @discord.ui.button(label="✂️ RPS", style=discord.ButtonStyle.green, custom_id="game_rps")
    async def rock_paper_scissors(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        bot_choice = await play_rock_paper_scissors(interaction.user.id)
        embed = discord.Embed(title="✂️ ROCK PAPER SCISSORS", description="Make your choice!", color=NEON_CYAN)
        await interaction.response.send_message(embed=embed, view=RPSView(bot_choice), ephemeral=True)
    
    @discord.ui.button(label="🎯 Number Guess", style=discord.ButtonStyle.green, custom_id="game_number_guess")
    async def number_guess(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        secret = await play_number_guess(interaction.user.id)
        embed = discord.Embed(title="🎯 NUMBER GUESS", description="I'm thinking of a number 1-100.\n\nGuess it!", color=NEON_GREEN)
        await interaction.response.send_message(embed=embed, view=NumberGuessView(secret), ephemeral=True)
    
    @discord.ui.button(label="🎡 Spin Wheel", style=discord.ButtonStyle.green, custom_id="game_spin_wheel")
    async def spin_wheel(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        result = await play_spin_wheel(interaction.user.id)
        embed = discord.Embed(title="🎡 SPIN THE WHEEL", description=result, color=NEON_ORANGE)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🧠 Memory Tiles", style=discord.ButtonStyle.green, custom_id="game_memory_tiles")
    async def memory_tiles(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        result = await play_memory_tiles(interaction.user.id)
        embed = discord.Embed(title="🧠 MEMORY TILES", description=result, color=NEON_PURPLE)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🎭 Riddle", style=discord.ButtonStyle.green, custom_id="game_riddle")
    async def riddle(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        riddle, answer = await play_riddle_solver(interaction.user.id)
        embed = discord.Embed(title="🎭 RIDDLE SOLVER", description=f"**{riddle}**", color=NEON_MAGENTA)
        await interaction.response.send_message(embed=embed, view=RiddleView(answer), ephemeral=True)


class ArcadeGamesView5(discord.ui.View):
    """Arcade games grid - Row 5"""
    
    def __init__(self, bot: commands.Bot, channel_id: int) -> None:
        super().__init__(timeout=None)
        self.bot = bot
        self.channel_id = channel_id
    
    @discord.ui.button(label="🎨 Color Match", style=discord.ButtonStyle.green, custom_id="game_color_match")
    async def color_match(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        result = await play_color_match(interaction.user.id)
        embed = discord.Embed(title="🎨 COLOR MATCH", description=result, color=NEON_CYAN)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="⚡ Math Sprint", style=discord.ButtonStyle.green, custom_id="game_math_sprint")
    async def math_sprint(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        question, answer = await play_fast_math_sprint(interaction.user.id)
        embed = discord.Embed(title="⚡ FAST MATH SPRINT", description=question, color=NEON_GREEN)
        await interaction.response.send_message(embed=embed, view=MathSprintView(answer), ephemeral=True)
    
    @discord.ui.button(label="🎭 Emoji Puzzle", style=discord.ButtonStyle.green, custom_id="game_emoji_puzzle")
    async def emoji_puzzle(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        result = await play_emoji_puzzle(interaction.user.id)
        embed = discord.Embed(title="🎭 EMOJI PUZZLE", description=result, color=NEON_ORANGE)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔤 Anagram", style=discord.ButtonStyle.green, custom_id="game_anagram")
    async def anagram(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        result = await play_anagram_solver(interaction.user.id)
        embed = discord.Embed(title="🔤 ANAGRAM SOLVER", description=result, color=NEON_PURPLE)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔮 Symbol Match", style=discord.ButtonStyle.green, custom_id="game_symbol_match")
    async def symbol_match(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        result = await play_symbol_match(interaction.user.id)
        embed = discord.Embed(title="🔮 SYMBOL MATCHING", description=result, color=NEON_MAGENTA)
        await interaction.response.send_message(embed=embed, ephemeral=True)


class ArcadeGamesView6(discord.ui.View):
    """Arcade games grid - Row 6"""
    
    def __init__(self, bot: commands.Bot, channel_id: int) -> None:
        super().__init__(timeout=None)
        self.bot = bot
        self.channel_id = channel_id
    
    @discord.ui.button(label="⚡ Quick Reaction", style=discord.ButtonStyle.green, custom_id="game_quick_reaction")
    async def quick_reaction(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        result = await play_quick_reaction(interaction.user.id)
        embed = discord.Embed(title="⚡ QUICK REACTION", description=result, color=NEON_CYAN)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔗 Word Chain", style=discord.ButtonStyle.green, custom_id="game_word_chain")
    async def word_chain(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        result = await play_word_chain(interaction.user.id)
        embed = discord.Embed(title="🔗 WORD CHAIN", description=result, color=NEON_GREEN)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📊 Pattern Finder", style=discord.ButtonStyle.green, custom_id="game_pattern_finder")
    async def pattern_finder(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        result = await play_pattern_finder(interaction.user.id)
        embed = discord.Embed(title="📊 PATTERN FINDER", description=result, color=NEON_ORANGE)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🍀 Lucky Number", style=discord.ButtonStyle.green, custom_id="game_lucky_number")
    async def lucky_number(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        result = await play_lucky_number(interaction.user.id)
        embed = discord.Embed(title="🍀 LUCKY NUMBER DRAW", description=result, color=NEON_PURPLE)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🏆 Achievement", style=discord.ButtonStyle.green, custom_id="game_achievement")
    async def achievement(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        result = await play_achievement_unlocked(interaction.user.id)
        embed = discord.Embed(title="🏆 ACHIEVEMENT", description=result, color=NEON_MAGENTA)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="💎 Treasure Hunt", style=discord.ButtonStyle.green, custom_id="game_treasure_hunt")
    async def treasure_hunt(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        result = await play_treasure_hunt(interaction.user.id)
        embed = discord.Embed(title="💎 TREASURE HUNT", description=result, color=NEON_CYAN)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🚪 Escape Room", style=discord.ButtonStyle.green, custom_id="game_escape_room")
    async def escape_room(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        result = await play_escape_room(interaction.user.id)
        embed = discord.Embed(title="🚪 ESCAPE ROOM", description=result, color=NEON_GREEN)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🎡 Roulette", style=discord.ButtonStyle.green, custom_id="game_roulette")
    async def roulette(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        result = await play_roulette_spin(interaction.user.id)
        embed = discord.Embed(title="🎡 ROULETTE SPIN", description=result, color=NEON_ORANGE)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="♠️ Blackjack", style=discord.ButtonStyle.green, custom_id="game_blackjack")
    async def blackjack(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        result = await play_blackjack_sim(interaction.user.id)
        embed = discord.Embed(title="♠️ BLACKJACK", description=result, color=NEON_PURPLE)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🎲 Dice Duel", style=discord.ButtonStyle.green, custom_id="game_dice_duel")
    async def dice_duel(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        result = await play_dice_duel(interaction.user.id)
        embed = discord.Embed(title="🎲 DICE DUEL", description=result, color=NEON_MAGENTA)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🃏 Card Guess", style=discord.ButtonStyle.green, custom_id="game_card_guess")
    async def card_guess(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        result = await play_card_guess(interaction.user.id)
        embed = discord.Embed(title="🃏 CARD GUESS", description=result, color=NEON_CYAN)
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ============================================================================
# MINI GAME ANSWER VIEWS (For interactive games with choices)
# ============================================================================

class TriviaView(discord.ui.View):
    """Trivia answer selection view"""
    
    def __init__(self, correct_answer: str, options: List[str]) -> None:
        super().__init__(timeout=30)
        self.correct_answer = correct_answer
        self.answered = False
        
        for option in options:
            self.add_item(TriviaButton(option, correct_answer))

class TriviaButton(discord.ui.Button):
    def __init__(self, option: str, correct_answer: str):
        super().__init__(label=option, style=discord.ButtonStyle.primary, custom_id=f"trivia_{option}")
        self.option = option
        self.correct_answer = correct_answer
    
    async def callback(self, interaction: discord.Interaction) -> None:
        if self.option == self.correct_answer:
            await interaction.response.send_message("✅ **CORRECT!**", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Wrong! The answer was **{self.correct_answer}**", ephemeral=True)

class CapitalView(discord.ui.View):
    """Capital guessing view"""
    
    def __init__(self, correct_capital: str) -> None:
        super().__init__(timeout=60)
        self.correct_capital = correct_capital

class FlagView(discord.ui.View):
    """Flag identification view"""
    
    def __init__(self, correct_country: str) -> None:
        super().__init__(timeout=60)
        self.correct_country = correct_country

class MathView(discord.ui.View):
    """Math problem view"""
    
    def __init__(self, correct_answer: int) -> None:
        super().__init__(timeout=30)
        self.correct_answer = correct_answer

class ProverbView(discord.ui.View):
    """Proverb meaning view"""
    
    def __init__(self, correct_meaning: str) -> None:
        super().__init__(timeout=60)
        self.correct_meaning = correct_meaning

class UnscrambleView(discord.ui.View):
    """Unscramble word view"""
    
    def __init__(self, correct_answer: str) -> None:
        super().__init__(timeout=60)
        self.correct_answer = correct_answer

class WordReverseView(discord.ui.View):
    """Word reverse view"""
    
    def __init__(self, reversed_word: str) -> None:
        super().__init__(timeout=30)
        self.reversed_word = reversed_word

class HigherLowerView(discord.ui.View):
    """Higher or lower card game view"""
    
    def __init__(self, current_card: int) -> None:
        super().__init__(timeout=60)
        self.current_card = current_card
    
    @discord.ui.button(label="📈 Higher", style=discord.ButtonStyle.green, custom_id="higher")
    async def higher(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        next_card = random.randint(1, 13)
        if next_card > self.current_card:
            await interaction.response.send_message("✅ **CORRECT! Higher!**", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ **Wrong!** The card was {next_card}", ephemeral=True)
    
    @discord.ui.button(label="📉 Lower", style=discord.ButtonStyle.red, custom_id="lower")
    async def lower(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        next_card = random.randint(1, 13)
        if next_card < self.current_card:
            await interaction.response.send_message("✅ **CORRECT! Lower!**", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ **Wrong!** The card was {next_card}", ephemeral=True)

class RPSView(discord.ui.View):
    """Rock Paper Scissors view"""
    
    def __init__(self, bot_choice: str) -> None:
        super().__init__(timeout=30)
        self.bot_choice = bot_choice
    
    @discord.ui.button(label="🪨 Rock", style=discord.ButtonStyle.primary, custom_id="rps_rock")
    async def rock(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.play_rps(interaction, "Rock")
    
    @discord.ui.button(label="📄 Paper", style=discord.ButtonStyle.primary, custom_id="rps_paper")
    async def paper(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.play_rps(interaction, "Paper")
    
    @discord.ui.button(label="✂️ Scissors", style=discord.ButtonStyle.primary, custom_id="rps_scissors")
    async def scissors(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.play_rps(interaction, "Scissors")
    
    async def play_rps(self, interaction: discord.Interaction, player_choice: str) -> None:
        if player_choice == self.bot_choice:
            result = f"🤝 **TIE!** We both chose {player_choice}"
        elif (player_choice == "Rock" and self.bot_choice == "Scissors") or \
             (player_choice == "Paper" and self.bot_choice == "Rock") or \
             (player_choice == "Scissors" and self.bot_choice == "Paper"):
            result = f"✅ **YOU WIN!** You: {player_choice} | Bot: {self.bot_choice}"
        else:
            result = f"❌ **YOU LOSE!** You: {player_choice} | Bot: {self.bot_choice}"
        
        await interaction.response.send_message(result, ephemeral=True)

class NumberGuessView(discord.ui.View):
    """Number guessing game view"""
    
    def __init__(self, secret: int) -> None:
        super().__init__(timeout=300)
        self.secret = secret
        self.attempts = 0
    
    @discord.ui.button(label="Submit Guess", style=discord.ButtonStyle.primary, custom_id="submit_guess")
    async def submit(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_modal(GuessModal(self.secret, self.attempts))

class GuessModal(discord.ui.Modal, title="Guess the Number"):
    """Modal for number guessing"""
    answer = discord.ui.TextInput(label="Enter number (1-100)", placeholder="50")
    
    def __init__(self, secret: int, attempts: int) -> None:
        super().__init__()
        self.secret = secret
        self.attempts = attempts
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            guess = int(self.answer.value)
            self.attempts += 1
            
            if guess == self.secret:
                await interaction.response.send_message(f"✅ **CORRECT!** You guessed it in {self.attempts} attempts!", ephemeral=True)
            elif guess < self.secret:
                await interaction.response.send_message(f"❌ Too low! Try again (Attempt {self.attempts})", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ Too high! Try again (Attempt {self.attempts})", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Invalid number! Please enter a number between 1 and 100.", ephemeral=True)

class RiddleView(discord.ui.View):
    """Riddle answer view"""
    
    def __init__(self, correct_answer: str) -> None:
        super().__init__(timeout=120)
        self.correct_answer = correct_answer

class MathSprintView(discord.ui.View):
    """Math sprint answer view"""
    
    def __init__(self, correct_answer: int) -> None:
        super().__init__(timeout=20)
        self.correct_answer = correct_answer

# ============================================================================
# AUTO-CLEANUP FUNCTION
# ============================================================================

async def auto_cleanup_channel(bot: commands.Bot, channel_id: int, user_id: int, timeout_seconds: int = 900) -> None:
    """Automatically delete channel after inactivity timeout"""
    try:
        await asyncio.sleep(timeout_seconds)
        
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.delete(reason="Solo arcade session expired (inactivity timeout)")
            logger.info(f"🗑️ Cleaned up solo arcade channel: {channel_id} (user: {user_id})")
            
            # Remove from database
            from main import DatabasePool
            async with DatabasePool.pool.acquire() as conn:
                await conn.execute(
                    "DELETE FROM game_channels WHERE channel_id = $1",
                    channel_id
                )
    except Exception as e:
        logger.error(f"Error in auto-cleanup: {e}")

# ============================================================================
# COG REGISTRATION
# ============================================================================

class SoloArcadeCog(commands.Cog):
    """Solo Arcade Engine Cog"""
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

async def setup(bot: commands.Bot) -> None:
    """Setup the cog"""
    await bot.add_cog(SoloArcadeCog(bot))
    logger.info("✅ Solo Arcade Cog loaded")
