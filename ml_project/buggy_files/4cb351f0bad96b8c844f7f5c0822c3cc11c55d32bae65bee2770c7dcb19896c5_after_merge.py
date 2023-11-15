    def get_start_time(self):
        """
        Returns the start time of the bag.
        @return: a timestamp of the start of the bag
        @rtype: float, timestamp in seconds, includes fractions of a second
        """
        
        if self._chunks:
            start_stamp = self._chunks[0].start_time.to_sec()
        else:
            if not self._connection_indexes:
                raise ROSBagException('Bag contains no message')
            start_stamps = [index[0].time.to_sec() for index in self._connection_indexes.values() if index]
            start_stamp = min(start_stamps) if start_stamps else 0
        
        return start_stamp