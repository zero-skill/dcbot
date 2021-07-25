import discord
from discord.embeds import Embed
from discord.ext import commands
import datetime
from urllib import parse, request
import re
import os
import youtube_dl
from discord.ext.commands import guild_only
from discord.utils import get

TOKEN = os.getenv('TOKEN')
PREFIX = os.getenv('PREFIX')

bot=commands.Bot(command_prefix=PREFIX, description='Bot for development')

#CUSTOM HELP
@bot.command()
async def helpme(ctx):
    embed = Embed(title="Help", description="List of commands",timestamp=datetime.datetime.utcnow(), color=discord.Colour.dark_orange())
    embed.add_field(name=f"{PREFIX}help", value="Shows this help message", inline=False)
    embed.add_field(name=f"{PREFIX}hola", value="Gives a hello message", inline=False)
    embed.add_field(name=f"{PREFIX}ok", value="Gives a ok message", inline=False)
    embed.add_field(name=f"{PREFIX}info", value="Gives the info of the current server", inline=False)
    embed.add_field(name=f"{PREFIX}chstatus [verb]", value="Change the status of the bot", inline=False)
    embed.add_field(name=f"{PREFIX}youtube [search]", value="Search youtube, return first result", inline=False)
    embed.add_field(name=f"{PREFIX}ytlist [search]", value="Return the fivest result", inline=False)
    await ctx.send(embed=embed)
    
#responde al saludo
@bot.command(help="Responde al saludo del usuario")
async def hola(ctx):
    await ctx.send('hello '+ctx.author.mention+' ¿Que tal?')

@bot.command(help="Test the bot saying ok")
async def ok(ctx):
    await ctx.send('okei gugul')

# GET INFO OF THE SERVER
@bot.command(help="Get info of the current server")
async def info(ctx):
    embed=discord.Embed(
        title=f"{ctx.guild.name}",
        description="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
        timestamp=datetime.datetime.utcnow(),
        color=discord.Color.blue())
    embed.set_author(name="Bot info")
    embed.add_field(name="Server created at", value=f"{ctx.guild.created_at}")
    embed.add_field(name="Server owner", value=f"{ctx.guild.owner}")
    embed.add_field(name="Server region",value=f"{ctx.guild.region}")
    embed.add_field(name="Server members", value=f"{ctx.guild.member_count}")
    embed.add_field(name="Server ID", value=f"{ctx.guild.id}")
    embed.add_field(name="Server channels", value=f"{len(ctx.guild.channels)}")
    """embed.set_thumbnail(url="")"""
    await ctx.send(embed=embed)

# TTS
@bot.command(help="Text to speech",description="say anything")
async def tts(ctx, *, text):
    await ctx.send(f"{text}",tts=True)
#KICK FROM THE SERVER
@bot.command(help="Kick a user from the server")
async def kick(ctx, user: discord.Member):
    await ctx.send(f"{user.mention} has been kicked from the server")
    await user.kick()

#BAN FROM THE SERVER
@bot.command(help="Ban a user from the server")
async def ban(ctx, user: discord.Member):
    await ctx.send(f"{user.mention} has been banned from the server")
    await user.ban()

#UNBAN FROM THE SERVER
@bot.command(help="This shit doesnt work. Unban a user from the server")
async def notban(ctx, *, user):
    try:
        user = await commands.converter.UserConverter().convert(ctx, user)
    except:
        await ctx.send("Error: user could not be found!")
        return

    try:
        bans = tuple(ban_entry.user for ban_entry in await ctx.guild.bans())
        if user in bans:
            await ctx.guild.unban(user, reason="Responsible moderator: "+ str(ctx.author))
        else:
            await ctx.send("User not banned!")
            return

    except discord.Forbidden:
        await ctx.send("I do not have permission to unban!")
        return

    except:
        await ctx.send("Unbanning failed!")
        return

    await ctx.send(f"Successfully unbanned {user.mention}!")

# CHANGE THE PRESENCE OF THE BOT TO LISTENING {SONG}
@bot.command(help="Change the status of the bot",description="Listening <something>")
async def chlisten(ctx, *, verb:str):
    embed=discord.Embed(
        title="Cambiando status",
        description=f"{verb}",
        timestamp=datetime.datetime.utcnow(),
        color=discord.Color.green())
    await ctx.send(embed=embed)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{verb}"))

# CHANGE THE PRESENCE OF THE BOT TO GAMING {GAME}
@bot.command(help="Change the status of the bot",description="Playing <somegame>")
async def chgame(ctx, *, verb:str):
    embed=discord.Embed(
        title="Cambiando status",
        description=f"{verb}",
        timestamp=datetime.datetime.utcnow(),
        color=discord.Color.green())
    await ctx.send(embed=embed)
    game = discord.Game(name=f"{verb}")
    await bot.change_presence(status=discord.Status.idle, activity=game)

