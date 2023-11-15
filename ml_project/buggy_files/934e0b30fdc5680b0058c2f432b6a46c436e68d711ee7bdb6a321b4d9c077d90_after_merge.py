    def getUpdates(self, offset=None, limit=100, timeout=0, network_delay=5., **kwargs):
        """Use this method to receive incoming updates using long polling.

        Args:
          offset (Optional[int]):
            Identifier of the first update to be returned. Must be greater by  one than the highest
            among the identifiers of previously received updates. By default, updates starting with
            the earliest unconfirmed update are returned. An update is considered confirmed as soon
            as getUpdates is called with an offset higher than its update_id.
          limit (Optional[int]):
            Limits the number of updates to be retrieved. Values between 1-100 are accepted.
            Defaults to 100.
          timeout (Optional[int]):
            Timeout in seconds for long polling. Defaults to 0, i.e. usual short polling.
          network_delay (Optional[float]):
            Additional timeout in seconds to allow the response from Telegram servers. This should
            cover network latency around the globe, SSL handshake and slowness of the Telegram
            servers (which unfortunately happens a lot recently - 2016-05-28). Defaults to 5.

        Returns:
            list[:class:`telegram.Update`]

        Raises:
            :class:`telegram.TelegramError`

        """

        url = '{0}/getUpdates'.format(self.base_url)

        data = {'timeout': timeout}

        if offset:
            data['offset'] = offset
        if limit:
            data['limit'] = limit

        urlopen_timeout = timeout + network_delay

        result = request.post(url, data, timeout=urlopen_timeout)

        if result:
            self.logger.debug('Getting updates: %s', [u['update_id'] for u in result])
        else:
            self.logger.debug('No new updates found.')

        return [Update.de_json(x) for x in result]