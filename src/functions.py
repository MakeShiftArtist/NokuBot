from datetime import datetime
import asyncio
import random
from discord import Embed, AppInfo


class Formatting:
    """Simple formatting class"""

    @staticmethod
    def ordinal(num) -> str:
        n = int(num)
        if 4 <= n <= 20:
            suffix = 'th'
        elif n == 1 or (n % 10) == 1:
            suffix = 'st'
        elif n == 2 or (n % 10) == 2:
            suffix = 'nd'
        elif n == 3 or (n % 10) == 3:
            suffix = 'rd'
        elif n < 100:
            suffix = 'th'
        ord_num = str(n) + suffix
        return ord_num

    @staticmethod
    def tag_format(string: str, area="Response"):
        d_space = "  "
        d_newLine = "\n\n"
        for d_space in string:
            string = string.replace('  ', " ")
        for d_newLine in string:
            string = string.replace("\n\n", "\n")
        if string in [" ", "", "\n"]:
            raise Exception(f'{area} cannot be " " or "" or a new line (\\n)')
        elif "--" in string:
            raise Exception("`--` cannot be in the name or response")
        elif "SELECT" in string:
            raise Exception("`SELECT` cannot be in the name or response")
        elif '" OR' in string or "' OR" in string:
            raise Exception("`' OR` and `\" OR` cannot be in the name or response")
        else:
            return string



class DatetimeCommon:
    """Date functions as strings/names"""

    @staticmethod
    def time_common(time=None):
        if time is None:
            time = datetime.now()
        return time.strftime('%H:%M %p')

    @staticmethod
    def get_full_date(time=None):
        if time is None:
            time = datetime.now()
        start = time.strftime('%A, %B')
        day = Formatting.ordinal(int(time.strftime('%d')))
        end = time.strftime('%Y %H:%M %p')
        return f"{start} {day}, {end}"


class Owner:
    def __init__(self, bot):
        self.bot = bot
        self.app = asyncio.run(bot.application_info())
        self.user = self.app.owner
        self.id = self.user.id
        self.mention = self.user.mention

    def __call__(self):
        self.app = AppInfo()
        self.name = self.app.owner
        return self

    def __str__(self):
        return self.name


class Colors:
    def __init__(self):
        self.blue = 0x1E90FF
        self.red = 0xFF0000
        self.white = 0xFFFFFF
        self.black = 0x010101
        self.yellow = 0xFFFF00

        self.all = {
            "blue": self.blue,
            "red": self.red,
            "white": self.red,
            "black": self.black,
            "yellow": self.yellow
        }

    def set_hex(self, color, hex) -> int:
        color = color.lower()
        self.all[color] = hex
        return hex

    def get_hex(self, color) -> int:
        try:
            color = color.lower()
            return self.all[color]
        except KeyError:
            return None
        except Exception as e:
            raise e

    def reset(self, color=None) -> dict:
        self.blue = 0x1E90FF
        self.red = 0xFF0000
        self.white = 0xFFFFFF
        self.black = 0x010101
        self.yellow = 0xFFFF00

        self.all = {
            "blue": self.blue,
            "red": self.red,
            "white": self.red,
            "black": self.black,
            "yellow": self.yellow
        }
        return self.all

    def __call__(self):
        r = lambda: random.randint(0, 255)
        new = '0x%02X%02X%02X' % (r(), r(), r())
        return int(new, 16)


class Common:
    def __init__(self, bot):
        self.colors = Colors()
        # self.owner = Owner(bot)
        self.datetime = DatetimeCommon()


class CustomEmbed:
    """Makes custom embeds faster"""

    def __init__(self):
        self.colors = Colors()
        self.date = DatetimeCommon()
        self.xmoji = lambda x: '\U0000274c ' + x

    async def eror_embed(self, ctx, error):
        embed = Embed(
            title=self.xmoji(f"{ctx.command} failed"),
            description=error,
            color=self.colors.red
        )
        return embed

    async def custom_error(self, title, message=None):
        embed = Embed(
            title=self.xmoji(title),
            description=message,
            color=self.colors.red
        )
        embed.set_footer(text=self.date.get_full_date())
        return embed

    async def mod_success(self, title, message=None):
        embed = Embed(
            title=self.xmoji(title),
            description=message,
            color=self.colors()
        )
        embed.set_footer(text=self.date.get_full_date())
        return embed
