from __future__ import annotations

import re
import discord
from redbot.core import data_manager, commands

from .base import ChatBase
from . import discord_handling, model_querying

SYSTEM_PROMPT = f"""
You are to to generate a Pathfinder 2e character using provided reference materials in an automated agent 
loop. Do not refer to Zoe or any other people in this process as you'll only be interacting with yourself and your own chain-of-thought.
The process will be as follows.

    1. Generate a character concept using the provided prompt. Be creative!
    2. Choose a name that fits their ancestry. Be creative with this name!
    3. Choose an ancestry for the character.
    4. Choose a background.
    5. Choose a class for the character.
    6. Finalize your attributes
    7. Note all class details
        a. Choose your skills.
        b. Choose your feats.
        c. Choose your spells (if you have them as part of your class)
        d. If there's important equipment, note that too. If necessary, choose a weapon, armor, and feel free to build creative magic items if the character requires it.

As you go through these steps, identify all followup URLs needed to flesh out more information. In your 
response, insert all required URLS. If a URL has already been provided, do not repeat it again. If you made a
mistake and found a URL that isn't needed for the character, ignore it and ensure that you collect the correct
information from the updated URL.

We'll then iterate on the following steps, and again, there's no human interactions here and you'll just be 
responding to yourself, so keep your answers brief and to the point. There's no need to summarize at the end 
of each step, as for the following steps you'll have access to the full chain-of-thought history.

    1. Look through what answers you've already provided
    2. Download all urls and extract the relevant information
    3. Decide on the next steps

We'll iterate until the character is fully fleshed out. If you have everything you need for the character,
start your response with <<<DONE>>> followed by the character stat block. Your goal is to finish in 5 steps. 
For every step beyond 5, you'll lose 1 point of your final score. If you finish in 5 steps, you'll get a bonus point.

The final stat block should be in the following format (DO NOT include URLs in the stat block, only attach them at the end)

# <Creature Name>

*<Level breakdown e.g. "Fighter 1, Wizard 2">*

*<Concept and description>*

**Roleplaying notes:**
    * <roleplaying notes - make sure to be succinct but thorough>

## Core

**Perception:** The creature’s Perception modifier is listed here, followed by any special senses.

**Languages:** The languages for a typical creature of that kind are listed here, followed by any special communication abilities. If a creature lacks this entry, it cannot communicate with or understand another creature through language.

**Skills:** The creature is trained or better in these skills. For untrained skills, use the corresponding attribute modifier.

**Attribute Modifiers:** The creature’s attribute modifiers are listed here.

**Items:** Any significant gear the creature carries is listed here.

**Interaction:** Abilities Special abilities that affect how a creature perceives and interacts with the world are listed here.

**AC:** followed by any special bonuses to AC

**Saving Throws:** A special bonus to a specific save appears in parentheses after that save’s bonus. Any special bonuses to all three saving throws against particular types of effects are listed after the three saves.

**HP:** followed by automatic abilities that affect the creature’s Hit Points or healing

**Immunities, Weaknesses, Resistances:** Any immunities, weaknesses, or resistances the creature has are listed here.

**Automatic Abilities:** The creature’s auras, any abilities that automatically affect its defenses, and the like are listed here.

**Reactive Abilities:** Free actions or reactions that are usually triggered when it’s not the creature’s turn are listed here.

**Speed:** followed by any other Speeds or movement abilities.

## Abilities & Feats

**Melee:** (traits; some weapon traits, such as deadly, include their calculations for convenience) The name of the weapon or unarmed attack the creature uses for a melee Strike, followed by the attack modifier and traits in parentheses. If a creature has any abilities or gear that would affect its attack modifier, such as a weapon with a +1 weapon potency rune, those calculations are already included, Damage amount and damage type, plus any additional effects (this entry is Effect if the Strike doesn’t deal damage).

**Ranged:** As Melee, but also lists range or range increment with traits, Damage as Melee.

**Spells:* The entry starts with the magical tradition and whether the spells are prepared or spontaneous, followed by the DC (and spell attack modifier if any spells require spell attack rolls). Spells are listed by rank, followed by cantrips. A spell prepared multiple times lists the number of times in parentheses—for example, “(×2).” Spontaneous spells list the number of spell slots after the spell rank.

**Innate Spells:** These are listed like other spells, but can also include constant, at-will, and focus spells. If the creature has a focus spell as an innate spell, it works like other innate spells with listed uses, rather than costing Focus Points. Spells that can be used an unlimited number of times list “(at will)” after the spell’s name. Constant spells appear at the end, separated by rank. Rules for constant and at-will spells appear in the Ability Glossary.

**Focus Spells:** If a creature has focus spells, this entry lists the spells’ rank, the Focus Points in the creature’s focus pool, the DC, and those spells.

**Rituals:** Any rituals the creature can cast appear here.

**Offensive or Proactive Abilities:** Any actions, activities, or abilities that automatically affect the creature’s offense, as well as free actions or reactions that are usually triggered on the creature’s turn, appear here in alphabetical order.

**Other Abilities:** Anything that didn't fit into the above categories, such as special abilities, feats, or spells, appears here in alphabetical order. If a creature has a lot of these abilities, they might be listed in a separate section.

## Reference

Reference URLS (ignore any class or ancestry URLs, only provide specific feat/spells/ability URLs)
    *
    *
    *

# Magic Items

If any magic items were created for this character, list them separately here.
"""


