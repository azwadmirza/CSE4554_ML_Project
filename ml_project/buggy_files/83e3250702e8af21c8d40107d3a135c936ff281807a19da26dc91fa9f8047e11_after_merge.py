    def extend(self, other):
        """
        Extend the data from the current StatsEntry with the stats from another
        StatsEntry instance. 
        """
        # save the old last_request_timestamp, to see if we should store a new copy
        # of the response times in the response times cache
        old_last_request_timestamp = self.last_request_timestamp
        
        if self.last_request_timestamp is not None and other.last_request_timestamp is not None:
            self.last_request_timestamp = max(self.last_request_timestamp, other.last_request_timestamp)
        elif other.last_request_timestamp is not None:
            self.last_request_timestamp = other.last_request_timestamp
        self.start_time = min(self.start_time, other.start_time)

        self.num_requests = self.num_requests + other.num_requests
        self.num_none_requests = self.num_none_requests + other.num_none_requests
        self.num_failures = self.num_failures + other.num_failures
        self.total_response_time = self.total_response_time + other.total_response_time
        self.max_response_time = max(self.max_response_time, other.max_response_time)
        if self.min_response_time is not None and other.min_response_time is not None:
            self.min_response_time = min(self.min_response_time, other.min_response_time)
        elif other.min_response_time is not None:
            # this means self.min_response_time is None, so we can safely replace it
            self.min_response_time = other.min_response_time
        self.total_content_length = self.total_content_length + other.total_content_length

        for key in other.response_times:
            self.response_times[key] = self.response_times.get(key, 0) + other.response_times[key]
        for key in other.num_reqs_per_sec:
            self.num_reqs_per_sec[key] = self.num_reqs_per_sec.get(key, 0) + other.num_reqs_per_sec[key]
        for key in other.num_fail_per_sec:
            self.num_fail_per_sec[key] = self.num_fail_per_sec.get(key, 0) + other.num_fail_per_sec[key]
        
        if self.use_response_times_cache:
            # If we've entered a new second, we'll cache the response times. Note that there 
            # might still be reports from other worker nodes - that contains requests for the same
            # time periods - that hasn't been received/accounted for yet. This will cause the cache to 
            # lag behind a second or two, but since StatsEntry.current_response_time_percentile() 
            # (which is what the response times cache is used for) uses an approximation of the 
            # last 10 seconds anyway, it should be fine to ignore this. 
            last_time = self.last_request_timestamp and int(self.last_request_timestamp) or None
            if last_time and last_time > (old_last_request_timestamp and int(old_last_request_timestamp) or 0):
                self._cache_response_times(last_time)