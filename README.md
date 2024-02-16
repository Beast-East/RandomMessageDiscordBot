# Random Message Discord Bot

## Description
This Discord bot can select a random message from a text channel's history and send it. The selection of said message can be configured through the use commands. For example, including/excluding messages that contain 
URLs/attachments/mentions.

## Features
- **Random Messages**: Selects a random message based on the specified text channel's entire history and sends it($selectandsend must be called first for it to work).
- **Random Message Configuration**: Allows server-specific settings for the bot's selection of random messages(urls, attachments, mentions).

## Installation
To install and run this bot on your server, follow these steps:


## Usage
After inviting the bot to your Discord server, you can use the following commands:
- `$help`: Shows a help message with all available commands.
- `$selectandsend *#sourcechannel* *#destchannel*` - Set the channel where random messages will be selected from and the channel where said message will be sent to.
- `$urls`: Toggles the inclusion of messages with URLs(True/False).
- `$attachments`: Toggles the inclusion of messages with attachments(True/False).
- `$mentions`: Toggles the inclusion of messages with mentions(True/False).
- `$ranmsg`: Sends a random message from the configured channel(targetchat). 
<br/>Initialize the bot by using `$selectandsend` to define the source and destination channels for the random message feature to function correctly.


### Planned Features
1. Allow users to set an interval where the bot will send a random message on its own ($interval minutes)
2. Listen for the event of joining a new server and update the config accordingly.




