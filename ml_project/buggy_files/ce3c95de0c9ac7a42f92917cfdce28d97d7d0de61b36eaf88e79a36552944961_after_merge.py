    def get_added_date_string(self):
        FORMAT = '%Y-%m-%dT%H:%M:%S'

        if self.added_date:
            return self.added_date.strftime(FORMAT)
        else:
            return datetime.now().strftime(FORMAT)