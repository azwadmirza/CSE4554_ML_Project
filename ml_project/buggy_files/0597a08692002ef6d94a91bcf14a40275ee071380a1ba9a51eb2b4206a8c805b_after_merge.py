    def get_returns_no_block(
            self,
            tag,
            match_type=None):
        '''
        Raw function to just return events of jid excluding timeout logic

        Yield either the raw event data or None

        Pass a list of additional regular expressions as `tags_regex` to search
        the event bus for non-return data, such as minion lists returned from
        syndics.
        '''

        while True:
            try:
                raw = self.event.get_event(wait=0.01, tag=tag, match_type=match_type, full=True, no_block=True)
                yield raw
            except tornado.iostream.StreamClosedError:
                if self.auto_reconnect:
                    log.warning('Connection to master lost. Reconnecting.')
                    self.event.close_pub()
                    self.event.connect_pub(timeout=self._get_timeout(None))
                else:
                    raise