    def push_data_to_plot(self, upload, download):
        # Keep only last 100 records to show in graph
        if len(self.plot_data[1]) > 100:
            self.plot_data[1] = self.plot_data[1][-100:]
            self.plot_data[0][0] = self.plot_data[0][0][-100:]
            self.plot_data[0][1] = self.plot_data[0][1][-100:]

        self.plot_data[1].append(datetime.datetime.now())
        self.plot_data[0][0].append(upload / self.byte_scale)
        self.plot_data[0][1].append(download / self.byte_scale)