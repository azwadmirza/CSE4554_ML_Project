    async def issue_new_wss_url(self) -> str:
        try:
            response = await self.web_client.apps_connections_open(
                app_token=self.app_token
            )
            return response["url"]
        except SlackApiError as e:
            self.logger.error(f"Failed to retrieve Socket Mode URL: {e}")
            raise e