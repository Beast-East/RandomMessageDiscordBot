import discord
import random
import logging
import asyncio
from helper_funcs import HelperFuncs
from typing import NoReturn, Optional
from random_message import RandomMessage
from config_manager import ConfigManager


class PollGames:
    def __init__(self, random_message_manager: RandomMessage, config_manager: ConfigManager):
        self.random_message_manager = random_message_manager
        self.config_manager = config_manager

    async def pollgame_who_sent_it(self, message: discord.Message, retries: int = 0):
        # Generate a list of (up to) 101 random messages, shuffle the list, and get the first message for the poll
        channel = message.channel
        duration = self.get_duration_from_message(message.content)
        if duration is None:
            await channel.send("Please provide a valid countdown duration in seconds.")
            return

        config = self.config_manager.load_guild_config(channel.guild.id)
        random_date = HelperFuncs.generate_random_date_time(config)
        random_messages = await self.random_message_manager.get_random_messages(config, random_date)
        random.shuffle(random_messages)

        if not random_messages:
            await self.retry_pollgame_who_sent_it(channel, retries)
            return

        poll_message = random_messages[0]
        poll_message_correct_user = poll_message.author.name
        poll_message_incorrect_users = []

        for random_message in random_messages[1:]:
            if (random_message.author.name != poll_message_correct_user and len(poll_message_incorrect_users) < 2
                    and random_message.author.name not in poll_message_incorrect_users):
                poll_message_incorrect_users.append(random_message.author.name)

        if len(poll_message_incorrect_users) < 2:
            await self.retry_pollgame_who_sent_it(channel, retries + 1)
            return

        # Create the poll message
        choices = [str(poll_message_correct_user), str(poll_message_incorrect_users[0]), str(poll_message_incorrect_users[1])]
        random.shuffle(choices)
        poll_content = (f"Who sent this message?\n\"{poll_message.content}\"\n" +
                        f"1. {choices[0]}\n2. {choices[1]}\n3. {choices[2]}")
        poll = await channel.send(poll_content)
        for i in range(len(choices)):
            await poll.add_reaction(f"{i + 1}\u20E3")  # 1️⃣, 2️⃣, 3️⃣, etc.
        await self.start_countdown(channel, duration, poll_message_correct_user)

    async def retry_pollgame_who_sent_it(self, channel, retries: int) -> NoReturn:
        if retries < 3:
            await self.pollgame_who_sent_it(channel, retries + 1)
        else:
            logging.info("Max retries reached for pollgame_who_sent_it, stopping.")

    @staticmethod
    async def start_countdown(channel: discord.TextChannel, duration: int, answer: str):
        # Send the initial countdown message
        countdown_message = await channel.send(f"Countdown: {duration}")

        for remaining in range(duration, 0, -1):
            await asyncio.sleep(1)  # Wait for 1 second
            await countdown_message.edit(content=f"Countdown: {remaining}")

        await countdown_message.edit(content=f"Answer: {answer}")

    @staticmethod
    def get_duration_from_message(content: str) -> Optional[int]:
        """Extracts the duration from the message content."""
        try:
            # Split the content and get the second part
            _, duration_str = content.split()
            duration = int(duration_str)
            return duration if duration > 0 else None
        except (ValueError, IndexError):
            return None
