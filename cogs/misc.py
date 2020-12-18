from discord.ext import commands
from src import database
from src.functions import Colors, Formatting
from discord import Embed
import re


class Checks:
    @staticmethod
    def manage_tags():
        def predicate(ctx):
            return ctx.author.guild_permissions.administrator or \
                ctx.author.guild_permissions.manage_messages
        return commands.check(predicate)


class Reactions:
    def __init__(self):
        self.vote = self.Vote()
        self.gfx = self.GFX()
        self.pings = self.Pings()
        self.verified = self.Verified()

    class Pings:
        def __init__(self):
            self.msg = 784988275739328533
            self.emoji = "❗"
            self.role = 784981350125797447

    class GFX:
        def __init__(self):
            self.msg = 784979092209795102
            self.emoji = '🎨'
            self.role = 784977776314155028

    class Verified:
        def __init__(self):
            self.msg = 783972046358839317
            self.emoji = 784017531874312223
            self.role_id = 783807170898296872
            self.role = None

    class Vote:
        def __init__(self):
            self.msg = 784975971748020224
            self.emoji = 784948095908970496
            self.role = 784948645044027422


class Misc(commands.Cog):
    """
    Miscellaneous Commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.reactions = Reactions()
        self.colors = Colors()

    @commands.Cog.listener()
    async def on_ready(self):
        print('Misc Cog loaded')
        database.createRolesPersist()
        database.createTags()
        database.createTables()
        self.guild = self.bot.guilds[0]
        role = self.guild.get_role(self.reactions.verified.role_id)
        self.reactions.verified.role = role

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if self.reactions.verified.role in member.roles:
            return
        else:
            data = database.getuserroles(member.id)
            if data != []:
                await member.add_roles(self.reactions.verified.role, "Verified")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == self.reactions.verified.msg:
            try:
                if payload.emoji.id == self.reactions.verified.emoji:
                    if self.reactions.verified.role in payload.member.roles:
                        return
                    await payload.member.add_roles(
                        self.reactions.verified.role,
                        reason="Verified"
                        )
                    database.setuserrole(
                        payload.member.id, self.reactions.verified.role.id
                        )
                else:
                    pass
            except AttributeError:
                return

        elif payload.message_id == self.reactions.vote.msg:
            try:
                if payload.emoji.id == self.reactions.vote.emoji:
                    role = payload.member.guild.get_role(self.reactions.vote.role)
                    if role in payload.member.roles:
                        return
                    await payload.member.add_roles(
                        role,
                        reason="Reacted to be voter"
                        )
            except AttributeError:
                return

        elif payload.message_id == self.reactions.gfx.msg:
            try:
                if payload.emoji.name == self.reactions.gfx.emoji:
                    role = payload.member.guild.get_role(self.reactions.gfx.role)
                    if role in payload.member.roles:
                        return
                    await payload.member.add_roles(
                        role,
                        reason="Reacted to be voter"
                        )
            except AttributeError:
                return

        elif payload.message_id == self.reactions.pings.msg:
            try:
                if payload.emoji.name == self.reactions.pings.emoji:
                    role = payload.member.guild.get_role(self.reactions.pings.role)
                    if role in payload.member.roles:
                        return
                    await payload.member.add_roles(
                        role,
                        reason="Reacted to be voter"
                        )
            except AttributeError:
                return

    @commands.command(
        name="Embed", brief="Creates a custom embed",
        help="Creates a custom embed with a title, description and fields.",
        usage="[title] <description>\n<field title | field description>"
        )
    @commands.is_owner()
    async def send_embed(self, ctx, title=None, *, desc=None):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        if title is None:
            return await ctx.send("You need a title for an embed")

        if desc is None:
            desc = ""
        extra = desc.split("\n")
        embed = Embed(
            title=title,
            description=extra[0],
            color=self.colors()
            )

        for field in extra[1:]:
            data = re.split(r"((?<!\\)(\s\|\s|\s\||\|\s|\|))", field)
            regex = re.compile(r'(\s\|\s|\s\||\|\s|\|)')
            filtered = [i for i in data if not regex.match(i)]
            if len(filtered) == 1:
                embed.add_field(
                    name="Field",
                    value=filtered[0],
                    inline=False
                    )
            else:
                print(filtered)
                if filtered[0] == "":
                    filtered[0] = "Field"
                embed.add_field(name=filtered[0], value="\n".join(filtered[1:]), inline=False)
        embed.set_footer(text=ctx.author)
        return await ctx.send(embed=embed)

    @commands.group(
        name="Tag", brief="Custom tags command",
        help="Lets you create a tag, delete a tag, or change a tag.",
        usage="tag <create | change | delete>",
        invoke_without_command=True, case_insensitive=True
        )
    @commands.check_any(commands.is_owner(), Checks.manage_tags())
    async def tag_group(self, ctx, arg):
        try:
            name = Formatting.tag_format(arg, "Name")
        except Exception as e:
            return await ctx.send(e)
        response = database.getTag(name)
        try:
            return await ctx.send(response[0])
        except IndexError:
            return await ctx.send(f"Tag {arg} does not exist")

    @tag_group.command(
        name="create", brief="Creates a tag",
        usage="`tag create [tag name] [tag response]`",
        help="Creates a new tag for `-tag`"
        )
    @commands.check_any(commands.is_owner(), Checks.manage_tags())
    async def make_tag(self, ctx, name=None, *, value=None):
        if value is None or value is None:
            return await ctx.send("You need a name and a response to create a tag")
        try:
            name = Formatting.tag_format(name, "Name")
            name = Formatting.tag_format(value)
        except Exception as e:
            return await ctx.send(e)
        try:
            exists = database.getTag(name)
            if not exists:
                database.makeTag(name, value, ctx.author.id)
            else:
                return await ctx.send(f"Tag {name} already exists")
        except Exception as error:
            return await ctx.send(error)

        return await ctx.send(f'Tag: {name} created')

    @tag_group.command(
        name="delete", brief="Deletes a tag",
        help="Deletes a tag from the list of tags. This cannot be undone.",
        usage="tag delete [tag name]", aliases=['remove', 'del']
        )
    @commands.check_any(commands.is_owner(), Checks.manage_tags())
    async def delete_tag(self, ctx, name=None):
        if name is None:
            return await ctx.send("You need a name for the tag you want to delete")
        try:
            name = Formatting.tag_format(name, "Name")
        except Exception as e:
            return await ctx.send(e)
        try:
            response = database.deleteTag(name)
            return await ctx.send(response)
        except Exception as error:
            return await ctx.send(error)

    @tag_group.command(
        name="Change", brief="Lets you edit a tag",
        help="Edits a tag from the current list of tags",
        usage="tag change [tag name] [tag response]",
        alises=['edit']
        )
    @commands.check_any(commands.is_owner(), Checks.manage_tags())
    async def edit_tag(self, ctx, name=None, value=None):
        if name is None or value is None:
            return await ctx.send("I need a name and a new response to edit a tag")
        try:
            name = Formatting.tag_format(name, "Name")
            name = Formatting.tag_format(value)
        except Exception as e:
            return await ctx.send(e)
        try:
            database.getTag(name)
            exists = True
        except Exception:
            database.makeTag(name, value, ctx.author.id)
            exists = False
            pass
        finally:
            if exists:
                return await ctx.send("Tag {name} was edited")

def setup(bot):
    bot.add_cog(Misc(bot))
