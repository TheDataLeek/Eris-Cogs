import random

from redbot.core import commands

BaseCog = getattr(commands, "Cog", object)


nums = [':zero:', ':one:', ':two:', ':three:', ':four:', ':five:', ':six:', ':seven:', ':eight:', ':nine:']

class MineSweeper(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def msnew(self, ctx, width: int = 9, length: int = 9, bombs: int=10):
        if bombs >= width * length:
            await ctx.send('Need to have less bombs than locations!')
            return

        field = [
            [0 for _ in range(width)]
            for _ in range(length)
        ]

        for _ in range(bombs):
            while True:
                xloc = random.randint(0, width - 1)
                yloc = random.randint(0, length - 1)
                if field[yloc][xloc] == 0:
                    field[yloc][xloc] = '||:boom:||'
                    break

        for i in range(width):
            for j in range(length):
                if field[j][i] == '||:boom:||':
                    continue

                num_bombs = 0
                for idelta in range(-1, 2):
                    for jdelta in range(-1, 2):
                        new_i = i + idelta
                        new_j = j + jdelta

                        if new_i < 0 or new_j < 0 or new_i >= width or new_j >= length:
                            continue

                        if field[new_j][new_i] == '||:boom:||':
                            num_bombs += 1

                field[j][i] = f"||{nums[num_bombs]}||"

        while True:
            xloc = random.randint(0, width - 1)
            yloc = random.randint(0, length - 1)
            if field[yloc][xloc] == '||:boom:||':
                continue

            field[yloc][xloc] = field[yloc][xloc][2:-2]
            break

        await ctx.send('\n'.join(''.join(cell for cell in row) for row in field))
