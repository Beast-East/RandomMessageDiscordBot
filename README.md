# Random Message Discord Bot

## Description
This Discord bot can select a random message from a text channel's history and send it. The criteria for the selection of said message and the text channel where it is sent to can be configured through the use of commands. For example, selecting a random message including/excluding messages that contain URLs/attachments/mentions from #chat1 to #chat2 or from #chat1 to itself.

## Features
- **Random Messages**: Selects a random message based on the specified text channel's entire history and sends it($selectandsend must be called first for it to work).
- **Random Message Configuration**: Allows server-specific settings for the bot's selection of random messages(urls, attachments, mentions).
- **Multi-server Support**: Capable of running on multiple servers simultaneously.
  
## Installation
To install and run this bot on your server(can support mutliple servers), follow these steps:
1. Install [python](https://www.python.org/downloads/)(be sure to check the "Add Python to PATH" checkbox during installation).
2. Download this repository and extract the files onto a folder.
3. Install dependencies by executing the following command on the terminal: `pip install -r directory\requirements.txt` where *directory* the path of the folder that the extracted files are in.
4. Generate a [discord bot token](https://discordgsm.com/guide/how-to-get-a-discord-bot-token) and make sure to enable the following permissions: 
![image](https://github.com/Beast-East/random-message-discord-bot/assets/138492796/78e11a91-bd03-403d-ad10-0e1b73ba42b3)
5. Open .env.template with a text editor of your choice. In it, `BOT_TOKEN=your_token_here`, where *your_token_here* should be replaced with your token(spaces should not be included anywhere in the .env file).
Finally, click "save as" and name it `.env`.
7. Execute run.py on the terminal using `python directory\run.py` where *directory* is the same as in step 3.
<br/><br/>❗Close the terminal or press Ctrl + C(in the terminal) to terminate the program❗

## Usage
After inviting the bot to your Discord server, you can use the following commands:
- `$help`: Shows a help message with all available commands.
- `$selectandsend *#sourcechannel* *#destchannel*`: - Set the channel where random messages will be selected from and the channel where said message will be sent to.
- `$urls`: Toggles the inclusion of messages containing URLs(True/False). False by default.
- `$attachments`: Toggles the inclusion of messages containing attachments(True/False). False by default.
- `$mentions`: Toggles the inclusion of messages containing mentions(True/False). False by default. When enabled, @everyone, @rolementions and @member mentions are all included.
- `$ranmsg`: Sends a random message from the configured #sourcechannel to the #destchannel.
<br/><br/>❗Initialize the bot by using `$selectandsend` to define the source and destination channels for the random message feature to function correctly❗
