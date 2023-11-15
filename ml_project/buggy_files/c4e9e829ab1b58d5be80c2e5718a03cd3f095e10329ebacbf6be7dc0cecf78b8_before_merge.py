    async def _retrieve_websocket_info(self):
        """Retrieves the WebSocket info from Slack.

        Returns:
            A tuple of websocket information.
            e.g.
            (
                "wss://...",
                {
                    "self": {"id": "U01234ABC","name": "robotoverlord"},
                    "team": {
                        "domain": "exampledomain",
                        "id": "T123450FP",
                        "name": "ExampleName"
                    }
                }
            )

        Raises:
            SlackApiError: Unable to retrieve RTM URL from Slack.
        """
        if self._web_client is None:
            self._web_client = WebClient(
                token=self.token,
                base_url=self.base_url,
                ssl=self.ssl,
                proxy=self.proxy,
                run_async=True,
                loop=self._event_loop,
                session=self._session,
                headers=self.headers,
            )
        self._logger.debug("Retrieving websocket info.")
        use_rtm_start = self.connect_method in ["rtm.start", "rtm_start"]
        if self.run_async:
            if use_rtm_start:
                resp = await self._web_client.rtm_start()
            else:
                resp = await self._web_client.rtm_connect()
        else:
            if use_rtm_start:
                resp = self._web_client.rtm_start()
            else:
                resp = self._web_client.rtm_connect()

        url = resp.get("url")
        if url is None:
            msg = "Unable to retrieve RTM URL from Slack."
            raise client_err.SlackApiError(message=msg, response=resp)
        return url, resp.data