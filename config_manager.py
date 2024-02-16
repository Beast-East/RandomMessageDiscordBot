import json
import discord
import logging
from typing import NoReturn
from datetime import datetime
from constants import (KEY_GUILD_NAME, KEY_TARGET_CHANNEL_ID, KEY_ENABLE_ATTACHMENTS, KEY_ENABLE_URLS,
                       KEY_ENABLE_MENTIONS, KEY_START_DATE, KEY_END_DATE)


class ConfigManager:
    """Manages the configurations for different servers that the bot operates in.

        Attributes:
            bot (discord.Client): The bot instance to interact with Discord.
            config_path (str): The file path for storing server configurations.
            server_configs (dict): A dictionary holding server-specific configurations.
    """
    def __init__(self, bot: discord.Client, config_path="server_configs.json") -> NoReturn:
        """Initializes the configuration manager with the bot instance and configuration path.

        Args:
            bot (discord.Client): The Discord client instance.
            config_path (str): The path to the JSON file for storing configurations. Defaults to 'server_configs.json'.
        """
        self.bot = bot
        self.config_path = config_path
        self.server_configs = {}
        self.load_configs()

    def update_configs_on_run(self) -> NoReturn:
        """Updates the server configurations with any new servers the bot has joined since it last run."""
        for guild in self.bot.guilds:
            # Convert guild.id to string to store it to avoid discrepancies in accessing it and storing it.
            guild_id = str(guild.id)
            if guild_id not in self.server_configs:
                self.server_configs[guild_id] = {
                    KEY_GUILD_NAME: guild.name,
                    KEY_TARGET_CHANNEL_ID: None,
                    KEY_ENABLE_ATTACHMENTS: False,
                    KEY_ENABLE_URLS: False,
                    KEY_ENABLE_MENTIONS: False,
                    KEY_START_DATE: None,
                    KEY_END_DATE: None,
                }
                logging.info(f"{guild.name}({guild.id}) is being added to server_configs")
                self.save_configs_to_file()

    def load_configs(self) -> NoReturn:
        """Loads the server configurations from a JSON file."""
        try:
            with open('server_configs.json', 'r') as file:
                self.server_configs = json.load(file)
        except FileNotFoundError:
            logging.info("JSON file not found. server_configs was initialized to {}.")
        except json.JSONDecodeError:
            logging.info("JSON file is likely empty. server_configs was initialized to {}.")

    def save_configs_to_file(self) -> NoReturn:
        """Saves the current server configurations to a JSON file."""
        def custom_converter(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable.")

        with open('server_configs.json', 'w') as file:
            json.dump(self.server_configs, file, default=custom_converter)
