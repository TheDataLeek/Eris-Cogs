from .agentlib import Agent


async def setup(bot):
    agent = Agent(bot)
    await agent.build_model()
    await bot.add_cog(agent)
