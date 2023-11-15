    def get_last_updated_series(self, from_time, weeks=1, filter_show_list=None):
        """Retrieve a list with updated shows.

        :param from_time: epoch timestamp, with the start date/time
        :param weeks: number of weeks to get updates for.
        :param filter_show_list: Optional list of show objects, to use for filtering the returned list.
        :returns: A list of show_id's.
        """
        total_updates = []
        updates = True

        count = 0
        try:
            while updates and count < weeks:
                updates = self.updates_api.updated_query_get(from_time).data
                if updates is not None:
                    last_update_ts = max(x.last_updated for x in updates)
                    from_time = last_update_ts
                    total_updates += [int(_.id) for _ in updates]
                count += 1
        except (ApiException, MaxRetryError, RequestError) as e:
            raise IndexerUnavailable('Error connecting to Tvdb api. Caused by: {0!r}'.format(e))

        if total_updates and filter_show_list:
            new_list = []
            for show in filter_show_list:
                if show.indexerid in total_updates:
                    new_list.append(show.indexerid)
            total_updates = new_list

        return total_updates