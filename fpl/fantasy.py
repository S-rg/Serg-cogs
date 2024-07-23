from redbot.core import commands
import json
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')
from redbot.core import Config


class Fantasy(commands.Cog):

    def __init__(self, bot):
        self.config = Config.get_conf(self, identifier=93209320, force_registration=True)
        self.bot = bot

        self.config.register_user(
            att = ['None', 'None', 'None'],
            mid = ['None', 'None', 'None'],
            dfn = ['None', 'None', 'None', 'None'],
            gk = ['None'],
            bench = ['None','None','None','None','None'],
            swaps = 50,
            bal = 100,
            powerUpsLeft = ['TC'],
            powerUpsCurrent = []
        )

        self.config.register_global()


    def getGameDataframes(url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content,'html.parser')
        tables = soup.find_all('table')

        dfs = []
        for i in tables:
            df = pd.read_html(str(i))[0]
            dfs.append(df)

        scores = soup.find_all('div', class_='score')
        for i in scores:
            dfs.append(i.get_text())
            print(i.get_text())
        return dfs

    def getStarting11AndSubs(s11df, summary):
        is_bench = False
        s11df.columns = ['Shirt', 'Name']
        return_dict = {}

        for row in s11df.itertuples():
            if row.Name == 'Bench':
                is_bench = True
                continue

            return_dict[row.Name] = {
                'bench': is_bench,
                'goals': 0, 
                'assists': 0, 
                'mins': 0, 
                'cs': 0, 
                'pen_saved': 0,
                'pen_missed': 0, 
                'goal_conceded': 0, 
                'yellow_card': 0, 
                'red_card': 0, 
                'own_goal': 0, 
                'saves': 0, 
                'tackles': 0, 
                'passes': 0, 
                'sot': 0 
            }

        for index, row in summary.iterrows():
            name = row[('Unnamed: 0_level_0', 'Player')]
            mins = row[('Unnamed: 4_level_0', 'Min')]

            if mins == 0:
                return_dict.pop(name)
            else:
                try:
                    return_dict[name]['mins'] = mins
                except KeyError:
                    continue

        return_dict = {player: i for player, i in return_dict.items() if i['mins'] != 0}

        return return_dict


    def get_stats(data, summary, misc, gk, opp_score):
        
        for index, row in summary.iterrows():

            if row[('Unnamed: 0_level_0', 'Player')] not in data:
                continue

            name = row[('Unnamed: 0_level_0', 'Player')]
            goals = row[('Performance','Gls')]
            assists = row[('Performance','Ast')]
            pen_miss = row[('Performance','PKatt')] - row[('Performance','PK')]
            sot = row[('Performance','SoT')]
            yc = row[('Performance','CrdY')]
            rc = row[('Performance','CrdR')]
            passes = row[('Passes','Cmp')]

            if opp_score == 0 and data[name]['mins'] >= 60:
                    cs = 1
                    gc = 0
            else:
                    gc = opp_score
                    cs = 0

            data[name]['goals'] = goals
            data[name]['assists'] = assists
            data[name]['cs'] = cs
            data[name]['pen_missed'] = pen_miss
            data[name]['goal_conceded'] = gc
            data[name]['yellow_card'] = yc
            data[name]['red_card'] = rc
            data[name]['passes'] = passes
            data[name]['sot'] = sot
        
        for index, row in misc.iterrows():

            if row[('Unnamed: 0_level_0', 'Player')] not in data:
                continue
            name = row[('Unnamed: 0_level_0', 'Player')]
            tackles = row[('Performance','TklW')]
            og = row[('Performance','OG')]

            data[name]['own_goal'] = og
            data[name]['tackles'] = tackles

        for index, row in gk.iterrows():
            if row[('Unnamed: 0_level_0', 'Player')] not in data:
                continue
            name = row[('Unnamed: 0_level_0', 'Player')]
            data[name]['saves'] = row[('Shot Stopping','Saves')]
                
        return data

    def playerPoints(vals, position):
        points = (1 if vals['bench'] else 2)
        + ((5 if position == 'att' else 6 if position == 'mid' else 7 if position in ['def', 'gk'] else None) * vals['goals'])
        + (3 * vals['assists'])
        + ((7 if position == 'gk' else 5) * vals['cs'])
        + (5 * vals['pen_saved'])
        + (-3 * vals['pen_missed'])
        + (-1 * ((vals['goal_conceded'] - 1) if vals['goal_conceded'] > 1 else 0))
        + (-1 * vals['yellow_card'])
        + (-3 * vals['red_card'])
        + (-2 * vals['own_goal'])
        + (0 if vals['saves'] < 3 else 2 if 3 <= vals['saves'] <= 4 else 3)
        + (0 if vals['tackles'] < 4 else 2 if vals['tackles'] == 4 else 3)
        + (0 if vals['passes'] < 60 else 2 if 60 <= vals['passes'] < 70 else 3)
        + (0 if vals['sot'] < 2 else 2 if vals['sot'] == 2 else 3)

        return points

    def calcPoints(data):
        json.load("players.json")



    @commands.command()
    async def getPlayers(self, ctx):
        att = await self.config.user(ctx.author).get_raw(att)
        mid = await self.config.user(ctx.author).get_raw(mid)
        dfn = await self.config.user(ctx.author).get_raw(dfn)
        return await ctx.send(att + mid + dfn)