# CONNECT TO AUDIO CHANNEL
@bot.command(help="Connect to the audio channel")
async def join(ctx):
    channel= ctx.author.voice.channel
    if not channel:
        await ctx.send(f"{ctx.author.mention} you have to be in a voice channel to use this command")
        return
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

# DISCONNECT AUDIO CHANNEL
@bot.command(help="Disconnect from the audio channel")
async def leave(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.disconnect()

# PLAY A SONG
@bot.command(help="Play a song from youtube")
async def play(ctx,url:str):
    active_song = os.path.isfile("song.mp3")
    try:
        if active_song:
            os.remove("song.mp3")
            print("La cancion se ha removido")
    except PermissionError:
        print("Hay una cancion reproduciendose")
        await ctx.send("There is a song playing")
        return 
    await ctx.send("Todo listo ")
    voice = get(bot.voice_clients, guild=ctx.guild)
    youtube_dl_options = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(youtube_dl_options) as ydl:
        print("Descargando cancion")
        ydl.download([url])
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renombrando archivo {name}")
            os.rename(name, "song.mp3")
            print("Archivo renombrado")
    voice.play(discord.FFmpegPCMAudio('song.mp3'), after=lambda e: print('Ha terminado', e))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.5

    name_song = name.rsplit("-", 2)
    await ctx.send(f"Reproduciendo {name_song[0]}")

            
#youtube commands
@bot.command(help='Search on youtube',description="Get the first result of a query")
async def youtube(ctx, *, search):
    query_string = parse.urlencode({'search_query': search})
    html_content = request.urlopen('http://www.youtube.com/results?' + query_string)
    # print(html_content.read().decode())
    search_results = re.findall(r"watch\?v=(\S{11})", html_content.read().decode())
    print(search_results)
    await ctx.send('https://www.youtube.com/watch?v=' + search_results[0])

#DEVUELVE LOS 5 PRIMEROS RESULTADOS DE UNA BUSQUEDA EN YOUTUBE
@bot.command(help="Top search on youtube",description="Get the fivest results of a query")
async def ytlist(ctx, *, search):
    query_string = parse.urlencode({'search_query': search})
    query_url = 'http://www.youtube.com/results?' + query_string
    html_content = request.urlopen(query_url)
    search_results = re.findall(r"watch\?v=(\S{11})", html_content.read().decode())
    result_url1 = 'https://www.youtube.com/watch?v=' + search_results[0]
    result_url2 = 'https://www.youtube.com/watch?v=' + search_results[1]
    result_url3 = 'https://www.youtube.com/watch?v=' + search_results[2]
    result_url4 = 'https://www.youtube.com/watch?v=' + search_results[3]
    result_url5 = 'https://www.youtube.com/watch?v=' + search_results[4]
    embed= discord.Embed(title="Busqueda rapida de YouTube",
        description="Buscaste "+f"{search}",
        timestamp=datetime.datetime.utcnow(),
        color=discord.Color.dark_purple())
    embed.add_field(name="Número de Resultados", value=f"{len(search_results)}")
    embed.add_field(name="1==>", value=f"{result_url1}", inline=False)
    embed.add_field(name="2==>", value=f"{result_url2}", inline=False)
    embed.add_field(name="3==>", value=f"{result_url3}", inline=False)
    embed.add_field(name="4==>", value=f"{result_url4}", inline=False)
    embed.add_field(name="5==>", value=f"{result_url5}", inline=False)
    await ctx.send(embed=embed)

        
#Events
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name=(f"{PREFIX}"+"command")))

#ANTI UWU METHOD
@bot.listen('on_message')
async def delete_uwu(message):
    if "uwu" in message.content or "Uwu" in message.content or "UWU" in message.content or "UwU" in message.content or "uwU" in message.content:
        print(f"{message.author.mention}"+" dijo " + f"{message.content}")
        embed=discord.Embed(
            title="ALERTA",
            description="Dijiste uwu perro ql",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.red())
        embed.add_field(name="Usuario", value=f"{message.author}")
        embed.add_field(name="Mensaje", value=f"{message.content}")
        embed.add_field(name="Advertencia",value="Para la proxima te vai kickeao",inline=False)
        await message.channel.send(embed=embed)
        await message.delete()

#LOG DE MENSAJES BORRADOS
@bot.event
async def on_message_delete(message):
    author=message.author
    content=message.content
    print(f"Se ha borrado el mensaje de {author} que decia <{content}>")

bot.run(TOKEN)