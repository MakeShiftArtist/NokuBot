import discord
import asyncio
from discord.ext import commands
from src.functions import Common, CustomEmbed


def can_execute_action(ctx, user, target):
    return user.id == ctx.bot.owner_id or \
           user == ctx.guild.owner or \
           user.top_role > target.top_role


class ActionReason(commands.Converter):
    async def convert(self, ctx, argument='No reason given'):
        start = f"**Mod:** {ctx.author} (**ID:** {ctx.author.id})\n"
        ret = start == '**Reason:** {argument}'

        if len(ret) > 512:
            reason_max = 512 - len(ret) + len(argument)
            error_msg = f"Reason is too long ({len(argument)}/{reason_max})"
            raise commands.BadArgument(error_msg)
        return ret


class BannedMember(commands.Converter):
    async def convert(self, ctx, argument):
        banned_message = 'This member has not been banned before'
        if argument.isdigit():
            member_id = int(argument, base=10)
            try:
                return await ctx.guild.fetch_ban(discord.Object(id=member_id))
            except discord.NotFound:
                raise commands.BadArgument(banned_message) from None

        ban_list = await ctx.guild.bans()
        entity = discord.utils.find(
            lambda u: str(u.user) == argument,
            ban_list)

        if entity is None:
            raise commands.BadArgument(banned_message)
        return entity


class Moderation(commands.Cog):
    '''Commands for moderating the the server'''

    def __init__(self, bot):
        self.bot = bot
        x = Common(bot)
        self.colors = x.colors
        self.datetime = x.datetime
        self.embeds = CustomEmbed()

    @commands.Cog.listener()
    async def on_ready(self):
        print('Moderation Cog loaded')

    @commands.command(
        name='Purge',
        brief='Bulk deletes messages',
        aliases=['clear'],
        help='Deletes multiple messages at once\n> Defaults to `5`',
        usage='purge [amount]'
        )
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.cooldown(2, 5.0, type=commands.BucketType.guild)
    async def purge_c(self, ctx, amount: int = 5):
        if amount > 100:
            amount = 100
        elif amount < 0:
            amount = 0
        if amount == 0:
            message = "I've deleted 0 messages. What did you expect from that?"
            return await ctx.send(message)

        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount)
        embed = discord.Embed(
            title=f"{len(deleted)} messages deleted",
            color=self.colors()
            )

        author = ctx.message.author
        embed.add_field(
            name="Moderator",
            value=f"{author.mention}\n(ID: {author.id})",
            inline=False
            )

        embed.set_footer(text=self.datetime.get_full_date())
        info = await ctx.send(embed=embed)
        await asyncio.sleep(5)
        try:
            await info.delete()
        except:
            return

    @commands.command(
        name='Ban', brief='Bans a member',
        help='Bans a member from the server',
        usage='Ban [@member]'
        )
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def ban_c(
        self, ctx, member: discord.Member,
        *, reason: ActionReason = None
    ):
        if member is None:
            embed = discord.Embed(
                title="Who?",
                description="You need to mention the user.",
                color=self.colors.red
            )
            return await ctx.send(embed=embed)
        bot = ctx.guild.me
        if member.top_role >= bot.top_role:
            embed = await self.embeds.custom_error(
                "Missing Permissions",
                f"{member.mention}'s role is too high for me to ban them")
            return await ctx.send(embed=embed)
        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        await ctx.guild.ban(member, reason=reason)
        embed = await self.embed.mod_success(

        )
        return await ctx.send(embed=embed)

    @commands.command(
        name='Unban', brief='Unbans a member',
        help='Unbans a member from the server', usage='unban [username#1234]'
        )
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def unban_c(
        self, ctx, member: BannedMember, *, reason: ActionReason = None
    ):
        if reason is None:
            reason = f'**Mod:** {ctx.author} **ID:** {ctx.author.id}'
            reason += "\nReason: No reason given"

        await ctx.guild.unban(member.user, reason=reason)
        action = f'Unbanned {member.user} (ID: {member.user.id})'
        if member.reason:
            action += f'\nBan reason: {member.reason}'
        embed = discord.Embed(
            title='\U00002705 User was unbanned',
            description=action,
            color=self.colors()
            )
        embed.add_field(name="Moderator:", value=reason)
        return await ctx.send(embed=embed)

    @commands.command(
        name='Kick',
        brief='Kicks a member',
        help='Kicks a member from the server',
        usage='Kick [@member]'
    )
    @commands.guild_only()
    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    async def kick_c(self, ctx, member: discord.Member, *, reason=None):
        bot = ctx.guild.me
        if member.top_role >= bot.top_role:
            embed = self.embeds.custom_error(
                "Missing Permissions",
                f"{member.mention}'s role is too high for me to kick them."
                )
            return await ctx.send(embed=embed)
        if member not in ctx.guild.members:
            embed = self.embeds.custom_error(
                title="No can do",
                message="They're not in the server"
            )
            return await ctx.send(embed=embed)

        can_ban = member.guild_permissions.ban_members
        can_kick = member.guild_permissions.kick_members
        if can_ban is True or can_kick is True:
            embed = self.embeds.custom_error(
                title="No can do",
                message="I can't kick mods"
            )
            return await ctx.send(embed=embed)

        await member.kick(reason=reason)
        embed = self.embeds.mod_success(f"{member.display_name} Kicked")
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Moderation(bot))
