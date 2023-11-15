    def format_ts(value):
        if value is None:
            return None
        return datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')