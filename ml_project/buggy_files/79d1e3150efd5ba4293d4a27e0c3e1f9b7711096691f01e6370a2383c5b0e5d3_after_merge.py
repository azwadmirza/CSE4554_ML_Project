    def format_ts(value):
        if value is None or np.isnan(value):
            return None
        return datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')