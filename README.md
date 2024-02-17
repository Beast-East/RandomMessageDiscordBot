# Random Message Discord Bot

## Description
This Discord bot can select a random message from a text channel's history and send it(this behaviour can be configured). The criteria for the selection of said message can be configured through the use of commands. For example, including/excluding messages that contain URLs/attachments/mentions.

## Features
- **Random Messages**: Selects a random message based on the specified text channel's entire history and sends it($selectandsend must be called first for it to work).
- **Random Message Configuration**: Allows server-specific settings for the bot's selection of random messages(urls, attachments, mentions).

## Installation
To install and run this bot on your server(can support mutliple servers), follow these steps:
1. Install [python](https://www.python.org/downloads/)(be sure to check the "Add Python to PATH" checkbox during installation).
2. Download this repository and extract the files onto a folder.
3. Install dependencies by executing the following command on the terminal: `pip install -r directory\requirements.txt` where *directory* the path of the folder that the extracted files are in.
4. Generate a [discord bot token](https://discordgsm.com/guide/how-to-get-a-discord-bot-token) and make sure to enable the following permissions: 
![image](https://github.com/Beast-East/random-message-discord-bot/assets/138492796/78e11a91-bd03-403d-ad10-0e1b73ba42b3)
5. Rename .env.template to `.env` and open it with a text editor of your choice. 
In it, `BOT_TOKEN=your_token_here`, where *your_token_here* should be replaced with your token(spaces should not be included anywhere in the .env file).
6. Execute run.py on the terminal using `directory\run.py` where *directory* the same as step 3.

## Usage
After inviting the bot to your Discord server, you can use the following commands:
- `$help`: Shows a help message with all available commands.
- `$selectandsend *#sourcechannel* *#destchannel*` - Set the channel where random messages will be selected from and the channel where said message will be sent to.
- `$urls`: Toggles the inclusion of messages with URLs(True/False). False by default.
- `$attachments`: Toggles the inclusion of messages with attachments(True/False). False by default.
- `$mentions`: Toggles the inclusion of messages with mentions(True/False). False by default. When enabled, @everyone, @rolementions and @member mentions are all included.
- `$ranmsg`: Sends a random message from the configured #sourcechannel to the #destchannel.
<br/><br/>❗Initialize the bot by using `$selectandsend` to define the source and destination channels for the random message feature to function correctly❗
