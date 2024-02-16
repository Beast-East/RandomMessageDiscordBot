# Random Message Discord Bot

## Description
This Discord bot can select a random message from a text channel's history and send it. The selection of said message can be configured through the use commands. For example, including/excluding messages that contain 
URLs/attachments/mentions.

## Features
- **Random Messages**: Selects a random message based on the target text channel's entire history and sends it there($targetchat must be called first for it to work).
- **Random Message Configuration**: Allows server-specific settings for the bot's selection of random messages(urls, attachments).

## Installation
To install and run this bot on your server, follow these steps:


## Usage
After inviting the bot to your Discord server, you can use the following commands:
- `$help`: Shows a help message with all available commands.
- `$targetchat #channel`: Sets the target channel for random message fetching.
- `$urls`: Toggles the inclusion of messages with URLs(True/False).
- `$attachments`: Toggles the inclusion of messages with attachments(True/False).
- `$mentions`: Toggles the inclusion of messages with mentions(True/False).
- `$ranmsg`: Sends a random message from the configured channel(targetchat).


### Planned Features
1. Configure where the message should be selected from and where it should be sent to($selectfrom and $sendto commands).
2. Allow users to set an interval where the bot will send a random message on its own ($interval minutes)
3. Listen for the event of joining a new server and update the config accordingly.




