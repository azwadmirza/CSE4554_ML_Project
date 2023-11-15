    def write_resource_logs(self, time_seconds):
        with open(self.resource_log_file, "a+") as output_file:
            output_file.write("%s, %s, %s\n" % (time_seconds,
                                                self.memory_data[len(self.memory_data)-1][1],
                                                self.cpu_data[len(self.cpu_data)-1][1]))