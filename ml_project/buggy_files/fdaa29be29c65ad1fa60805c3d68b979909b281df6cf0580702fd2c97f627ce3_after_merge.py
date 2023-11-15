def setup_distributed_stats_event_listeners(events, stats):
    def on_report_to_master(client_id, data):
        data["stats"] = stats.serialize_stats()
        data["stats_total"] = stats.total.get_stripped_report()
        data["errors"] =  stats.serialize_errors()
        stats.errors = {}
    
    def on_worker_report(client_id, data):
        for stats_data in data["stats"]:
            entry = StatsEntry.unserialize(stats_data)
            request_key = (entry.name, entry.method)
            if not request_key in stats.entries:
                stats.entries[request_key] = StatsEntry(stats, entry.name, entry.method, use_response_times_cache=True)
            stats.entries[request_key].extend(entry)
    
        for error_key, error in data["errors"].items():
            if error_key not in stats.errors:
                stats.errors[error_key] = StatsError.from_dict(error)
            else:
                stats.errors[error_key].occurrences += error["occurrences"]
        
        stats.total.extend(StatsEntry.unserialize(data["stats_total"]))
        
    events.report_to_master.add_listener(on_report_to_master)
    events.worker_report.add_listener(on_worker_report)