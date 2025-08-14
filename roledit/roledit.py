from redbot.core import commands #type: ignore

class Roledit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def trystuff(self, ctx, roleid=0):
        role = ctx.guild.get_role(roleid)

        await ctx.send(role)