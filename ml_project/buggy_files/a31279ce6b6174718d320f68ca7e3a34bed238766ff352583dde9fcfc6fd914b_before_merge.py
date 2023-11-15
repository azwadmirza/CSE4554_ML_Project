    def add_data(self, timestamp, data, skip_old=False):
        if skip_old and timestamp < self.last_timestamp:
            return
        self.plot_data[0].append(timestamp)
        for i, data_item in enumerate(data):
            self.plot_data[1][i].append(data_item)
        self.last_timestamp = timestamp