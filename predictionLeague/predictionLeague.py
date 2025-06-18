from redbot.core import commands, checks, Config
from redbot.core.utils.chat_formatting import box
import json
from io import BytesIO

class PredictionLeague(commands.Cog):
    
    def __init__(self,bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=9320767881)
        default_guild = {
            "round_num" : 0,
            "match_num" : 0,
            "matches" : {}
        }
        self.config.register_guild(**default_guild)      

    @commands.command()
    async def predict(self, ctx, scoreline, fgs, fgm, motm):
        """Command to get prediction from user"""
        # guild = self.config.guild(ctx.guild)  

        # #preprocess input
        # scores = scoreline.split("-")
        # fgm = int(fgm.strip("'"))

        # #define prediction list 
        # """City Score, Opp Score, FGS, FGM, MOTM"""
        # prediction = [scores[0], scores[1], fgs, fgm, motm]


    @checks.admin_or_permissions(manage_channels = True)
    @commands.group(autohelp=True)
    async def plset(self,ctx):
        """Prediction League Settings Group"""
        

    @plset.command()
    async def show(self,ctx):
        """Shows the Current Prediction League Settings"""
        round_num = await self.config.guild(ctx.guild).round_num()
        match_num = await self.config.guild(ctx.guild).match_num()
        msg = ""
        msg += "Round Number: {}\n".format(round_num)
        msg += "Match Number: {}\n".format(match_num)
        await ctx.send(box(msg))
    
    @plset.command()
    async def setround(self, ctx, round : int):
        """Sets Round"""
        await self.config.guild(ctx.guild).round_num.set(round)
        return await ctx.send("The Current Round is Now : {}".format(round))

    @plset.command()
    async def setmatch(self, ctx, match : int):
        """Sets Matchday Number"""
        await self.config.guild(ctx.guild).match_num.set(match)
        return await ctx.send("The Current Match is Now : {}".format(match))
    
    @plset.command()
    async def advancematch(self, ctx):
        """Advances the Current Matchday"""
        async with self.config.guild(ctx.guild).all() as guild_config:
            round_num = guild_config["round_num"]
            match_num = guild_config["match_num"]
            if match_num != 10:
                match_num += 1
            else:
                round_num += 1
                match_num = 0
            guild_config["round_num"] = round_num
            guild_config["match_num"] = match_num

        await ctx.send(f"Round: {round_num}, Match: {match_num}")

    
    @plset.command()
    async def setinfo(self, ctx, opp, date, comp):
        async with self.config.guild(ctx.guild).all() as guild_config:
            match_key = (guild_config['season_num'], guild_config['round_num'], guild_config['match_num'])
            if match_key not in guild_config["matches"]:
                guild_config['matches'][match_key] = {
                'info': {},
                'predictions': {},
                'scores': {},
                'vals': {}
            }
                
            guild_config['matches'][match_key]['info'] = {
                'opponent' : opp,
                'date' : date,
                'competition' : comp
            }

    @plset.command()
    async def debug_infodump(self, ctx):
        """Dumps the entire config for debugging"""
        async with self.config.guild(ctx.guild).all() as guild_config:
            await ctx.send(box(str(guild_config)))

    @plset.command()
    async def reset(self, ctx):
        """Resets the Prediction League Config"""
        async with self.config.guild(ctx.guild).all() as guild_config:
            data = json.dumps(guild_config, indent=4)
            file = BytesIO(data.encode("utf-8"))
            file.name = "infodump.json"
            await ctx.send("Here is the current config before reset:", file=discord.File(file))
        await self.config.guild(ctx.guild).clear()
        await self.config.guild(ctx.guild).set({
            "round_num": 0,
            "match_num": 0,
            "matches": {}
        })
        await ctx.send("Prediction League Config has been reset.")