    def get_output_channel(
        self, channel: Optional[Text] = None, thread_id: Optional[Text] = None
    ) -> OutputChannel:
        channel = channel or self.slack_channel
        return SlackBot(self.slack_token, channel, thread_id)