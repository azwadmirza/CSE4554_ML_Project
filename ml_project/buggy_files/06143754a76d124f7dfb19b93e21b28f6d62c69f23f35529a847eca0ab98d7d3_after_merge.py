    def compute_initial_figure(self):
        self.axes.cla()
        self.axes.set_title("MBytes given/taken over time", color="#e0e0e0")
        self.axes.set_xlabel("Date")
        self.axes.set_ylabel("Given/taken data (MBytes)")

        self.axes.xaxis.set_major_formatter(DateFormatter('%d-%m-%y'))

        self.axes.plot(self.plot_data[1], self.plot_data[0][0], label="MBytes given", marker='o')
        self.axes.plot(self.plot_data[1], self.plot_data[0][1], label="MBytes taken", marker='o')
        self.axes.grid(True)

        for line in self.axes.get_xgridlines() + self.axes.get_ygridlines():
            line.set_linestyle('--')

        # Color the axes
        if hasattr(self.axes, 'set_facecolor'):  # Not available on Linux
            self.axes.set_facecolor('#464646')
        self.axes.xaxis.label.set_color('#e0e0e0')
        self.axes.yaxis.label.set_color('#e0e0e0')
        self.axes.tick_params(axis='x', colors='#e0e0e0')
        self.axes.tick_params(axis='y', colors='#e0e0e0')

        # Create the legend
        handles, labels = self.axes.get_legend_handles_labels()
        self.axes.legend(handles, labels)

        if len(self.plot_data[0][0]) == 1:  # If we only have one data point, don't show negative axis
            self.axes.set_ylim(-0.3, 10)
            self.axes.set_xlim(datetime.datetime.now() - datetime.timedelta(hours=1),
                               datetime.datetime.now() + datetime.timedelta(days=4))

        self.draw()