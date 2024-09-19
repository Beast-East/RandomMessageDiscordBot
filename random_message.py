import discord
import logging
import random
import re
import asyncio
from typing import NoReturn
from datetime import timezone, timedelta, datetime
from config_manager import ConfigManager
from constants import (KEY_SELECT_FROM, KEY_SEND_TO, KEY_ENABLE_ATTACHMENTS, KEY_ENABLE_URLS, KEY_START_DATE,
                       KEY_ENABLE_MENTIONS)


class RandomMessage:
    """Manages the fetching and sending of random messages within the Discord bot."""
    def __init__(self, bot: discord.Client, config_manager: ConfigManager) -> NoReturn:
        self.bot = bot
        self.config_manager = config_manager

    async def send_random_message_around_random_date(self, guild_id: int, retries: int = 0) -> NoReturn:
        """Main function to fetch a random message and send it based on criteria."""
        if retries >= 3:
            logging.info(f"Max retries reached for guild_id={guild_id}, stopping.")
            return
        try:
            config = self.load_guild_config(guild_id)
            random_date = self.generate_random_date_time(config)
            random_messages = await self.get_random_messages(config['select_from'], random_date)
            random.shuffle(random_messages)
            # Loop through messages and send the first valid one
            for random_message in random_messages:
                if random_message and self.should_send_message(config, random_message):
                    logging.info(f"Random messages sent: '{random_message.content}' from '{random_message.author}' at '{random_message.created_at}'")
                    await self.send_message(config['send_to'], random_message)
                    return  # Stop after first valid message is found
            # Retry if no valid message was found and sent
            await self.retry_send_message(guild_id, retries)

        except discord.Forbidden:
            logging.error("Permissions error when accessing channel history.")
            await self.retry_send_message(guild_id, retries)
        except discord.HTTPException:
            logging.error("Network error when fetching message history.")
            await self.retry_send_message(guild_id, retries)

    def load_guild_config(self, guild_id: int) -> dict:
        """Loads the configuration for the specified guild."""
        str_guild_id = str(guild_id)
        return {
            'start_date': self.config_manager.server_configs[str_guild_id][KEY_START_DATE],
            'select_from': self.config_manager.server_configs[str_guild_id][KEY_SELECT_FROM],
            'send_to': self.config_manager.server_configs[str_guild_id][KEY_SEND_TO],
            'enable_attachments': self.config_manager.server_configs[str_guild_id][KEY_ENABLE_ATTACHMENTS],
            'enable_urls': self.config_manager.server_configs[str_guild_id][KEY_ENABLE_URLS],
            'enable_mentions': self.config_manager.server_configs[str_guild_id][KEY_ENABLE_MENTIONS]
        }

    @staticmethod
    def generate_random_date_time(config: dict) -> datetime:
        """Generates a random datetime within the configured start and end dates."""
        start_date = datetime.fromisoformat(config['start_date'])
        end_date = datetime.now().replace(tzinfo=timezone.utc)
        random_seconds = random.randint(0, int((end_date - start_date).total_seconds()))
        random_date_time = start_date + timedelta(seconds=random_seconds)
        logging.info(f"Generated random date: {random_date_time}")
        return random_date_time.replace(tzinfo=timezone.utc)

    async def get_random_messages(self, channel_id: int, date: datetime) -> list[discord.Message]:
        """Fetches (up to) 100 random messages from the channel history around a specified datetime."""
        channel = await self.bot.fetch_channel(channel_id)
        messages = [message async for message in channel.history(limit=100, around=date) if message.author != self.bot.user]

        logging.info(f"Fetched {len(messages)} messages from #{channel.name} in {channel.guild.name}")
        return messages

    def should_send_message(self, config: dict, message: discord.Message) -> bool:
        """Checks whether the message meets the criteria for being sent."""
        contains_url = self.search_for_url(message.content)

        should_send = (config['enable_urls'] or not contains_url)
        should_send &= (config['enable_attachments'] or not message.attachments)
        should_send &= (config['enable_mentions'] or not self.message_has_mentions(message))

        return should_send

    @staticmethod
    def message_has_mentions(message: discord.Message) -> bool:
        """Checks if the message contains mentions."""
        return bool(message.mentions or message.role_mentions or message.mention_everyone)

    async def send_message(self, channel_id: int, message: discord.Message) -> NoReturn:
        """Sends the message content or attachment to the specified channel."""
        channel = await self.bot.fetch_channel(channel_id)
        if message.attachments:
            await channel.send(message.attachments[0].url)
        else:
            await channel.send(message.content)
        logging.info(f"Message sent in {channel.name}: '{message.content}'")

    async def retry_send_message(self, guild_id: int, retries: int) -> NoReturn:
        """Retries sending a message after a short delay."""
        await asyncio.sleep(1)
        await self.send_random_message_around_random_date(guild_id, retries + 1)

    @staticmethod
    def search_for_url(message: str) -> bool:
        """Checks if the message contains a URL."""
        url_pattern = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        return re.search(url_pattern, message) is not None
