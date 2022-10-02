# This example requires the 'message_content' privileged intent to function.
import os

import discord
from discord.ext import commands

from meetup_rest_api import fetch_meetup_events_detail

DISCORD_TOKEN = os.getenv("BARISTA_TOKEN")

# Defines a custom Select containing colour options
# that the user can choose. The callback function
# of this class is called when the user changes their choice
class Dropdown(discord.ui.Select):
    def __init__(self, scheduled_events: dict):

        # Set the options that will be presented inside the dropdown
        self.scheduled_events = scheduled_events
        options = []
        for event_id, event in scheduled_events.items():
            options.append(
                discord.SelectOption(
                    value=event_id,
                    label=event["name"],
                    description=event["start_time"].strftime("%m/%d/%Y"),
                )
            )

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(
            placeholder="Choose your event",
            min_values=1,
            max_values=len(scheduled_events),
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.
        guild = interaction.guild
        for event_id in self.values:
            event = self.scheduled_events[event_id]
            await guild.create_scheduled_event(**event)

        await interaction.response.send_message(f"{len(self.values)} event(s) created")


class DropdownView(discord.ui.View):
    def __init__(self, scheduled_events: dict):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Dropdown(scheduled_events))


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=commands.when_mentioned_or("!"), intents=intents
        )

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")


bot = Bot()


@bot.command()
@commands.has_any_role("nyc")
async def event(ctx, chapter=None):
    """Sends a message with our dropdown containing colours"""

    if chapter is not None:
        scheduled_events = fetch_meetup_events_detail(chapter)

        # Create the view containing our dropdown
        view = DropdownView(scheduled_events)

        # Sending a message containing our view
        await ctx.send("Pick your event(s):", view=view)
    else:
        await ctx.send(
            "Pull meetup.com events over to discord\n\nUsage: !event <INSERT MEETUP.COM GROUP URL>"
        )


bot.run(DISCORD_TOKEN)
