from redbot.core import commands, checks, Config
from redbot.core.utils.chat_formatting import box
import json
from io import BytesIO
import re
from rapidfuzz import process, fuzz

class PredictionLeague(commands.Cog):
    
    def __init__(self,bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=9320767881)
        default_guild = {
            "round_num" : 0,
            "match_num" : 0,
            "matches" : {},
            "playerlist": []
        }
        self.config.register_guild(**default_guild)

    def get_prediction(self, message):
        """Extracts the prediction from the message"""
        message = message.lower()
        parts = message.split(',')
        for part in parts:

            if 'fgs' in part:
                fgs = part.replace('fgs', '').strip()
                
            elif 'fgm' in part or "'" in part:
                fgm = int(part.replace('fgm', '').replace("'", '').strip())

            elif 'motm' in part:
                motm = part.replace('motm', '').strip()

            elif '-' in part:
                scoreline_pattern = re.compile(r'(\d+)\s*-\s*(\d+)')
                match = scoreline_pattern.search(part)
                if match:
                    score1 = int(match.group(1))
                    score2 = int(match.group(2))
                    if "city" in part.lower():
                        if part.lower().find("city") < part.find(match.group(0)):
                            cityscore, otherscore = score1, score2
                        else:
                            cityscore, otherscore = score2, score1
                    else:
                        cityscore, otherscore = None, None

            else:
                return ValueError("Invalid prediction format")

        return {
            "fgs": fgs if 'fgs' in locals() else None,
            "fgm": fgm if 'fgm' in locals() else None,
            "motm": motm if 'motm' in locals() else None,
            "cityscore": cityscore if 'cityscore' in locals() else None,
            "otherscore": otherscore if 'otherscore' in locals() else None
        }
    
    def find_player(self, in_name, player_list, threshold=80):
        """Finds a player in the player list"""
        match, score, index = process.extractOne(
            in_name,
            player_list,
            scorer=fuzz.partial_ratio
        )
        
        if score >= threshold:
            return player_list[index]
        else:
            return None



    @commands.command()
    async def predict(self, ctx, *, message):
        """Command to get prediction from user"""
        try:
            predictions = self.get_prediction(message)
            await ctx.message.add_reaction("✅")
        except:
            return await ctx.message.add_reaction("❌")      

        async with self.config.guild(ctx.guild).all() as guild_config:
            match_key = str((guild_config['round_num'], guild_config['match_num']))
            if match_key not in guild_config["matches"]:
                guild_config['matches'][match_key] = {
                    'info': {},
                    'predictions': {},
                    'correct_predictions': {}
                }
                
            guild_config['matches'][match_key]['predictions'][ctx.author.id] = predictions  
            

    @checks.admin_or_permissions(manage_channels = True)
    @commands.group(autohelp=True)
    async def plset(self,ctx):
        """Prediction League Settings Group"""
        
    
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
        async with self.config.guild(ctx.guild).all() as config:
            match_key = str((config['round_num'], config['match_num']))
            if match_key not in config["matches"]:
                config['matches'][match_key] = {
                    'info': {},
                    'predictions': {},
                    'correct_predictions': {}
                }
                
            config['matches'][match_key]['info'] = {
                'opponent' : opp,
                'date' : date,
                'competition' : comp
            }

    @plset.command()
    async def correctprediction(self, ctx, *, message):
        async with self.config.guild(ctx.guild).all() as config:
            match_key = str((config['round_num'], config['match_num']))
            if match_key not in config['matches']:
                config['matches'][match_key] = {
                    'info': {},
                    'predictions': {},
                    'correct_predictions': {}
                }

            predictions = self.get_prediction(message)
            
            config['matches'][match_key]['correct_predictions'] = predictions

    @plset.group()
    async def playerlist(self, ctx):
        """Manages the Player List for Prediction League"""
        async with self.config.guild(ctx.guild).all() as guild_config:
            player_list = guild_config.get("playerlist", [])
            if not player_list:
                return await ctx.send("No players found in the list.")
            msg = "Current Player List:\n"
            for player in player_list:
                msg += f"- {player}\n"
            await ctx.send(box(msg))

    @playerlist.command(name="addplayer")
    async def add_player(self, ctx, *, player_name):
        """Adds a player to the Prediction League"""
        player_name = player_name.lower()
        async with self.config.guild(ctx.guild).all() as guild_config:
            player_list = guild_config.get("playerlist", [])
            if player_name in player_list:
                return await ctx.send(f"Player '{player_name}' already exists in the list.")
            
            player_list.append(player_name)
            guild_config["playerlist"] = player_list
            await ctx.send(f"Player '{player_name}' has been added to the list.")

    @playerlist.command(name="removeplayer")
    async def remove_player(self, ctx, *, player_name):
        """Removes a player from the Prediction League"""
        async with self.config.guild(ctx.guild).all() as guild_config:
            player_list = guild_config.get("playerlist", [])
            player = self.find_player(player_name, player_list)
            if not player:
                return await ctx.send(f"Player '{player_name}' not found in the list.")
            
            player_list.remove(player)
            guild_config["playerlist"] = player_list
            await ctx.send(f"Player '{player_name}' has been removed from the list.")

    @playerlist.command(name="addplayers")
    async def add_players(self, ctx, *, players: str):
        """Adds multiple players to the Prediction League"""
        players = players.lower()
        player_names = [name.strip() for name in players.split(',')]

        async with self.config.guild(ctx.guild).all() as guild_config:
            player_list = guild_config.get("playerlist", [])
            for player_name in player_names:
                if player_name in player_list:
                    await ctx.send(f"Player '{player_name}' already exists in the list.")
                    continue
                player_list.append(player_name)
            guild_config["playerlist"] = player_list
            await ctx.send(f"Players added: {', '.join(player_names)}")

    @plset.group()
    async def debug(self, ctx):
        """Debugging commands for Prediction League"""

    @debug.command()
    async def infodump(self, ctx):
        """Dumps the entire config for debugging"""
        async with self.config.guild(ctx.guild).all() as guild_config:
            await ctx.send(box(str(guild_config)))

    @debug.command()
    async def REMOVETHISSERG(self, ctx):
        """Resets the Prediction League Config"""
        await self.config.guild(ctx.guild).clear()
        await self.config.guild(ctx.guild).set({
            "round_num": 0,
            "match_num": 0,
            "matches": {}
        })
        await ctx.send("Prediction League Config has been reset.")

    @debug.command()
    async def show(self,ctx):
        """Shows the Current Prediction League Settings"""
        round_num = await self.config.guild(ctx.guild).round_num()
        match_num = await self.config.guild(ctx.guild).match_num()
        msg = ""
        msg += "Round Number: {}\n".format(round_num)
        msg += "Match Number: {}\n".format(match_num)
        await ctx.send(box(msg))

    @debug.command()
    async def findplayer(self, ctx, *, player_name):
        """Finds a player in the player list"""
        async with self.config.guild(ctx.guild).all() as guild_config:
            player_list = guild_config.get("playerlist", [])
            player = self.find_player(player_name, player_list)
            if player:
                await ctx.send(f"Player found: {player}")
            else:
                await ctx.send("Player not found.")