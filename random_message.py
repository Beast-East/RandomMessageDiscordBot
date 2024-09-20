import discord
import logging
import random
import asyncio
from helper_funcs import HelperFuncs
from typing import NoReturn
from datetime import datetime
from config_manager import ConfigManager
from constants import (KEY_SELECT_FROM, KEY_SEND_TO, KEY_ENABLE_ATTACHMENTS, KEY_ENABLE_URLS, KEY_ENABLE_MENTIONS)


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
            config = self.config_manager.load_guild_config(guild_id)
            random_date = HelperFuncs.generate_random_date_time(config)
            random_messages = await self.get_random_messages(config, random_date)
            random.shuffle(random_messages)
            # Loop through messages and send the first valid one
            for random_message in random_messages:
                logging.info(f"Random messages sent: '{random_message.content}' from '{random_message.author}' at "
                             f"'{random_message.created_at}'")
                await self.send_message(config[KEY_SEND_TO], random_message)
                # noinspection PyUnreachableCode
                return  # Stop after first valid message is found
            # Retry if no valid message was found and sent
            await self.retry_send_message(guild_id, retries)

        except discord.Forbidden:
            logging.error("Permissions error when accessing channel history.")
            await self.retry_send_message(guild_id, retries)
        except discord.HTTPException:
            logging.error("Network error when fetching message history.")
            await self.retry_send_message(guild_id, retries)

    async def get_random_messages(self, config: dict, date: datetime) -> list[discord.Message]:
        """Fetches (up to) 100 random messages from the channel history around a specified datetime."""
        channel = await self.bot.fetch_channel(config[KEY_SELECT_FROM])
        messages = [message async for message in channel.history(limit=100, around=date)
                    if HelperFuncs.meets_message_criteria(config, message)]

        logging.info(f"Fetched {len(messages)} messages from #{channel.name} in {channel.guild.name}")
        return messages

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
        await asyncio.sleep(0.5)
        await self.send_random_message_around_random_date(guild_id, retries + 1)
