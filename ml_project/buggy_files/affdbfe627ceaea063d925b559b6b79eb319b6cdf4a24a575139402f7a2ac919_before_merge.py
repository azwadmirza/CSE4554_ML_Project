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
            except Exception as exc:
                self.logger.exception('Failed to parse line.')
                self.__failed.append((exc, line))
            else:
                self.send_message(*events)

        for exc, line in self.__failed:
            self._dump_message(exc, self.recover_line(line))

        self.acknowledge_message()