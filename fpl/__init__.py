from .fantasy import Fantasy

async def setup(bot):
    await bot.add_cog(Fantasy(bot))
