    def send_message(self, *messages):
        messages = filter(self.__filter_empty_report, messages)
        messages = map(self.__add_report_fields, messages)
        super(CollectorBot, self).send_message(*messages)