    def serve_once(self):
        self.sc = SlackClient(self.token)
        log.info("Verifying authentication token")
        self.auth = self.api_call("auth.test", raise_errors=False)
        if not self.auth['ok']:
            log.error("Couldn't authenticate with Slack. Server said: %s" % self.auth['error'])
        log.debug("Token accepted")
        self.jid = SlackIdentifier(
            node=self.auth["user_id"],
            domain=self.sc.server.domain,
            resource=self.auth["user_id"]
        )

        log.info("Connecting to Slack real-time-messaging API")
        if self.sc.rtm_connect():
            log.info("Connected")
            self.reset_reconnection_count()
            try:
                while True:
                    for message in self.sc.rtm_read():
                        if 'type' not in message:
                            log.debug("Ignoring non-event message: %s" % message)
                            continue

                        event_type = message['type']
                        event_handler = getattr(self, '_%s_event_handler' % event_type, None)
                        if event_handler is None:
                            log.debug("No event handler available for %s, ignoring this event" % event_type)
                            continue
                        try:
                            log.debug("Processing slack event: %s" % message)
                            event_handler(message)
                        except Exception:
                            log.exception("%s event handler raised an exception" % event_type)
                    time.sleep(1)
            except KeyboardInterrupt:
                log.info("Interrupt received, shutting down..")
                return True
            except:
                log.exception("Error reading from RTM stream:")
            finally:
                log.debug("Triggering disconnect callback")
                self.disconnect_callback()
        else:
            raise Exception('Connection failed, invalid token ?')