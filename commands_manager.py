import discord
import logging
import helper_funcs
from discord.ext import commands
from typing import NoReturn, Optional
from poll_games import PollGames
from config_manager import ConfigManager
from random_message import RandomMessage
from constants import (KEY_GUILD_NAME, KEY_SELECT_FROM, KEY_SEND_TO, KEY_ENABLE_ATTACHMENTS, KEY_ENABLE_URLS,
                       KEY_ENABLE_MENTIONS, KEY_START_DATE, HELP_MESSAGE)


class Commands(commands.Cog):
    """
       Handles command processing and execution for the Discord bot.

       Attributes:
           bot (discord.Client): The Discord client instance.
           config_manager (ConfigManager): The configuration manager instance to handle server configurations.
           random_message (RandomMessage): The random message handler instance to manage sending random messages.
       """
    def __init__(self, bot: discord.Client, config_manager: ConfigManager, random_message: RandomMessage, pollgames: PollGames) -> NoReturn:
        """Initializes the Commands object with necessary instances. """
        self.bot = bot
        self.config_manager = config_manager
        self.random_message = random_message
        self.pollgames = pollgames

    # COMMAND LIST
    async def handle_command(self, message: discord.Message) -> NoReturn:
        """Determines the type of command received and executes the corresponding action."""
        current_config = self.config_manager.server_configs[str(message.guild.id)]
        if message.content == "$help":
            await self.help_command(message)
        elif message.content.startswith("$selectandsend"):
            await self.select_and_send_command(message, current_config)
        elif message.content == "$urls":
            await self.urls_command(message, current_config)
        elif message.content == "$attachments":
            await self.attachments_command(message, current_config)
        elif message.content == "$mentions":
            await self.mentions_command(message, current_config)
        elif message.content == "$ranmsg":
            if current_config[KEY_SELECT_FROM] is None or current_config[KEY_SEND_TO] is None:
                await message.channel.send("Set up the bot first with $selectandsend command(use $help for more info)")
                return
        elif message.content.startswith("$whosentit"):
            await self.pollgames.pollgame_who_sent_it(message)

    # COMMAND IMPLEMENTATIONS
    @staticmethod
    async def help_command(message: discord.Message) -> NoReturn:
        """Sends a help message listing all available commands and descriptions."""
        await message.channel.send(HELP_MESSAGE)

    async def select_and_send_command(self, message: discord.Message, config: dict) -> NoReturn:
        """Sets the target text channel for random messages and updates the configuration."""
        channel_mentions = message.channel_mentions
        if not channel_mentions:
            await message.channel.send(f"There was an error in setting up the target channel")
            return

        config[KEY_START_DATE] = await helper_funcs.get_first_message_datetime(channel_mentions[0])
        config[KEY_SELECT_FROM] = str(channel_mentions[0].id)
        config[KEY_SEND_TO] = str(message.channel_mentions[1].id)
        await message.channel.send(f"Random messages will be selected from {channel_mentions[0]}"
                                       f" and send to {channel_mentions[1]}")
        logging.info(f"Select from {channel_mentions[0]} and send to {channel_mentions[1]}"
                         f" with startdate: {config[KEY_START_DATE]}"
                         f"in {config[KEY_GUILD_NAME]}")
        self.config_manager.save_configs_to_file()

    async def urls_command(self, message: discord.Message, config: dict) -> NoReturn:
        """Toggles the inclusion of URLs in random message selections."""
        config[KEY_ENABLE_URLS] = not config[KEY_ENABLE_URLS]
        await message.channel.send(f"URLs set to {config[KEY_ENABLE_URLS]}")
        logging.info(f"URLs were set to {config[KEY_ENABLE_URLS]} in {config[KEY_GUILD_NAME]}")
        self.config_manager.save_configs_to_file()

    async def attachments_command(self, message: discord.Message, config: dict) -> NoReturn:
        """Toggles the inclusion of attachments in random message selections."""
        config[KEY_ENABLE_ATTACHMENTS] = not config[KEY_ENABLE_ATTACHMENTS]
        await message.channel.send(f"Attachments set to {config[KEY_ENABLE_ATTACHMENTS]}")
        logging.info(f"Attachments was set to: {config[KEY_ENABLE_ATTACHMENTS]} in {config[KEY_GUILD_NAME]}")
        self.config_manager.save_configs_to_file()

    async def mentions_command(self, message: discord.Message, config: dict) -> NoReturn:
        """Toggles the inclusion of attachments in random message selections."""
        config[KEY_ENABLE_MENTIONS] = not config[KEY_ENABLE_MENTIONS]
        await message.channel.send(f"Mentions set to {config[KEY_ENABLE_MENTIONS]}")
        logging.info(f"Mentions was set to: {config[KEY_ENABLE_MENTIONS]} in {config[KEY_GUILD_NAME]}")
        self.config_manager.save_configs_to_file()

    async def random_message_command(self, guild: discord.Guild) -> NoReturn:
        """Triggers the sending of a random message from the configured channel."""
        await self.random_message.send_random_message_around_random_date(guild.id)
