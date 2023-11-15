def stats_history(runner):
    """Save current stats info to history for charts of report."""
    while True:
        stats = runner.stats
        r = {
            'time': datetime.datetime.now().strftime("%H:%M:%S"),
            'current_rps': stats.total.current_rps or 0,
            'current_fail_per_sec': stats.total.current_fail_per_sec or 0,
            'response_time_percentile_95': stats.total.get_current_response_time_percentile(0.95) or 0,
            'response_time_percentile_50': stats.total.get_current_response_time_percentile(0.5) or 0,
            'user_count': runner.user_count or 0,
        }
        stats.history.append(r)
        gevent.sleep(HISTORY_STATS_INTERVAL_SEC)