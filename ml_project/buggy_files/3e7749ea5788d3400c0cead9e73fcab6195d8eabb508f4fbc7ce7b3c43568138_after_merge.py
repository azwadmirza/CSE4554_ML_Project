    def issue_new_wss_url(self) -> str:
        """Acquires a new WSS URL using rtm.connect API method"""
        try:
            api_response = self.web_client.rtm_connect()
            return api_response["url"]
        except SlackApiError as e:
            if e.response["error"] == "ratelimited":
                delay = int(e.response.headers.get("Retry-After", "30"))  # Tier1
                self.logger.info(f"Rate limited. Retrying in {delay} seconds...")
                time.sleep(delay)
                # Retry to issue a new WSS URL
                return self.issue_new_wss_url()
            else:
                # other errors
                self.logger.error(f"Failed to retrieve WSS URL: {e}")
                raise e