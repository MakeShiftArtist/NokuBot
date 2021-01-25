from discord.ext import commands
from discord import Embed
from src.functions import Colors


class HelpObject:
    """
> `[arg]` = Required
> `<arg>` = Optional
    """

    def __init__(self, bot):
        self.color = Colors()
        self.bot = bot

    def __call__(self, ctx, prefix="-"):
        embed = Embed(
            title="Help",
            description=HelpObject.__doc__,
            color=self.color()
        )
        for cog in self.bot.cogs:
            if cog == "Help":
                continue
            cog = self.bot.cogs[cog]
            runnable = cog.cog_check(ctx)
            if runnable:
                embed.add_field(
                    name=cog.qualified_name,
                    value=cog.description,
                    inline=False
                )
        embed.set_footer(text=f"{prefix}help <category | command>")
        return embed

    async def category(self, ctx, category: str):
        cog = self.bot.get_cog(category.capitalize())
        if cog.qualified_name == "Help":
            return self(ctx)
        embed = Embed(
            title=cog.qualified_name,
            description=cog.description,
            color=self.color()
        )
        cmds = cog.get_commands()
        for cmd in cmds:
            if cmd.hidden:
                continue

            for check in cmd.checks:
                try:
                    runnable = await check(ctx)
                except TypeError:
                    runnable = check(ctx)

            if not runnable:
                continue
            embed.add_field(
                name=cmd.name,
                value=cmd.brief,
                inline=False
                )

        embed.set_footer(text="-help <category | command>")
        return embed

    async def group(self, ctx, group: str):
        return self()

    async def command(self, ctx, cmd):
        if cmd.hidden:
            return self()
        checks = cmd.checks
        can_do = True
        for check in checks:
            try:
                can_do = await check(ctx)
            except Exception:
                can_do = check(ctx)
            if can_do is False:
                break
        if can_do:
            embed = Embed(
                title=cmd.name.capitalize(),
                description=cmd.help,
                color=self.color()
            )
            embed.add_field(
                name="Usage", value=f"-{cmd.name} {cmd.usage}"
            )
            embed.set_footer(text=f"In {cmd.cog.qualified_name}")
            return embed


class Help(commands.Cog):
    """
    > `<arg>` = Required argument
    > `[arg]` = NOT Required argument
    """

    def __init__(self, bot):
        self.bot = bot
        self.help = HelpObject(bot)

    @commands.group(name="Help")
    async def help(self, ctx, *, arg=None):
        if arg is None:
            return await ctx.send(embed=self.help(ctx))
        elif arg.capitalize() in self.bot.cogs:
            embed = await self.help.category(ctx, arg)
            return await ctx.send(embed=embed)
        else:
            cmd = self.bot.get_command(arg)
            if cmd is None:
                return await ctx.send(embed=self.help(ctx))
            else:
                embed = await self.help.command(ctx, cmd)
                return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
