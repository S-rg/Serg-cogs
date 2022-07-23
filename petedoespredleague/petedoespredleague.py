from redbot.core import commands, checks
import random

shirtnums = {
    18:"Ortega",
    31:"Ederson",
    33:"Scott Carson",
    2:"Walker",
    3:"Ruben Dias",
    6:"Ake",
    7:"Cancelo",
    11:"Zinchenko",
    14:"Laporte",
    4:"Phillips",
    8:"Gundogan",
    10:"Grealish",
    16:"Rodri",
    17:"KDB",
    20:"Bernardo",
    47:"Foden",
    80:"Palmer",
    9:"Haaland",
    19:"Julian Alvarez",
    26:"Mahrez"
    }

class petedoespredleague(commands.Cog):
    """My custom cog"""

    def __init__(self, bot):
        self.bot = bot

    @checks.admin_or_permissions(manage_channels=True)
    @commands.command()
    async def predict(self, ctx, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11):
        pl = [p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11]
        cityr = random.randint(1,5)
        oppr = random.randint(0,3)
        fgs = random.choice(pl+["None"])
        motm = random.choice(pl)
        min = random.randint(1,45)
        if cityr>oppr:
            res = "win"
        elif cityr<oppr:
            res = "lose"
        else:
            res = "draw"
        if fgs.isnumeric():
            fgs = shirtnums[int(fgs)]
        if motm.isnumeric():
            motm = shirtnums[int(motm)]
        await ctx.send(f"City {res} {str(cityr)}-{str(oppr)}, fgs {fgs} {min}' motm {motm}")
        try:
            await ctx.message.delete()
        except discord.errors.Forbidden:
            try:
                await ctx.send(_("Not enough permissions to delete messages."), delete_after=2)
            except discord.errors.Forbidden:
                await author.send(_("Not enough permissions to delete messages."), delete_after=15)
