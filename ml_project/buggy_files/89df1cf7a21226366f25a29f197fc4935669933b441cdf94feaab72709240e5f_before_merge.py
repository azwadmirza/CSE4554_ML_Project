    def end_time(self):
        return datetime.strptime(self.nc.attrs['time_coverage_end'].decode(), '%Y-%m-%dT%H:%M:%S.%fZ')