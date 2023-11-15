    async def issue_new_wss_url(self) -> str:
        try:
            response = await self.web_client.apps_connections_open(
                app_token=self.app_token
            )
            return response["url"]
        except SlackApiError as e:
            if e.response["error"] == "ratelimited":
                # NOTE: ratelimited errors rarely occur with this endpoint
                delay = int(e.response.headers.get("Retry-After", "30"))  # Tier1
                self.logger.info(f"Rate limited. Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
                # Retry to issue a new WSS URL
                return await self.issue_new_wss_url()
            else:
                # other errors
                self.logger.error(f"Failed to retrieve WSS URL: {e}")
                raise e