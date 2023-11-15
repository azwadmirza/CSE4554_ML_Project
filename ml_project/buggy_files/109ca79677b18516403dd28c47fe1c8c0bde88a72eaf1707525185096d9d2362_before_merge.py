    def parse(self, report):
        if self.mode == 'fixed':
            return self.parse_csv_dict(report)

        # Set config to parse report
        self.report_name = report.get('extra.file_name')
        filename_search = self.__is_filename_regex.search(self.report_name)

        if not filename_search:
            raise ValueError("Report's 'extra.file_name' {!r} is not valid.".format(self.report_name))
        else:
            self.report_name = filename_search.group(1)
            self.logger.debug("Detected report's file name: {!r}.".format(self.report_name))
            retval = config.get_feed_by_filename(self.report_name)

            if not retval:
                raise ValueError('Could not get a config for {!r}, check the documentation.'
                                 ''.format(self.report_name))
            self.feedname, self.sparser_config = retval

        # Set default csv parse function
        return self.parse_csv_dict(report)