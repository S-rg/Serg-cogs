from .roledit import Roledit

async def setup(bot):
    await bot.add_cog(Roledit(bot))
