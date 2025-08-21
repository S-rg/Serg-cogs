from redbot.core import commands, checks, Config # type: ignore
from redbot.core.utils.chat_formatting import box, pagify # type: ignore
import json
from io import BytesIO
import re
from discord import File, Forbidden, NotFound # type: ignore
from rapidfuzz import process, fuzz # type: ignore

class PredictionLeague(commands.Cog):
    
    def __init__(self,bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=9320767881)
        default_guild = {
            "round_num" : 0,
            "match_num" : 0,
            "matches" : {},
            "playerlist": [],
            "open": True,
            "round_scores": {},
            "debug_mode": False,
            "user_id_map": {}
        }
        self.config.register_guild(**default_guild)

    def get_prediction(self, message):
        """Extracts the prediction from the message"""
        message = message.lower()
        parts = message.split(',')
        for part in parts:

            if part.strip() == "":
                continue

            if 'fgs' in part:
                fgs = part.replace('fgs', '').strip()
                
            elif 'fgm' in part or "'" in part or "’" in part or "‘" in part:
                fgm = int(part.replace('fgm', '').replace("'", '').replace("’", '').replace("‘", '').replace('′', '').strip())

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
                raise ValueError("Invalid prediction format")

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
        
    def score(self, predictions, correct_predictions):
        """Calculates the score based on predictions and correct predictions"""
        score = 0
        
        predicted_result = 'w' if predictions['cityscore'] > predictions['otherscore'] else 'l' if predictions['cityscore'] < predictions['otherscore'] else 't'
        correct_result = 'w' if correct_predictions['cityscore'] > correct_predictions['otherscore'] else 'l' if correct_predictions['cityscore'] < correct_predictions['otherscore'] else 't'

        predicted_gd = abs(predictions['cityscore'] - predictions['otherscore'])
        correct_gd = abs(correct_predictions['cityscore'] - correct_predictions['otherscore'])

        predicted_total = predictions['cityscore'] + predictions['otherscore']
        correct_total = correct_predictions['cityscore'] + correct_predictions['otherscore']

        if predicted_result == correct_result:
            score += 1
        else:
            score -= 1

        if predicted_gd == correct_gd:
            score += 1
        if predicted_total == correct_total:
            score += 1
        if predictions['cityscore'] == correct_predictions['cityscore']:
            score += 2
        if predictions['otherscore'] == correct_predictions['otherscore']:
            score += 2

        if predictions['fgs'] == correct_predictions['fgs']:
            score += 5
        else:
            score -= 1


        if predictions['fgm'] is None or correct_predictions['fgm'] is None:
            score += 0
        elif predictions['fgm'] == correct_predictions['fgm']:
            score += 10
        elif abs(predictions['fgm'] - correct_predictions['fgm']) < 6:
            score += 5
        else:
            score -= 1

        if predictions['motm'] == correct_predictions['motm']:
            score += 7
        else:
            score -= 1

        return score

    
    def score_matchday(self, predictions, correct_predictions):
        """Scores the matchday based on predictions and correct predictions"""
        scores = {}
        for player_id, player_prediction in predictions.items():
            player_score = self.score(player_prediction, correct_predictions)
            scores[player_id] = player_score
        return scores


    @commands.command()
    async def predict(self, ctx, *, message):
        """Command to get prediction from user"""
        
        try:
            predictions = self.get_prediction(message)
            
            if predictions['fgs'] is not None:
                predictions['fgs'] = self.find_player(predictions['fgs'], await self.config.guild(ctx.guild).playerlist())
            if predictions['motm'] is not None:
                predictions['motm'] = self.find_player(predictions['motm'], await self.config.guild(ctx.guild).playerlist())
        except:
            return await ctx.message.add_reaction("❌")      

        async with self.config.guild(ctx.guild).all() as guild_config:
            if not guild_config["open"]:
                return await ctx.message.add_reaction("❌")

            match_key = str((guild_config['round_num'], guild_config['match_num']))
            if match_key not in guild_config["matches"]:
                guild_config['matches'][match_key] = {
                    'info': {},
                    'predictions': {},
                    'correct_predictions': {}
                }
                
            guild_config['matches'][match_key]['predictions'][ctx.author.id] = predictions

            if guild_config["debug_mode"]:
                predictions_str = json.dumps(predictions, indent=2)
                await ctx.send(box(predictions_str))

            await ctx.message.add_reaction("✅")

            try:
                predictions_str = json.dumps(predictions, indent=2)
                await ctx.author.send(box(predictions_str))
            except Forbidden:
                await ctx.send("I couldn't DM you — maybe you have DMs disabled?")
            

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

    @plset.command(aliases=["correct"])
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

            if predictions['fgs'] is not None:
                predictions['fgs'] = self.find_player(predictions['fgs'], await self.config.guild(ctx.guild).playerlist())
            if predictions['motm'] is not None:
                predictions['motm'] = self.find_player(predictions['motm'], await self.config.guild(ctx.guild).playerlist())
            
            config['matches'][match_key]['correct_predictions'] = predictions

            await ctx.message.add_reaction("✅")


    @plset.command()
    async def scorematchday(self, ctx, round=None, match=None):
        """Scores the Matchday"""
        async with self.config.guild(ctx.guild).all() as guild_config:
            if round is None:
                round = guild_config['round_num']
            if match is None:
                match = guild_config['match_num']
            
            match_key = str((round, match))
            if match_key not in guild_config["matches"]:
                return await ctx.send("No predictions found for this matchday.")
            
            match_data = guild_config["matches"][match_key]
            correct_predictions = match_data.get('correct_predictions', {})
            predictions = match_data.get('predictions', {})
            
            if not correct_predictions:
                return await ctx.send("No correct predictions set for this matchday.")
            
            scores = self.score_matchday(predictions, correct_predictions)

            if round not in guild_config["round_scores"]:
                guild_config["round_scores"][round] = {}

            for player_id, score in scores.items():
                if player_id not in guild_config["round_scores"][round]:
                    guild_config["round_scores"][round][player_id] = {}
                guild_config["round_scores"][round][player_id][match_key] = score

        await ctx.send("Matchday scores have been updated.")

    @plset.command()
    async def showmatchscore(self, ctx, round=None, match=None):
        async with self.config.guild(ctx.guild).all() as guild_config:
            if round is None:
                round = guild_config['round_num']
            if match is None:
                match = guild_config['match_num']

            match_key = str((round, match))
            round_scores = guild_config["round_scores"].get(str(round), {})
            if not round_scores:
                return await ctx.send("No scores available for this matchday.")

            msg = f"Scores for Round {round} Match {match}:\n"
            predictions = guild_config["matches"].get(match_key, {}).get('predictions', {})
            correct_predictions = guild_config["matches"].get(match_key, {}).get('correct_predictions', {})
            rows = [["Player", "Score", "City", "Opp", "FGS", "FGM", "MOTM"]]
            rows.append(['', '', correct_predictions.get('cityscore', ''), correct_predictions.get('otherscore', ''), correct_predictions.get('fgs', ''), str(correct_predictions.get('fgm', '')) + "'", correct_predictions.get('motm', '')])

            for player_id, matches in round_scores.items():
                score = matches.get(match_key)
                if score is None:
                    continue
                username = guild_config["user_id_map"].get(player_id)
                if not username:
                    try:
                        user = await self.bot.fetch_user(player_id)
                        username = user.display_name
                        guild_config["user_id_map"][player_id] = username

                    except NotFound:
                        username = None

                player_name = username if username else f"User ID {player_id}"
                rows.append([
                    player_name,
                    score,
                    predictions.get(player_id, {}).get('cityscore', ''),
                    predictions.get(player_id, {}).get('otherscore', ''),
                    predictions.get(player_id, {}).get('fgs', ''),
                    str(predictions.get(player_id, {}).get('fgm', '')) + "'",
                    predictions.get(player_id, {}).get('motm', '')
                ])

            if len(rows) == 2:
                return await ctx.send("No scores available for this matchday.")
            
            #widths = [min(max(len(str(cell)), 15) for cell in col) for col in zip(*rows)]
            widths = [10, 5, 5, 5, 15, 5, 15]
            lines = []

            for row in rows:
                cells = []
                for cell, w in zip(row, widths):
                    s = str(cell)
                    if len(s) > w:
                        s = s[: w - 1] + "…"
                    cells.append(s.ljust(w))
                lines.append("  ".join(cells))

            msg = "\n".join(lines)

            for page in pagify(msg, delims=["\n"], page_length=1900):
                await ctx.send(box(page))



    @plset.command()
    async def open(self, ctx):
        """Opens the Prediction League for predictions"""
        async with self.config.guild(ctx.guild).all() as guild_config:
            guild_config["open"] = True
            await ctx.send("Prediction League is now open for predictions.")

    @plset.command()
    async def close(self, ctx):
        """Closes the Prediction League for predictions"""
        async with self.config.guild(ctx.guild).all() as guild_config:
            guild_config["open"] = False
            await ctx.send("Prediction League is now closed for predictions.")

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


    @plset.command(name="editprediction")
    async def editprediction(self, ctx, user, *, message):
        """Edits a prediction for a user"""
        try:
            predictions = self.get_prediction(message)
        except ValueError as e:
            return await ctx.send(f"Error parsing prediction: {str(e)}")

        async with self.config.guild(ctx.guild).all() as guild_config:
            match_key = str((guild_config['round_num'], guild_config['match_num']))
            if match_key not in guild_config["matches"]:
                return await ctx.send("No predictions found for this matchday.")
            
            guild_config["matches"][match_key]['predictions'][user] = predictions

            await ctx.message.add_reaction("✅")

            if guild_config["debug_mode"]:
                predictions_str = json.dumps(predictions, indent=2)
                await ctx.send(box(predictions_str))

    @plset.group()
    async def debug(self, ctx):
        """Debugging commands for Prediction League"""

    @debug.command()
    async def infodump(self, ctx):
        """Dumps the entire config for debugging"""
        async with self.config.guild(ctx.guild).all() as guild_config:
            await ctx.send(box(str(guild_config)))

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

    @debug.command()
    async def toggledebugmode(self, ctx):
        """Toggles the debug mode for Prediction League"""
        async with self.config.guild(ctx.guild).all() as guild_config:
            guild_config["debug_mode"] = not guild_config.get("debug_mode", False)
            status = "enabled" if guild_config["debug_mode"] else "disabled"
            await ctx.send(f"Debug mode is now {status}.")

    @debug.command()
    async def backup(self, ctx):
        """Creates a backup of the Prediction League config"""
        async with self.config.guild(ctx.guild).all() as guild_config:
            backup_data = json.dumps(guild_config, indent=4)
            backup_file = BytesIO(backup_data.encode('utf-8'))
            backup_file.seek(0)
            file = File(fp=backup_file, filename="backup.json")
            await ctx.send("Here is your backup file:", file=file)

    @debug.command()
    async def nuke_scores(self, ctx):
        """Removes all scores from the Prediction League"""
        async with self.config.guild(ctx.guild).all() as guild_config:
            guild_config["round_scores"] = {}
            guild_config["matches"] = {}
            await ctx.send("All scores have been removed from the Prediction League.")

    @debug.command()
    async def edit_username(self, ctx, player_id, username):
        """Edits the username of a player in the Prediction League"""
        async with self.config.guild(ctx.guild).all() as guild_config:
            guild_config["user_id_map"][player_id] = username
            await ctx.send(f"Username for {player_id} has been updated to {username}.")