class PathfinderCommands(ChatBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        data_dir = data_manager.bundled_data_path(self)
        self.content_store = content.ContentStore(cache_dir=data_dir / "page_cache")

    @commands.command()
    async def generate_pf2e_character(self, ctx: commands.Context):
        """
        OK so the thinking here is that we can have her crawl through the site like a human would
        We'll start with the overview page, and then give her full crawling access over the entire site.
        We'll need to do this as a loop:
            * Starting page
            * What's my next step?
            * What links will I need?
            * download each link and cram into context window (leveraging the 1million token limit)
            * send a message each time we make an update

        Very similar to agent structure
        """
        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        author: discord.Member = message.author
        contents: str = " ".join(message.clean_content.split(" ")[1:])
        token = await self.get_openai_token()
        prefix: str = await self.get_prefix(ctx)
        model = await self.config.guild(ctx.guild).model()

        prompt = f"{SYSTEM_PROMPT}\n\nYour goal is to create a character that matches: {contents}"

        for url in [
            "https://2e.aonprd.com/Backgrounds.aspx",
            "https://2e.aonprd.com/Ancestries.aspx",
            "https://2e.aonprd.com/Ancestries.aspx?Versatile=true",
            "https://2e.aonprd.com/Classes.aspx",
        ]:
            await self.content_store.fetch_content(url)

        try:
            (
                thread_name,
                formatted_query,
                user_names,
            ) = await discord_handling.extract_chat_history_and_format(
                prefix, channel, message, author
            )
        except ValueError:
            await ctx.send("Something went wrong!")
            return

        response = await model_querying.query_text_model(
            token,
            prompt,
            formatted_query + self.content_store.to_openai(),
            model=model,
            user_names=user_names,
        )
        thread = await discord_handling.send_response(
            response, message, channel, thread_name
        )

        for i in range(10):
            formatted_query.append(
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": "\n".join(response),
                        },
                    ],
                }
            )
            new_urls = re.findall(
                r"(https?://2e\.aonprd\.com[^\s]+)", prompt, flags=re.IGNORECASE
            )
            for new_url in new_urls:
                await self.content_store.fetch_content(new_url)

            response = await model_querying.query_text_model(
                token,
                prompt,
                formatted_query + self.content_store.to_openai(),
                model=model,
                user_names=user_names,
            )
            await discord_handling.send_response(response, message, thread, thread_name)
            if "<<<DONE>>>" in "\n".join(response):
                break
