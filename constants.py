KEY_GUILD_NAME = "guild_name"
KEY_ENABLE_ATTACHMENTS = "enable_attachments"
KEY_ENABLE_URLS = "enable_urls"
KEY_ENABLE_MENTIONS = "enable_mentions"
KEY_START_DATE = "start_date"
KEY_SEND_TO = "channel_to_send_to"
KEY_SELECT_FROM = "channel_to_select_from"

HELP_MESSAGE = """
        ** Commands **

        `$help` - Shows this help message.
        `$selectandsend *#sourcechannel* *#destchannel*` - Set the channel where random messages will be selected from
        and the channel where said message will be sent to.
        `$urls` - Toggles the inclusion of messages containing URLs in random message selection(True/False).
         False by default.
        `$mentions` -  Toggles the inclusion of messages with mentions(True/False). False by default. When enabled, 
        @(everyone), @(rolementions) and @(member) mentions are all included.
        `$attachments` - Toggles the inclusion of messages with attachments(True/False). False by default.
        `$ranmsg` - Sends a random message from configured #sourcechannel to the #destchannel.

        Use $selectandsend to define the source and destination channels for the random message feature to 
        function correctly❗
        """