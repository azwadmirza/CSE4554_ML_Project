    def viewlog(self, minLevel=logger.INFO, logFilter='<NONE>', logSearch=None, maxLines=1000):
        min_level = minLevel
        log_filter = logFilter

        def Get_Data(Levelmin, data_in, lines_in, regex, Filter, Search, mlines):

            last_line = False
            num_lines = lines_in
            num_to_show = min(maxLines, num_lines + len(data_in))

            final_data = []

            for x in reversed(data_in):
                match = re.match(regex, x)

                if match:
                    level = match.group(7)
                    log_name = match.group(8)
                    if level not in logger.LOGGING_LEVELS:
                        last_line = False
                        continue

                    if logSearch and logSearch.lower() in x.lower():
                        last_line = True
                        final_data.append(x)
                        num_lines += 1
                    elif not logSearch and logger.LOGGING_LEVELS[level] >= min_level and (log_filter == '<NONE>' or log_name.startswith(log_filter)):
                        last_line = True
                        final_data.append(x)
                        num_lines += 1
                    else:
                        last_line = False
                        continue

                elif last_line:
                    final_data.append('AA' + x)
                    num_lines += 1

                if num_lines >= num_to_show:
                    return final_data

            return final_data

        t = PageTemplate(rh=self, filename='viewlogs.mako')

        min_level = int(min_level)

        log_name_filters = {
            '<NONE>': '&lt;No Filter&gt;',
            'DAILYSEARCHER': 'Daily Searcher',
            'BACKLOG': 'Backlog',
            'SHOWUPDATER': 'Show Updater',
            'CHECKVERSION': 'Check Version',
            'SHOWQUEUE': 'Show Queue',
            'SEARCHQUEUE': 'Search Queue (All)',
            'SEARCHQUEUE-DAILY-SEARCH': 'Search Queue (Daily Searcher)',
            'SEARCHQUEUE-BACKLOG': 'Search Queue (Backlog)',
            'SEARCHQUEUE-MANUAL': 'Search Queue (Manual)',
            'SEARCHQUEUE-FORCED': 'Search Queue (Forced)',
            'SEARCHQUEUE-RETRY': 'Search Queue (Retry/Failed)',
            'SEARCHQUEUE-RSS': 'Search Queue (RSS)',
            'SHOWQUEUE-FORCE-UPDATE': 'Show Queue (Forced Update)',
            'SHOWQUEUE-UPDATE': 'Show Queue (Update)',
            'SHOWQUEUE-REFRESH': 'Show Queue (Refresh)',
            'SHOWQUEUE-FORCE-REFRESH': 'Show Queue (Forced Refresh)',
            'FINDPROPERS': 'Find Propers',
            'POSTPROCESSOR': 'PostProcessor',
            'FINDSUBTITLES': 'Find Subtitles',
            'TRAKTCHECKER': 'Trakt Checker',
            'EVENT': 'Event',
            'ERROR': 'Error',
            'TORNADO': 'Tornado',
            'Thread': 'Thread',
            'MAIN': 'Main',
        }

        if log_filter not in log_name_filters:
            log_filter = '<NONE>'

        regex = r'^(\d\d\d\d)\-(\d\d)\-(\d\d)\s*(\d\d)\:(\d\d):(\d\d)\s*([A-Z]+)\s*(.+?)\s*\:\:\s*(.*)$'

        data = []

        if ek(os.path.isfile, logger.log_file):
            with io.open(logger.log_file, 'r', encoding='utf-8') as f:
                data = Get_Data(min_level, f.readlines(), 0, regex, log_filter, logSearch, maxLines)

        for i in range(1, int(sickbeard.LOG_NR)):
            log_file = '{file}.{number}'.format(file=logger.log_file, number=i)
            if ek(os.path.isfile, log_file) and (len(data) <= maxLines):
                with io.open(log_file, 'r', encoding='utf-8') as f:
                    data += Get_Data(min_level, f.readlines(), len(data), regex, log_filter, logSearch, maxLines)

        return t.render(
            header='Log File', title='Logs', topmenu='system',
            logLines=''.join(data), minLevel=min_level, logNameFilters=log_name_filters,
            logFilter=log_filter, logSearch=logSearch,
            controller='errorlogs', action='viewlogs')