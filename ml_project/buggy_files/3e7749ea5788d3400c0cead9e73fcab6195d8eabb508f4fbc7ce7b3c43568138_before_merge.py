    def issue_new_wss_url(self) -> str:
        """Acquires a new WSS URL using rtm.connect API method"""
        try:
            api_response = self.web_client.rtm_connect()
            return api_response["url"]
        except SlackApiError as e:
            self.logger.error(f"Failed to retrieve WSS URL: {e}")
            raise e