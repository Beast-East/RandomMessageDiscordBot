import discord
import logging
import random
import re
import asyncio
from typing import NoReturn
from datetime import timezone, timedelta, datetime
from config_manager import ConfigManager
from constants import (KEY_TARGET_CHANNEL_ID, KEY_ENABLE_ATTACHMENTS, KEY_ENABLE_URLS, KEY_START_DATE,
                       KEY_END_DATE)


class RandomMessage:
    """Manages the fetching and sending of random messages within the Discord bot.

    Attributes:
        bot (discord.Client): The Discord client instance.
        config_manager (ConfigManager): The configuration manager instance to handle server configurations.
    """
    def __init__(self, bot: discord.Client, config_manager: ConfigManager) -> NoReturn:
        self.bot = bot
        self.config_manager = config_manager

    async def send_random_message_around_random_date(self, guild_id: int, retries: int = 0) -> NoReturn:
        """Attempts to send a random message from a target channel based on configured criteria.

        Selects a random message from the history of a specified target channel within a guild. The selection is based
        on a random datetime generated between configured start and end dates. It retries up to a maximum number of times
        if conditions are not met.

        Args:
            guild_id (int): The ID of the guild from which to fetch and send the message.
            retries (int): The current number of attempts made. Starts by defualt from 0.

        Raises:
            discord.HTTPException: Failure in fetching guild information or message history due to network issues.
            discord.Forbidden: Bot lacks permissions to fetch channel information or message history.
        """
        max_retries = 8
        if retries >= max_retries:
            logging.info(f"Maximum attempts reached, stopping further message fetching.(attempts={retries})")
            return

        str_guild_id = str(guild_id)
        guild_config = self.config_manager.server_configs[str_guild_id]
        logging.debug(f"Start date type: {type(guild_config[KEY_START_DATE])}, value: '{guild_config[KEY_START_DATE]}'")
        logging.debug(f"End date type: {type(guild_config[KEY_END_DATE])}, value: '{guild_config[KEY_END_DATE]}'")

        start_date = guild_config[KEY_START_DATE]
        end_date = guild_config[KEY_END_DATE]
        target_channel_id = guild_config[KEY_TARGET_CHANNEL_ID]
        enable_attachments = guild_config[KEY_ENABLE_ATTACHMENTS]
        enable_urls = guild_config[KEY_ENABLE_URLS]

        # Fetch random message from channel's history
        try:
            if target_channel_id is not None:
                # Fetch target channel, if it exists
                channel = await self.bot.fetch_channel(target_channel_id)

                random_date = self.generate_random_date_time(str_guild_id)

                if start_date is None or end_date is None:
                    await channel.send("Use !targetchannel first")
                    logging.info("Start date or end date not set for this server.")
                    return

                random_message = await self.get_random_message(channel=channel, date=random_date)
                if random_message:
                    # Check difference between generated time and the date the message was created at
                    # and if the message contains a URL
                    max_difference = timedelta(days=10)
                    difference = abs(random_message.created_at - random_date)
                    contains_url = self.search_for_url(random_message.content)

                    should_send = difference <= max_difference
                    should_send &= enable_urls or not contains_url
                    should_send &= enable_attachments or not random_message.attachments

                    if should_send:
                        await channel.send(random_message.content)
                        logging.info(f"Message was sent in {channel.name}: \'{random_message.content}\'")
                    else:
                        await asyncio.sleep(1)  # Add a short delay before retrying
                        await self.send_random_message_around_random_date(guild_id, retries + 1)
        except discord.Forbidden:
            logging.error("You do not have permissions to get channel message history")
            await asyncio.sleep(1)  # Add a short delay before retrying
            await self.send_random_message_around_random_date(guild_id, retries + 1)
        except discord.HTTPException:
            logging.error("The request to get message history failed.")
            await asyncio.sleep(1)  # Add a short delay before retrying
            await self.send_random_message_around_random_date(guild_id, retries + 1)

    def generate_random_date_time(self, str_guild_id: str) -> datetime:
        """Generates a random datetime within the configured start and end dates for a guild.

        Args:
            str_guild_id (str): The guild ID as a string to fetch configuration for.

        Returns:
            datetime.datetime: A randomly selected datetime object within the configured range.
        """
        guild_config = self.config_manager.server_configs[str_guild_id]

        start_date = datetime.fromisoformat(guild_config[KEY_START_DATE])
        end_date = datetime.fromisoformat(guild_config[KEY_END_DATE])

        difference_between_start_end_seconds = int((end_date - start_date).total_seconds())
        random_date_time = (start_date
                            + timedelta(0, random.randint(0, difference_between_start_end_seconds)))
        logging.info(f"Generated random date: {random_date_time}")
        # Convert date to UTC
        return random_date_time.replace(tzinfo=timezone.utc)

    async def get_random_message(self, channel: discord.TextChannel, date: datetime) -> discord.Message:
        """Fetches a message from the channel history around a specified datetime.

        Args:
            channel (discord.TextChannel): The channel from which to fetch the message.
            date (datetime.datetime): The datetime around which to fetch a message.

        Returns:
            discord.Message: The fetched message if successful, None otherwise.

        Raises:
            discord.HTTPException: Failure in fetching message history due to network issues.
            discord.Forbidden: Bot lacks permission to access message history.
        """
        try:
            async for message in channel.history(limit=4, around=date):
                logging.info(f"Random message fetched: {message.content} by {message.author} "
                             f"date: {message.created_at}")
                if message and message.author != self.bot.user:
                    return message
        except discord.Forbidden:
            logging.error("You do not have permissions to get channel message history")
        except discord.HTTPException:
            logging.error(f"The request to get message history failed. Channel ID: {channel}")

    @staticmethod
    def search_for_url(message: str) -> bool:
        """Determines if a message contains a URL.

        Args:
            message (str): The content of the message to search.

        Returns:
            bool: True if the message contains a URL, False otherwise.
        """
        url_pattern = (r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|"
                       r"(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")
        return re.search(url_pattern, message) is not None
