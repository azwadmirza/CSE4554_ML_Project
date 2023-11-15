    def start_time(self):
        return datetime.strptime(self.nc.attrs['time_coverage_start'].decode(), '%Y-%m-%dT%H:%M:%S.%fZ')