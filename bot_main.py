import discord
import logging
from typing import NoReturn
from config_manager import ConfigManager
from random_message import RandomMessage
from commands_manager import Commands


logging.basicConfig(
    filename="logs.txt",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - Module: %(module)s - Function: %(funcName)s \n\tMessage: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class Bot(discord.Client):
    """A Discord bot for managing server configurations and responding to commands.

    This bot handles user commands, manages server-specific configurations, and can send random messages from
    a specified channel's history.

    Attributes:
        token (str): The Discord bot token used for authentication.
        config_manager (ConfigManager): Manages server-specific configurations.
        random_message (RandomMessage): Handles fetching and sending random messages.
        commands (Commands): Processes and responds to user commands.
    """
    def __init__(self, token: str) -> NoReturn:
        """Initializes the bot with necessary configurations and permissions.

        Args:
            token: A string representing the Discord bot token for authentication.
        """
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents)
        self.token = token
        self.config_manager = ConfigManager(self)
        self.random_message = RandomMessage(self, self.config_manager)
        self.commands = Commands(self, self.config_manager, self.random_message)

    async def on_ready(self) -> NoReturn:
        """Handles actions to be performed once the bot is ready and connected to Discord."""
        logging.info(f"Ready: {self.user}")
        # Load server configutarions and add new server configuaration to it if availabe
        self.config_manager.load_configs()
        self.config_manager.update_configs()

    async def on_guild_join(self, guild: discord.Guild) -> NoReturn:
        """Initialize guild's config upon joining, if it doesn't already exist
        Args:
            guild (discord.Guild): Discord guild instance.
        """
        logging.info(f"Joinned a new guild: {guild.name} (ID: {guild.id})")
        if str(guild.id) not in self.config_manager.server_configs:
            self.config_manager.initialize_guild_config(guild)
            self.config_manager.save_configs_to_file()
            logging.info(f"Default configuration initialized for guild: {guild.name} (ID: {guild.id})")
        else:
            logging.info(f"Existing configuration found for guild: {guild.name} (ID: {guild.id}), no update necessary.")

    async def on_message(self, message: discord.Message) -> NoReturn:
        """Responds to new messages, excluding those sent by the bot itself.

        Args:
            message (discord.Message): A discord.Message object representing the message to respond to.
        """
        if message.author == self.user:
            return
        await self.commands.handle_command(message)

    def run_bot(self) -> NoReturn:
        """Starts bot using the provided token"""
        self.run(self.token)
