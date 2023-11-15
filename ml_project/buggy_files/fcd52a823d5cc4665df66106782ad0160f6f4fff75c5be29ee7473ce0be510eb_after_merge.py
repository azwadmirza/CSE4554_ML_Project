    def filter(self, record):
        record.user = FilterUserInjector.username
        return True