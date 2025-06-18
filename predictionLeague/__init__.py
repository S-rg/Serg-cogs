from .predictionLeague import PredictionLeague


async def setup(bot):
    await bot.add_cog(PredictionLeague(bot))
