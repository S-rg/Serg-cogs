import discord
from discord.ui import Select, View

class DropdownSelect(Select):
    def __init__(self, options, on_select_callback, placeholder="Select"):
        super().__init__(placeholder = placeholder, options = options)
        self.on_select_callback = on_select_callback

    async def callback(self, interaction: discord.Interaction):
        await self.on_select_callback(interaction)

class DropdownView(View):
    def __init__(self, select):
        super().__init__()
        self.add_item(select)

async def select_pos(interaction: discord.Interaction, conf):
    options = [
            discord.SelectOption(label="Attackers", value='att'),
            discord.SelectOption(label="Midfielders", value='mid'),
            discord.SelectOption(label="Defenders", value='dfn'),
            discord.SelectOption(label="Goalkeeper", value='gk'),
            discord.SelectOption(label="Bench", value='bench')
        ]
    select = DropdownSelect(options, select_player, conf, "Select a Position")
    view = DropdownView(select)
    await interaction.response.send_message("Select a position: ", view=view)

async def select_player(interaction: discord.Interaction, conf):
    selection = conf[interaction.data['values'][0]]


async def select_player_2(interaction: discord.Interaction):
    pass