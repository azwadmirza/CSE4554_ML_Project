    def viewlog(self, minLevel=logger.INFO, logFilter='<NONE>', logSearch=None, maxLines=1000, **kwargs):
        """View the log given the specified filters."""
        min_level = int(minLevel)
        log_filter = logFilter if logFilter in log_name_filters else '<NONE>'
        log_search = logSearch
        max_lines = maxLines

        t = PageTemplate(rh=self, filename='viewlogs.mako')

        data = []
        log_files = [logger.log_file] + ['{file}.{number}'.format(file=logger.log_file, number=i) for i in range(1, int(sickbeard.LOG_NR))]
        for log_file in log_files:
            if len(data) <= max_lines and ek(os.path.isfile, log_file):
                with io.open(log_file, 'r', encoding='utf-8') as f:
                    data += ErrorLogs._get_data(f.readlines(), min_level, log_filter, log_search, len(data), max_lines)

        return t.render(header='Log File', title='Logs', topmenu='system', logLines=''.join([html_escape(line) for line in data]),
                        minLevel=min_level, logNameFilters=log_name_filters, logFilter=log_filter, logSearch=log_search,
                        controller='errorlogs', action='viewlogs')