    async def connect(self):
        """Connect to the chat service."""
        _LOGGER.info("Connecting to Slack")

        try:
            connection = await self.slacker.rtm.start()
            self.websocket = await websockets.connect(connection.body['url'])

            _LOGGER.debug("Connected as %s", self.bot_name)
            _LOGGER.debug("Using icon %s", self.icon_emoji)
            _LOGGER.debug("Default room is %s", self.default_room)
            _LOGGER.info("Connected successfully")

            if self.keepalive is None or self.keepalive.done():
                self.keepalive = self.opsdroid.eventloop.create_task(
                    self.keepalive_websocket())
        except aiohttp.ClientOSError as error:
            _LOGGER.error(error)
            _LOGGER.error("Failed to connect to Slack, retrying in 10")
            await self.reconnect(10)
        except slacker.Error as error:
            _LOGGER.error("Unable to connect to Slack due to %s - "
                          "The Slack Connector will not be available.", error)
        except Exception:
            await self.disconnect()
            raise