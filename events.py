import os

import discord
from discord.ext import commands, tasks

from meetup_rest_api import fetch_meetup_events_detail

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

description = """An example bot that retreives event name"""

bot = commands.Bot(command_prefix="?", description=description, intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


@bot.command()
async def event(ctx, chapter):
    """
    Fetch event details from meetup.com and create the same event in the server
    """
    guild = ctx.guild
    scheduled_events = fetch_meetup_events_detail(chapter)

    for event in scheduled_events:
        await guild.create_scheduled_event(**event)

    await ctx.send(f"{len(scheduled_events)} event(s) created")


bot.run(DISCORD_TOKEN)
