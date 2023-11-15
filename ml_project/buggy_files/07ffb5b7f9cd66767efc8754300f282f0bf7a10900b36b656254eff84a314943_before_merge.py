    def __init__(self, append_text):
        logging.Handler.__init__(self)
        self.append_text = append_text
        self.update_log_level()