import os
from collections import OrderedDict

import discord

import dotenv
import dataset
from discord import *
import pymysql
dotenv.load_dotenv()

TOKEN=os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
bot=discord.Bot(intents=intents)
# db: dataset.Database = dataset.connect('sqlite:///db.sqlite')
db: dataset.Database = dataset.connect()
print(f'Connected to {db.url}')
#db: dataset.Database = dataset.connect("mysql://root:IMuzJeVcnQquFnlxDQOciwKWjuhtHEKk@mysql.railway.internal:3306/railway")
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
@bot.event
async def on_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
    if after.channel is not None:
        print(f'{member.name} has joined {after.channel.name} channel')
        setvc_create = None
        for x in db[str(member.guild.id)]:
            x: OrderedDict
            setvc_create = x.get('setvc_create')
            if not setvc_create == None:
                break
            # print(x.get('setvc_create'))
        # table: dataset.Table = db[str(member.guild.id)]
        # if table['setvc_create'] == str(after.channel.id):
        if after.channel.id == int(setvc_create):
            # before.channel: discord.VoiceChannel
            vc1 = await member.guild.create_voice_channel(f'{member.name}のVC',
                                                          overwrites=after.channel.overwrites,
                                                          category=after.channel.category)
            await member.move_to(vc1)
            table = db[str(member.guild.id)]
            table.upsert(dict(vcid=str(vc1.id), vcowner=str(member.id)), ['id'])
    if before.channel is not None and len(before.channel.members) == 0:
        table: dataset.Table = db[str(member.guild.id)]
        for x in table:
            x: OrderedDict
            vcid = x.get('vcid')
            vcowner = x.get('vcowner')
            if vcid == str(before.channel.id):
                await before.channel.delete()
                table.delete(id=x.get('id'))
                break

@bot.slash_command(name='setvcforcreate', description='Set voice channel for create')
@commands.option('vcid', 'Voice channel id', type=str)
async def setvcforcreate(ctx: ApplicationContext, vc: str):
    if not ctx.author.guild_permissions.administrator:
        return await ctx.respond('You do not have administrator permission.')
    table = db[str(ctx.guild.id)]
    table.upsert(dict(setvc_create=str(vc)), ['id'])
    await ctx.respond(f'Set voice channel for create {vc}')
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    # if message.content.startswith('.debug'):
    #     for x in db[str(message.guild.id)]:
    #         x: OrderedDict
    #         print(x.get('setvc_create'))

bot.run(TOKEN)
