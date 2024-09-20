import logging
import discord
import random
import re
from datetime import timezone, timedelta, datetime
from typing import Optional
from constants import (KEY_START_DATE, KEY_ENABLE_URLS, KEY_ENABLE_MENTIONS, KEY_ENABLE_ATTACHMENTS)


class HelperFuncs:
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @staticmethod
    def meets_message_criteria(config: dict, message: discord.Message) -> bool:
        """Checks whether the message meets the criteria for being sent."""
        contains_url = HelperFuncs.search_for_url(message.content)

        criteria_result = (config[KEY_ENABLE_URLS] or not contains_url)
        criteria_result &= (message.author != message.guild.me)
        criteria_result &= (config[KEY_ENABLE_ATTACHMENTS] or not message.attachments)
        criteria_result &= (config[KEY_ENABLE_MENTIONS] or not HelperFuncs.message_has_mentions(message))

        return criteria_result

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

    @staticmethod
    def generate_random_date_time(config: dict) -> datetime:
        """Generates a random datetime within the configured start and end dates."""
        start_date = datetime.fromisoformat(config[KEY_START_DATE])
        end_date = datetime.now().replace(tzinfo=timezone.utc)
        random_seconds = random.randint(0, int((end_date - start_date).total_seconds()))
        random_date_time = start_date + timedelta(seconds=random_seconds)
        logging.info(f"Generated random date: {random_date_time}")
        return random_date_time.replace(tzinfo=timezone.utc)

    @staticmethod
    def search_for_url(message: str) -> bool:
        """Checks if the message contains a URL."""
        url_pattern = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        return re.search(url_pattern, message) is not None

    @staticmethod
    def message_has_mentions(message: discord.Message) -> bool:
        """Checks if the message contains mentions."""
        return bool(message.mentions or message.role_mentions or message.mention_everyone)
