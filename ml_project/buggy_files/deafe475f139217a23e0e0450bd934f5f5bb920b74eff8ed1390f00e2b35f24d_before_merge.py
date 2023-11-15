    def set_filters(self, can_filters=None):
        """Apply filtering to all messages received by this Bus.

        Calling without passing any filters will reset the applied filters.

        Since Kvaser only supports setting one filter per handle, the filtering
        will be done in the :meth:`recv` if more than one filter is requested.

        :param list can_filters:
            A list of dictionaries each containing a "can_id" and a "can_mask".

            >>> [{"can_id": 0x11, "can_mask": 0x21}]

            A filter matches, when ``<received_can_id> & can_mask == can_id & can_mask``
        """
        if can_filters and len(can_filters) == 1:
            can_id = can_filters[0]['can_id']
            can_mask = can_filters[0]['can_mask']
            extended = 1 if can_filters[0].get('extended') else 0
            log.info('canlib is filtering on ID 0x%X, mask 0x%X', can_id, can_mask)
            for handle in (self._read_handle, self._write_handle):
                canSetAcceptanceFilter(handle, can_id, can_mask, extended)
        else:
            log.info('Hardware filtering has been disabled')
            for handle in (self._read_handle, self._write_handle):
                for extended in (0, 1):
                    canSetAcceptanceFilter(handle, 0, 0, extended)