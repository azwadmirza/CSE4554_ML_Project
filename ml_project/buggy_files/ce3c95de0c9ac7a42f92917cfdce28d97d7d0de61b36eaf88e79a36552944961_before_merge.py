    def get_added_date_string(self):
        if self.added_date:
            return self.added_date.strftime("%Y-%m-%dT%H:%M:%S")
        else:
            return Date.now()