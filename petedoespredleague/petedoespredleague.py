from redbot.core import commands, checks
import random

shirtnums = {
    18:"Ortega",
    31:"Ederson",
    33:"Scott Carson",
    2:"Walker",
    3:"Ruben Dias",
    5:"Stones",
    6:"Ake",
    7:"Cancelo",
    14:"Laporte",
    21:"Sergio Gomez",
    25:"Akanji",
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
    26:"Mahrez",
    82:"Rico Lewis"
    }

class petedoespredleague(commands.Cog):
    """My custom cog"""

    def __init__(self, bot):
        self.bot = bot

    @checks.admin_or_permissions(manage_channels=True)
    @commands.command()
    async def predict(self, ctx, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10):
        pl = [p1,p2,p3,p4,p5,p6,p7,p8,p9,p10]
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

    @checks.admin_or_permissions(manage_channels=True)
    @commands.command()
    async def predictscore(self, ctx):
        cityr = random.randint(1,5)
        oppr = random.randint(0,3)
        if cityr>oppr:
            res = "win"
        elif cityr<oppr:
            res = "lose"
        else:
            res = "draw"
        await ctx.send(f"City {res} {str(cityr)}-{str(oppr)}")

    @checks.admin_or_permissions(manage_channels=True)
    @commands.command()
    async def predictscorefgm(self, ctx):
        cityr = random.randint(1,5)
        oppr = random.randint(0,3)
        min = random.randint(1,45)
        if cityr>oppr:
            res = "win"
        elif cityr<oppr:
            res = "lose"
        else:
            res = "draw"
        await ctx.send(f"City {res} {str(cityr)}-{str(oppr)}, FGM: {min}'")
