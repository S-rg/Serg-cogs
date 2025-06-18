from redbot.core import commands, checks, Config
from redbot.core.utils.chat_formatting import box

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
        round_num = await self.config.guild(ctx.guild).round_num()
        match_num = await self.config.guild(ctx.guild).match_num()
        msg = ""
        msg += "Round Number: {}\n".format(round_num)
        msg += "Match Number: {}\n".format(match_num)
        await ctx.send(box(msg))

    @plset.command()
    async def season(self, ctx, season : int):
        """Sets Season"""
        await self.config.guild(ctx.guild).season_num.set(season)
        return await ctx.send("The Current Season is Now : {}".format(season))
    
    @plset.command()
    async def round(self, ctx, round : int):
        """Sets Round"""
        await self.config.guild(ctx.guild).round_num.set(round)
        return await ctx.send("The Current Round is Now : {}".format(round))

    @plset.command()
    async def match(self, ctx, match : int):
        """Sets Matchday Number"""
        await self.config.guild(ctx.guild).match_num.set(match)
        return await ctx.send("The Current Match is Now : {}".format(match))
    
    @plset.command()
    async def advance(self, ctx):
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
    async def matchinfo(self, ctx, season_num: int = None, round_num: int = None, match_num: int = None):
        async with self.config.guild(ctx.guild).all() as guild_config:
            if season_num is None:
                season_num = guild_config['season_num']
            if round_num is None:
                round_num = guild_config['round_num']
            if match_num is None:
                match_num = guild_config['match_num']
            match_key = (season_num, round_num, match_num)

            if match_key in guild_config['matches']:
                await ctx.send('yep')
            else:
                await ctx.send('nope')
