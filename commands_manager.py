import discord
import logging
from discord.ext import commands
from typing import NoReturn, Optional
from config_manager import ConfigManager
from random_message import RandomMessage
from constants import (KEY_GUILD_NAME, KEY_TARGET_CHANNEL_ID, KEY_ENABLE_ATTACHMENTS, KEY_ENABLE_URLS,
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
        elif message.content.startswith("$targetchat"):
            await self.target_chat_command(message, current_config)
        elif message.content == "$urls":
            await self.urls_command(message, current_config)
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
        `$targetchat #channel` - Sets the target channel where random messages will be fetched from.
        `$urls` - Enables or disables the inclusion of messages containing URLs in random message selection.
        `$mentions` - Enables or disables the inclusion of messages containing URLs in random message selection.
        `$attachments` - Enables or disables the inclusion of messages with attachments in random message selection.
        `$ranmsg` - Sends a random message from the target channel.

        Configure the bot by setting up a target channel first using `!targetchat`, followed by other configurations
        as needed. 
        """
        await message.channel.send(help_message)

    async def target_chat_command(self, message: discord.Message, config: dict) -> NoReturn:
        """Sets the target text channel for random messages and updates the configuration.

        Args:
            message (discord.Message): The command message with channel mention.
            config (dict): The server's current configuration settings.
        """
        first_message_datetime = await self.get_first_message_datetime(message.channel_mentions[0])
        if first_message_datetime:
            config[KEY_TARGET_CHANNEL_ID] = str(message.channel_mentions[0].id)
            config[KEY_START_DATE] = first_message_datetime
            config[KEY_END_DATE] = message.created_at.isoformat()
            await message.channel.send(f"Target channel of is set to {message.channel_mentions[0]}")
            logging.info(f"Target channel of is set to {message.channel_mentions[0]} with startdate: "
                         f"{config[KEY_START_DATE]} and \n\tenddate: {config[KEY_END_DATE]}"
                         f"in {config[KEY_GUILD_NAME]}")
            self.config_manager.save_configs_to_file()
        else:
            await message.channel.send(f"There was an error in setting ({message.channel.name} as the target channel")

    async def urls_command(self, message: discord.Message, config: dict) -> NoReturn:
        """Toggles the inclusion of URLs in random message selections.

        Args:
            message (discord.Message): The message invoking the urls command.
            config (dict): The server's current configuration settings.
        """
        config[KEY_ENABLE_URLS] = not config[KEY_ENABLE_URLS]
        await message.channel.send(f"URLs set to {config[KEY_ENABLE_URLS]}")
        logging.info(f"URLs were set to {config[KEY_ENABLE_URLS]} in {config[KEY_GUILD_NAME]}")
        self.config_manager.save_configs_to_file()

    async def attachments_command(self, message: discord.Message, config: dict) -> NoReturn:
        """Toggles the inclusion of attachments in random message selections.

        Args:
            message (discord.Message): The message invoking the attachments command.
            config (dict): The server's current configuration settings.
        """
        config[KEY_ENABLE_ATTACHMENTS] = not config[KEY_ENABLE_ATTACHMENTS]
        await message.channel.send(f"Attachemnts set to {config[KEY_ENABLE_ATTACHMENTS]}")
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
