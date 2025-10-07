import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # ต้องมีเพื่อดึง role ของสมาชิก

bot = commands.Bot(command_prefix="!", intents=intents)

# ----------------- ตั้งค่า Channel -----------------
CHANNEL_INFO = 1418797464277880962       # ข้อมูล 1–8
CHANNEL_CASE_MID = 1384152611585921128    # ข้อมูลสรุป 2–8
CHANNEL_CASE_RESULT = 1384157602060959907 # ข้อมูล 9–13
VOICE_CHANNEL_ID = 1424990144263487490

# ----------------- Role ที่สามารถใช้คำสั่งนี้ -----------------
ADMIN_ROLE_NAMES = ["[ Court Official | เจ้าพนักงานศาล ]"]  # ใส่ชื่อ Role ที่อนุญาต

# ----------------- บอทออนไลน์ -----------------
@bot.event
async def on_ready():
    print(f"✅ บอท {bot.user} ออนไลน์แล้ว!")
    
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel and isinstance(channel, discord.VoiceChannel):
        await channel.connect()
        print("🎤 บอทเข้าห้องเสียงเรียบร้อยแล้ว")
    else:
        print("❌ Channel นี้ไม่ใช่ voice channel หรือไม่พบ")

# ----------------- คำสั่งกรอกคดี -----------------
@bot.command()
async def กรอกคดี(ctx):
    # 🔒 ตรวจสอบว่าเป็น Admin Role หรือไม่
    author_roles = [role.name for role in ctx.author.roles]
    if not any(role in ADMIN_ROLE_NAMES for role in author_roles):
        await ctx.send("❌ คุณไม่มีสิทธิ์ในการใช้คำสั่งนี้ (เฉพาะ Admin เท่านั้น)")
        return

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    # 1️⃣ ถามหมายเลขคดี
    await ctx.send("📄 กรุณากรอกหมายเลขคดี:")
    try:
        msg_case = await bot.wait_for("message", check=check, timeout=300)
        case_number = msg_case.content
    except asyncio.TimeoutError:
        await ctx.send("❌ หมดเวลาตอบคำถาม โปรดลองใหม่ด้วยคำสั่ง !กรอกคดี")
        return

    # 2️⃣ คำถามทีละข้อ
    questions = [
        f"[ ชื่อผู้กระทำผิด | Name ] (คดี #{case_number}) :",
        f"[ ยศผู้กระทำผิด | Ranking ] (คดี #{case_number}) :",
        f"[ กระผิดในข้อหา | Reason ] (คดี #{case_number}) :",
        f"[ บทลงทันฑ์ | Blame ] (คดี #{case_number}) :",
        f"[ ผู้พิพากษาคดี | Judiciary ] (คดี #{case_number}) :",
        f"[ อัยการผู้รับผิดชอบ | Attorney ] (คดี #{case_number}) :",
        f"[ ผู้ประสานงาน | Judge Staff ] (คดี #{case_number}) :",
        f"[ กระทำความผิดครั้งที่ | Strike ] (คดี #{case_number}) :"
    ]

    answers = []
    for q in questions:
        await ctx.send(q)
        try:
            msg = await bot.wait_for("message", check=check, timeout=600)
        except asyncio.TimeoutError:
            await ctx.send("❌ หมดเวลาตอบคำถาม โปรดลองใหม่ด้วยคำสั่ง !กรอกคดี")
            return
        answers.append(msg.content)

    # ----------------- ข้อ 1–8 -----------------
    text_info = f"""
# บันทึกคดี #{case_number} / 68
[ ชื่อผู้กระทำผิด | Name ] : {answers[0]}
[ ยศผู้กระทำผิด | Ranking ] : {answers[1]}
[ กระผิดในข้อหา | Reason ] : {answers[2]}
[ บทลงทันฑ์ | Blame ] : {answers[3]}
[ ผู้พิพากษาคดี | Judiciary ] : {answers[4]}
[ อัยการผู้รับผิดชอบ | Attorney ] : {answers[5]}
[ ผู้ประสานงาน | Judge Staff ] : {answers[6]}
"""

    # ----------------- ข้อมูลสรุป 2–8 -----------------
    text_mid = f"""
# [ ข้อมูลสรุปคดี #{case_number} ]
[ ชื่อผู้กระทำผิด | Name ] : {answers[0]}
[ ยศผู้กระทำผิด | Ranking ] : {answers[1]}
[ กระผิดในข้อหา | Reason ] : {answers[2]}
[ บทลงทันฑ์ | Blame ] : {answers[3]}
[ ผู้พิพากษาคดี | Judiciary ] : {answers[4]}
[ อัยการผู้รับผิดชอบ | Attorney ] : {answers[5]}
[ ผู้ประสานงาน | Judge Staff ] : {answers[6]}
"""

    # ----------------- ข้อ 9–13 -----------------
    text_result = f"""
[ ชื่อผู้ต้องหา | Username ] : {answers[0]}
[ ยศผู้ต้องหา | Rank ] : {answers[1]}
[ กระผิดในข้อหา | Reason ] : {answers[2]}
[ บทลงทันฑ์ | Blame ] : {answers[3]}
[ กระทำความผิดครั้งที่ | Strike ] : {answers[7]}
"""

    # ----------------- ส่งข้อความ -----------------
    channel_info = bot.get_channel(CHANNEL_INFO)
    channel_mid = bot.get_channel(CHANNEL_CASE_MID)
    channel_result = bot.get_channel(CHANNEL_CASE_RESULT)

    missing = [str(c.id) for c in [channel_info, channel_mid, channel_result] if c is None]
    if missing:
        await ctx.send(f"❌ ไม่พบ Channel ID: {', '.join(missing)}")
        return

    await channel_info.send(text_info)
    await channel_mid.send(text_mid)
    await channel_result.send(text_result)

    await ctx.send(f"✅ บันทึกคดี #{case_number} ถูกส่งไปยังทุกช่องเรียบร้อยแล้ว!")

# ✅ เปลี่ยน TOKEN ตรงนี้ให้เป็น ENV จริงเมื่อใช้งานจริง
bot.run("MTM5MzQ0MDUwMzc3NjY3ODAwOQ.GqJpen.xOhBPMlsshGG1jIJihtb7Loptt9-W37DlgsvrQ")
