    def tmpl_time(s, fmt):
        """Format a time value using `strftime`.
        """
        cur_fmt = beets.config['time_format'].get(unicode)
        return time.strftime(fmt, time.strptime(s, cur_fmt))