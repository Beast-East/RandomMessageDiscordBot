import discord
import logging
from discord.ext import commands
from typing import NoReturn, Optional
from config_manager import ConfigManager
from random_message import RandomMessage
from constants import (KEY_GUILD_NAME, KEY_SELECT_FROM, KEY_SEND_TO, KEY_ENABLE_ATTACHMENTS,
                       KEY_ENABLE_MENTIONS, KEY_START_DATE, KEY_END_DATE)


class Commands(commands.Cog):
    """
       Handles command processing and execution for the Discord bot.

       Attributes:
           bot (discord.Client): The Discord client instance.
           config_manager (ConfigManager): The configuration manager instance to handle server configurations.
           random_message (RandomMessage): The random message handler instance to manage sending random messages.
       """
    def __init__(self, bot: discord.Client, config_manager: ConfigManager, random_message: RandomMessage) -> NoReturn:
        """Initializes the Commands object with necessary instances.

        Args:
            bot (discord.Client): The Discord client instance.
            config_manager (ConfigManager): The configuration manager for server settings.
            random_message (RandomMessage): The handler for random message functionality.
        """
        self.bot = bot
        self.config_manager = config_manager
        self.random_message = random_message

    async def handle_command(self, message: discord.Message) -> NoReturn:
        """Determines the type of command received and executes the corresponding action.

        Args:
               message (discord.Message): The message. Possibly containing the command.
        """
        current_config = self.config_manager.server_configs[str(message.guild.id)]
        if message.content == "$help":
            await self.help_command(message)
        elif message.content.startswith("$selectandsend"):
            await self.select_and_send_command(message, current_config)
        elif message.content == "$attachments":
            await self.attachments_command(message, current_config)
        elif message.content == "$mentions":
            await self.mentions_command(message, current_config)
        elif message.content == "$ranmsg":
            await self.random_message_command(message.guild)

    @staticmethod
    async def help_command(message: discord.Message) -> NoReturn:
        """Sends a help message listing all available commands and descriptions.

        Args:
            message (discord.Message): The message invoking the help command.
        """
        help_message = """
        ** Commands **

        `$help` - Shows this help message.
        `$selectandsend *#sourcechannel* *#destchannel*` - Set the channel where random messages will be selected from
        and the channel where said message will be sent to.
        `$urls` - Toggles the inclusion of messages containing URLs in random message selection(True/False).
         False by default.
        `$mentions` -  Toggles the inclusion of messages with mentions(True/False). False by default. When enabled, 
        @(everyone), @(rolementions) and @(member) mentions are all included.
        `$attachments` - Toggles the inclusion of messages with attachments(True/False). False by default.
        `$ranmsg` - Sends a random message from configured #sourcechannel to the #destchannel.

        Use $selectandsend to define the source and destination channels for the random message feature to 
        function correctly❗
        """
        await message.channel.send(help_message)

    async def select_and_send_command(self, message: discord.Message, config: dict) -> NoReturn:
        """Sets the target text channel for random messages and updates the configuration.

        Args:
            message (discord.Message): The command message with channel mention.
            config (dict): The server's current configuration settings.
        """
        channel_mentions = message.channel_mentions
        if channel_mentions:
            first_message_datetime = await self.get_first_message_datetime(channel_mentions[0])
            config[KEY_SELECT_FROM] = str(channel_mentions[0].id)
            send_to_channel = message.channel_mentions[1] if len(channel_mentions) > 1 \
                else message.channel_mentions[0]
            config[KEY_SEND_TO] = str(send_to_channel.id)

            config[KEY_START_DATE] = first_message_datetime
            config[KEY_END_DATE] = message.created_at.isoformat()

            await message.channel.send(f"Random messages will be selected from {channel_mentions[0]}"
                                       f" and send to {send_to_channel}")
            logging.info(f"Select from {channel_mentions[0]} and send to {send_to_channel}"
                         f" with startdate: {config[KEY_START_DATE]} and \n\tenddate: {config[KEY_END_DATE]}"
                         f"in {config[KEY_GUILD_NAME]}")
            self.config_manager.save_configs_to_file()
        else:
            await message.channel.send(f"There was an error in setting ({message.channel.name} as the target channel")

    async def attachments_command(self, message: discord.Message, config: dict) -> NoReturn:
        """Toggles the inclusion of attachments in random message selections.

        Args:
            message (discord.Message): The message invoking the attachments command.
            config (dict): The server's current configuration settings.
        """
        config[KEY_ENABLE_ATTACHMENTS] = not config[KEY_ENABLE_ATTACHMENTS]
        await message.channel.send(f"Attachments set to {config[KEY_ENABLE_ATTACHMENTS]}")
        logging.info(f"Attachments was set to: {config[KEY_ENABLE_ATTACHMENTS]} in {config[KEY_GUILD_NAME]}")
        self.config_manager.save_configs_to_file()

    async def mentions_command(self, message: discord.Message, config: dict) -> NoReturn:
        """Toggles the inclusion of attachments in random message selections.

        Args:
            message (discord.Message): The message invoking the mentions command.
            config (dict): The server's current configuration settings.
        """
        config[KEY_ENABLE_MENTIONS] = not config[KEY_ENABLE_MENTIONS]
        await message.channel.send(f"Mentions set to {config[KEY_ENABLE_MENTIONS]}")
        logging.info(f"Mentions was set to: {config[KEY_ENABLE_MENTIONS]} in {config[KEY_GUILD_NAME]}")
        self.config_manager.save_configs_to_file()

    async def random_message_command(self, guild: discord.Guild) -> NoReturn:
        """Triggers the sending of a random message from the configured channel.

        Args:
           guild (discord.Guild): The guild where the command was issued.
        """
        await self.random_message.send_random_message_around_random_date(guild.id)

    @staticmethod
    async def get_first_message_datetime(channel: discord.TextChannel) -> Optional[str]:
        """Fetches the datetime of the first message in the specified channel.

        Args:
            channel (discord.TextChannel): The channel to check.

        Returns:
            str: The ISO format datetime string of the first message, or None if unable to fetch.

        Raises:
            discord.Forbidden: If the bot does not have permissions to access message history.
            discord.HTTPException: If fetching the message history fails.
        """
        try:
            first_message = None
            async for message in channel.history(limit=1, oldest_first=True):
                first_message = message
            return str(first_message.created_at)
        except discord.Forbidden:
            logging.error("You do not have permissions to get channel message history")
            return
        except discord.HTTPException:
            logging.error("The request to get message history failed(can't get first message).")
            return
