    def __init__(self, token: Text, slack_channel: Optional[Text] = None) -> None:

        self.slack_channel = slack_channel
        self.client = WebClient(token, run_async=True)
        super().__init__()