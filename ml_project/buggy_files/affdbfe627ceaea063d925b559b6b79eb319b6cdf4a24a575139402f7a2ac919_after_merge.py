    def process(self):
        self.tempdata = []  # temporary data for parse, parse_line and recover_line
        self.__failed = []
        report = self.receive_message()

        for line in self.parse(report):
            if not line:
                continue
            try:
                # filter out None
                events = list(filter(bool, self.parse_line(line, report)))
            except Exception:
                self.logger.exception('Failed to parse line.')
                self.__failed.append((traceback.format_exc(), line))
            else:
                self.send_message(*events)

        for exc, line in self.__failed:
            report_dump = report.copy()
            report_dump.update('raw', self.recover_line(line))
            self._dump_message(exc, report_dump)

        self.acknowledge_message()