from redbot.core import commands #type: ignore

class Roledit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def trystuff(self, ctx, roleid):
        role = ctx.guild.get_role(roleid)

        if role:
            await ctx.send(role)
            await ctx.send(dir(role))
        else:
            await ctx.send("Role not found.")