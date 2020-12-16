import os
import json
from discord.ext import commands
import discord
from src.functions import CustomEmbed

embeds = CustomEmbed()


intents = discord.Intents.all()
allowed_mentions = discord.AllowedMentions(everyone=False)
client = commands.Bot(
    command_prefix=commands.when_mentioned_or('-'),
    case_insensitive=True,
    intents=intents,
    allowed_mentions=allowed_mentions
    )
client.remove_command('help')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


@client.event
async def on_ready():
    print(f'Bot signed in as {client.user}')
    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Game("@NokuBot help")
    )


@client.command(hidden=True)
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send("Logging off...")
    await ctx.bot.logout()


@shutdown.error
async def shutdown_error(ctx, error):
    return


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.NotOwner):
        return
    elif isinstance(error, commands.CommandOnCooldown):
        time = round(error.retry_after*100)/100
        error = f"Command is on cooldown for {time} seconds"
        try:
            embed = embeds.eror_embed(ctx, error)
            return await ctx.send(embed=embed)
        except Exception as e:
            return print(e)
    else:
        try:
            embed = embeds.eror_embed(ctx, error)
            return await ctx.send(embed=embed)
        except Exception as e:
            return print(e)


with open("tokens.json") as f:
    data = json.load(f)
    client.run(data["discord"])
