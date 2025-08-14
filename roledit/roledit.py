from redbot.core import commands #type: ignore

class Roledit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def trystuff(self, ctx, roleid):
        role = ctx.guild.get_role(int(roleid))

        if role:
            await ctx.send(role)
            await ctx.send(dir(role))

            for attr in dir(role):
                if not attr.startswith("_"):
                    await ctx.send(f"{attr}: {getattr(role, attr)}")
        else:
            await ctx.send("Role not found.")