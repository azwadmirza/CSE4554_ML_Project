    def get_end_time(self):
        """
        Returns the end time of the bag.
        @return: a timestamp of the end of the bag
        @rtype: float, timestamp in seconds, includes fractions of a second
        """
        
        if self._chunks:
            end_stamp = self._chunks[-1].end_time.to_sec()
        else:
            if not self._connection_indexes:
                raise ROSBagException('Bag contains no message')
            end_stamp = max([index[-1].time.to_sec() for index in self._connection_indexes.values()])
        
        return end_stamp