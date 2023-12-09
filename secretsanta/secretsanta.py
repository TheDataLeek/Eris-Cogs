import csv
import random
import io

import discord
from redbot.core import commands, bot, checks, data_manager, Config
from redbot.core.utils import embed

BaseCog = getattr(commands, "Cog", object)


class SecretSanta(BaseCog):
    def __init__(self, bot_instance: bot):
        self.bot = bot_instance

    @commands.command()
    async def secretsanta(self, ctx: commands.Context):
        """
        CSV assumes these columns, anything else is included in the message.

            Email Address
            What's your discord username?
            do_not_match
        """
        message: discord.Message = ctx.message
        attachments: list[discord.Attachment] = message.attachments
        if not len(attachments):
            await ctx.send('Need to provide CSV file with inputs!')
            return

        csv_file = attachments[0]

        extension = csv_file.filename.split('.')[-1]
        if extension != 'csv':
            await ctx.send("Needs to be a .csv!")
            return

        # snag first attachment
        buf = io.StringIO()
        await csv_file.save(buf)
        buf.seek(0)

        reader = csv.reader(buf)
        data = [row for row in reader]
        header = data[0]
        header[1] = 'email'
        header[2] = 'discord'
        data = data[1:]
        data = [dict(zip(header, row)) for row in data]

        # ok so we have a few that can't match up to each other
        # we could be clever and solve this the right way
        # OR
        # we just keep shuffling until we're happy with it
        while True:
            random.shuffle(data)

            bad_pairings = False
            for i, person in enumerate(data):
                matched = data[i - 1]
                if person['discord'] == matched['do_not_match'] or matched['discord'] == person['do_not_match']:
                    bad_pairings = True
                    break

            if not bad_pairings:
                break

        final_matches = {}
        for i, person in enumerate(data):
            matched = data[i - 1]
            message_template = f"""
                # HAPPY HOLIDAYS!
                
                Thanks for signing up for the Secret Santa, Snek by Praised!
                
                Your match is {matched['discord']}. Here's what they filled out in the form,
            """

            for col in header[4:]:
                message_template += f"\n## {col}\n{matched[col]}"

            final_message = '\n'.join(line.strip() for line in message_template.splitlines())
            final_matches[person['discord']] = final_message

        for santa, match_message in final_matches.items():
            await ctx.send(santa)
            await ctx.send(match_message)
