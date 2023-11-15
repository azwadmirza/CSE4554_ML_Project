    def from_line(cls, line):
        """Create a Log Line from a string line.

        :param line:
        :type line: str
        :return:
        :rtype: LogLine or None
        """
        lines = line.split('\n')
        match = LogLine.log_re.match(lines[0])
        if not match:
            return

        g = match.groupdict()
        return LogLine(line=lines[0], message=g['message'], level_name=g['level_name'], extra=g.get('extra'), curhash=g['curhash'],
                       thread_name=g['thread_name'], thread_id=int(g['thread_id']) if g['thread_id'] else None, traceback_lines=lines[1:],
                       timestamp=datetime.datetime(year=int(g['year']), month=int(g['month']), day=int(g['day']),
                                                   hour=int(g['hour']), minute=int(g['minute']), second=int(g['second'])))