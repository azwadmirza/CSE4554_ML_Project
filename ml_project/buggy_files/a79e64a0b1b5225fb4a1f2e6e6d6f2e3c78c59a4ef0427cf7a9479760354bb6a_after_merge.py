    def send_message(self, *messages, auto_add=True):
        """"
        Parameters:
            messages: Instances of intelmq.lib.message.Message class
            auto_add: Add some default report fields form parameters
        """
        messages = filter(self.__filter_empty_report, messages)
        if auto_add:
            messages = map(self.__add_report_fields, messages)
        super(CollectorBot, self).send_message(*messages)