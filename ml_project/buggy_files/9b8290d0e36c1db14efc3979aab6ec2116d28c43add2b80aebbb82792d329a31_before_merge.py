    def on_worker_report(client_id, data):
        for stats_data in data["stats"]:
            entry = StatsEntry.unserialize(stats_data)
            request_key = (entry.name, entry.method)
            if not request_key in stats.entries:
                stats.entries[request_key] = StatsEntry(stats, entry.name, entry.method)
            stats.entries[request_key].extend(entry)
    
        for error_key, error in data["errors"].items():
            if error_key not in stats.errors:
                stats.errors[error_key] = StatsError.from_dict(error)
            else:
                stats.errors[error_key].occurrences += error["occurrences"]
        
        # save the old last_request_timestamp, to see if we should store a new copy
        # of the response times in the response times cache
        old_last_request_timestamp = stats.total.last_request_timestamp
        # update the total StatsEntry
        stats.total.extend(StatsEntry.unserialize(data["stats_total"]))
        if stats.total.last_request_timestamp and stats.total.last_request_timestamp > (old_last_request_timestamp or 0):
            # If we've entered a new second, we'll cache the response times. Note that there 
            # might still be reports from other worker nodes - that contains requests for the same
            # time periods - that hasn't been received/accounted for yet. This will cause the cache to 
            # lag behind a second or two, but since StatsEntry.current_response_time_percentile() 
            # (which is what the response times cache is used for) uses an approximation of the 
            # last 10 seconds anyway, it should be fine to ignore this. 
            stats.total._cache_response_times(int(stats.total.last_request_timestamp))