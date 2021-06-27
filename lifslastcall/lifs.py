# stdlib
from time import sleep
from random import choice as randchoice
import random

# third party
import discord
from redbot.core import commands, data_manager
import aiohttp


BaseCog = getattr(commands, "Cog", object)


class Lifs(BaseCog):
    def __init__(self, bot):
        self.bot = bot
        self.patrons = [
            "Tally Fellbranch (Bent Nail)",
            "Embric & Avi (Steam and Steal)",
            "Fala Lefaliir (Corellon's Crown)",
            "Vincent Trench (Tiger's Eye)",
            "Rishaal the Page-Turner (Book Wyrm)",
            "Renaer Neverember",
            "Renaer's Friends (see sub-table)",
            "Renaer's Friends (see sub-table)",
            "Meloon Wardragon",
            "Floon Blagmaar",
            "Hammond Kraddoc (Vintners' Guild)",
            "Broxley Fairkettle (Innkeepers)",
            "Ulkoria Stonemarrow",
            'Mattrim "Threestrings" Mereg',
            "Jalester Silvermane",
            "Yagra Stonefist",
            "[Faction Contact] FACTION CONTACT: This result should be keyed to the PCs’ contact for whatever faction they end up doing faction missions for. (If they become members of multiple factions, randomly determine or choose one.)",
            "[Campaign NPC] (or reroll) CAMPAIGN NPC: This slot is left open for adding an NPC that the players like from other parts of the campaign. (I’m currently using this slot for Valetta & Nim.) This can includes characters from the Renaer’s Friends table below if the PCs seem to have forged a strong relationship with them and you’d like to increase the likelihood of them showing up. (Of course, you can always arbitrarily decide that so-and-so will be dropping by the tavern that night.)",
            "Jarlaxle (or reroll)",
            "Faction Response Team (or reroll)",
        ]
        self.renears = {
            (1, 6): "Renaer Neverember + Roll Again",
            (7, 8): "Vajra Safahr (the Blackstaff)",
            (9, 10): 'Laraelra "Elra" Harsard',
            (11, 12): "Osco Salibuck",
            (13, 14): "Lord Torlyn Wands",
            (15, 15): "Eiruk Weskur",
            (16, 16): "Harug Shieldmaster",
            (17, 17): "Parlek Lateriff",
            (18, 18): "Meloon Wardragon",
            (19, 19): "Floon Blagmaar",
            (20, 20): "[Faction Spy Watching Renaer], FACTION SPY: Determine faction randomly or choose appropriately based on the events in the campaign so far.",
        }
        self.renears_friends = []
        for (lower, upper), friend in self.renears.items():
            num_entries = (upper - lower) + 1
            self.renears_friends += [friend for _ in range(num_entries)]
        self.events = [
            s.strip()
            for s in """
    A spontaneous arm-wrestling competition breaks out.
    A local kenku street gang comes into the tavern. They try to sell traveler’s dust to the patrons. (Traveler’s Dust: Tiny roseate crystals. A single grain is usually dropped into the eye, where it dissolves. Those using it are said to be walking the crimson road. Those using traveler’s dust often have trembling hands, slurred speech, and eyes the color of blood. Creates a euphoric feeling paired to a sensation of the world slowing down around you.)
    PCs walk in to find a horse standing in the middle of the common room. No one can explain how it got there or who owns it.
    A patron slips a drug into a drink before returning to their own table.
    A 12-year-old pickpocket named Stannis is working the crowd. His handler, a half-orc named Sabeen, is waiting outside.
    A portal opens in the middle of the tavern. An elven wizard named Kyser Tameno walks out, orders a drink, and goes back through the portal. (He might become a regular.)
    The City Watch makes an arrest on the premises.
    Volo shows up and would like to make arrangements for a signing of Volo’s Guide to Monsters. Also has a number of questions regarding the haunting of Trollskull Manor for Volo’s Guide to Spirits and Specters.
    Staff Event (e.g., the star elf triplets float up to the ceiling and a spontaneous light show erupts; after a few minutes they float back down and resume service as if nothing happened)
        """.split(
                "\n"
            )
        ]

    @commands.command()
    async def evening_at_lifs(self, ctx):
        """
        For each night at the tavern:

        1. There is a 1 in 1d6 chance that an Event will occur that night.

        2. Roll 1d6 to determine the number of significant patrons in the tavern that night, then use the Patron Table
        to randomly determine which patrons are present. If a result of “Renaer’s Friends” is rolled, roll on the
        Patrons – Renaer’s Friends table to determine the final result.

        3. Look at the Topics/Agendas for the patrons who are present. Generally speaking, you can use one per patron or
        just select one from among the patrons. When in doubt, default  to the first unused bullet point. Supplement or
        replace these topics with other major events occurring in your campaign.
        """
        summary = []
        event_occurs = random.randint(1, 6) == 1
        if event_occurs:
            summary.append(f"**Event occurs!** {random.choice(self.events)}")
        else:
            summary.append("**No event today**")

        num_sig_patrons = random.randint(1, 6)
        summary.append(f"**{num_sig_patrons} / 6 patrons**")
        choices = random.sample(self.patrons, k=num_sig_patrons)
        how_many_of_renears_friends = len([c for c in choices if 'sub-table' in c])
        renears_friends = random.sample(self.renears_friends, k=how_many_of_renears_friends)
        r_i = 0
        for i, c in enumerate(choices):
            if 'sub-table' in c:
                choices[i] = f"{choices[i]} - {renears_friends[r_i]}"
                r_i += 1

            summary.append(f'- {choices[i]}')

        summary = '\n'.join(summary)
        await ctx.send(summary)
